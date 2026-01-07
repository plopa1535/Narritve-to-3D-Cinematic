# Personal Shorts 서비스 요약

## 서비스 개요

사용자의 사진과 개인 서사를 기반으로 **1분짜리 감성 숏츠 영화**를 자동 생성하는 웹 서비스

---

## 기술 스택

### 프론트엔드
- React 18 + TypeScript
- Vite (빌드 도구)
- Tailwind CSS
- Axios (API 클라이언트)

### 백엔드
- FastAPI (Python)
- Pydantic (데이터 검증)
- 비동기 처리 (async/await)

### 배포
- **Render** (단일 Web Service)
- 프론트엔드 + 백엔드 통합 배포 (하나의 URL)

---

## AI 서비스 구성 (모두 무료, 카드 불필요!)

| 단계 | 서비스 | 용도 | 비용 |
|------|--------|------|------|
| 1 | **Google Gemini 1.5 Flash** | 이미지 분석 | 무료 (분당 15회) |
| 2 | **Groq (Qwen-2.5-72B)** | 스크립트 생성 | 무료 |
| 3 | **Replicate (Minimax video-01)** | 영상 생성 | 무료 (카드 불필요) |

---

## 처리 파이프라인

```
1. 사진 업로드 (3~10장)
       ↓
2. Gemini 이미지 분석
   - 인물 정보 (수, 관계, 표정)
   - 장소/배경 (실내외, 시간대, 계절)
   - 감정 톤 (행복, 슬픔, 설렘 등)
   - 시각적 요소 (색상, 조명, 구도)
       ↓
3. 사용자 서사 입력 (자연어)
       ↓
4. Groq 스크립트 생성
   - 씬 구성 (시작/종료 시간)
   - 영상 프롬프트
   - 트랜지션 효과
       ↓
5. Replicate 영상 생성 (Minimax video-01)
   - 씬별 6초 영상
   - 720p, 25fps
       ↓
6. 완성된 숏츠 영상 다운로드
```

---

## 무료 티어 한도 분석

### 서비스별 한도

| 서비스 | 무료 한도 | 영상 1개당 사용 | 생성 가능 |
|--------|----------|----------------|----------|
| Gemini | 1,500회/일 | ~10회 | ~150개/일 |
| Groq | 수천 회/일 | 1회 | 수천 개/일 |
| **Replicate** | **제한된 무료 횟수** | **~10회** | **테스트용** |

### Replicate 무료 티어 특징

- ✅ **카드 등록 불필요** (가입만으로 사용 가능)
- ✅ 제한된 횟수 무료 제공
- ⚠️ 무료 한도 초과 시 크레딧 구매 필요

---

## 영상 사양

| 항목 | 값 |
|------|-----|
| 씬당 길이 | **6초** |
| 총 영상 길이 | 약 60초 (10씬 기준) |
| 해상도 | **720p** |
| FPS | **25** |
| 화면 비율 | 세로/가로 (이미지에 따라) |

---

## 환경변수 설정

```env
# Gemini API (이미지 분석 - 무료)
GEMINI_API_KEY=your_gemini_api_key_here

# Groq API (스크립트 생성 - 무료)
GROQ_API_KEY=your_groq_api_key_here

# Replicate API (영상 생성 - 카드 없이 무료)
REPLICATE_API_KEY=your_replicate_api_token_here
```

### API 키 발급 링크

| 서비스 | 발급 링크 | 카드 필요 |
|--------|----------|----------|
| Gemini | https://aistudio.google.com/app/apikey | ❌ |
| Groq | https://console.groq.com/keys | ❌ |
| Replicate | https://replicate.com/account/api-tokens | ❌ |

---

## 프로젝트 구조

```
NT3DC/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── projects.py         # API 엔드포인트
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic 스키마
│   │   ├── services/
│   │   │   ├── gemini_service.py   # 이미지 분석
│   │   │   ├── groq_service.py     # 스크립트 생성
│   │   │   ├── replicate_service.py # 영상 생성
│   │   │   └── storage_service.py  # 파일 저장
│   │   ├── config.py               # 설정
│   │   └── main.py                 # FastAPI 앱
│   ├── requirements.txt
│   ├── render.yaml                 # Render 배포 설정
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/             # React 컴포넌트
│   │   ├── api.ts                  # API 클라이언트
│   │   └── App.tsx                 # 메인 앱
│   ├── package.json
│   └── vite.config.ts
├── PERSONAL_SHORTS_SERVICE.md      # 상세 기획서
├── RENDER_DEPLOY.md                # 배포 가이드
└── SERVICE_SUMMARY.md              # 이 파일
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/projects` | 새 프로젝트 생성 |
| GET | `/api/v1/projects/{id}` | 프로젝트 조회 |
| POST | `/api/v1/projects/{id}/photos` | 사진 업로드 |
| PUT | `/api/v1/projects/{id}/narrative` | 서사 입력 |
| POST | `/api/v1/projects/{id}/analyze` | 이미지 분석 시작 |
| POST | `/api/v1/projects/{id}/generate` | 영상 생성 시작 |
| GET | `/api/v1/projects/{id}/status` | 생성 상태 조회 |
| DELETE | `/api/v1/projects/{id}` | 프로젝트 삭제 |

---

## 비용 비교 (영상 생성 서비스)

### 검토한 서비스들

| 서비스 | 무료 티어 | 카드 필요 | 최대 길이 | 월 비용 |
|--------|----------|----------|----------|---------|
| **Replicate** ✅ | 제한적 무료 | **❌ 불필요** | 6초 | 사용량 기반 |
| Pika Labs | 250+30/일 | ✅ 필요 (fal.ai) | 10초 | ~$8 |
| Hugging Face | API 미지원 | ❌ | - | - |
| Kling AI | 제한적 | ✅ 필요 | 2분 | $6.99 |
| Runway Gen-3 | 125 (1회) | ✅ 필요 | 10초 | ~$12 |

### 선택 이유: Replicate

1. **카드 등록 불필요** (가입만으로 무료 사용)
2. **Minimax video-01** 고품질 모델 제공
3. **간단한 API** (Python SDK 지원)
4. **다양한 모델** 선택 가능

---

## 로컬 개발

### 백엔드만 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드만 실행
```bash
cd frontend
npm install
npm run dev
```

### 통합 테스트 (프로덕션과 동일)
```bash
cd frontend && npm run build
cd ../backend
rm -rf static && cp -r ../frontend/dist static
uvicorn app.main:app --port 8000
# http://localhost:8000 접속
```

---

## 배포 (Render)

1. GitHub 저장소 연결
2. Web Service 생성
3. 환경변수 설정 (GEMINI_API_KEY, GROQ_API_KEY, REPLICATE_API_KEY)
4. 자동 배포

자세한 내용은 [RENDER_DEPLOY.md](./RENDER_DEPLOY.md) 참조

---

## 최종 비용 요약

| 항목 | 비용 | 카드 필요 |
|------|------|----------|
| 이미지 분석 (Gemini) | **$0** | ❌ |
| 스크립트 생성 (Groq) | **$0** | ❌ |
| 영상 생성 (Replicate) | **$0** | ❌ |
| 서버 호스팅 (Render 무료) | **$0** | ❌ |
| **총 비용** | **$0 (완전 무료)** | **❌ 카드 불필요** |

> ✅ **모든 서비스 카드 등록 없이 무료 사용 가능**
> ⚠️ Replicate 무료 한도 초과 시 크레딧 구매 필요 (사용량 기반 과금)

---

*문서 버전: 2.0*
*최종 수정: 2025년 1월*
*변경사항: Pika Labs → Replicate 변경 (카드 불필요)*
