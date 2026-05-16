# AI 模拟面试系统

面向保研场景的 AI 模拟面试应用。用户注册登录后，可以上传或粘贴简历，系统会生成专属 AI 面试官，围绕自我介绍、科研经历、项目细节、专业基础和申请动机进行多轮追问，并在结束后生成结构化评分报告。系统支持文字问答，也支持浏览器语音模式：AI 面试官可以朗读问题，用户可以用语音回答并转成文字后提交。每个用户只能查看和操作自己的面试、简历和模型配置数据。
## 鎶€鏈爤

- 鍓嶇锛歊eact銆乀ypeScript銆乂ite銆丄nt Design銆丷eact Router銆丄xios銆乀anStack Query
- 鍚庣锛欶astAPI銆丳ython銆丳ydantic銆丼QLAlchemy銆丳ostgreSQL銆乭ttpx銆乸ython-dotenv
- AI锛氶€氳繃 `LLMService` 鎺ュ叆锛屽彲鍒囨崲 `mock`銆乣openai`銆乣deepseek`銆乣tongyi`銆乣doubao`

## 鐩綍缁撴瀯

```text
ai-interview/
  frontend/                # React 鍓嶇
  backend/                 # FastAPI 鍚庣
    app/api/routes         # API 璺敱
    app/core               # 閰嶇疆涓庢暟鎹簱
    app/models             # SQLAlchemy 妯″瀷
    app/schemas            # Pydantic Schema
    app/services           # 涓氬姟鏈嶅姟
    app/services/ai        # LLM Provider 涓?Prompt
  docker-compose.yml       # 鏈湴 PostgreSQL
  README.md
```

## 鐜瑕佹眰

- Docker
- Python 3.11锛屾帹鑽愪娇鐢?Anaconda 鎴?Miniconda
- Node.js 18+

## 蹇€熷惎鍔?
### 1. 鍚姩鏁版嵁搴?
```bash
cd ai-interview
docker compose up -d postgres
```

PostgreSQL 榛樿閰嶇疆锛?
- 鏁版嵁搴擄細`ai_interview`
- 鐢ㄦ埛鍚嶏細`postgres`
- 瀵嗙爜锛歚postgres`
- 绔彛锛歚5432`

### 2. 閰嶇疆鍚庣鐜鍙橀噺

鍚庣浼氳鍙?`backend/.env`銆傞娆″惎鍔ㄥ墠澶嶅埗绀轰緥鏂囦欢锛?
```bash
cd ai-interview/backend
copy .env.example .env
```

榛樿 `LLM_PROVIDER=mock`锛屼笉闇€瑕?API Key锛屽彲浠ョ洿鎺ヨ窇瀹屾暣娴佺▼銆傞渶瑕佹帴鍏ョ湡瀹炲ぇ妯″瀷鏃讹紝鎸変笅闈€岀幆澧冨彉閲忋€嶇珷鑺備慨鏀?`.env`銆?
### 3. 鍚姩鍚庣

棣栨瀹夎渚濊禆锛?
```bash
cd backend
conda create -n ai-interview python=3.11 -y
conda run -n ai-interview pip install -r requirements.txt
```

鍚姩鏈嶅姟锛?
```bash
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

鍚庣榛樿鍦板潃锛歚http://127.0.0.1:8000`

鍋ュ悍妫€鏌ワ細`http://127.0.0.1:8000/api/health`

濡傛灉杩斿洖 `{"status":"ok"}`锛岃鏄庡悗绔湇鍔℃甯搞€傞娆″惎鍔ㄦ椂浼氳嚜鍔ㄥ垱寤烘暟鎹簱琛ㄣ€?
濡傛灉浣犳槸鍦ㄦ棫鐗堟湰鏁版嵁搴撲笂鍗囩骇锛屽悗绔惎鍔ㄦ椂浼氳嚜鍔ㄥ皾璇曠粰 `interviews` 琛ㄨˉ鍏?`user_id` 瀛楁銆傛棫鐨勫尶鍚嶉潰璇曡褰曚笉浼氬綊灞炲埌浠讳綍鐢ㄦ埛锛屽紑鍙戦樁娈靛缓璁洿鎺ラ噸寤烘暟鎹簱鏁版嵁鍗枫€?
### 4. 鍚姩鍓嶇

```bash
cd ai-interview/frontend
npm install
npm run dev
```

鍓嶇榛樿鍦板潃锛歚http://localhost:5173`

Vite 宸插皢 `/api` 浠ｇ悊鍒?`http://127.0.0.1:8000`锛屾湰鍦板紑鍙戞椂鍓嶇閫氬父涓嶉渶瑕侀澶栭厤缃幆澧冨彉閲忋€?
## 鐜鍙橀噺

鐜鍙橀噺鏂囦欢浣嶇疆锛歚ai-interview/backend/.env`

瀹屾暣绀轰緥锛?
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

甯哥敤鍙橀噺璇存槑锛?
- `DATABASE_URL`锛氬悗绔繛鎺?PostgreSQL 鐨勫湴鍧€锛岄渶瑕佸拰 `docker-compose.yml` 涓殑鏁版嵁搴撻厤缃竴鑷淬€?- `LLM_PROVIDER`锛氶€夋嫨浣跨敤鍝釜妯″瀷鏈嶅姟銆傚彲閫夊€硷細`mock`銆乣openai`銆乣deepseek`銆乣tongyi`銆乣doubao`銆?- `JWT_SECRET_KEY`锛欽WT 绛惧悕瀵嗛挜锛岀敓浜х幆澧冨繀椤绘浛鎹㈡垚瓒冲闀跨殑闅忔満瀛楃涓层€?- `JWT_ALGORITHM`锛欽WT 绛惧悕绠楁硶锛岄粯璁?`HS256`銆?- `ACCESS_TOKEN_EXPIRE_MINUTES`锛氱櫥褰?token 鏈夋晥鏈燂紝榛樿 10080 鍒嗛挓锛屽嵆 7 澶┿€?- `*_API_KEY`锛氬搴旀ā鍨嬫湇鍔＄殑 API Key銆俙mock` 妯″紡涓嶉渶瑕佸～鍐欍€?- `*_BASE_URL`锛氬搴旀ā鍨嬫湇鍔＄殑 OpenAI-compatible API 鍦板潃銆?- `*_MODEL`锛氭ā鍨嬪悕鎴栨湇鍔″晢鐨勬帹鐞嗘帴鍏ョ偣 ID銆?- `CORS_ORIGINS`锛氬厑璁歌闂悗绔殑鍓嶇鍦板潃锛屽涓湴鍧€鐢ㄨ嫳鏂囬€楀彿鍒嗛殧銆?
### 鍒囨崲 LLM Provider

榛樿 mock 妯″紡锛?
```env
LLM_PROVIDER=mock
```

濡傛灉涓嶆兂浣跨敤 mock锛岄渶瑕佹妸 `LLM_PROVIDER` 鏀规垚鐪熷疄妯″瀷鏈嶅姟锛屽苟濉啓瀵瑰簲鐨?API Key銆丅ase URL 鍜屾ā鍨嬪悕銆備緥濡傝浣跨敤 DeepSeek锛屽氨閰嶇疆锛?
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=浣犵殑 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

娉ㄦ剰锛氬綋鍓嶅悗绔繚鐣欎簡 mock 鍏滃簳閫昏緫銆傚嵆浣?`LLM_PROVIDER` 宸茬粡鏀规垚鐪熷疄 provider锛屽鏋?API Key 缂哄け銆佹ā鍨嬪悕涓虹┖銆佹帴鍙ｈ姹傚け璐ワ紝鎴栬繑鍥炲唴瀹规棤娉曡В鏋愪负绯荤粺闇€瑕佺殑 JSON锛屽悗绔粛浼氬洖閫€鍒?mock 缁撴灉锛屼繚璇?MVP 娴佺▼涓嶄腑鏂€傚鏋滃笇鏈涘交搴曠姝?mock锛岄渶瑕佷慨鏀瑰悗绔?`LLMService`锛岃 provider 鍒濆鍖栨垨璋冪敤澶辫触鏃剁洿鎺ユ姏鍑洪敊璇€?
OpenAI锛?
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=浣犵殑 API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

DeepSeek锛?
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=浣犵殑 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

閫氫箟鍗冮棶 DashScope 鍏煎妯″紡锛?
```env
LLM_PROVIDER=tongyi
TONGYI_API_KEY=浣犵殑 DashScope API Key
TONGYI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
TONGYI_MODEL=qwen-plus
```

璞嗗寘鐏北鏂硅垷锛?
```env
LLM_PROVIDER=doubao
DOUBAO_API_KEY=浣犵殑鐏北鏂硅垷 API Key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=浣犵殑鏂硅垷鎺ㄧ悊鎺ュ叆鐐?ID 鎴栨ā鍨嬪悕
```

闈?`mock` provider 浼氬鐢?OpenAI-compatible 璇锋眰鏍煎紡锛岃姹傝矾寰勪负 `{BASE_URL}/chat/completions`銆傚鏋?API Key銆佹ā鍨嬪悕缂哄け锛屾垨杩斿洖鍐呭鏃犳硶瑙ｆ瀽涓虹郴缁熼渶瑕佺殑 JSON锛屽悗绔細鍥為€€鍒?mock 缁撴灉锛屼繚璇?MVP 娴佺▼涓嶄腑鏂€?
淇敼 `.env` 鍚庨渶瑕侀噸鍚悗绔湇鍔★紝鏂扮殑閰嶇疆鎵嶄細鐢熸晥銆?
## API 绠€浠?
- `GET /api/health`锛氬仴搴锋鏌?- `POST /api/auth/register`锛氭敞鍐岃处鍙?- `POST /api/auth/login`锛氱櫥褰曞苟鑾峰彇 Bearer token
- `GET /api/users/me`锛氳幏鍙栧綋鍓嶇櫥褰曠敤鎴?- `GET /api/interviews`锛氳幏鍙栧綋鍓嶇敤鎴疯嚜宸辩殑闈㈣瘯鍒楄〃
- `POST /api/interviews`锛氬垱寤洪潰璇曪紝鍒嗘瀽绠€鍘嗗苟鐢熸垚绗竴闂紝闇€瑕佺櫥褰?- `GET /api/interviews/{interview_id}`锛氳幏鍙栭潰璇曡鎯呭拰娑堟伅鍒楄〃锛岄渶瑕佺櫥褰曚笖鍙兘璁块棶鑷繁鐨勬暟鎹?- `POST /api/interviews/{interview_id}/messages`锛氭彁浜ゅ€欓€変汉鍥炵瓟骞剁敓鎴愪笅涓€闂紝闇€瑕佺櫥褰曚笖鍙兘璁块棶鑷繁鐨勬暟鎹?- `POST /api/interviews/{interview_id}/finish`锛氱粨鏉熼潰璇曞苟鐢熸垚鎶ュ憡锛岄渶瑕佺櫥褰曚笖鍙兘璁块棶鑷繁鐨勬暟鎹?- `GET /api/interviews/{interview_id}/report`锛氳幏鍙栭潰璇曟姤鍛婏紝闇€瑕佺櫥褰曚笖鍙兘璁块棶鑷繁鐨勬暟鎹?
鐧诲綍鎴愬姛鍚庯紝鍓嶇浼氭妸 `access_token` 淇濆瓨鍒?`localStorage`锛屽苟鍦?Axios 璇锋眰涓嚜鍔ㄦ坊鍔狅細

```http
Authorization: Bearer <access_token>
```

## 甯歌寮€鍙戝懡浠?
鍚庣锛?
```bash
cd ai-interview/backend
conda run --no-capture-output -n ai-interview uvicorn app.main:app --reload
```

鍓嶇锛?
```bash
cd ai-interview/frontend
npm run dev
npm run build
```

鏁版嵁搴擄細

```bash
cd ai-interview
docker compose up -d postgres
docker compose down
```

## 鍚庣画鎵╁睍鏂瑰悜

- 浣跨敤 Alembic 绠＄悊鏁版嵁搴撹縼绉?- 浣跨敤鏇村畬鏁寸殑鐢ㄦ埛璧勬枡涓庢潈闄愪綋绯?- 鏀寔 PDF/Word 绠€鍘嗕笂浼犱笌瑙ｆ瀽
- 澧炲姞璇煶杈撳叆杈撳嚭
- 鎺ュ叆鑱旂綉鎼滅储鎴栭櫌鏍°€佷笓涓氭柟鍚戠煡璇嗗簱
## 鏂板鍔熻兘锛氱畝鍘嗕腑蹇冧笌鐢ㄦ埛妯″瀷閰嶇疆

### 绠€鍘嗕腑蹇?
- 椤甸潰锛歚/resumes`銆乣/resumes/:id`
- 鏀寔涓婁紶 PDF 绠€鍘嗐€佽В鏋愭枃鏈€佹煡鐪嬪垪琛ㄣ€佹煡鐪嬭鎯呫€佽缃粯璁ゃ€佸垹闄ょ畝鍘嗐€?- 鏀寔瀵规煇浠界畝鍘嗙敓鎴?AI 绠€鍘嗚瘖鏂紝璇婃柇缁撴灉浼氳褰曞疄闄呬娇鐢ㄧ殑 provider/model銆?- 鍒涘缓闈㈣瘯鏃跺彲浠ラ€夋嫨宸叉湁绠€鍘嗭紝涔熷彲浠ョ户缁矘璐寸畝鍘嗘枃鏈€?- 绗竴鐗堝彧鏀寔鍙鍒舵枃瀛楃殑 PDF锛屼笉鏀寔鎵弿浠?OCR銆?- 榛樿涓婁紶澶у皬闄愬埗涓?10MB锛屽彲閫氳繃 `RESUME_UPLOAD_MAX_MB` 璋冩暣銆?- 鏂囦欢榛樿淇濆瓨鍒?`backend/storage/resumes/{user_id}/{resume_id}.pdf`锛屽彲閫氳繃 `RESUME_STORAGE_DIR` 璋冩暣銆?
### 鐢ㄦ埛鑷畾涔夋ā鍨嬮厤缃?
- 椤甸潰锛歚/settings/llm`
- 鏀寔 `mock`銆乣openai`銆乣deepseek`銆乣tongyi`銆乣doubao`銆乣custom_openai_compatible`銆?- 姣忎釜鐢ㄦ埛鍙互鍒涘缓銆佺紪杈戙€佸垹闄ゃ€佹祴璇曡繛鎺ャ€佽缃粯璁ゆā鍨嬮厤缃€?- `api_key` 涓嶄細杩斿洖鍓嶇锛涙暟鎹簱涓繚瀛樼殑鏄姞瀵嗗悗鐨?`encrypted_api_key`銆?- 鍔犲瘑瀵嗛挜鍙厤缃?`LLM_CONFIG_ENCRYPTION_KEY`銆傚紑鍙戠幆澧冩湭閰嶇疆鏃朵細鍩轰簬 `JWT_SECRET_KEY` 娲剧敓瀵嗛挜銆?- 闈㈣瘯鍒涘缓鍜岀畝鍘嗚瘖鏂兘鍙互閫夋嫨鐢ㄦ埛鑷繁鐨勬ā鍨嬮厤缃紱鏈€夋嫨鏃朵紭鍏堜娇鐢ㄧ敤鎴烽粯璁ら厤缃紝鍐嶅洖閫€鍒扮郴缁?`.env` 閰嶇疆鎴?mock銆?
鏂板鍚庣渚濊禆锛?
```bash
conda run -n ai-interview pip install -r requirements.txt
```

## 鏁版嵁搴撹縼绉?Alembic

鍚庣宸叉帴鍏?Alembic锛岃〃缁撴瀯鍙樻洿涓嶅啀渚濊禆搴旂敤鍚姩鏃惰嚜鍔?`create_all`銆?
棣栨鍒涘缓鏂版暟鎹簱鏃讹紝鍦?`backend` 鐩綍鎵ц锛?
```bash
conda run -n ai-interview alembic upgrade head
```

濡傛灉浣犳槸鍦ㄥ凡鏈夊紑鍙戞暟鎹簱涓婂崌绾э紝骞朵笖杩欎簺琛ㄥ凡缁忕敱鏃х増鏈嚜鍔ㄥ垱寤鸿繃锛屽彲浠ュ彧鎵撲竴娆″熀绾挎爣璁帮細

```bash
conda run -n ai-interview alembic stamp head
```

浠ュ悗鏂板瀛楁鎴栬〃鏃讹紝鎺ㄨ崘娴佺▼锛?
```bash
conda run -n ai-interview alembic revision --autogenerate -m "your change"
conda run -n ai-interview alembic upgrade head
```

## 鍒犻櫎闈㈣瘯璁板綍

闈㈣瘯鍘嗗彶椤垫敮鎸佸垹闄よ嚜宸辩殑闈㈣瘯璁板綍銆傚垹闄や細鍚屾绉婚櫎璇ラ潰璇曚笅鐨勫璇濇秷鎭拰鎶ュ憡锛涗笉浼氬奖鍝嶇畝鍘嗗簱涓殑绠€鍘嗘枃浠跺拰绠€鍘嗚瘖鏂褰曘€?
