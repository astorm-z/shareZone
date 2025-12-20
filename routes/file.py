from flask import Blueprint, request, jsonify, send_file
from services.file_service import FileService
from services.space_service import SpaceService
from services.auth_service import AuthService

bp = Blueprint('file', __name__)
file_service = FileService()
space_service = SpaceService()
auth_service = AuthService()


@bp.route('/api/spaces/<int:space_id>/files', methods=['GET'])
def get_files(space_id):
    """获取空间内的文件列表"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    space = space_service.get_space_by_id(space_id)
    if not space:
        return jsonify({'success': False, 'message': '空间不存在'}), 404

    files = file_service.get_files_by_space(space_id)
    return jsonify({'success': True, 'files': files, 'space': space})


@bp.route('/api/spaces/<int:space_id>/files', methods=['POST'])
def upload_file(space_id):
    """上传文件或提交文本"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    space = space_service.get_space_by_id(space_id)
    if not space:
        return jsonify({'success': False, 'message': '空间不存在'}), 404

    # 判断是文本还是文件
    if request.content_type and 'application/json' in request.content_type:
        # 文本内容
        data = request.get_json()
        content_type = data.get('type')
        content = data.get('content')

        if content_type == 'text' and content:
            result = file_service.create_text_content(space_id, content)
            return jsonify(result)
        else:
            return jsonify({'success': False, 'message': '参数错误'}), 400
    else:
        # 文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '文件名为空'}), 400

        result = file_service.upload_file(space_id, file)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400


@bp.route('/api/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """获取文件信息"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    file = file_service.get_file_by_id(file_id)
    if not file:
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    return jsonify({'success': True, 'file': file})


@bp.route('/api/files/<int:file_id>/content', methods=['GET'])
def get_file_content(file_id):
    """获取文件内容（用于预览图片）"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    result = file_service.get_file_content(file_id)
    if not result:
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    content, mime_type = result

    if isinstance(content, bytes):
        # 文本内容
        from flask import Response
        return Response(content, mimetype=mime_type)
    else:
        # 文件路径
        return send_file(content, mimetype=mime_type)


@bp.route('/api/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """下载文件"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    file = file_service.get_file_by_id(file_id)
    if not file:
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    if file['file_type'] == 'text':
        # 文本内容
        from flask import Response
        content = file['content'].encode('utf-8')
        return Response(
            content,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment; filename=text.txt'}
        )
    else:
        # 文件
        return send_file(
            file['file_path'],
            as_attachment=True,
            download_name=file['filename']
        )


@bp.route('/api/files/<int:file_id>', methods=['PUT'])
def update_file(file_id):
    """更新文件（仅文本）"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    content = data.get('content')

    if content is None:
        return jsonify({'success': False, 'message': '内容不能为空'}), 400

    result = file_service.update_text_content(file_id, content)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@bp.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    auth_token = request.cookies.get('auth_token')
    if not auth_token or not auth_service.validate_token(auth_token):
        return jsonify({'success': False, 'message': '未登录'}), 401

    result = file_service.delete_file(file_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400
