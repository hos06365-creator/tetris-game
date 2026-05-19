# Mini Tetris FastAPI Fullstack

브라우저 테트리스 게임을 FastAPI 백엔드와 SQLite 데이터베이스에 연결한 풀스택 프로젝트입니다.

## 주요 기능

- FastAPI 서버가 프론트엔드 정적 파일과 API를 함께 제공
- SQLite + SQLAlchemy 기반 사용자/점수 저장
- 이메일 기반 회원가입 및 로그인
- 비밀번호 해시 저장
- JWT access token 발급 및 인증
- 로그인한 사용자의 플레이 기록 저장
- 사용자별 최고 점수 저장
- 전체 사용자 중 최고 점수 조회 및 메인 화면 표시
- 기존 Canvas 테트리스 게임과 `fetch` API 연동

## 프로젝트 구조

```text
tetris/
├── backend/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── index.html
├── script.js
├── styles.css
├── requirements.txt
└── README.md
```

## 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8989
```

브라우저에서 접속:

```text
http://localhost:8989
```

또는 아래 명령으로도 실행할 수 있습니다.

```bash
python run_server.py
```

서버 실행 후 `tetris.db` SQLite 파일이 프로젝트 루트에 생성됩니다.

## API

| Method | Endpoint | 설명 | 인증 |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register` | 이메일 회원가입 및 JWT 발급 | 필요 없음 |
| `POST` | `/api/auth/login` | 로그인 및 JWT 발급 | 필요 없음 |
| `GET` | `/api/users/me` | 현재 로그인 사용자 조회 | 필요 |
| `GET` | `/api/scores/high-score` | 전체 최고 점수 조회 | 필요 없음 |
| `GET` | `/api/scores/me` | 내 최근 점수 기록 조회 | 필요 |
| `POST` | `/api/scores` | 게임 점수 저장 | 필요 |

인증이 필요한 API는 아래 헤더를 사용합니다.

```http
Authorization: Bearer <access_token>
```

## DB 모델

`users`

- `id`
- `email`
- `password_hash`
- `high_score`
- `created_at`

`scores`

- `id`
- `user_id`
- `score`
- `lines`
- `created_at`

## 프론트엔드 동작

- 메인 화면에서 전체 최고 점수를 조회해 표시합니다.
- 로그인/회원가입 폼은 `/api/auth/*` API와 통신합니다.
- JWT 토큰은 `localStorage`에 저장하고 보호된 요청에 `Authorization` 헤더로 전송합니다.
- 로그인하지 않아도 게임 플레이는 가능하지만 점수 저장은 되지 않습니다.
- 로그인한 사용자는 게임오버 시 현재 점수와 라인 수가 자동 저장됩니다.

## 개발 확인 명령

```bash
node --check script.js
python3 -m compileall backend
```
