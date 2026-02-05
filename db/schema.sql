CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT,
    stored_path TEXT NOT NULL,
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    file_id INTEGER,
    content_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (file_id) REFERENCES files (id)
);

CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER,
    audit_status TEXT NOT NULL,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files (id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suspicious_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    details TEXT,
    is_dismissed INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_activity_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    upload_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,
    pow_failure_count INTEGER DEFAULT 0,
    last_upload_time DATETIME,
    window_start DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS moderation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    violation_type TEXT NOT NULL,
    violation_details TEXT,
    confidence_score REAL,
    flagged_keywords TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed INTEGER DEFAULT 0,
    reviewer_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS idx_moderation_user ON moderation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_moderation_timestamp ON moderation_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_moderation_reviewed ON moderation_logs(reviewed);
