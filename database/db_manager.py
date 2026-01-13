import sqlite3
from datetime import datetime
from contextlib import contextmanager
import config
from .models import CREATE_TABLES_SQL, MIGRATE_SPACES_TABLE


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()

    def init_database(self):
        """初始化数据库，创建表"""
        with self.get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()
            # 检查是否需要迁移（去掉 UNIQUE 约束）
            self._migrate_if_needed(conn)

    def _migrate_if_needed(self, conn):
        """检查并执行数据库迁移"""
        try:
            # 检查 spaces 表是否有 UNIQUE 约束
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='spaces'")
            result = cursor.fetchone()
            if result and 'UNIQUE' in result[0]:
                # 需要迁移
                print("[数据库] 正在迁移 spaces 表，去掉 UNIQUE 约束...")
                conn.executescript(MIGRATE_SPACES_TABLE)
                conn.commit()
                print("[数据库] 迁移完成")
        except Exception as e:
            print(f"[数据库] 迁移检查失败: {e}")

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=()):
        """执行SQL语句（INSERT, UPDATE, DELETE）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def query(self, query, params=()):
        """查询数据（SELECT）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def query_one(self, query, params=()):
        """查询单条数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None


# 全局数据库实例
db = DatabaseManager()
