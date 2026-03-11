# 육아톡 (ChildcareTalk) 🍼

AI 기반 육아 상담 챗봇 — 친구같은 육아 엄빠 상담사

## 주요 기능

- **AI 육아 상담**: Claude API 기반, 최신 육아 연구 기반 코칭 및 상담
- **부부 상담**: 육아로 인한 부부 갈등 상담 (비판 없이 경청)
- **일상 대화**: 시시콜콜한 수다도 환영
- **대화 기억**: 사용자별 대화 이력 저장, 언제든 이어서 대화 가능
- **실시간 스트리밍**: SSE 기반 실시간 AI 응답

## 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend** | Python FastAPI + SQLAlchemy (SQLite) |
| **Frontend (Web)** | HTML/CSS/JS (GitHub Pages 배포 가능) |
| **Frontend (Mobile)** | Flutter (Web + iOS + Android) |
| **AI** | Claude API (Anthropic) |
| **인증** | JWT (JSON Web Token) |
| **배포** | GitHub Pages (프론트) + Render (백엔드) |

---

## 빠른 시작 (로컬 실행)

### 1. 백엔드 서버 실행

```bash
# 레포 클론
git clone https://github.com/BosukNam/childcare-talk.git
cd childcare-talk

# Python 가상환경 생성 및 활성화
cd backend
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 ANTHROPIC_API_KEY 입력

# 서버 실행
uvicorn app.main:app --reload
```

서버가 실행되면:
- API 서버: http://localhost:8000
- Swagger API 문서: http://localhost:8000/docs
- 루트 엔드포인트: http://localhost:8000/ → `{"message": "육아톡 API 서버가 실행 중입니다 🍼"}`

### 2. 웹 프론트엔드 (정적 파일)

백엔드 서버가 실행 중인 상태에서 `docs/index.html`을 브라우저로 열면 됩니다.

```bash
# 프로젝트 루트에서
open docs/index.html    # macOS
xdg-open docs/index.html   # Linux
start docs/index.html   # Windows
```

또는 간단한 HTTP 서버로 실행:
```bash
cd docs
python3 -m http.server 3000
# http://localhost:3000 접속
```

### 3. Flutter 앱 (선택사항)

```bash
cd frontend/childcare_talk
flutter pub get
flutter run    # 또는 flutter run -d chrome (웹)
```

---

## 배포 방법

### 프론트엔드 → GitHub Pages

1. GitHub 레포 Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main` (또는 원하는 브랜치), 폴더: `/docs`
4. Save → `https://<username>.github.io/childcare-talk/` 에서 접근 가능

### 백엔드 → Render (무료)

1. [render.com](https://render.com) 가입
2. New → Web Service → GitHub 레포 연결
3. 설정:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 환경변수 추가:
   - `ANTHROPIC_API_KEY`: Anthropic API 키
   - `SECRET_KEY`: 임의의 시크릿 키 (자동 생성 가능)
5. Deploy

### 프론트엔드에서 백엔드 URL 설정

배포 후 브라우저 콘솔에서:
```javascript
localStorage.setItem('api_url', 'https://your-app.onrender.com/api');
location.reload();
```

또는 `docs/app.js` 첫 줄의 `API_BASE`를 직접 수정해도 됩니다.

---

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/register` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |
| GET | `/api/auth/me` | 내 정보 조회 |
| GET | `/api/conversations` | 대화 목록 |
| POST | `/api/conversations` | 새 대화 생성 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| GET | `/api/conversations/{id}/messages` | 메시지 조회 |
| POST | `/api/chat/{conversation_id}` | 메시지 전송 (SSE 스트리밍) |
| POST | `/api/chat/{conversation_id}/sync` | 메시지 전송 (동기, 테스트용) |

### API 사용 예시

```bash
# 회원가입
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nickname": "테스트맘", "password": "1234"}'

# 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"nickname": "테스트맘", "password": "1234"}'

# 새 대화 생성 (TOKEN은 로그인 응답의 access_token)
curl -X POST http://localhost:8000/api/conversations \
  -H "Authorization: Bearer TOKEN"

# 메시지 전송
curl -X POST http://localhost:8000/api/chat/CONVERSATION_ID \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "아이가 밤에 잠을 안 자요ㅠ"}'
```

---

## 프로젝트 구조

```
childcare-talk/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py             # FastAPI 앱 엔트리포인트
│   │   ├── config.py           # 환경변수 설정
│   │   ├── api/
│   │   │   ├── auth.py         # 인증 API (회원가입, 로그인, JWT)
│   │   │   ├── chat.py         # 채팅 API (SSE 스트리밍)
│   │   │   └── conversations.py # 대화 관리 API
│   │   ├── models/             # SQLAlchemy 모델
│   │   │   ├── user.py         # 사용자
│   │   │   ├── conversation.py # 대화
│   │   │   └── message.py      # 메시지
│   │   ├── schemas/            # Pydantic 스키마
│   │   ├── services/
│   │   │   ├── ai_service.py   # Claude API 연동
│   │   │   └── chat_service.py # 채팅 비즈니스 로직
│   │   ├── prompts/
│   │   │   └── system_prompt.py # 육아톡 AI 페르소나
│   │   └── db/
│   │       └── database.py     # DB 연결 (SQLite/PostgreSQL)
│   ├── requirements.txt
│   ├── .env.example
│   └── Procfile                # Render 배포용
├── frontend/                   # Flutter 프론트엔드
│   └── childcare_talk/
│       ├── pubspec.yaml
│       └── lib/
│           ├── main.dart
│           ├── screens/        # 화면 (로그인, 대화목록, 채팅)
│           ├── widgets/        # 위젯 (채팅버블, 입력창)
│           ├── services/       # API 서비스
│           └── models/         # 데이터 모델
├── docs/                       # GitHub Pages 웹 프론트엔드
│   ├── index.html
│   ├── style.css
│   └── app.js
├── render.yaml                 # Render 배포 설정
└── README.md
```

---

## 환경변수

| 변수 | 설명 | 필수 |
|------|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API 키 | O |
| `SECRET_KEY` | JWT 시크릿 키 | O (프로덕션) |
| `DATABASE_URL` | DB 연결 문자열 | X (기본: SQLite) |

---

## 향후 계획

- [ ] 카카오톡/LINE 채널 연동 (webhook 기반)
- [ ] 웹 검색 연동 (최신 육아 정보 RAG)
- [ ] 사용자 프로필 (아이 나이, 성별) 기반 맞춤 상담
- [ ] 푸시 알림
- [ ] PostgreSQL 전환 및 클라우드 배포
- [ ] 대화 내보내기 기능

## 라이선스

MIT License
