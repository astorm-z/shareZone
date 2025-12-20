from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for
from datetime import timedelta
from services.auth_service import AuthService
import config

bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_service = AuthService()


@bp.route('/login-page')
def login_page():
    """登录页面"""
    return render_template('login.html')


@bp.route('/login', methods=['POST'])
def login():
    """登录验证"""
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'success': False, 'message': '请输入密码'}), 400

    if auth_service.verify_system_password(password):
        token, expires_at = auth_service.generate_token()
        response = make_response(jsonify({'success': True}))
        response.set_cookie(
            'auth_token',
            token,
            max_age=config.AUTH_TOKEN_EXPIRES * 24 * 60 * 60,
            httponly=True,
            samesite='Lax'
        )
        return response

    return jsonify({'success': False, 'message': '密码错误'}), 401


@bp.route('/logout', methods=['POST'])
def logout():
    """登出"""
    auth_token = request.cookies.get('auth_token')
    if auth_token:
        auth_service.invalidate_token(auth_token)

    response = make_response(jsonify({'success': True}))
    response.set_cookie('auth_token', '', max_age=0)
    return response


@bp.route('/verify', methods=['GET'])
def verify():
    """验证token"""
    auth_token = request.cookies.get('auth_token')
    is_valid = auth_service.validate_token(auth_token)
    return jsonify({'success': is_valid})
