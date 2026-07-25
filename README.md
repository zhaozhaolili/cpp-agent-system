<<<<<<< HEAD
# C++ 课程智能体系统

基于大语言模型的 C++ 课程智能教学平台，支持教师上传课件构建知识库、配置章节考核，学生 AI 对话答疑、在线考核、错题整理。

---

## 功能概览

### 学生端
- **AI 智能对话** — 基于 RAG 的流式对话，自动推荐学习资源，智能追问提示
- **课程资料** — 浏览资料、在线预览（PDF/图片/文本/代码）、下载
- **章节考核** — LLM 自动出题，选择题/判断题/简答题/编程题，限时作答
- **评价报告** — 多维度自动批改，生成能力雷达图，导出 HTML 报告
- **错题本** — 自动收集错题，已掌握可移除
- **学习仪表盘** — 进度追踪、成绩统计、能力维度分析
- **在线编程** — C++17 在线编译运行（GCC 16.1）

### 教师端
- **资料管理** — 上传 PDF/PPT/Word/Markdown/TXT/代码文件，自动解析并构建知识库
- **考核配置** — 按章节配置题型数量、知识点、评价维度、时间限制
- **学生管理** — 查看学生列表、编辑信息、重置密码、批量导入（CSV/Excel）
- **成绩查看** — 查看班级成绩分布，逐题查看学生答卷
- **模型配置** — 运行时切换 LLM API Key / Base URL / Model

### 公共
- **登录注册** — 学生/教师双角色，JWT 认证
- **忘记密码** — 邮箱重置密码
- **个人中心** — 编辑资料、修改密码、系统设置
- **全局搜索** — 搜索对话记录、课程资料、错题
- **列表分页** — 所有列表支持分页加载

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python 3.11+) |
| 数据库 | SQLite + SQLAlchemy ORM |
| 向量存储 | Chroma（备选，当前使用关键词匹配 + 磁盘持久化） |
| 大模型 | DeepSeek / OpenAI 兼容接口 |
| 前端框架 | Vue 3 + Vite |
| UI 组件 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 5 |
| 认证 | JWT (python-jose) + bcrypt |
| 文件解析 | PyPDF2, python-docx, python-pptx |
| 部署 | Docker + Docker Compose + Nginx |

---

## 项目结构

```
cpp-agent-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API 路由（7 个模块，50 个端点）
│   │   │   ├── auth.py      # 认证（注册/登录/重置密码/个人信息）
│   │   │   ├── chat.py      # AI 对话（SSE 流式/RAG/历史管理）
│   │   │   ├── teacher.py   # 教师端（资料/考核/学生管理/模型配置）
│   │   │   ├── student.py   # 学生端（资料/考核/错题/C++运行/教师选择）
│   │   │   ├── dashboard.py # 学习仪表盘
│   │   │   ├── search.py    # 全局搜索
│   │   │   ├── admin.py     # 系统管理
│   │   │   └── deps.py      # 依赖注入（JWT 验证/角色守卫）
│   │   ├── core/            # 配置、安全、数据库
│   │   ├── models/          # 数据模型（8 张表）
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── services/        # 业务逻辑
│   │   │   ├── llm_service.py    # LLM 调用
│   │   │   ├── exam_service.py   # 考核出题/批改
│   │   │   ├── cpp_runner.py     # C++ 在线编译运行
│   │   │   └── rag/              # RAG 检索/向量存储/持久化
│   │   └── utils/           # 工具函数
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env                 # 环境变量
├── frontend/
│   ├── src/
│   │   ├── views/           # 页面组件（19 个）
│   │   │   ├── student/     # 学生端 8 页
│   │   │   └── teacher/     # 教师端 5 页
│   │   ├── components/      # 公共组件
│   │   ├── api/             # API 调用封装
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── router/          # 路由配置（25 条路由）
│   │   ├── utils/           # 工具函数
│   │   └── assets/          # 静态资源/全局样式
│   ├── Dockerfile
│   ├── nginx.conf
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

---

## 快速开始（本地开发）

### 环境要求

- Python 3.11+
- Node.js 18+
- g++ (MinGW-w64) — C++ 在线运行功能需要
- Windows / Linux / macOS

### 1. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 并填写 API Key）
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key：
#   OPENAI_API_KEY=sk-xxxxxxxx
#   OPENAI_BASE_URL=https://api.deepseek.com/v1
#   LLM_MODEL=deepseek-chat

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问：
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

### 2. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npx vite --host
```

前端启动后访问：`http://localhost:5173`

Vite 已配置代理将 `/api` 请求转发到 `http://localhost:8000`，无需额外配置。

### 3. 验证

1. 打开 `http://localhost:5173`
2. 注册一个教师账号
3. 登录后上传课件资料
4. 配置章节考核
5. 注册一个学生账号
6. 选择教师，开始 AI 对话或参加考核

---

## Docker 部署

### 环境要求

- Docker Desktop（Windows/Mac）或 Docker Engine（Linux）
- WSL2（Windows 用户需要）

### 一键部署

```bash
# 在项目根目录下
docker-compose up -d
```

部署后访问：
- 前端：`http://localhost`
- 后端 API：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | Nginx + Vue 静态文件 |
| backend | 8000 | FastAPI + Uvicorn |

Nginx 自动将 `/api/` 和 `/uploads/` 请求反向代理到后端。

### 数据持久化

- `backend_data` — SQLite 数据库
- `uploads_data` — 上传的课件文件

---

## 环境变量配置

编辑 `backend/.env`：

```env
# JWT 安全配置
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM API 配置（兼容 OpenAI 接口）
OPENAI_API_KEY=sk-xxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
EMBEDDING_MODEL=text-embedding-ada-002

# 上传目录（可选，默认自动计算）
# UPLOAD_DIR=./app/static/uploads
```

---

## API 端点清单（50 个）

| 模块 | 数量 | 前缀 |
|------|------|------|
| 认证 | 6 | `/api/v1/auth` |
| 教师 | 18 | `/api/v1/teacher` |
| 学生 | 15 | `/api/v1/student` |
| 对话 | 6 | `/api/v1/chat` |
| 仪表盘 | 2 | `/api/v1/dashboard` |
| 搜索 | 1 | `/api/v1/search` |
| 管理 | 2 | `/api/v1/admin` |

完整接口文档：启动后端后访问 `http://localhost:8000/docs`

---

## 数据库模型

| 表 | 说明 |
|----|------|
| users | 用户（id, username, password_hash, role, full_name, email） |
| chapters | 课程章节（id, title, description, order） |
| course_materials | 课件资料（id, teacher_id, chapter_id, file_name, file_path, file_type, parsed_content） |
| exam_configs | 考核配置（id, chapter_id, teacher_id, total_questions, 题型计数, 知识点, 评价维度, time_limit） |
| exam_records | 考核记录（id, student_id, exam_config_id, answers, score, dimensions_scores, report_text） |
| chat_logs | 对话日志（id, user_id, question, answer, rag_sources, recommended_resources） |
| teacher_students | 师生关系（id, teacher_id, student_id, status） |
| wrong_answers | 错题本（id, student_id, exam_record_id, chapter_title, question_type, 答案等） |

---

## 常见问题

**Q: C++ 在线运行报错 "未安装 g++"？**  
安装 MinGW-w64：`winget install BrechtSanders.WinLibs.POSIX.UCRT`，重启后端。

**Q: 前端页面空白/报错？**  
检查浏览器控制台（F12），确认后端 `localhost:8000/health` 返回 `{"status":"ok"}`。

**Q: AI 对话无回复？**  
检查 `.env` 中 `OPENAI_API_KEY` 是否正确，DeepSeek API 余额是否充足。

**Q: 忘记密码无法使用？**  
当前为开发模式，重置 token 直接返回在 API 响应中。生产环境需配置 SMTP 邮件服务。
=======
# cpp-agent-system
随着大语言模型（LLM）和智能体（AI Agent）技术的发展，传统教学系统正逐步向智能教学平台演进。本次实践目标是培养学生在大模型应用开发、智能体设计、RAG知识库构建、教育数据处理等方面的综合能力，强化软件设计与开发的能力。
>>>>>>> 6016fe7a071bb2be4a6ad2b473c29917a28583af
