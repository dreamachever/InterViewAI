# AI 文字版模拟面试系统

面向保研面试和求职面试的文字版 AI 模拟面试应用。用户填写面试配置并粘贴简历文本后，系统会生成专属 AI 面试官，进行多轮文字追问，并在结束后生成结构化评分报告。

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
- `POST /api/interviews`：创建面试，分析简历并生成第一问
- `GET /api/interviews/{interview_id}`：获取面试详情和消息列表
- `POST /api/interviews/{interview_id}/messages`：提交候选人回答并生成下一问
- `POST /api/interviews/{interview_id}/finish`：结束面试并生成报告
- `GET /api/interviews/{interview_id}/report`：获取面试报告

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
- 增加登录注册与用户隔离
- 支持 PDF/Word 简历上传与解析
- 增加语音输入输出
- 接入联网搜索或岗位、院校知识库
