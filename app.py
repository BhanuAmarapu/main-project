from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import sqlite3
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import Config
from ml_model import MLModel, get_ext_code
from dedup import Deduplicator
from auditing import Auditor
from utils import log_action
from suspicious_upload_detector import SuspiciousUploadDetector

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Initialize modules
ml_model = MLModel()
deduplicator = Deduplicator()
auditor = Auditor()
suspicious_detector = SuspiciousUploadDetector()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
        conn.close()
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_TEMP'], filename)
            file.save(temp_path)
            
            # Step 1: ML Prediction (instant analysis)
            file_size = os.path.getsize(temp_path)
            ext_code = get_ext_code(filename)
            
            # Open database connection for all queries
            conn = get_db_connection()
            
            # Get frequency
            freq = conn.execute("SELECT COUNT(*) FROM files WHERE file_name = ?", (filename,)).fetchone()[0]
            
            # Find similar files based on metadata
            similar_files = conn.execute("""
                SELECT id, file_name, file_size, file_hash, upload_timestamp 
                FROM files 
                WHERE file_name = ? OR (file_size BETWEEN ? AND ? AND file_type = ?)
                ORDER BY upload_timestamp DESC
                LIMIT 5
            """, (filename, file_size - 1024, file_size + 1024, filename.split('.')[-1])).fetchall()
            
            # Close connection after all queries
            conn.close()
            
            prediction = ml_model.predict({
                'file_size': file_size,
                'extension_code': ext_code,
                'frequency': freq + 1
            })
            
            # If ML predicts duplicate, show confirmation page
            if prediction == 1 or freq > 0:
                return render_template('upload_confirmation.html',
                                     filename=filename,
                                     temp_path=temp_path,
                                     file_size=file_size,
                                     prediction=prediction,
                                     similar_files=similar_files,
                                     ml_confidence="High" if prediction == 1 else "Medium")

            
            # Step 2: Deduplication (if user confirms or no duplicates predicted)
            is_duplicate, file_id = deduplicator.process_file(temp_path, filename, current_user.id)
            
            # Step 3: Suspicious Activity Detection
            if Config.ENABLE_SUSPICIOUS_DETECTOR:
                # Track rapid uploads
                is_rapid, rapid_msg = suspicious_detector.track_upload(current_user.id)
                if is_rapid and rapid_msg:
                    flash(rapid_msg, 'warning')
                
                # Track duplicate attempts if this is a duplicate
                if is_duplicate:
                    # Get file hash from database
                    temp_conn = get_db_connection()
                    file_hash_row = temp_conn.execute("SELECT file_hash FROM files WHERE id = ?", (file_id,)).fetchone()
                    temp_conn.close()
                    
                    if file_hash_row:
                        is_excessive, dup_msg = suspicious_detector.track_duplicate_attempt(current_user.id, file_hash_row[0])
                        if is_excessive and dup_msg:
                            flash(dup_msg, 'danger')

            
            if is_duplicate:
                flash(f"DUPLICATE ALERT: An identical file was already found in the system. Redirecting for access mapping.")
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return render_template('results.html', 
                                   filename=filename, 
                                   prediction=prediction, 
                                   is_duplicate=is_duplicate,
                                   file_id=file_id)
            
    return render_template('upload.html')

@app.route('/confirm_upload', methods=['POST'])
@login_required
def confirm_upload():
    """Handle user's decision to store or skip the file"""
    action = request.form.get('action')
    filename = request.form.get('filename')
    
    if action == 'skip':
        flash(f'Upload cancelled. File "{filename}" was not stored.', 'info')
        return redirect(url_for('upload_file'))
    
    # User chose to store - process the file
    temp_path = os.path.join(app.config['UPLOAD_TEMP'], filename)
    
    if not os.path.exists(temp_path):
        flash('File not found. Please upload again.', 'danger')
        return redirect(url_for('upload_file'))
    
    # Process the file
    is_duplicate, file_id = deduplicator.process_file(temp_path, filename, current_user.id)
    
    # Track suspicious activity
    if Config.ENABLE_SUSPICIOUS_DETECTOR:
        is_rapid, rapid_msg = suspicious_detector.track_upload(current_user.id)
        if is_rapid and rapid_msg:
            flash(rapid_msg, 'warning')
        
        if is_duplicate:
            temp_conn = get_db_connection()
            file_hash_row = temp_conn.execute("SELECT file_hash FROM files WHERE id = ?", (file_id,)).fetchone()
            temp_conn.close()
            
            if file_hash_row:
                is_excessive, dup_msg = suspicious_detector.track_duplicate_attempt(current_user.id, file_hash_row[0])
                if is_excessive and dup_msg:
                    flash(dup_msg, 'danger')
    
    if is_duplicate:
        flash(f"File stored successfully! Duplicate detected - linked to existing file.", 'success')
    else:
        flash(f'File "{filename}" uploaded and encrypted successfully!', 'success')
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    files = conn.execute("SELECT * FROM files").fetchall()
    total_files = len(files)
    
    logical_size = conn.execute("""
        SELECT SUM(f.file_size) 
        FROM uploads u 
        JOIN files f ON u.file_id = f.id
    """).fetchone()[0] or 0
    
    physical_size = conn.execute("SELECT SUM(file_size) FROM files").fetchall()[0][0] or 0
    
    dedup_rate = 0
    if logical_size > 0:
        dedup_rate = ((logical_size - physical_size) / logical_size) * 100
        
    audit_logs = conn.execute("SELECT a.*, f.file_name FROM audits a JOIN files f ON a.file_id = f.id ORDER BY a.timestamp DESC LIMIT 10").fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                           files=files, 
                           total_files=total_files,
                           logical_size=logical_size,
                           physical_size=physical_size,
                           dedup_rate=round(dedup_rate, 2),
                           audit_logs=audit_logs)

@app.route('/audit/<int:file_id>')
@login_required
def audit(file_id):
    success, message = auditor.audit_file(file_id)
    flash(message)
    return redirect(url_for('dashboard'))

@app.route('/view/<int:file_id>')
@login_required
def view_file(file_id):
    if current_user.role != 'admin':
        flash('Permission denied. Privileged access required.')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    file_data = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    conn.close()
    
    if not file_data:
        flash('File not found')
        return redirect(url_for('dashboard'))
    
    stored_path = file_data['stored_path']
    filename = file_data['file_name']
    
    if stored_path.startswith("s3://"):
        # Stream from S3
        from utils import get_s3_client, decrypt_file
        s3 = get_s3_client()
        if not s3:
            flash("S3 service is not available.")
            return redirect(url_for('dashboard'))
            
        s3_object_name = stored_path.split("/")[-1]
        temp_encrypted_path = os.path.join(Config.UPLOAD_TEMP, f"enc_{s3_object_name}")
        temp_decrypted_path = os.path.join(Config.UPLOAD_TEMP, f"view_{filename}")
        
        try:
            # Download encrypted file from S3
            s3.download_file(Config.S3_BUCKET_NAME, s3_object_name, temp_encrypted_path)
            
            # Decrypt it
            decrypt_file(temp_encrypted_path, temp_decrypted_path, None)
            
            def generate():
                with open(temp_decrypted_path, 'rb') as f:
                    yield from f
                # Cleanup after streaming
                if os.path.exists(temp_encrypted_path):
                    os.remove(temp_encrypted_path)
                if os.path.exists(temp_decrypted_path):
                    os.remove(temp_decrypted_path)

            from flask import Response
            return Response(generate(), mimetype='application/octet-stream',
                            headers={"Content-Disposition": f"attachment;filename={filename}"})
            
        except Exception as e:
            flash(f"Error fetching or decrypting from S3: {e}")
            if os.path.exists(temp_encrypted_path):
                os.remove(temp_encrypted_path)
            return redirect(url_for('dashboard'))
    else:
        # Local file
        # In this system, local files are encrypted, so we need to decrypt for viewing
        temp_view_path = os.path.join(Config.UPLOAD_TEMP, f"view_{filename}")
        from utils import decrypt_file
        try:
            decrypt_file(stored_path, temp_view_path, None) # Uses default key logic
            
            def generate():
                with open(temp_view_path, 'rb') as f:
                    yield from f
                if os.path.exists(temp_view_path):
                    os.remove(temp_view_path)

            from flask import Response
            return Response(generate(), mimetype='application/octet-stream',
                            headers={"Content-Disposition": f"attachment;filename={filename}"})
        except Exception as e:
            flash(f"Error decrypting file: {e}")
            return redirect(url_for('dashboard'))

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    if current_user.role != 'admin':
        flash('Permission denied.')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    file_data = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    
    if file_data:
        stored_path = file_data['stored_path']
        file_name = file_data['file_name']
        
        try:
            # 1. Delete from S3 if applicable
            if stored_path.startswith("s3://"):
                from utils import get_s3_client
                s3 = get_s3_client()
                if not s3:
                    flash("Warning: S3 service is not available for deletion.")
                else:
                    s3_key = stored_path.replace(f"s3://{Config.S3_BUCKET_NAME}/", "")
                    try:
                        s3.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=s3_key)
                        log_action("Delete", f"Deleted {file_name} from S3")
                    except Exception as e:
                        flash(f"Warning: S3 deletion failed ({e}), proceed with DB cleanup.")
            elif os.path.exists(stored_path):
                # Delete local file
                os.remove(stored_path)
                log_action("Delete", f"Deleted {file_name} from local storage")

            # 2. Delete database records in order of dependency
            conn.execute("DELETE FROM uploads WHERE file_id = ?", (file_id,))
            conn.execute("DELETE FROM audits WHERE file_id = ?", (file_id,))
            conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
            flash(f"Success: File '{file_name}' and all associated records deleted.")
        except Exception as e:
            conn.rollback()
            flash(f"Error during deletion: {str(e)}")
        finally:
            conn.close()
    else:
        conn.close()
        flash("Error: File record not found in database.")
    
    return redirect(url_for('dashboard'))

@app.route('/rename/<int:file_id>', methods=['POST'])
@login_required
def rename_file(file_id):
    if current_user.role != 'admin':
        flash('Permission denied.')
        return redirect(url_for('dashboard'))
    
    new_name = request.form.get('new_name')
    if not new_name:
        flash("New name cannot be empty.")
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    conn.execute("UPDATE files SET file_name = ? WHERE id = ?", (new_name, file_id))
    conn.commit()
    conn.close()
    
    flash(f"File renamed to '{new_name}'.")
    return redirect(url_for('dashboard'))

@app.route('/alerts')
@login_required
def alerts():
    if current_user.role != 'admin':
        flash('Permission denied. Admin access required.')
        return redirect(url_for('dashboard'))
    
    include_dismissed = request.args.get('dismissed', 'false').lower() == 'true'
    all_alerts = suspicious_detector.get_all_alerts(include_dismissed=include_dismissed)
    
    return render_template('alerts.html', alerts=all_alerts, include_dismissed=include_dismissed)

@app.route('/alerts/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def dismiss_alert(alert_id):
    if current_user.role != 'admin':
        flash('Permission denied.')
        return redirect(url_for('dashboard'))
    
    suspicious_detector.dismiss_alert(alert_id)
    flash('Alert dismissed successfully.')
    return redirect(url_for('alerts'))

@app.route('/api/activity-stats')
@login_required
def activity_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    user_id = request.args.get('user_id', type=int)
    hours = request.args.get('hours', default=24, type=int)
    
    if user_id:
        stats = suspicious_detector.get_user_stats(user_id, hours)
        return jsonify(stats)
    else:
        # Return overall stats
        alert_count = suspicious_detector.get_alert_count()
        return jsonify({'alert_count': alert_count})

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Hybrid ML-CNS Deduplication System...")
    print("=" * 60)
    
    # Check if model exists, only train if needed
    print("\n[1/3] Checking ML Model...")
    if os.path.exists(Config.ML_MODEL_PATH):
        print("✓ ML Model found, skipping training")
    else:
        print("  Training new ML Model...")
        try:
            ml_model.train(Config.ML_DATASET)
            print("✓ ML Model trained successfully")
        except Exception as e:
            print(f"✗ ML Model training failed: {e}")
            print("  Continuing without ML predictions...")
    
    print("\n[2/3] Initializing database...")
    try:
        conn = get_db_connection()
        conn.close()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database error: {e}")
        print("  Please run: python init_db.py")
    
    print("\n[3/3] Starting Flask server...")
    print("=" * 60)
    print("🚀 Server starting on http://127.0.0.1:5000")
    print("   Press CTRL+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print("\n❌ ERROR: Port 5000 is already in use!")
            print("   Please stop other Python processes and try again.")
            print("   Run: Stop-Process -Name python -Force")
        else:
            print(f"\n❌ ERROR: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
