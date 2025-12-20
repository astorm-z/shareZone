import hashlib
import secrets


def hash_password(password):
    """使用SHA256加盐哈希密码"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password, hash_string):
    """验证密码"""
    try:
        salt, pwd_hash = hash_string.split('$')
        return pwd_hash == hashlib.sha256((password + salt).encode()).hexdigest()
    except:
        return False
