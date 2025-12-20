import os
from werkzeug.utils import secure_filename
import config


def validate_filename(filename):
    """验证文件名安全性"""
    if not filename:
        return False
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    ext = get_file_extension(filename)
    if ext in config.DANGEROUS_EXTENSIONS:
        return False
    return True


def sanitize_filename(filename):
    """清理文件名"""
    return secure_filename(filename)


def get_file_extension(filename):
    """获取文件扩展名"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def is_image_file(filename):
    """判断是否为图片文件"""
    ext = get_file_extension(filename)
    return ext in config.ALLOWED_IMAGE_EXTENSIONS


def is_text_file(filename):
    """判断是否为文本文件"""
    ext = get_file_extension(filename)
    text_extensions = {'txt', 'md', 'log', 'json', 'xml', 'yaml', 'yml',
                       'csv', 'ini', 'conf', 'py', 'js', 'html', 'css',
                       'java', 'cpp', 'c', 'h', 'go', 'rs', 'sh', 'bat'}
    return ext in text_extensions


def validate_file_size(file_size):
    """验证文件大小"""
    return file_size <= config.MAX_FILE_SIZE
