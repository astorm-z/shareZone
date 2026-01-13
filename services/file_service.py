from datetime import datetime, timedelta
import os
import config
from database.db_manager import db
from utils.validators import validate_filename, sanitize_filename, is_image_file, validate_file_size
from utils.file_handler import generate_stored_filename, get_upload_path, delete_physical_file, get_mime_type


class FileService:
    """文件管理服务"""

    def create_text_content(self, space_id, content):
        """创建纯文本内容"""
        preview_text = content[:100] + '...' if len(content) > 100 else content
        expires_at = datetime.now() + timedelta(hours=config.FILE_EXPIRES_HOURS)

        file_id = db.execute(
            """INSERT INTO files (space_id, file_type, content, preview_text, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (space_id, 'text', content, preview_text, expires_at)
        )

        return {'success': True, 'file_id': file_id}

    def upload_file(self, space_id, file):
        """上传文件"""
        # 验证文件名
        if not validate_filename(file.filename):
            return {'success': False, 'message': '文件名不合法'}

        # 验证文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if not validate_file_size(file_size):
            return {'success': False, 'message': '文件大小超过20MB限制'}

        # 生成存储文件名
        original_filename = sanitize_filename(file.filename)
        stored_filename = generate_stored_filename(original_filename)

        # 确定文件类型
        from utils.validators import is_text_file
        file_type = 'image' if is_image_file(original_filename) else 'file'
        mime_type = get_mime_type(original_filename)

        # 保存文件
        file_path = get_upload_path(stored_filename)
        file.save(file_path)

        # 如果是文本文件，读取内容用于预览
        content = None
        preview_text = None
        if is_text_file(original_filename):
            from utils.file_handler import read_text_file
            content = read_text_file(file_path)
            if content:
                preview_text = content[:100] + '...' if len(content) > 100 else content

        # 存入数据库
        expires_at = datetime.now() + timedelta(hours=config.FILE_EXPIRES_HOURS)
        file_id = db.execute(
            """INSERT INTO files (space_id, filename, stored_filename, file_type, mime_type,
                                  file_size, file_path, content, preview_text, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (space_id, original_filename, stored_filename, file_type, mime_type,
             file_size, file_path, content, preview_text, expires_at)
        )

        return {'success': True, 'file_id': file_id}

    def get_files_by_space(self, space_id):
        """获取空间内的所有文件"""
        files = db.query(
            """SELECT * FROM files
               WHERE space_id = ? AND is_deleted = 0 AND expires_at > ?
               ORDER BY created_at DESC""",
            (space_id, datetime.now())
        )
        return files

    def get_file_by_id(self, file_id):
        """根据ID获取文件"""
        file = db.query_one(
            """SELECT * FROM files
               WHERE id = ? AND is_deleted = 0 AND expires_at > ?""",
            (file_id, datetime.now())
        )
        return file

    def update_text_content(self, file_id, content):
        """更新文本内容"""
        file = self.get_file_by_id(file_id)
        if not file or file['file_type'] != 'text':
            return {'success': False, 'message': '文件不存在或不是文本类型'}

        preview_text = content[:100] + '...' if len(content) > 100 else content

        db.execute(
            "UPDATE files SET content = ?, preview_text = ? WHERE id = ?",
            (content, preview_text, file_id)
        )

        return {'success': True}

    def delete_file(self, file_id):
        """删除文件"""
        file = self.get_file_by_id(file_id)
        if not file:
            return {'success': False, 'message': '文件不存在'}

        # 如果是物理文件，删除物理文件
        if file['file_path']:
            delete_physical_file(file['file_path'])

        # 标记为已删除
        db.execute(
            "UPDATE files SET is_deleted = 1 WHERE id = ?",
            (file_id,)
        )

        return {'success': True}

    def get_file_content(self, file_id):
        """获取文件内容（用于下载或预览）"""
        file = self.get_file_by_id(file_id)
        if not file:
            return None

        if file['file_type'] == 'text':
            return file['content'].encode('utf-8'), 'text/plain; charset=utf-8'
        else:
            return file['file_path'], file['mime_type']

    def extend_file_expiry(self, file_id, hours=24):
        """延长文件过期时间"""
        file = self.get_file_by_id(file_id)
        if not file:
            return {'success': False, 'message': '文件不存在'}

        # 计算新的过期时间
        current_expires = datetime.fromisoformat(file['expires_at']) if isinstance(file['expires_at'], str) else file['expires_at']
        new_expires = current_expires + timedelta(hours=hours)

        # 检查是否超过最大延长时间（从创建时间算起最多7天）
        created_at = datetime.fromisoformat(file['created_at']) if isinstance(file['created_at'], str) else file['created_at']
        max_expires = created_at + timedelta(days=config.MAX_EXTEND_DAYS)

        if new_expires > max_expires:
            new_expires = max_expires

        # 如果已经达到最大时间，不能再延长
        if current_expires >= max_expires:
            return {'success': False, 'message': '已达到最大保留时间（7天）'}

        db.execute(
            "UPDATE files SET expires_at = ? WHERE id = ?",
            (new_expires, file_id)
        )

        return {'success': True, 'new_expires_at': new_expires.isoformat()}
