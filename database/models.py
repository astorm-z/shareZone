"""
数据库表结构定义
"""

CREATE_TABLES_SQL = """
-- 空间表
CREATE TABLE IF NOT EXISTS spaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_spaces_expires ON spaces(expires_at);
CREATE INDEX IF NOT EXISTS idx_spaces_password ON spaces(password_hash);
CREATE INDEX IF NOT EXISTS idx_spaces_name ON spaces(name);

-- 文件表
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    space_id INTEGER NOT NULL,
    filename VARCHAR(255),
    stored_filename VARCHAR(255),
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100),
    file_size INTEGER,
    content TEXT,
    preview_text TEXT,
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT 0,
    FOREIGN KEY (space_id) REFERENCES spaces(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_files_space ON files(space_id);
CREATE INDEX IF NOT EXISTS idx_files_expires ON files(expires_at);

-- 认证令牌表
CREATE TABLE IF NOT EXISTS auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_valid BOOLEAN DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_tokens_token ON auth_tokens(token);
CREATE INDEX IF NOT EXISTS idx_tokens_expires ON auth_tokens(expires_at);

-- 空间访问记录表
CREATE TABLE IF NOT EXISTS space_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR(255) NOT NULL,
    space_id INTEGER NOT NULL,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (space_id) REFERENCES spaces(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_access_token ON space_access(token);
CREATE INDEX IF NOT EXISTS idx_access_space ON space_access(space_id);
"""

# 迁移脚本：去掉 spaces 表的 UNIQUE 约束
MIGRATE_SPACES_TABLE = """
-- 创建新表（无 UNIQUE 约束）
CREATE TABLE IF NOT EXISTS spaces_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT 0
);

-- 复制数据
INSERT INTO spaces_new (id, name, password_hash, created_at, last_accessed_at, expires_at, is_deleted)
SELECT id, name, password_hash, created_at, last_accessed_at, expires_at, is_deleted FROM spaces;

-- 删除旧表
DROP TABLE spaces;

-- 重命名新表
ALTER TABLE spaces_new RENAME TO spaces;

-- 重建索引
CREATE INDEX IF NOT EXISTS idx_spaces_expires ON spaces(expires_at);
CREATE INDEX IF NOT EXISTS idx_spaces_password ON spaces(password_hash);
CREATE INDEX IF NOT EXISTS idx_spaces_name ON spaces(name);
"""
