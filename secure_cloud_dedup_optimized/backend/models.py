"""
Database models for the secure cloud deduplication system
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    uploads = db.relationship('Upload', backref='user', lazy='dynamic')
    ownerships = db.relationship('Ownership', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class File(db.Model):
    """File model for stored files"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50))
    stored_path = db.Column(db.String(500), nullable=False)
    is_encrypted = db.Column(db.Boolean, default=True)
    encryption_method = db.Column(db.String(50), default='convergent')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    reference_count = db.Column(db.Integer, default=1)
    is_deduplicated = db.Column(db.Boolean, default=False)
    
    # Block-level deduplication
    has_blocks = db.Column(db.Boolean, default=False)
    
    # Cloud storage
    is_in_cloud = db.Column(db.Boolean, default=False)
    cloud_path = db.Column(db.String(500))
    
    # Relationships
    uploads = db.relationship('Upload', backref='file', lazy='dynamic')
    blocks = db.relationship('Block', backref='file', lazy='dynamic')
    ownerships = db.relationship('Ownership', backref='file', lazy='dynamic')
    
    def __repr__(self):
        return f'<File {self.file_name}>'


class Upload(db.Model):
    """Upload tracking model"""
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    was_duplicate = db.Column(db.Boolean, default=False)
    upload_time_ms = db.Column(db.Integer)  # Upload time in milliseconds
    
    def __repr__(self):
        return f'<Upload user={self.user_id} file={self.file_id}>'


class Block(db.Model):
    """Block model for block-level deduplication"""
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    block_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    block_size = db.Column(db.Integer, nullable=False)
    stored_path = db.Column(db.String(500), nullable=False)
    reference_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    
    def __repr__(self):
        return f'<Block {self.block_hash[:8]}...>'


class Ownership(db.Model):
    """Ownership verification model"""
    __tablename__ = 'ownerships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    challenge_hash = db.Column(db.String(64))
    response_hash = db.Column(db.String(64))
    verification_method = db.Column(db.String(50), default='pow')
    
    def __repr__(self):
        return f'<Ownership user={self.user_id} file={self.file_id}>'


class PerformanceMetric(db.Model):
    """Performance metrics model"""
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)  # 'upload', 'dedup', 'encryption', etc.
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20))  # 'ms', 'bytes', 'ratio', etc.
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    metadata = db.Column(db.Text)  # JSON string for additional data
    
    def __repr__(self):
        return f'<Metric {self.metric_type}={self.metric_value}{self.metric_unit}>'


class AuditLog(db.Model):
    """Audit log model"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} at {self.timestamp}>'


class BloomFilterState(db.Model):
    """Bloom filter state for persistence"""
    __tablename__ = 'bloom_filter_state'
    
    id = db.Column(db.Integer, primary_key=True)
    filter_data = db.Column(db.LargeBinary, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    hash_count = db.Column(db.Integer, nullable=False)
    item_count = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BloomFilter items={self.item_count}>'


class KEKTreeNode(db.Model):
    """KEK Tree node for key management"""
    __tablename__ = 'kek_tree_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    parent_id = db.Column(db.String(64), db.ForeignKey('kek_tree_nodes.node_id'))
    key_hash = db.Column(db.String(64), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    is_leaf = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for tree structure
    children = db.relationship('KEKTreeNode', backref=db.backref('parent', remote_side=[node_id]))
    
    def __repr__(self):
        return f'<KEKNode {self.node_id} level={self.level}>'
