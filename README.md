# 共享空间项目

一个基于 Flask 的临时文件共享 Web 应用，采用 Claymorphism（黏土形态）UI 设计风格。支持多人通过密码创建独立的共享空间，在空间内上传和分享文本、图片、文件等内容。

## ✨ 功能特性

### 核心功能
- 🔐 **系统密码保护** - 访问应用需要系统密码验证（默认：123456）
- 📁 **独立共享空间** - 每个空间通过唯一密码隔离，互不干扰
- 📝 **多种内容类型** - 支持纯文本、图片、各类文件上传
- 🖼️ **智能预览** - 图片自动预览，文本内容可在线编辑
- 📋 **快捷操作** - 支持拖拽上传、粘贴上传、快捷键提交
- 💾 **文件管理** - 支持文件下载、删除、文本编辑等操作

### 安全特性
- 🔒 **空间密码唯一性** - 每个空间密码全局唯一，防止冲突
- 🛡️ **文件类型检查** - 自动拦截危险文件类型（exe、sh、bat 等）
- 📏 **文件大小限制** - 单个文件最大 20MB
- ⏰ **自动过期清理** - 空间和文件 24 小时后自动清理

### 用户体验
- 🎨 **Claymorphism 设计** - 柔和的黏土质感 UI，视觉舒适
- 📱 **响应式布局** - 完美适配 PC 和移动端
- ⚡ **实时更新** - 文件列表实时刷新
- 🔄 **自动清理** - 后台定时清理过期内容（每 10 分钟）

## 🛠️ 技术栈

- **后端框架**：Flask 3.0.0
- **数据库**：SQLite
- **任务调度**：APScheduler 3.10.4
- **图片处理**：Pillow 10.1.0
- **前端**：原生 HTML/CSS/JavaScript
- **UI 风格**：Claymorphism（黏土形态）

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

依赖包说明：
- `Flask==3.0.0` - Web 框架
- `Flask-CORS==4.0.0` - 跨域支持
- `Werkzeug==3.0.1` - WSGI 工具库
- `APScheduler==3.10.4` - 定时任务调度
- `Pillow==10.1.0` - 图片处理

## 🚀 运行项目

### 标准方式
```bash
python app.py
```

### WSL 环境（使用宿主机 Python）
```bash
wpython app.py
```

启动成功后，访问：**http://localhost:3333**

## 📖 使用指南

### 1️⃣ 系统登录
1. 在浏览器中打开 `http://localhost:3333`
2. 输入系统密码：`123456`
3. 点击"登录"进入主页

### 2️⃣ 创建共享空间
1. 在主页点击"创建共享空间"按钮
2. 输入空间名称（用于标识，可重复）
3. 输入空间密码（**必须全局唯一**）
4. 点击"创建"完成

> 💡 **提示**：空间密码是进入空间的唯一凭证，请妥善保管

### 3️⃣ 进入共享空间
1. 在主页点击"进入共享空间"按钮
2. 输入空间密码
3. 点击"进入"

或者：
- 在主页的"最近访问"列表中，直接点击空间卡片进入

### 4️⃣ 上传内容

#### 📝 纯文本
- 在文本输入框中输入内容
- 点击"提交文本"按钮
- 或使用快捷键 `Ctrl + Enter`

#### 🖼️ 图片/文件
支持三种上传方式：
1. **拖拽上传**：将文件拖拽到上传区域
2. **点击上传**：点击"选择文件"按钮，选择文件
3. **粘贴上传**：使用 `Ctrl + V` 粘贴剪贴板中的图片

> ⚠️ **限制**：单个文件最大 20MB，禁止上传 exe、sh、bat 等危险文件

### 5️⃣ 管理内容

#### 查看文件
- 点击左侧文件列表中的文件项
- 右侧预览区会显示文件内容
- 图片自动显示预览
- 文本内容可直接查看

#### 编辑文本
1. 点击文本文件
2. 在预览区点击"编辑"按钮
3. 修改内容后点击"保存"

#### 下载文件
- 点击文件预览区的"下载"按钮
- 或右键文件列表项选择"下载"

#### 删除文件
- 点击文件预览区的"删除"按钮
- 确认后文件将被永久删除

### 6️⃣ 删除空间
1. 在空间页面点击"删除空间"按钮
2. 确认删除操作
3. 空间及其所有文件将被永久删除

## 📂 项目结构

```
shareZone/
├── app.py                      # Flask 应用入口，注册路由和错误处理
├── config.py                   # 配置文件（端口、密码、文件大小等）
├── requirements.txt            # Python 依赖列表
├── style.txt                   # Claymorphism UI 设计规范文档
│
├── database/                   # 数据库模块
│   ├── __init__.py            # 数据库管理器导出
│   ├── db_manager.py          # 数据库连接和操作管理
│   └── models.py              # 数据表结构定义（SQL）
│
├── routes/                     # 路由模块（蓝图）
│   ├── __init__.py            # 路由注册
│   ├── auth.py                # 认证相关路由（登录、登出）
│   ├── space.py               # 空间相关路由（创建、进入、删除）
│   └── file.py                # 文件相关路由（上传、下载、删除）
│
├── services/                   # 业务逻辑层
│   ├── __init__.py            # 服务导出
│   ├── auth_service.py        # 认证服务（令牌管理）
│   ├── space_service.py       # 空间服务（空间 CRUD）
│   ├── file_service.py        # 文件服务（文件 CRUD）
│   └── cleanup_service.py     # 清理服务（定时清理过期数据）
│
├── utils/                      # 工具模块（预留）
│   └── __init__.py
│
├── static/                     # 静态资源
│   ├── css/                   # 样式文件
│   │   ├── clay-base.css      # Claymorphism 基础样式
│   │   ├── clay-components.css # Claymorphism 组件样式
│   │   └── main.css           # 主样式文件
│   ├── js/                    # JavaScript 文件
│   │   ├── auth.js            # 认证相关逻辑
│   │   ├── space.js           # 空间页面逻辑
│   │   ├── file.js            # 文件操作逻辑
│   │   └── utils.js           # 工具函数
│   └── uploads/               # 文件上传存储目录
│       └── YYYY/MM/DD/        # 按日期分层存储
│
├── templates/                  # HTML 模板
│   ├── base.html              # 基础模板（公共布局）
│   ├── login.html             # 登录页面
│   ├── home.html              # 主页（空间列表）
│   └── space.html             # 空间页面（文件管理）
│
└── data/                       # 数据存储
    └── sharezone.db           # SQLite 数据库文件
```

## ⚙️ 配置说明

在 `config.py` 中可以修改以下配置：

### 基础配置
```python
PORT = 3333                     # 服务端口
SYSTEM_PASSWORD = '123456'      # 系统登录密码
SECRET_KEY = 'dev-secret-key...' # Flask 密钥（生产环境请修改）
```

### 文件配置
```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # 单个文件大小限制（20MB）
UPLOAD_FOLDER = 'static/uploads'   # 文件上传目录
ALLOWED_IMAGE_EXTENSIONS = {...}   # 允许的图片格式
DANGEROUS_EXTENSIONS = {...}       # 禁止的危险文件类型
```

### 过期配置
```python
FILE_EXPIRES_HOURS = 24         # 文件有效期（小时）
SPACE_EXPIRES_HOURS = 24        # 空间有效期（小时）
CLEANUP_INTERVAL_MINUTES = 10   # 清理任务间隔（分钟）
```

### Cookie 配置
```python
AUTH_TOKEN_EXPIRES = 7          # 系统认证令牌有效期（天）
SPACE_TOKEN_EXPIRES = 1         # 空间访问令牌有效期（天）
```

## 🗄️ 数据库设计

### 表结构

#### spaces（空间表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 空间名称（唯一） |
| password_hash | VARCHAR(255) | 密码哈希（唯一） |
| created_at | TIMESTAMP | 创建时间 |
| last_accessed_at | TIMESTAMP | 最后访问时间 |
| expires_at | TIMESTAMP | 过期时间 |
| is_deleted | BOOLEAN | 软删除标记 |

#### files（文件表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| space_id | INTEGER | 所属空间 ID（外键） |
| filename | VARCHAR(255) | 原始文件名 |
| stored_filename | VARCHAR(255) | 存储文件名（UUID） |
| file_type | VARCHAR(50) | 文件类型（text/image/file） |
| mime_type | VARCHAR(100) | MIME 类型 |
| file_size | INTEGER | 文件大小（字节） |
| content | TEXT | 文本内容（仅文本类型） |
| preview_text | TEXT | 预览文本 |
| file_path | VARCHAR(500) | 文件存储路径 |
| created_at | TIMESTAMP | 创建时间 |
| expires_at | TIMESTAMP | 过期时间 |
| is_deleted | BOOLEAN | 软删除标记 |

#### auth_tokens（认证令牌表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| token | VARCHAR(255) | 令牌值（唯一） |
| created_at | TIMESTAMP | 创建时间 |
| expires_at | TIMESTAMP | 过期时间 |
| is_valid | BOOLEAN | 是否有效 |

#### space_access（空间访问记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| token | VARCHAR(255) | 用户令牌 |
| space_id | INTEGER | 空间 ID（外键） |
| accessed_at | TIMESTAMP | 访问时间 |

## ⚠️ 注意事项

### 安全相关
- 🔐 **生产环境部署**：请务必修改 `config.py` 中的 `SECRET_KEY` 和 `SYSTEM_PASSWORD`
- 🛡️ **文件类型限制**：系统会自动拦截 exe、sh、bat、cmd 等危险文件类型
- 📏 **文件大小限制**：单个文件最大 20MB，超过会被拒绝
- 🔒 **密码唯一性**：空间密码全局唯一，创建时会检查是否已被使用

### 数据管理
- ⏰ **自动过期**：所有空间和文件的默认有效期为 24 小时
- 🗑️ **自动清理**：后台任务每 10 分钟清理一次过期数据
- 💾 **级联删除**：删除空间会同时删除空间内所有文件
- 📁 **文件存储**：上传的文件按日期分层存储在 `static/uploads/YYYY/MM/DD/` 目录

### 使用建议
- 💡 **空间密码**：建议使用易记但不易猜测的密码
- 📝 **文本编辑**：纯文本内容支持在线编辑，修改后立即生效
- 🖼️ **图片预览**：支持 png、jpg、jpeg、gif、bmp、webp 格式
- 🔄 **定期清理**：建议定期清理 `static/uploads/` 目录下的过期文件

### 技术限制
- 🌐 **单机部署**：当前版本仅支持单机部署，不支持分布式
- 💾 **SQLite 数据库**：适合小规模使用，大规模请考虑迁移到 MySQL/PostgreSQL
- 📊 **并发限制**：SQLite 写入并发能力有限，高并发场景需优化
- 🔍 **无全文搜索**：当前版本不支持文件内容搜索功能

## 🎨 UI 设计风格

本项目采用 **Claymorphism（黏土形态）** 设计风格，详细设计规范请参考 `style.txt` 文件。

### 核心特点
- 🎨 **双层阴影系统**：外部阴影 + 内部阴影创造立体感
- 🔵 **极致圆润**：大圆角设计（16px - 48px）
- 🌈 **马卡龙配色**：柔和的高明度、低饱和度色彩
- ✨ **弹性动画**：使用 cubic-bezier 曲线创造自然的交互反馈

### 主要组件
- 按钮、输入框、卡片、导航栏等均遵循 Claymorphism 设计规范
- 所有交互元素都有 hover、active 状态的视觉反馈
- 响应式设计，自动适配不同屏幕尺寸

## 🔧 开发相关

### 目录说明
- `database/` - 数据库层，负责数据持久化
- `routes/` - 路由层，处理 HTTP 请求
- `services/` - 业务逻辑层，核心功能实现
- `utils/` - 工具层，公共函数（预留）

### 架构特点
- **分层架构**：路由 → 服务 → 数据库，职责清晰
- **蓝图模式**：使用 Flask Blueprint 组织路由
- **服务模式**：业务逻辑封装在独立的 Service 类中
- **定时任务**：使用 APScheduler 实现后台清理任务

### 扩展建议
- 添加用户系统（注册、登录、权限管理）
- 实现文件分享链接功能
- 添加文件搜索和标签功能
- 支持更多文件类型的在线预览
- 添加文件版本管理
- 实现实时协作编辑

## 📝 更新日志

### v1.0.0（当前版本）
- ✅ 基础功能实现（空间管理、文件上传下载）
- ✅ Claymorphism UI 设计
- ✅ 自动过期清理机制
- ✅ 文本在线编辑功能
- ✅ 多种上传方式支持
- ✅ 响应式布局

## 📄 许可证

本项目仅供学习和个人使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**享受你的共享空间之旅！** 🚀
