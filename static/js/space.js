/**
 * 空间管理相关JS
 */

document.addEventListener('DOMContentLoaded', function() {
    loadSpaceList();
    setupEventListeners();
});

// 加载空间列表
async function loadSpaceList() {
    try {
        const response = await fetch('/api/spaces');
        const data = await response.json();

        if (data.success) {
            displaySpaceList(data.spaces);
        }
    } catch (error) {
        console.error('加载空间列表失败:', error);
    }
}

// 显示空间列表
function displaySpaceList(spaces) {
    const spaceList = document.getElementById('spaceList');
    if (!spaceList) return;

    if (spaces.length === 0) {
        spaceList.innerHTML = '<p class="empty-message">暂无空间</p>';
        return;
    }

    spaceList.innerHTML = spaces.map(space => `
        <div class="space-item clay-card" onclick="goToSpace(${space.id})">
            <h3>${escapeHtml(space.name)}</h3>
            <p class="space-time">创建于 ${formatDateTime(space.created_at)}</p>
        </div>
    `).join('');
}

// 设置事件监听器
function setupEventListeners() {
    const createForm = document.getElementById('createForm');
    const enterForm = document.getElementById('enterForm');

    if (createForm) {
        createForm.addEventListener('submit', handleCreateSpace);
    }

    if (enterForm) {
        enterForm.addEventListener('submit', handleEnterSpace);
    }
}

// 显示创建空间模态框
function showCreateModal() {
    document.getElementById('createModal').style.display = 'flex';
}

// 关闭创建空间模态框
function closeCreateModal() {
    document.getElementById('createModal').style.display = 'none';
    document.getElementById('createForm').reset();
    document.getElementById('createError').style.display = 'none';
}

// 显示进入空间模态框
function showEnterModal() {
    document.getElementById('enterModal').style.display = 'flex';
}

// 关闭进入空间模态框
function closeEnterModal() {
    document.getElementById('enterModal').style.display = 'none';
    document.getElementById('enterForm').reset();
    document.getElementById('enterError').style.display = 'none';
}

// 处理创建空间
async function handleCreateSpace(e) {
    e.preventDefault();

    const name = document.getElementById('spaceName').value;
    const password = document.getElementById('spacePassword').value;

    try {
        const response = await fetch('/api/spaces', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, password })
        });

        const data = await response.json();

        if (data.success) {
            closeCreateModal();
            goToSpace(data.space_id);
        } else {
            showError(data.message, 'createError');
        }
    } catch (error) {
        console.error('创建空间失败:', error);
        showError('创建空间失败，请重试', 'createError');
    }
}

// 处理进入空间
async function handleEnterSpace(e) {
    e.preventDefault();

    const password = document.getElementById('enterPassword').value;

    try {
        const response = await fetch('/api/spaces/enter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });

        const data = await response.json();

        if (data.success) {
            closeEnterModal();
            goToSpace(data.space.id);
        } else {
            showError(data.message, 'enterError');
        }
    } catch (error) {
        console.error('进入空间失败:', error);
        showError('进入空间失败，请重试', 'enterError');
    }
}

// 跳转到空间页面
function goToSpace(spaceId) {
    window.location.href = `/space/${spaceId}`;
}

// 返回首页
function goHome() {
    window.location.href = '/home';
}

// 显示删除空间确认
function showDeleteSpaceConfirm() {
    document.getElementById('deleteSpaceModal').style.display = 'flex';
}

// 关闭删除空间模态框
function closeDeleteSpaceModal() {
    document.getElementById('deleteSpaceModal').style.display = 'none';
}

// 确认删除空间
async function confirmDeleteSpace() {
    try {
        const response = await fetch(`/api/spaces/${SPACE_ID}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            closeDeleteSpaceModal();
            showSuccess('空间已删除');
            setTimeout(() => {
                goHome();
            }, 1000);
        } else {
            showError(data.message);
        }
    } catch (error) {
        console.error('删除空间失败:', error);
        showError('删除空间失败，请重试');
    }
}
