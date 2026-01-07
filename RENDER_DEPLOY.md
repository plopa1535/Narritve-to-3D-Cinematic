# Render 배포 가이드

## 개요

Personal Shorts 서비스를 **하나의 URL**로 Render에 배포합니다.
- 프론트엔드와 백엔드가 통합되어 단일 서비스로 배포됩니다.

---

## 1. GitHub 저장소 준비

```bash
cd NT3DC
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/personal-shorts.git
git push -u origin main
```

---

## 2. Render 배포 (Web Service)

### Step 1: Render에서 새 Web Service 생성

1. [Render Dashboard](https://dashboard.render.com) 접속
2. **New** → **Web Service** 클릭
3. GitHub 저장소 연결

### Step 2: 설정

| 항목 | 값 |
|------|-----|
| **Name** | `personal-shorts` |
| **Root Directory** | (비워두기 - 루트) |
| **Runtime** | `Python 3` |
| **Build Command** | 아래 참조 |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Build Command (복사해서 붙여넣기)
```bash
cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cd ../backend && rm -rf static && cp -r ../frontend/dist static
```

### Step 3: 환경변수 설정

| Key | Value | 설명 |
|-----|-------|------|
| `GEMINI_API_KEY` | `AIza...` | Google AI Studio - 이미지 분석 (무료) |
| `GROQ_API_KEY` | `gsk_...` | Groq Console - 스크립트 생성 (무료) |
| `REPLICATE_API_KEY` | `r8_...` | Replicate - 영상 생성 (카드 없이 무료) |

### API 키 발급 링크
- **Gemini**: https://aistudio.google.com/app/apikey
- **Groq**: https://console.groq.com/keys
- **Replicate**: https://replicate.com/account/api-tokens

### Step 4: 배포

- **Create Web Service** 클릭
- 배포 완료까지 약 5-10분 소요

---

## 3. 배포 후 확인

```bash
# 헬스체크
curl https://personal-shorts.onrender.com/health

# API 문서
open https://personal-shorts.onrender.com/docs

# 웹앱 접속
open https://personal-shorts.onrender.com
```

---

## 4. 최종 URL 구조

| 경로 | 설명 |
|------|------|
| `https://personal-shorts.onrender.com` | 웹앱 (프론트엔드) |
| `https://personal-shorts.onrender.com/api/v1/...` | API 엔드포인트 |
| `https://personal-shorts.onrender.com/docs` | API 문서 (Swagger) |
| `https://personal-shorts.onrender.com/health` | 헬스체크 |

---

## 5. 커스텀 도메인 설정 (선택)

1. Render Dashboard → 서비스 선택 → Settings → Custom Domains
2. `yourdomain.com` 추가
3. DNS에 CNAME 레코드 추가: `yourdomain.com` → `personal-shorts.onrender.com`

---

## 6. 트러블슈팅

### 빌드 실패
- Node.js/Python 버전 확인
- 빌드 로그에서 에러 메시지 확인

### 페이지 로드 안됨
- `/health` 엔드포인트 먼저 확인
- 빌드 시 `static` 폴더가 생성되었는지 확인

### Free Tier 제한
- 15분 비활성 시 슬립 모드 → 첫 요청 시 30초~1분 cold start
- 유료 플랜으로 업그레이드하면 항상 활성 상태

---

## 7. 로컬 개발

### 백엔드만 실행 (API 개발)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드만 실행 (UI 개발)
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
