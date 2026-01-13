from datetime import datetime, timedelta
import config
from database.db_manager import db
from utils.security import hash_password, verify_password


class SpaceService:
    """空间管理服务"""

    def create_space(self, name, password):
        """创建空间"""
        # 先将已过期的同名空间标记为删除（释放名称）
        db.execute(
            "UPDATE spaces SET is_deleted = 1 WHERE name = ? AND expires_at <= ?",
            (name, datetime.now())
        )

        # 检查空间名称是否已存在（排除已删除和已过期的）
        existing_name = db.query_one(
            "SELECT id FROM spaces WHERE name = ? AND is_deleted = 0 AND expires_at > ?",
            (name, datetime.now())
        )
        if existing_name:
            return {'success': False, 'message': '空间名称已存在'}

        # 生成密码哈希
        password_hash = hash_password(password)

        # 先将已过期的同密码空间标记为删除（释放密码）
        db.execute(
            "UPDATE spaces SET is_deleted = 1 WHERE password_hash = ? AND expires_at <= ?",
            (password_hash, datetime.now())
        )

        # 检查密码是否已被使用（排除已删除和已过期的）
        existing_password = db.query_one(
            "SELECT id FROM spaces WHERE password_hash = ? AND is_deleted = 0 AND expires_at > ?",
            (password_hash, datetime.now())
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

    def extend_space_expiry(self, space_id, hours=24):
        """延长空间过期时间"""
        space = self.get_space_by_id(space_id)
        if not space:
            return {'success': False, 'message': '空间不存在'}

        # 计算新的过期时间
        current_expires = datetime.fromisoformat(space['expires_at']) if isinstance(space['expires_at'], str) else space['expires_at']
        new_expires = current_expires + timedelta(hours=hours)

        # 检查是否超过最大延长时间（从创建时间算起最多7天）
        created_at = datetime.fromisoformat(space['created_at']) if isinstance(space['created_at'], str) else space['created_at']
        max_expires = created_at + timedelta(days=config.MAX_EXTEND_DAYS)

        if new_expires > max_expires:
            new_expires = max_expires

        # 如果已经达到最大时间，不能再延长
        if current_expires >= max_expires:
            return {'success': False, 'message': '已达到最大保留时间（7天）'}

        db.execute(
            "UPDATE spaces SET expires_at = ? WHERE id = ?",
            (new_expires, space_id)
        )

        return {'success': True, 'new_expires_at': new_expires.isoformat()}
