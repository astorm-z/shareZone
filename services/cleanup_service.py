from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import config
from database.db_manager import db
from utils.file_handler import delete_physical_file


class CleanupService:
    """定时清理服务"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
        self.scheduler.start()

    def setup_jobs(self):
        """设置定时任务"""
        # 每10分钟清理一次过期文件
        self.scheduler.add_job(
            self.cleanup_expired_files,
            'interval',
            minutes=config.CLEANUP_INTERVAL_MINUTES,
            id='cleanup_files'
        )

        # 每10分钟清理一次过期空间
        self.scheduler.add_job(
            self.cleanup_expired_spaces,
            'interval',
            minutes=config.CLEANUP_INTERVAL_MINUTES,
            id='cleanup_spaces'
        )

        # 每天清理一次过期的认证令牌
        self.scheduler.add_job(
            self.cleanup_expired_tokens,
            'interval',
            hours=24,
            id='cleanup_tokens'
        )

    def cleanup_expired_files(self):
        """清理过期文件"""
        try:
            now = datetime.now()

            # 查询过期文件
            expired_files = db.query(
                "SELECT * FROM files WHERE expires_at < ? AND is_deleted = 0",
                (now,)
            )

            count = 0
            for file in expired_files:
                # 删除物理文件
                if file['file_path']:
                    delete_physical_file(file['file_path'])

                # 标记为已删除
                db.execute(
                    "UPDATE files SET is_deleted = 1 WHERE id = ?",
                    (file['id'],)
                )
                count += 1

            if count > 0:
                print(f"[清理服务] 清理了 {count} 个过期文件")

        except Exception as e:
            print(f"[清理服务] 清理过期文件失败: {e}")

    def cleanup_expired_spaces(self):
        """清理过期空间"""
        try:
            now = datetime.now()

            # 查询过期空间
            expired_spaces = db.query(
                "SELECT * FROM spaces WHERE expires_at < ? AND is_deleted = 0",
                (now,)
            )

            count = 0
            for space in expired_spaces:
                # 查询空间内的所有文件
                files = db.query(
                    "SELECT * FROM files WHERE space_id = ? AND is_deleted = 0",
                    (space['id'],)
                )

                # 删除空间内的所有物理文件
                for file in files:
                    if file['file_path']:
                        delete_physical_file(file['file_path'])

                # 标记空间内所有文件为已删除
                db.execute(
                    "UPDATE files SET is_deleted = 1 WHERE space_id = ?",
                    (space['id'],)
                )

                # 标记空间为已删除
                db.execute(
                    "UPDATE spaces SET is_deleted = 1 WHERE id = ?",
                    (space['id'],)
                )
                count += 1

            if count > 0:
                print(f"[清理服务] 清理了 {count} 个过期空间")

        except Exception as e:
            print(f"[清理服务] 清理过期空间失败: {e}")

    def cleanup_expired_tokens(self):
        """清理过期的认证令牌"""
        try:
            now = datetime.now()

            # 删除过期的令牌
            db.execute(
                "DELETE FROM auth_tokens WHERE expires_at < ?",
                (now,)
            )

            print(f"[清理服务] 清理了过期的认证令牌")

        except Exception as e:
            print(f"[清理服务] 清理过期令牌失败: {e}")

    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
