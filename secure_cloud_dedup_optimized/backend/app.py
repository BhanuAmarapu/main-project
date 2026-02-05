"""
Main Flask application for Secure Cloud Deduplication System
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime

# Import backend modules
from backend.config import Config
from backend.models import db, User, File, Upload, AuditLog
from backend.dedup_manager import DeduplicationManager
from backend.pow_manager import ProofOfWorkManager
from backend.ownership_manager import OwnershipManager
from backend.block_level_dedup import BlockLevelDedup
from backend.performance_monitor import PerformanceMonitor
from backend.encryption import decrypt_file

# Import cloud simulator
from cloud_simulator.optimized_bloom_filter import OptimizedBloomFilter
from cloud_simulator.adaptive_pow import AdaptivePowManager
from cloud_simulator.kek_tree import KEKTree
from cloud_simulator.cloud_storage import CloudStorageSimulator

# Import database utilities
from database.db_manager import DatabaseManager
from database.cache_manager import get_hash_cache

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_SIZE

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize components
bloom_filter = None
dedup_manager = None
pow_manager = None
ownership_manager = None
performance_monitor = None
cloud_simulator = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def init_components():
    """Initialize system components"""
    global bloom_filter, dedup_manager, pow_manager, ownership_manager, performance_monitor, cloud_simulator
    
    # Load or create Bloom filter
    bloom_filter = OptimizedBloomFilter.load_from_db()
    if bloom_filter is None:
        bloom_filter = OptimizedBloomFilter()
        # Add existing file hashes to Bloom filter
        files = File.query.all()
        for file in files:
            bloom_filter.add(file.file_hash)
        bloom_filter.save_to_db()
    
    # Initialize managers
    dedup_manager = DeduplicationManager(bloom_filter=bloom_filter)
    pow_manager = AdaptivePowManager() if Config.POW_ADAPTIVE else ProofOfWorkManager()
    ownership_manager = OwnershipManager()
    performance_monitor = PerformanceMonitor()
    cloud_simulator = CloudStorageSimulator()


@app.route('/')
def index():
    """Homepage"""
    if current_user.is_authenticated:
        # Get user stats
        user_stats = ownership_manager.get_ownership_stats(current_user.id)
        system_stats = performance_monitor.get_system_overview()
        
        return render_template('index.html', 
                             user_stats=user_stats,
                             system_stats=system_stats)
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log action
        log = AuditLog(user_id=user.id, action='User Registration', 
                      details=f'New user registered: {username}',
                      ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Log action
            log = AuditLog(user_id=user.id, action='Login',
                          details=f'User logged in: {username}',
                          ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """File upload"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            
            # Save to temp directory
            temp_path = os.path.join(Config.TEMP_DIR, filename)
            file.save(temp_path)
            
            # Calculate file hash and metadata
            file_hash = get_file_hash(temp_path)
            file_size = os.path.getsize(temp_path)
            file_type = filename.split('.')[-1] if '.' in filename else 'unknown'
            
            # Check if this is a forced upload (user clicked "Store Anyway")
            force_upload = request.form.get('force_upload', 'false') == 'true'
            
            # If not forced, the duplicate check happens on client-side
            # This route only processes actual uploads
            
            # Process file with deduplication
            use_optimized = request.form.get('use_optimized', 'false') == 'true'
            result = dedup_manager.process_file(temp_path, filename, current_user.id, use_optimized=use_optimized)
            
            if result['success']:
                # Grant ownership
                ownership_manager.grant_ownership(current_user.id, result['file_id'])
                
                if result['is_duplicate']:
                    if force_upload:
                        flash(f'File stored successfully! This is a duplicate reference. Space saved: {result["space_saved"] / 1024:.2f} KB', 'success')
                    else:
                        flash(f'Duplicate file detected! Space saved: {result["space_saved"] / 1024:.2f} KB', 'info')
                else:
                    flash(f'File uploaded successfully! Processing time: {result["processing_time"]:.2f}s', 'success')
                
                # Save Bloom filter state
                bloom_filter.save_to_db()
                
                return redirect(url_for('files'))
            else:
                flash('Upload failed', 'error')
    
    return render_template('upload.html')


@app.route('/api/check_duplicate', methods=['POST'])
@login_required
def check_duplicate():
    """API endpoint to check for duplicate files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save to temp directory
        filename = secure_filename(file.filename)
        temp_path = os.path.join(Config.TEMP_DIR, f"check_{current_user.id}_{filename}")
        file.save(temp_path)
        
        # Calculate file hash and metadata
        file_hash = get_file_hash(temp_path)
        file_size = os.path.getsize(temp_path)
        file_type = filename.split('.')[-1] if '.' in filename else 'unknown'
        
        # Check for duplicates with details
        result = dedup_manager.check_duplicate_with_details(
            file_hash, filename, file_size, file_type
        )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if result['is_duplicate'] and result['similar_files']:
            similar_file_data = result['similar_files'][0]  # Get most similar
            existing_file = similar_file_data['file']
            similarity = similar_file_data['similarity']
            match_type = similar_file_data['match_type']
            
            return jsonify({
                'is_duplicate': True,
                'match_type': match_type,
                'similarity': similarity,
                'existing_file': {
                    'id': existing_file.id,
                    'name': existing_file.file_name,
                    'size': existing_file.file_size,
                    'size_mb': round(existing_file.file_size / (1024 * 1024), 2),
                    'type': existing_file.file_type,
                    'upload_date': existing_file.upload_date.strftime('%b %d, %Y'),
                    'reference_count': existing_file.reference_count
                }
            })
        else:
            return jsonify({'is_duplicate': False})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file_details/<int:file_id>')
@login_required
def file_details(file_id):
    """API endpoint to get file details"""
    try:
        file = File.query.get_or_404(file_id)
        
        # Get upload count
        upload_count = Upload.query.filter_by(file_id=file_id).count()
        
        return jsonify({
            'id': file.id,
            'name': file.file_name,
            'size': file.file_size,
            'size_mb': round(file.file_size / (1024 * 1024), 2),
            'type': file.file_type,
            'upload_date': file.upload_date.strftime('%b %d, %Y %H:%M'),
            'reference_count': file.reference_count,
            'upload_count': upload_count,
            'is_encrypted': file.is_encrypted,
            'encryption_method': file.encryption_method,
            'is_in_cloud': file.is_in_cloud
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/files')
@login_required
def files():
    """List user files"""
    user_files = ownership_manager.get_user_files(current_user.id)
    return render_template('files.html', files=user_files)


@app.route('/dashboard')
@login_required
def dashboard():
    """Performance dashboard"""
    system_overview = performance_monitor.get_system_overview()
    dedup_stats = dedup_manager.get_dedup_stats()
    upload_stats = performance_monitor.get_upload_stats(24)
    encryption_stats = performance_monitor.get_encryption_stats(24)
    
    # Bloom filter stats
    bf_stats = bloom_filter.get_stats()
    
    # Cache stats
    cache = get_hash_cache()
    cache_stats = cache.get_stats()
    
    return render_template('dashboard.html',
                         system_overview=system_overview,
                         dedup_stats=dedup_stats,
                         upload_stats=upload_stats,
                         encryption_stats=encryption_stats,
                         bloom_filter_stats=bf_stats,
                         cache_stats=cache_stats)


@app.route('/api/metrics/realtime')
@login_required
def realtime_metrics():
    """Get real-time metrics for dashboard"""
    metrics = performance_monitor.get_realtime_metrics()
    return jsonify(metrics)


@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for statistics"""
    stats = {
        'dedup': dedup_manager.get_dedup_stats(),
        'bloom_filter': bloom_filter.get_stats(),
        'pow': pow_manager.get_stats() if hasattr(pow_manager, 'get_adaptive_stats') else pow_manager.get_stats(),
        'cache': get_hash_cache().get_stats()
    }
    return jsonify(stats)


@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    """Download file"""
    # Verify ownership
    if not ownership_manager.verify_ownership(current_user.id, file_id):
        flash('You do not have permission to download this file', 'error')
        return redirect(url_for('files'))
    
    file = File.query.get_or_404(file_id)
    
    # Decrypt file to temp location
    temp_output = os.path.join(Config.TEMP_DIR, f"download_{file.id}_{file.file_name}")
    
    if file.is_in_cloud:
        # Download from cloud first
        from backend.cloud_utils import download_from_s3
        cloud_temp = os.path.join(Config.TEMP_DIR, f"cloud_{file.id}")
        object_name = os.path.basename(file.cloud_path)
        
        if download_from_s3(object_name, cloud_temp):
            decrypt_file(cloud_temp, temp_output)
            os.remove(cloud_temp)
        else:
            flash('Failed to download from cloud', 'error')
            return redirect(url_for('files'))
    else:
        decrypt_file(file.stored_path, temp_output)
    
    return send_file(temp_output, as_attachment=True, download_name=file.file_name)


if __name__ == '__main__':
    # Initialize app
    Config.init_app()
    
    with app.app_context():
        db.create_all()
        
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        db_manager.create_admin_user()
        
        # Initialize components
        init_components()
    
    # Run app
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
