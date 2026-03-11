# 육아톡 (ChildcareTalk) 🍼

AI 기반 육아 상담 챗봇 앱 — 친구같은 육아 엄빠 상담사

## 주요 기능
- **AI 육아 상담**: Claude API 기반, 최신 육아 연구 기반 코칭 및 상담
- **부부 상담**: 육아로 인한 부부 갈등 상담 (비판 없이 경청)
- **일상 대화**: 시시콜콜한 수다도 환영
- **대화 기억**: 사용자별 대화 이력 저장, 언제든 이어서 대화 가능

## 기술 스택
- **Backend**: Python FastAPI + SQLAlchemy (SQLite/PostgreSQL)
- **Frontend**: Flutter (Web + Mobile)
- **AI**: Claude API (Anthropic)
- **인증**: JWT

## 시작하기

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력

# 서버 실행
uvicorn app.main:app --reload
```

API 문서: http://localhost:8000/docs

### Frontend (Flutter)

```bash
cd frontend/childcare_talk
flutter pub get
flutter run
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/register` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |
| GET | `/api/auth/me` | 내 정보 |
| GET | `/api/conversations` | 대화 목록 |
| POST | `/api/conversations` | 새 대화 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| GET | `/api/conversations/{id}/messages` | 메시지 조회 |
| POST | `/api/chat/{conversation_id}` | 메시지 전송 (SSE) |
| POST | `/api/chat/{conversation_id}/sync` | 메시지 전송 (동기) |

## 프로젝트 구조

```
childcare-talk/
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── api/       # API 라우터 (auth, chat, conversations)
│   │   ├── models/    # SQLAlchemy 모델
│   │   ├── schemas/   # Pydantic 스키마
│   │   ├── services/  # 비즈니스 로직 (AI, 채팅)
│   │   ├── prompts/   # 시스템 프롬프트
│   │   └── db/        # 데이터베이스 설정
│   └── requirements.txt
├── frontend/          # Flutter 프론트엔드
│   └── childcare_talk/
│       └── lib/
│           ├── screens/   # 화면 (로그인, 대화목록, 채팅)
│           ├── widgets/   # 위젯 (채팅버블, 입력창)
│           ├── services/  # API 서비스
│           └── models/    # 데이터 모델
└── README.md
```

## 라이선스
MIT License
