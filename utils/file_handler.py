import os
import uuid
from datetime import datetime
from PIL import Image
import config


def generate_stored_filename(original_filename):
    """生成存储文件名"""
    ext = ''
    if '.' in original_filename:
        ext = '.' + original_filename.rsplit('.', 1)[1].lower()
    return str(uuid.uuid4()) + ext


def get_upload_path(filename):
    """获取上传文件的存储路径"""
    # 按日期创建子目录
    now = datetime.now()
    date_path = os.path.join(str(now.year), str(now.month).zfill(2), str(now.day).zfill(2))
    full_path = os.path.join(config.UPLOAD_FOLDER, date_path)

    # 确保目录存在
    os.makedirs(full_path, exist_ok=True)

    return os.path.join(full_path, filename)


def read_text_file(file_path):
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except:
            return None
    except:
        return None


def delete_physical_file(file_path):
    """删除物理文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"删除文件失败: {e}")
    return False


def get_mime_type(filename):
    """根据文件扩展名获取MIME类型"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    mime_types = {
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        '7z': 'application/x-7z-compressed',
    }

    return mime_types.get(ext, 'application/octet-stream')
