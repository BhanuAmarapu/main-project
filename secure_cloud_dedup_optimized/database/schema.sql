-- Enhanced database schema for secure cloud deduplication system

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50),
    stored_path VARCHAR(500) NOT NULL,
    is_encrypted BOOLEAN DEFAULT 1,
    encryption_method VARCHAR(50) DEFAULT 'convergent',
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference_count INTEGER DEFAULT 1,
    is_deduplicated BOOLEAN DEFAULT 0,
    has_blocks BOOLEAN DEFAULT 0,
    is_in_cloud BOOLEAN DEFAULT 0,
    cloud_path VARCHAR(500)
);

-- Uploads table
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    was_duplicate BOOLEAN DEFAULT 0,
    upload_time_ms INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (file_id) REFERENCES files(id)
);

-- Blocks table (for block-level deduplication)
CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_hash VARCHAR(64) UNIQUE NOT NULL,
    block_size INTEGER NOT NULL,
    stored_path VARCHAR(500) NOT NULL,
    reference_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_id INTEGER,
    FOREIGN KEY (file_id) REFERENCES files(id)
);

-- Ownership table
CREATE TABLE IF NOT EXISTS ownerships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    challenge_hash VARCHAR(64),
    response_hash VARCHAR(64),
    verification_method VARCHAR(50) DEFAULT 'pow',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (file_id) REFERENCES files(id)
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type VARCHAR(50) NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Bloom filter state table
CREATE TABLE IF NOT EXISTS bloom_filter_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filter_data BLOB NOT NULL,
    size INTEGER NOT NULL,
    hash_count INTEGER NOT NULL,
    item_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KEK tree nodes table
CREATE TABLE IF NOT EXISTS kek_tree_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id VARCHAR(64) UNIQUE NOT NULL,
    parent_id VARCHAR(64),
    key_hash VARCHAR(64) NOT NULL,
    level INTEGER NOT NULL,
    is_leaf BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES kek_tree_nodes(node_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash);
CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(block_hash);
CREATE INDEX IF NOT EXISTS idx_uploads_user ON uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_file ON uploads(file_id);
CREATE INDEX IF NOT EXISTS idx_ownerships_user ON ownerships(user_id);
CREATE INDEX IF NOT EXISTS idx_ownerships_file ON ownerships(file_id);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_kek_nodes_id ON kek_tree_nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
