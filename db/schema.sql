CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(500) NOT NULL,
    file_hash VARCHAR(255) UNIQUE NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50),
    stored_path VARCHAR(1000) NOT NULL,
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_id INT,
    content_text LONGTEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (file_id) REFERENCES files (id)
);

CREATE TABLE IF NOT EXISTS audits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT,
    audit_status VARCHAR(255) NOT NULL,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files (id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suspicious_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    description TEXT,
    details TEXT,
    is_dismissed TINYINT DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_activity_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    upload_count INT DEFAULT 0,
    duplicate_count INT DEFAULT 0,
    pow_failure_count INT DEFAULT 0,
    last_upload_time DATETIME,
    window_start DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS moderation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    violation_type VARCHAR(255) NOT NULL,
    violation_details TEXT,
    confidence_score FLOAT,
    flagged_keywords TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed TINYINT DEFAULT 0,
    reviewer_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE INDEX idx_moderation_user ON moderation_logs(user_id);
CREATE INDEX idx_moderation_timestamp ON moderation_logs(timestamp);
CREATE INDEX idx_moderation_reviewed ON moderation_logs(reviewed);
