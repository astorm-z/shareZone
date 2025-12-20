import os

# 基础配置
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-sharezone-2025'

# 端口配置
PORT = 3333

# 系统密码
SYSTEM_PASSWORD = 'astorm666'

# 数据库配置
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'sharezone.db')

# 文件上传配置
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

# Cookie配置
AUTH_TOKEN_EXPIRES = 7  # 天
SPACE_TOKEN_EXPIRES = 1  # 天

# 清理配置
FILE_EXPIRES_HOURS = 24
SPACE_EXPIRES_HOURS = 24
CLEANUP_INTERVAL_MINUTES = 10

# 允许的图片扩展名
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# 危险的文件扩展名（禁止上传）
DANGEROUS_EXTENSIONS = {'exe', 'sh', 'bat', 'cmd', 'com', 'scr', 'vbs', 'ps1'}
