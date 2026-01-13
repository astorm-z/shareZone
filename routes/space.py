from flask import Blueprint, render_template, request, jsonify, make_response, redirect
from datetime import timedelta
from services.space_service import SpaceService
from services.auth_service import AuthService
import config

bp = Blueprint('space', __name__)
space_service = SpaceService()
auth_service = AuthService()


@bp.route('/home')
def home_page():
    """首页"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return redirect('/api/auth/login-page')
    return render_template('home.html')


@bp.route('/space/<int:space_id>')
def space_page(space_id):
    """空间页面"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return redirect('/api/auth/login-page')
    return render_template('space.html', space_id=space_id)


@bp.route('/api/spaces', methods=['GET'])
def get_spaces():
    """获取空间列表"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    spaces = space_service.get_spaces_by_token(auth_token)
    return jsonify({'success': True, 'spaces': spaces})


@bp.route('/api/spaces', methods=['POST'])
def create_space():
    """创建空间"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'success': False, 'message': '空间名称和密码不能为空'}), 400

    result = space_service.create_space(name, password)

    if result['success']:
        # 记录访问
        space_service.record_space_access(auth_token, result['space_id'])

        # 设置空间密码cookie
        response = make_response(jsonify(result))
        response.set_cookie(
            f'space_{result["space_id"]}',
            result['password_hash'],
            max_age=config.SPACE_TOKEN_EXPIRES * 24 * 60 * 60,
            httponly=True,
            samesite='Lax'
        )
        return response

    return jsonify(result), 400


@bp.route('/api/spaces/enter', methods=['POST'])
def enter_space():
    """进入空间"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'success': False, 'message': '密码不能为空'}), 400

    result = space_service.enter_space(password)

    if result['success']:
        space = result['space']
        # 记录访问
        space_service.record_space_access(auth_token, space['id'])

        # 设置空间密码cookie
        response = make_response(jsonify(result))
        response.set_cookie(
            f'space_{space["id"]}',
            space['password_hash'],
            max_age=config.SPACE_TOKEN_EXPIRES * 24 * 60 * 60,
            httponly=True,
            samesite='Lax'
        )
        return response

    return jsonify(result), 400


@bp.route('/api/spaces/<int:space_id>', methods=['DELETE'])
def delete_space(space_id):
    """删除空间"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    result = space_service.delete_space(space_id)

    if result['success']:
        # 删除空间密码cookie
        response = make_response(jsonify(result))
        response.set_cookie(f'space_{space_id}', '', max_age=0)
        return response

    return jsonify(result), 400


@bp.route('/api/spaces/<int:space_id>/access', methods=['PUT'])
def update_access(space_id):
    """更新访问时间"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    space_service.record_space_access(auth_token, space_id)
    return jsonify({'success': True})


@bp.route('/api/spaces/<int:space_id>/extend', methods=['POST'])
def extend_space(space_id):
    """延长空间过期时间"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json() or {}
    hours = data.get('hours', 24)

    result = space_service.extend_space_expiry(space_id, hours)

    if result['success']:
        return jsonify(result)
    return jsonify(result), 400
