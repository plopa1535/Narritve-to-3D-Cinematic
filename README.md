# Personal Shorts Service

개인화된 1분 숏츠 영화 생성 서비스

## 프로젝트 구조

```
NT3DC/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 라우터
│   │   ├── models/         # Pydantic 스키마
│   │   ├── services/       # AI 서비스 (Qwen, Pika)
│   │   ├── config.py       # 환경 설정
│   │   └── main.py         # FastAPI 앱
│   ├── storage/            # 로컬 파일 저장소
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # UI 컴포넌트
│   │   ├── api.ts          # API 클라이언트
│   │   └── App.tsx         # 메인 앱
│   ├── package.json
│   └── vite.config.ts
└── PERSONAL_SHORTS_SERVICE.md  # 기획서
```

## 기술 스택

- **백엔드**: FastAPI, Python 3.11+
- **프론트엔드**: React 18, TypeScript, Tailwind CSS, Vite
- **AI**: Qwen2.5-VL (이미지 분석), Qwen-Max (스크립트), Pika (영상 생성)
- **저장소**: 로컬 (개발), AWS S3 (프로덕션)

## 시작하기

### 1. 백엔드 설정

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

### 2. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 3. 접속

- 프론트엔드: http://localhost:3000
- 백엔드 API 문서: http://localhost:8000/docs

## 환경변수

```env
# Qwen API (Alibaba Cloud DashScope)
QWEN_API_KEY=sk-xxxxxxxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Pika API
PIKA_API_KEY=your_pika_api_key

# AWS S3 (선택사항 - 프로덕션용)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
AWS_REGION=ap-northeast-2
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/projects` | 새 프로젝트 생성 |
| GET | `/api/v1/projects/{id}` | 프로젝트 조회 |
| POST | `/api/v1/projects/{id}/photos` | 사진 업로드 |
| PUT | `/api/v1/projects/{id}/narrative` | 서사 입력 |
| POST | `/api/v1/projects/{id}/analyze` | AI 분석 시작 |
| POST | `/api/v1/projects/{id}/generate` | 영상 생성 시작 |
| GET | `/api/v1/projects/{id}/status` | 생성 상태 조회 |
| DELETE | `/api/v1/projects/{id}` | 프로젝트 삭제 |

## 사용 흐름

1. 사진 3~10장 업로드
2. 개인 서사(스토리) 입력
3. 스타일 선택 (로맨틱/추억/행복/감성/시네마틱)
4. AI 분석 → 스크립트 생성 → 영상 생성
5. 결과 영상 다운로드/공유

## 예상 비용

| 서비스 | 영상 1개당 비용 |
|--------|----------------|
| Qwen2.5-VL (이미지 분석) | $0.01~0.03 |
| Qwen-Max (스크립트) | $0.01~0.02 |
| Pika (60초 영상) | $1.00~2.50 |
| **총계** | **$1.02~2.55** |

## 개발 노트

### Mock 모드

Pika API 키가 없으면 자동으로 Mock 서비스가 활성화됩니다.
테스트용 가짜 영상 URL이 반환됩니다.

### 추후 확장 계획

- [ ] 나레이션 음성 추가 (ElevenLabs)
- [ ] 배경 음악 추가 (Suno AI)
- [ ] 영상 병합 기능 (FFmpeg)
- [ ] 사용자 인증 시스템
- [ ] 모바일 앱 개발
