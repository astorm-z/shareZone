from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import config
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

# 启用CORS
CORS(app)

# 确保上传目录存在
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

# 初始化数据库
from database import DatabaseManager
db = DatabaseManager()

# 导入路由
from routes import auth, space, file

# 注册蓝图
app.register_blueprint(auth.bp)
app.register_blueprint(space.bp)
app.register_blueprint(file.bp)

# 启动清理服务
from services.cleanup_service import CleanupService
cleanup_service = CleanupService()


@app.route('/')
def index():
    """首页路由"""
    # 检查是否已登录
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        return redirect(url_for('auth.login_page'))

    # 验证token
    from services.auth_service import AuthService
    auth_service = AuthService()
    if not auth_service.validate_token(auth_token):
        return redirect(url_for('auth.login_page'))

    return redirect(url_for('space.home_page'))


@app.errorhandler(413)
def request_entity_too_large(error):
    """文件过大错误处理"""
    return jsonify({'success': False, 'message': '文件大小超过20MB限制'}), 413


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'success': False, 'message': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=True)
