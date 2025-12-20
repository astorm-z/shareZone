from datetime import datetime, timedelta
import config
from database.db_manager import db
from utils.security import hash_password, verify_password


class SpaceService:
    """空间管理服务"""

    def create_space(self, name, password):
        """创建空间"""
        # 检查空间名称是否已存在
        existing_name = db.query_one(
            "SELECT id FROM spaces WHERE name = ? AND is_deleted = 0",
            (name,)
        )
        if existing_name:
            return {'success': False, 'message': '空间名称已存在'}

        # 生成密码哈希
        password_hash = hash_password(password)

        # 检查密码是否已被使用（密码必须唯一）
        existing_password = db.query_one(
            "SELECT id FROM spaces WHERE password_hash = ? AND is_deleted = 0",
            (password_hash,)
        )
        if existing_password:
            return {'success': False, 'message': '该密码已被使用，请更换密码'}

        # 创建空间
        expires_at = datetime.now() + timedelta(hours=config.SPACE_EXPIRES_HOURS)
        space_id = db.execute(
            "INSERT INTO spaces (name, password_hash, expires_at) VALUES (?, ?, ?)",
            (name, password_hash, expires_at)
        )

        return {'success': True, 'space_id': space_id, 'password_hash': password_hash}

    def enter_space(self, password):
        """通过密码进入空间"""
        # 查询所有未删除的空间
        spaces = db.query(
            "SELECT * FROM spaces WHERE is_deleted = 0 AND expires_at > ?",
            (datetime.now(),)
        )

        # 验证密码
        for space in spaces:
            if verify_password(password, space['password_hash']):
                # 更新最后访问时间
                db.execute(
                    "UPDATE spaces SET last_accessed_at = ? WHERE id = ?",
                    (datetime.now(), space['id'])
                )
                return {'success': True, 'space': space}

        return {'success': False, 'message': '密码错误或空间不存在'}

    def get_spaces_by_token(self, token):
        """获取用户访问过的空间列表"""
        spaces = db.query("""
            SELECT DISTINCT s.* FROM spaces s
            INNER JOIN space_access sa ON s.id = sa.space_id
            WHERE sa.token = ? AND s.is_deleted = 0 AND s.expires_at > ?
            ORDER BY sa.accessed_at DESC
        """, (token, datetime.now()))

        return spaces

    def record_space_access(self, token, space_id):
        """记录空间访问"""
        db.execute(
            "INSERT INTO space_access (token, space_id) VALUES (?, ?)",
            (token, space_id)
        )

    def delete_space(self, space_id):
        """删除空间"""
        # 标记空间为已删除
        db.execute(
            "UPDATE spaces SET is_deleted = 1 WHERE id = ?",
            (space_id,)
        )

        # 标记空间内所有文件为已删除
        db.execute(
            "UPDATE files SET is_deleted = 1 WHERE space_id = ?",
            (space_id,)
        )

        return {'success': True}

    def get_space_by_id(self, space_id):
        """根据ID获取空间"""
        space = db.query_one(
            "SELECT * FROM spaces WHERE id = ? AND is_deleted = 0 AND expires_at > ?",
            (space_id, datetime.now())
        )
        return space
