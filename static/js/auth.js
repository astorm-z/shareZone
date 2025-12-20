/**
 * 认证相关JS
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const password = document.getElementById('password').value;

            if (!password) {
                showError('请输入密码');
                return;
            }

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password })
                });

                const data = await response.json();

                if (data.success) {
                    // 登录成功，跳转到首页
                    window.location.href = '/';
                } else {
                    showError(data.message || '登录失败');
                }
            } catch (error) {
                console.error('登录错误:', error);
                showError('登录失败，请重试');
            }
        });
    }
});

// 登出函数
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            window.location.href = '/api/auth/login-page';
        }
    } catch (error) {
        console.error('登出错误:', error);
    }
}
