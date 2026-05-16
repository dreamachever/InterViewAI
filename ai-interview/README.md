# 保研 AI 模拟面试系统

一个面向保研场景的 AI 模拟面试应用。系统支持用户注册登录、简历上传与解析、AI 简历诊断、模拟面试、多轮问答、报告生成、语音面试，以及用户自定义 LLM 配置。当前版本新增了独立但可联动的“面经库”模块，用来沉淀真实面试经验，并在创建模拟面试时增强 AI 面试官的提问策略。

## 新增功能：面经库

第一版 MVP 支持：

- 手动新增面经
- 使用免费搜索引擎搜索面经并一键导入
- 粘贴经验贴正文
- 填写学校、专业、实验室、导师、面试类型、年份、来源 URL 等元信息
- 调用 LLM 自动提取结构化面经要点
- 查看面经列表与详情
- 重新提取面经要点
- 删除自己的面经
- 创建面试时选择最多 3 条面经
- AI 在提问时参考面经中的高频问题、流程、风险点和重点考察方向

说明：

- 当前版本默认接入 DuckDuckGo HTML 免费搜索方案，无需 API Key
- 所有面经、面经提取结果、面试关联关系都严格绑定 `user_id`

## 技术栈

- 前端：React + TypeScript + Vite + Ant Design + React Router + TanStack Query
- 后端：FastAPI + SQLAlchemy + PostgreSQL + Alembic + Pydantic
- LLM：`LLMService` 支持 `mock`、`openai`、`deepseek`、`tongyi`、`doubao`、`custom_openai_compatible`
- 语音：浏览器 Web Speech API

## 目录结构

```text
ai-interview/
  frontend/
  backend/
    app/api/routes
    app/core
    app/models
    app/repositories
    app/schemas
    app/services
    app/services/ai
    migrations
  docker-compose.yml
  README.md
```

## 启动方式

### 1. 启动 PostgreSQL

```bash
cd ai-interview
docker compose up -d postgres
```

### 2. 配置后端环境变量

```bash
cd ai-interview/backend
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

### 3. 安装后端依赖

```bash
cd backend
conda create -n ai-interview python=3.11 -y
conda run -n ai-interview pip install -r requirements.txt
```

### 4. 执行数据库迁移

```bash
cd backend
conda run -n ai-interview alembic upgrade head
```

新增的迁移包括：

- `20260516_0003_add_interview_experiences.py`
  - 创建 `interview_experiences`
  - 创建 `experience_insights`
  - 创建 `interview_experience_links`

### 5. 启动后端

```bash
cd backend
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

后端地址：

```text
http://127.0.0.1:8000
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

### 6. 启动前端

```bash
cd ai-interview/frontend
npm install
npm run dev
```

前端地址：

```text
http://localhost:5173
```

## 环境变量

后端环境变量文件：

```text
ai-interview/backend/.env
```

常用配置示例：

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
SEARCH_PROVIDER=duckduckgo_html
DUCKDUCKGO_HTML_URL=https://html.duckduckgo.com/html/
SEARCH_MAX_RESULTS=5

LLM_CONFIG_ENCRYPTION_KEY=
RESUME_UPLOAD_MAX_MB=10
RESUME_STORAGE_DIR=storage/resumes
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 面经库 API

### 面经列表与详情

- `GET /api/experiences`
  - 支持 `target_school`、`target_major`、`interview_type`、`source_type` 过滤
- `GET /api/experiences/{experience_id}`

### 创建与更新

- `POST /api/experiences/import-text`
- `PATCH /api/experiences/{experience_id}`

请求示例：

```json
{
  "title": "浙大计算机保研复试面经",
  "target_school": "浙江大学",
  "target_major": "计算机科学与技术",
  "interview_type": "保研科研面",
  "year": 2025,
  "source_url": "https://example.com/post/123",
  "raw_content": "这里粘贴真实经验贴正文",
  "llm_config_id": null
}
```

### 提取与删除

- `POST /api/experiences/{experience_id}/extract`
- `DELETE /api/experiences/{experience_id}`

### 网络搜索与导入

- `POST /api/experiences/search-web`
- `POST /api/experiences/import-web`

搜索请求示例：

```json
{
  "target_school": "浙江大学",
  "target_major": "计算机科学与技术",
  "interview_type": "保研科研面",
  "year": 2025,
  "keyword": "导师面 英语问答",
  "max_results": 5
}
```

导入搜索结果示例：

```json
{
  "title": "浙江大学计算机保研复试面经",
  "source_url": "https://example.com/post/1",
  "source_site": "example.com",
  "snippet": "复试主要包括自我介绍、科研追问、英语问答……",
  "raw_content": "搜索 API 返回的网页正文内容",
  "target_school": "浙江大学",
  "target_major": "计算机科学与技术",
  "interview_type": "保研科研面",
  "year": 2025,
  "llm_config_id": null
}
```

## 面试 API 变更

`POST /api/interviews` 新增：

```json
{
  "type": "保研科研面",
  "interviewer_style": "严谨导师",
  "target_school": "浙江大学",
  "target_major": "计算机科学与技术",
  "resume_id": "resume-id",
  "llm_config_id": null,
  "voice_enabled": false,
  "experience_ids": ["exp-1", "exp-2"]
}
```

规则：

- `experience_ids` 最多 3 条
- 所有 `experience_ids` 必须属于当前用户
- 会在 `interview_experience_links` 中建立关联
- AI 提问时会读取最新的 `experience_insights`

## 前端页面

新增页面：

- `/experiences`
- `/experiences/new`
- `/experiences/:id`

创建面试页新增：

- 面经增强区域
- 可选择最多 3 条面经
- 可预览高频问题数量、重点方向、高风险点

导航栏新增：

- 面经库

## 提问增强策略

当面试绑定面经后，AI 会在下一问 prompt 中结合：

- 面经摘要
- 面试流程
- 高频问题分类
- 真实问题
- 重点考察方向
- 高风险点
- 准备策略

目标行为：

- 优先覆盖高频问题
- 结合简历做个性化追问
- 不机械复读原始面经
- 如果面经强调专业基础，提升专业题比例
- 如果面经提到英语问答，适时加入英语问题
- 如果面经存在高风险点，在合适阶段追问

## 验证建议

### 后端

```bash
cd ai-interview/backend
conda run -n ai-interview alembic upgrade head
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

### 前端

```bash
cd ai-interview/frontend
npm run build
```

### 功能验收

1. 注册并登录一个新用户
2. 进入“面经库”新增一条粘贴型面经
3. 用“网络搜索”方式搜索并导入一条面经
4. 确认详情页能看到 AI 提取的结构化结果
5. 再创建一场模拟面试，并选择 1-3 条面经
6. 进入面试页，确认已显示关联面经摘要
7. 提交几轮回答，检查 AI 是否围绕面经重点追问
8. 用另一个用户账号验证无法访问前一个用户的面经

## 本次实现说明

本次实现遵循了现有项目分层风格：

- `route / service / repository / schema / model`
- 数据库变更通过 Alembic 管理
- 没有引入 `create_all`
- 复用了现有 `LLMService` 的 provider 选择与 fallback 机制

## 免费搜索方案说明

当前项目默认使用 `duckduckgo_html` 作为免费搜索方案。

优点：

- 无需 API Key
- 无需付费额度
- 对现有项目改动最少
- 可直接复用现有“搜索结果 -> 导入面经 -> AI 提取”链路
- 点进搜索结果后会优先使用 `trafilatura` 提取正文

限制与风险：

- 这不是官方开放 API，而是基于 DuckDuckGo 的 HTML 搜索结果页做解析
- 如果搜索结果页结构变化，后端解析逻辑可能需要调整
- 免费方案的稳定性通常弱于付费搜索 API
- 个别站点可能限制抓取，导致搜索结果有标题和摘要，但正文抓取不足
- 强依赖前端渲染、登录态、验证码或反爬策略较强的站点，正文仍可能提取不完整
- 搜索质量会明显依赖你填写的学校、专业、年份、关键词是否足够具体

当前正文提取策略：

1. 先用 DuckDuckGo HTML 搜索拿到候选链接和摘要
2. 再请求目标页面
3. 优先用 `trafilatura` 提取主正文
4. 如果失败，退回到通用纯文本清洗
5. 如果仍失败，再退回搜索摘要 `snippet`

当前仍可能抓不好的页面类型：

- 强前端渲染页面
- 登录后可见内容
- 反爬较强的论坛或内容站
- 正文被嵌在 iframe 或异步接口中的页面

## 注意事项

- 不要把 `.env` 提交到 Git
- 不要记录或打印用户 API Key
- `raw_content` 仅允许当前用户查看
- 当前环境若缺少后端依赖，请先执行 `pip install -r requirements.txt`
- 当前默认免费搜索方案无需额外配置 API Key
