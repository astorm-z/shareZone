import uuid
import hashlib
from datetime import datetime, timedelta
import config
from database.db_manager import db


class AuthService:
    """认证服务"""

    def verify_system_password(self, password):
        """验证系统密码"""
        return password == config.SYSTEM_PASSWORD

    def verify_system_password_hash(self, pwd_hash):
        """验证系统密码的哈希值"""
        expected_hash = hashlib.sha256(config.SYSTEM_PASSWORD.encode()).hexdigest()
        return pwd_hash == expected_hash

    def generate_token(self):
        """生成认证令牌"""
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=config.AUTH_TOKEN_EXPIRES)

        # 存入数据库
        db.execute(
            "INSERT INTO auth_tokens (token, expires_at) VALUES (?, ?)",
            (token, expires_at)
        )

        return token, expires_at

    def validate_token(self, token):
        """验证令牌有效性"""
        if not token:
            return False

        result = db.query_one(
            "SELECT * FROM auth_tokens WHERE token = ? AND is_valid = 1 AND expires_at > ?",
            (token, datetime.now())
        )

        return result is not None

    def invalidate_token(self, token):
        """使令牌失效"""
        db.execute(
            "UPDATE auth_tokens SET is_valid = 0 WHERE token = ?",
            (token,)
        )
