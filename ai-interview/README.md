# AI 模拟面试系统

面向保研场景的 AI 模拟面试应用。用户注册登录后，可以上传或粘贴简历，系统会生成专属 AI 面试官，围绕自我介绍、科研经历、项目细节、专业基础和申请动机进行多轮追问，并在结束后生成结构化评分报告。系统支持文字问答，也支持浏览器语音模式：AI 面试官可以朗读问题，用户可以用语音回答并转成文字后提交。

每个用户只能查看和操作自己的面试、简历和模型配置数据。

## 功能概览

- 用户注册、登录和 JWT 鉴权
- 创建 AI 模拟面试，支持粘贴简历文本或选择已上传简历
- 多轮 AI 面试问答和结构化评分报告
- 浏览器语音面试模式：
  - AI 面试官问题朗读
  - 用户语音回答转文字
  - 转写结果可编辑后再提交
- PDF 简历上传、解析、管理和默认简历设置
- AI 简历诊断，包含总分、优势、风险点、修改建议和可能追问
- 用户自定义大模型配置，支持测试连接和设置默认模型
- 模型调用失败时显示 fallback 提示，避免静默回退 mock
- Alembic 数据库迁移
- 删除面试记录，自动清理该面试下的消息和报告

## 技术栈

- 前端：React、TypeScript、Vite、Ant Design、React Router、Axios、TanStack Query
- 后端：FastAPI、Python、Pydantic、SQLAlchemy、PostgreSQL、Alembic、httpx、python-dotenv
- AI：通过 `LLMService` 接入，可使用 `mock`、`openai`、`deepseek`、`tongyi`、`doubao`，也支持用户自定义 OpenAI-compatible 配置
- 语音：浏览器 Web Speech API
  - `speechSynthesis` 用于 AI 问题朗读
  - `SpeechRecognition` / `webkitSpeechRecognition` 用于用户语音转文字

## 目录结构

```text
ai-interview/
  frontend/                 # React 前端
  backend/                  # FastAPI 后端
    app/api/routes          # API 路由
    app/core                # 配置、数据库、鉴权等基础模块
    app/models              # SQLAlchemy 模型
    app/repositories        # 数据访问层
    app/schemas             # Pydantic Schema
    app/services            # 业务服务
    app/services/ai         # LLM Provider 和 Prompt
    migrations/             # Alembic 数据库迁移
    storage/                # 本地上传文件目录，默认不提交 Git
  docker-compose.yml        # 本地 PostgreSQL
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

默认 PostgreSQL 配置：

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

macOS/Linux 可使用：

```bash
cp .env.example .env
```

默认 `LLM_PROVIDER=mock`，不需要 API Key，可以直接跑完整流程。

### 3. 安装后端依赖

```bash
cd ai-interview/backend
conda create -n ai-interview python=3.11 -y
conda run -n ai-interview pip install -r requirements.txt
```

### 4. 初始化或升级数据库

新数据库执行：

```bash
conda run -n ai-interview alembic upgrade head
```

如果你已经用旧版本自动创建过表，只想给当前开发库打 Alembic 基线，可执行：

```bash
conda run -n ai-interview alembic stamp head
```

以后新增表或字段时推荐流程：

```bash
conda run -n ai-interview alembic revision --autogenerate -m "your change"
conda run -n ai-interview alembic upgrade head
```

### 5. 启动后端

```bash
cd ai-interview/backend
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

后端默认地址：

```text
http://127.0.0.1:8000
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

返回：

```json
{"status": "ok"}
```

表示后端服务正常。

### 6. 启动前端

```bash
cd ai-interview/frontend
npm install
npm run dev
```

前端默认地址：

```text
http://localhost:5173
```

Vite 已将 `/api` 代理到：

```text
http://127.0.0.1:8000
```

本地开发时前端通常不需要额外配置环境变量。

## 环境变量

环境变量文件位置：

```text
ai-interview/backend/.env
```

示例：

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

LLM_CONFIG_ENCRYPTION_KEY=
RESUME_UPLOAD_MAX_MB=10
RESUME_STORAGE_DIR=storage/resumes

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

常用变量说明：

- `DATABASE_URL`：后端连接 PostgreSQL 的地址，需要和 `docker-compose.yml` 中的数据库配置一致
- `LLM_PROVIDER`：系统默认模型服务，可选 `mock`、`openai`、`deepseek`、`tongyi`、`doubao`
- `JWT_SECRET_KEY`：JWT 签名密钥，生产环境必须换成足够长的随机字符串
- `ACCESS_TOKEN_EXPIRE_MINUTES`：登录 token 有效期，默认 10080 分钟，即 7 天
- `*_API_KEY`：对应模型服务的 API Key，`mock` 模式不需要填写
- `*_BASE_URL`：对应模型服务的 OpenAI-compatible API 地址
- `*_MODEL`：模型名称或服务商推理接入点 ID
- `LLM_CONFIG_ENCRYPTION_KEY`：用户自定义模型 API Key 的加密密钥
- `RESUME_UPLOAD_MAX_MB`：PDF 简历上传大小限制，默认 10MB
- `RESUME_STORAGE_DIR`：PDF 简历本地保存目录
- `CORS_ORIGINS`：允许访问后端的前端地址，多个地址用英文逗号分隔

## 切换系统默认 LLM Provider

默认 mock 模式：

```env
LLM_PROVIDER=mock
```

使用 DeepSeek 示例：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

使用 OpenAI 示例：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

修改 `.env` 后需要重启后端服务。

注意：当前系统保留 mock fallback。真实 provider 调用失败、API Key 缺失、模型名为空、接口请求失败或返回 JSON 解析失败时，会回退到 mock，并在前端提示 fallback 原因。

## 用户自定义模型配置

登录后访问：

```text
/settings/llm
```

用户可以创建自己的模型配置：

- `mock`
- `openai`
- `deepseek`
- `tongyi`
- `doubao`
- `custom_openai_compatible`

配置项包括：

- 显示名称
- Provider
- Base URL
- Model
- API Key
- 是否启用
- 是否默认

安全说明：

- API Key 不会明文返回前端
- 数据库中保存的是加密后的 `encrypted_api_key`
- 加密密钥来自 `LLM_CONFIG_ENCRYPTION_KEY`
- 如果开发环境未配置该变量，会基于 `JWT_SECRET_KEY` 派生密钥

## 简历中心

登录后访问：

```text
/resumes
```

支持：

- 上传 PDF 简历
- 解析 PDF 文本
- 查看简历列表和详情
- 修改简历标题
- 编辑解析文本
- 重新解析 PDF
- 删除简历
- 设置默认简历
- AI 简历诊断
- 查看 AI 总分、风险点、修改建议和可能追问
- 创建面试时选择已有简历

限制：

- 第一版只支持可复制文字的 PDF
- 暂不支持扫描件 OCR
- 默认上传大小限制为 10MB
- 文件默认保存到 `backend/storage/resumes/{user_id}/{resume_id}.pdf`

## 语音面试模式

创建面试时可以开启“语音面试模式”。

开启后：

- AI 面试官的新问题会自动朗读
- 每条 AI 面试官消息可以手动点击朗读
- 用户可以点击“语音”按钮说出回答
- 浏览器会把用户语音转成文字填入输入框
- 用户可以编辑文字后再提交

语音能力使用浏览器 Web Speech API：

- 朗读：`speechSynthesis`
- 语音识别：`SpeechRecognition` 或 `webkitSpeechRecognition`

兼容性说明：

- Chrome 和 Edge 支持较好
- 部分浏览器可能不支持语音识别
- 不支持时系统会保留普通文字输入

## API 简介

### 基础与用户

- `GET /api/health`：健康检查
- `POST /api/auth/register`：注册账号
- `POST /api/auth/login`：登录并获取 Bearer token
- `GET /api/users/me`：获取当前登录用户

### 面试

- `GET /api/interviews`：获取当前用户的面试列表
- `POST /api/interviews`：创建面试
- `GET /api/interviews/{interview_id}`：获取面试详情和消息列表
- `DELETE /api/interviews/{interview_id}`：删除面试记录
- `POST /api/interviews/{interview_id}/messages`：提交候选人回答并生成下一问
- `POST /api/interviews/{interview_id}/finish`：结束面试并生成报告
- `GET /api/interviews/{interview_id}/report`：获取面试报告

### 简历

- `POST /api/resumes/upload`：上传 PDF 简历
- `GET /api/resumes`：获取简历列表
- `GET /api/resumes/{resume_id}`：获取简历详情
- `PATCH /api/resumes/{resume_id}`：修改标题、解析文本或默认状态
- `POST /api/resumes/{resume_id}/reparse`：重新解析 PDF
- `DELETE /api/resumes/{resume_id}`：删除简历
- `POST /api/resumes/{resume_id}/diagnose`：生成 AI 简历诊断
- `GET /api/resumes/{resume_id}/diagnostics`：获取简历诊断历史

### 模型配置

- `GET /api/llm-configs`：获取当前用户模型配置
- `POST /api/llm-configs`：创建模型配置
- `PATCH /api/llm-configs/{config_id}`：更新模型配置
- `DELETE /api/llm-configs/{config_id}`：删除模型配置
- `POST /api/llm-configs/{config_id}/test`：测试模型连接
- `POST /api/llm-configs/{config_id}/set-default`：设置默认模型配置

登录成功后，前端会把 `access_token` 保存到 `localStorage`，并在 Axios 请求中自动添加：

```http
Authorization: Bearer <access_token>
```

## 常用开发命令

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

Alembic：

```bash
cd ai-interview/backend
conda run -n ai-interview alembic current
conda run -n ai-interview alembic upgrade head
```

## 注意事项

- `.env` 不要提交到 Git
- 上传的 PDF 简历默认保存在 `backend/storage/`，该目录已加入 `.gitignore`
- 如果真实模型调用失败，系统会 fallback 到 mock，并在前端显示原因
- 如果用户模型配置的显示名称叫 DeepSeek，但 Provider 仍是 `mock`，实际仍会使用 mock
- 浏览器语音识别能力依赖浏览器实现，建议使用 Chrome 或 Edge 测试
