# AI 文字版模拟面试系统

面向保研面试的文字版 AI 模拟面试应用。用户注册登录后，可以填写保研面试配置并粘贴简历文本，系统会生成专属 AI 面试官，围绕自我介绍、科研经历、项目细节、专业基础和申请动机进行多轮文字追问，并在结束后生成结构化评分报告。每个用户只能查看和操作自己的面试数据。

## 技术栈

- 前端：React、TypeScript、Vite、Ant Design、React Router、Axios、TanStack Query
- 后端：FastAPI、Python、Pydantic、SQLAlchemy、PostgreSQL、httpx、python-dotenv
- AI：通过 `LLMService` 接入，可切换 `mock`、`openai`、`deepseek`、`tongyi`、`doubao`

## 目录结构

```text
ai-interview/
  frontend/                # React 前端
  backend/                 # FastAPI 后端
    app/api/routes         # API 路由
    app/core               # 配置与数据库
    app/models             # SQLAlchemy 模型
    app/schemas            # Pydantic Schema
    app/services           # 业务服务
    app/services/ai        # LLM Provider 与 Prompt
  docker-compose.yml       # 本地 PostgreSQL
  README.md
```

## 环境要求

- Docker
- Python 3.11，推荐使用 Anaconda 或 Miniconda
- Node.js 18+

## 快速启动

### 1. 启动数据库

```bash
cd ai-interview
docker compose up -d postgres
```

PostgreSQL 默认配置：

- 数据库：`ai_interview`
- 用户名：`postgres`
- 密码：`postgres`
- 端口：`5432`

### 2. 配置后端环境变量

后端会读取 `backend/.env`。首次启动前复制示例文件：

```bash
cd ai-interview/backend
copy .env.example .env
```

默认 `LLM_PROVIDER=mock`，不需要 API Key，可以直接跑完整流程。需要接入真实大模型时，按下面「环境变量」章节修改 `.env`。

### 3. 启动后端

首次安装依赖：

```bash
cd ai-interview/backend
conda create -n ai-interview python=3.11 -y
conda run -n ai-interview pip install -r requirements.txt
```

启动服务：

```bash
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

后端默认地址：`http://127.0.0.1:8000`

健康检查：`http://127.0.0.1:8000/api/health`

如果返回 `{"status":"ok"}`，说明后端服务正常。首次启动时会自动创建数据库表。

如果你是在旧版本数据库上升级，后端启动时会自动尝试给 `interviews` 表补充 `user_id` 字段。旧的匿名面试记录不会归属到任何用户，开发阶段建议直接重建数据库数据卷。

### 4. 启动前端

```bash
cd ai-interview/frontend
npm install
npm run dev
```

前端默认地址：`http://localhost:5173`

Vite 已将 `/api` 代理到 `http://127.0.0.1:8000`，本地开发时前端通常不需要额外配置环境变量。

## 环境变量

环境变量文件位置：`ai-interview/backend/.env`

完整示例：

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_interview
LLM_PROVIDER=mock
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

TONGYI_API_KEY=
TONGYI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
TONGYI_MODEL=qwen-plus

DOUBAO_API_KEY=
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

常用变量说明：

- `DATABASE_URL`：后端连接 PostgreSQL 的地址，需要和 `docker-compose.yml` 中的数据库配置一致。
- `LLM_PROVIDER`：选择使用哪个模型服务。可选值：`mock`、`openai`、`deepseek`、`tongyi`、`doubao`。
- `JWT_SECRET_KEY`：JWT 签名密钥，生产环境必须替换成足够长的随机字符串。
- `JWT_ALGORITHM`：JWT 签名算法，默认 `HS256`。
- `ACCESS_TOKEN_EXPIRE_MINUTES`：登录 token 有效期，默认 10080 分钟，即 7 天。
- `*_API_KEY`：对应模型服务的 API Key。`mock` 模式不需要填写。
- `*_BASE_URL`：对应模型服务的 OpenAI-compatible API 地址。
- `*_MODEL`：模型名或服务商的推理接入点 ID。
- `CORS_ORIGINS`：允许访问后端的前端地址，多个地址用英文逗号分隔。

### 切换 LLM Provider

默认 mock 模式：

```env
LLM_PROVIDER=mock
```

如果不想使用 mock，需要把 `LLM_PROVIDER` 改成真实模型服务，并填写对应的 API Key、Base URL 和模型名。例如要使用 DeepSeek，就配置：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

注意：当前后端保留了 mock 兜底逻辑。即使 `LLM_PROVIDER` 已经改成真实 provider，如果 API Key 缺失、模型名为空、接口请求失败，或返回内容无法解析为系统需要的 JSON，后端仍会回退到 mock 结果，保证 MVP 流程不中断。如果希望彻底禁止 mock，需要修改后端 `LLMService`，让 provider 初始化或调用失败时直接抛出错误。

OpenAI：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

DeepSeek：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

通义千问 DashScope 兼容模式：

```env
LLM_PROVIDER=tongyi
TONGYI_API_KEY=你的 DashScope API Key
TONGYI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
TONGYI_MODEL=qwen-plus
```

豆包火山方舟：

```env
LLM_PROVIDER=doubao
DOUBAO_API_KEY=你的火山方舟 API Key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=你的方舟推理接入点 ID 或模型名
```

非 `mock` provider 会复用 OpenAI-compatible 请求格式，请求路径为 `{BASE_URL}/chat/completions`。如果 API Key、模型名缺失，或返回内容无法解析为系统需要的 JSON，后端会回退到 mock 结果，保证 MVP 流程不中断。

修改 `.env` 后需要重启后端服务，新的配置才会生效。

## API 简介

- `GET /api/health`：健康检查
- `POST /api/auth/register`：注册账号
- `POST /api/auth/login`：登录并获取 Bearer token
- `GET /api/users/me`：获取当前登录用户
- `GET /api/interviews`：获取当前用户自己的面试列表
- `POST /api/interviews`：创建面试，分析简历并生成第一问，需要登录
- `GET /api/interviews/{interview_id}`：获取面试详情和消息列表，需要登录且只能访问自己的数据
- `POST /api/interviews/{interview_id}/messages`：提交候选人回答并生成下一问，需要登录且只能访问自己的数据
- `POST /api/interviews/{interview_id}/finish`：结束面试并生成报告，需要登录且只能访问自己的数据
- `GET /api/interviews/{interview_id}/report`：获取面试报告，需要登录且只能访问自己的数据

登录成功后，前端会把 `access_token` 保存到 `localStorage`，并在 Axios 请求中自动添加：

```http
Authorization: Bearer <access_token>
```

## 常见开发命令

后端：

```bash
cd ai-interview/backend
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

前端：

```bash
cd ai-interview/frontend
npm run dev
npm run build
```

数据库：

```bash
cd ai-interview
docker compose up -d postgres
docker compose down
```

## 后续扩展方向

- 使用 Alembic 管理数据库迁移
- 使用更完整的用户资料与权限体系
- 支持 PDF/Word 简历上传与解析
- 增加语音输入输出
- 接入联网搜索或院校、专业方向知识库
