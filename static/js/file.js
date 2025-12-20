/**
 * 文件操作相关JS
 */

let currentSpaceId = SPACE_ID;
let currentFileId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadSpaceInfo();
    loadFileList();
    setupFileUpload();
    loadSidebarSpaces();
});

// 加载空间信息
async function loadSpaceInfo() {
    try {
        const response = await fetch(`/api/spaces/${currentSpaceId}/files`);
        const data = await response.json();

        if (data.success && data.space) {
            document.getElementById('currentSpaceName').textContent = data.space.name;
        }
    } catch (error) {
        console.error('加载空间信息失败:', error);
    }
}

// 加载侧边栏空间列表
async function loadSidebarSpaces() {
    try {
        const response = await fetch('/api/spaces');
        const data = await response.json();

        if (data.success) {
            const sidebarList = document.getElementById('sidebarSpaceList');
            if (data.spaces.length === 0) {
                sidebarList.innerHTML = '<p class="empty-message">暂无空间</p>';
                return;
            }

            sidebarList.innerHTML = data.spaces.map(space => `
                <div class="sidebar-space-item ${space.id === currentSpaceId ? 'active' : ''}"
                     onclick="goToSpace(${space.id})">
                    ${escapeHtml(space.name)}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载空间列表失败:', error);
    }
}

// 加载文件列表
async function loadFileList() {
    try {
        const response = await fetch(`/api/spaces/${currentSpaceId}/files`);
        const data = await response.json();

        if (data.success) {
            displayFileList(data.files);
        }
    } catch (error) {
        console.error('加载文件列表失败:', error);
    }
}

// 显示文件列表
function displayFileList(files) {
    const fileList = document.getElementById('fileList');

    if (files.length === 0) {
        fileList.innerHTML = '<p class="empty-message">暂无内容</p>';
        return;
    }

    fileList.innerHTML = files.map(file => {
        let icon = '📄';
        if (file.file_type === 'text') {
            icon = '📝';
        } else if (file.file_type === 'image') {
            icon = '🖼️';
        }

        let preview = '';
        if (file.file_type === 'text' && file.preview_text) {
            preview = `<p class="file-preview">${escapeHtml(file.preview_text)}</p>`;
        } else if (file.filename) {
            preview = `<p class="file-name">${escapeHtml(file.filename)}</p>`;
        }

        return `
            <div class="file-item ${currentFileId === file.id ? 'active' : ''}"
                 onclick="selectFile(${file.id})">
                <span class="file-icon">${icon}</span>
                <div class="file-info">
                    ${preview}
                    <p class="file-time">${formatDateTime(file.created_at)}</p>
                </div>
                <button class="file-delete-btn" onclick="event.stopPropagation(); deleteFile(${file.id})" title="删除">🗑️</button>
            </div>
        `;
    }).join('');
}

// 选择文件
async function selectFile(fileId) {
    currentFileId = fileId;

    try {
        const response = await fetch(`/api/files/${fileId}`);
        const data = await response.json();

        if (data.success) {
            displayFilePreview(data.file);
            loadFileList(); // 重新加载列表以更新选中状态
        }
    } catch (error) {
        console.error('加载文件失败:', error);
    }
}

// 显示文件预览
function displayFilePreview(file) {
    const previewArea = document.getElementById('previewArea');

    if (file.file_type === 'text') {
        previewArea.innerHTML = `
            <div class="text-preview">
                <pre id="textContent">${escapeHtml(file.content)}</pre>
                <div class="preview-actions">
                    <button class="clay-btn-primary" onclick="copyText()">复制文本</button>
                    <button class="clay-btn-secondary" onclick="editText()">编辑</button>
                </div>
            </div>
        `;
    } else if (file.file_type === 'image') {
        previewArea.innerHTML = `
            <div class="image-preview">
                <img src="/api/files/${file.id}/content" alt="${escapeHtml(file.filename || '图片')}">
                <div class="preview-actions">
                    <button class="clay-btn-primary" onclick="downloadFile(${file.id})">下载</button>
                </div>
            </div>
        `;
    } else if (file.file_type === 'file' && file.content) {
        // 文本文件（有content字段）
        previewArea.innerHTML = `
            <div class="text-preview">
                <pre id="textContent">${escapeHtml(file.content)}</pre>
                <div class="preview-actions">
                    <button class="clay-btn-primary" onclick="copyText()">复制文本</button>
                    <button class="clay-btn-secondary" onclick="downloadFile(${file.id})">下载</button>
                </div>
            </div>
        `;
    } else {
        // 其他文件
        previewArea.innerHTML = `
            <div class="file-preview-info">
                <p><strong>文件名:</strong> ${escapeHtml(file.filename)}</p>
                <p><strong>大小:</strong> ${formatFileSize(file.file_size)}</p>
                <p><strong>类型:</strong> ${escapeHtml(file.mime_type || '未知')}</p>
                <div class="preview-actions">
                    <button class="clay-btn-primary" onclick="downloadFile(${file.id})">下载</button>
                </div>
            </div>
        `;
    }
}

// 设置文件上传
function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');

    // 文件选择上传
    fileInput.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        for (const file of files) {
            await uploadFile(file);
        }
        fileInput.value = '';
    });

    // 粘贴上传
    document.addEventListener('paste', async (e) => {
        // 如果在输入框中粘贴，不处理（让输入框自己处理）
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        e.preventDefault();
        const items = e.clipboardData.items;

        let hasFile = false;

        // 先检查是否有文件
        for (const item of items) {
            if (item.kind === 'file') {
                hasFile = true;
                const file = item.getAsFile();
                if (file) {
                    await uploadFile(file);
                }
            }
        }

        // 如果没有文件，处理纯文本
        if (!hasFile) {
            for (const item of items) {
                if (item.kind === 'string' && item.type === 'text/plain') {
                    item.getAsString(async (text) => {
                        if (text.trim()) {
                            await submitTextContent(text);
                        }
                    });
                    break;
                }
            }
        }
    });
}

// 提交文本内容
async function submitTextContent(text) {
    try {
        const response = await fetch(`/api/spaces/${currentSpaceId}/files`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'text',
                content: text
            })
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('文本已提交');
            loadFileList();
        } else {
            showError(data.message || '提交失败');
        }
    } catch (error) {
        console.error('提交文本失败:', error);
        showError('提交失败，请重试');
    }
}

// 上传文件
async function uploadFile(file) {
    if (file.size > 20 * 1024 * 1024) {
        showError('文件大小超过20MB限制');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`/api/spaces/${currentSpaceId}/files`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('文件上传成功');
            loadFileList();
        } else {
            showError(data.message || '上传失败');
        }
    } catch (error) {
        console.error('上传文件失败:', error);
        showError('上传失败，请重试');
    }
}

// 复制文本
function copyText() {
    const textContent = document.getElementById('textContent');
    if (textContent) {
        navigator.clipboard.writeText(textContent.textContent).then(() => {
            showSuccess('已复制到剪贴板');
        }).catch(() => {
            showError('复制失败');
        });
    }
}

// 编辑文本
function editText() {
    const textContent = document.getElementById('textContent');
    if (!textContent || !currentFileId) return;

    const currentText = textContent.textContent;
    const previewArea = document.getElementById('previewArea');

    previewArea.innerHTML = `
        <div class="text-edit">
            <textarea id="editTextarea" class="clay-input">${escapeHtml(currentText)}</textarea>
            <div class="preview-actions">
                <button class="clay-btn-primary" onclick="saveText()">保存</button>
                <button class="clay-btn-secondary" onclick="selectFile(${currentFileId})">取消</button>
            </div>
        </div>
    `;
}

// 保存文本
async function saveText() {
    const editTextarea = document.getElementById('editTextarea');
    if (!editTextarea || !currentFileId) return;

    const newText = editTextarea.value;

    try {
        const response = await fetch(`/api/files/${currentFileId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: newText })
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('保存成功');
            selectFile(currentFileId);
            loadFileList();
        } else {
            showError(data.message || '保存失败');
        }
    } catch (error) {
        console.error('保存失败:', error);
        showError('保存失败，请重试');
    }
}

// 下载文件
function downloadFile(fileId) {
    window.open(`/api/files/${fileId}/download`, '_blank');
}

// 删除文件
async function deleteFile(fileId) {
    if (!confirm('确定要删除这个文件吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('文件已删除');
            if (currentFileId === fileId) {
                currentFileId = null;
                document.getElementById('previewArea').innerHTML = '<p class="preview-placeholder">选择一个项目进行预览</p>';
            }
            loadFileList();
        } else {
            showError(data.message || '删除失败');
        }
    } catch (error) {
        console.error('删除文件失败:', error);
        showError('删除失败，请重试');
    }
}
