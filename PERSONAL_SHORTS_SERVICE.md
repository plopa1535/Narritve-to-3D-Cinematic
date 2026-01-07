# 개인화 숏츠 영화 생성 서비스 기획서

## 📋 서비스 개요

**서비스명**: Personal Story Shorts (가칭)

**핵심 가치**: 사용자의 사진과 개인 서사를 기반으로 감성적인 1분 숏츠 영화를 자동 생성

**타겟 플랫폼**: 노트북(웹) + 모바일(iOS/Android)

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        클라이언트                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   웹 앱     │    │  iOS 앱     │    │ Android 앱  │         │
│  │  (React)    │    │  (Swift)    │    │  (Kotlin)   │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (AWS/GCP)                       │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       백엔드 서버                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FastAPI / Node.js                     │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐           │   │
│  │  │ 사진 분석  │  │ 서사 분석  │  │ 영상 생성  │           │   │
│  │  │  서비스   │  │  서비스   │  │  서비스   │           │   │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘           │   │
│  └────────┼──────────────┼──────────────┼───────────────────┘   │
└───────────┼──────────────┼──────────────┼───────────────────────┘
            ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI 서비스 레이어                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │ GPT-4V /    │  │ Claude 3.5  │  │ Runway ML Gen-3 /   │     │
│  │ Claude      │  │ Sonnet      │  │ Pika / Kling AI     │     │
│  │ (이미지분석) │  │ (서사분석)   │  │ (영상생성)          │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │ ElevenLabs  │  │ Suno AI    │  │ Stable Diffusion    │     │
│  │ (음성생성)   │  │ (배경음악)  │  │ (이미지보정)         │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
            │              │              │
            ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         데이터 저장소                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PostgreSQL  │  │ AWS S3 /    │  │   Redis     │             │
│  │ (메타데이터) │  │ GCS (미디어)│  │  (캐시/큐)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 기술 스택

### 프론트엔드
| 플랫폼 | 기술 | 설명 |
|--------|------|------|
| 웹 | React + Next.js | SSR 지원, SEO 최적화 |
| iOS | Swift + SwiftUI | 네이티브 성능 |
| Android | Kotlin + Jetpack Compose | 현대적 UI |
| 공통 | React Native (대안) | 크로스플랫폼 |

### 백엔드
| 구성요소 | 기술 | 설명 |
|----------|------|------|
| API 서버 | FastAPI (Python) | 비동기 처리, AI 통합 용이 |
| 작업 큐 | Celery + Redis | 영상 생성 비동기 처리 |
| 인증 | Firebase Auth / Auth0 | 소셜 로그인 |
| 스토리지 | AWS S3 / GCS | 미디어 파일 저장 |

### AI/ML 서비스
| 기능 | 서비스 | 비용 | 대안 |
|------|--------|------|------|
| 이미지 분석 | **Google Gemini 1.5 Flash** | 무료 (분당 15회) | GPT-4 Vision |
| 서사 분석/스크립트 | **Groq (Qwen-2.5-72B)** | 무료 | Claude 3.5 Sonnet |
| 영상 생성 | **Replicate (Minimax video-01)** | 무료 (카드 불필요) | Pika, Runway Gen-3 |

---

## 📱 사용자 플로우

```
1. 사진 업로드 (3~10장)
        ↓
2. 개인 서사 입력 (자연어)
        ↓
3. 스타일/분위기 선택 (선택사항)
        ↓
4. AI 분석 & 스토리보드 생성
        ↓
5. 영상 생성 (1~3분 소요)
        ↓
6. 미리보기 & 수정
        ↓
7. 다운로드/공유
```

---

## 🤖 AI 프롬프트 시스템

### 1단계: 이미지 분석 프롬프트 (Google Gemini 1.5 Flash)

```
[SYSTEM PROMPT - IMAGE ANALYZER | Model: gemini-1.5-flash]

당신은 사진 분석 전문가입니다. 업로드된 사진들을 분석하여 다음 정보를 JSON 형식으로 추출해주세요.

## 분석 항목
1. **인물 정보**: 등장인물 수, 추정 관계, 표정, 포즈
2. **장소/배경**: 실내/실외, 장소 유형, 시간대, 계절
3. **감정 톤**: 행복, 슬픔, 평화, 설렘, 그리움 등
4. **시각적 요소**: 주요 색상, 조명, 구도
5. **시간 순서**: 사진들의 추정 시간 순서
6. **특별한 요소**: 특별한 이벤트, 상징적 물체

## 출력 형식
{
  "photos": [
    {
      "id": 1,
      "people": {"count": 2, "relationship": "연인", "emotions": ["행복", "설렘"]},
      "setting": {"type": "카페", "indoor": true, "time": "오후", "season": "가을"},
      "mood": "로맨틱",
      "colors": ["따뜻한 갈색", "베이지"],
      "key_elements": ["커피잔", "창가"]
    }
  ],
  "overall_theme": "연인의 일상",
  "suggested_narrative_arc": "만남 → 성장 → 현재",
  "emotional_journey": ["설렘", "안정", "행복"]
}
```

### 2단계: 서사 분석 및 스크립트 생성 프롬프트 (Groq - Qwen-2.5-72B)

```
[SYSTEM PROMPT - NARRATIVE ARCHITECT | Model: qwen-2.5-72b via Groq]

당신은 감성적인 숏폼 영상 스크립트 작가입니다.
사용자의 개인 서사와 사진 분석 결과를 바탕으로 1분짜리 감성 숏츠 영상 스크립트를 작성해주세요.

## 입력 정보
- 사진 분석 결과: {image_analysis}
- 사용자 서사: {user_narrative}
- 선호 스타일: {style_preference}

## 스크립트 구조 (60초 기준)
1. **오프닝** (0-10초): 훅/감성적 첫 장면
2. **전개** (10-40초): 스토리 전개, 감정 고조
3. **클라이맥스** (40-50초): 감정의 정점
4. **엔딩** (50-60초): 여운, 메시지

## 출력 형식
{
  "title": "영상 제목",
  "subtitle": "부제목/태그라인",
  "total_duration": 60,
  "scenes": [
    {
      "scene_id": 1,
      "start_time": 0,
      "end_time": 10,
      "photo_id": 1,
      "transition": "fade_in",
      "camera_movement": "slow_zoom_in",
      "narration": "처음 너를 만난 그 카페...",
      "text_overlay": null,
      "emotion": "nostalgic",
      "music_intensity": "low"
    }
  ],
  "narration_full": "전체 나레이션 텍스트",
  "music_style": "acoustic_emotional",
  "color_grading": "warm_vintage",
  "overall_mood": "감성적, 따뜻한"
}

## 작성 원칙
1. 사용자의 서사를 존중하되, 영상에 맞게 압축
2. 감정의 흐름을 자연스럽게 설계
3. 각 사진의 특성을 최대한 활용
4. 시청자의 공감을 이끌어내는 보편적 감성 포함
5. 너무 빠르지 않게, 여백의 미 활용
```

### 3단계: 영상 생성 프롬프트 (Replicate - Minimax video-01)

```
[SYSTEM PROMPT - VIDEO GENERATION ORCHESTRATOR]

입력된 스크립트와 사진을 바탕으로 각 씬별 영상 생성 프롬프트를 작성합니다.

## 씬별 프롬프트 생성 규칙

### 기본 구조
"[카메라 무브먼트], [주요 피사체], [배경 설명], [조명/분위기], [스타일], [감정 키워드]"

### 예시 프롬프트들

**Scene 1 - 감성적 오프닝**
```
Cinematic slow zoom into a vintage photograph, soft golden hour lighting,
film grain overlay, nostalgic atmosphere, gentle lens flare,
emotional documentary style, 4K quality
```

**Scene 2 - 인물 중심**
```
Smooth dolly shot, couple sitting in cozy cafe, warm ambient lighting,
shallow depth of field, romantic mood, soft focus background,
indie film aesthetic, natural color grading
```

**Scene 3 - 풍경/전환**
```
Aerial establishing shot transitioning to intimate close-up,
autumn leaves falling gently, golden sunset tones,
dreamy atmosphere, smooth motion blur, cinematic letterbox
```

**Scene 4 - 클라이맥스**
```
Dynamic push-in shot, emotional peak moment,
dramatic lighting contrast, time-lapse clouds in background,
epic cinematic feel, orchestral mood, lens breathing effect
```

**Scene 5 - 엔딩**
```
Slow pull-back revealing full scene, fade to warm glow,
peaceful resolution, soft vignette,
title card fade-in, gentle particle effects
```

## 트랜지션 프롬프트
- fade: "smooth cross-dissolve transition"
- morph: "seamless morph transition between scenes"
- zoom: "zoom through transition to next scene"
- slide: "gentle slide wipe transition"

## 출력 형식
{
  "scenes": [
    {
      "scene_id": 1,
      "source_image": "photo_1.jpg",
      "video_prompt": "생성된 프롬프트",
      "negative_prompt": "blurry, distorted faces, unnatural movement",
      "duration": 5,
      "motion_amount": 0.3,
      "seed": null
    }
  ]
}
```

### 4단계: 나레이션 음성 생성 프롬프트 (ElevenLabs용)

```
[SYSTEM PROMPT - VOICE GENERATION]

## 음성 스타일 가이드

### 감성 유형별 설정
1. **따뜻한 회상**
   - Voice: 부드러운 여성/남성 음성
   - Stability: 0.7
   - Similarity: 0.8
   - Style: 0.4 (약간의 감정 표현)
   - Speaking rate: 0.9 (약간 느리게)

2. **희망찬 이야기**
   - Voice: 밝고 따뜻한 톤
   - Stability: 0.6
   - Similarity: 0.75
   - Style: 0.5
   - Speaking rate: 1.0

3. **그리움/애틋함**
   - Voice: 깊고 잔잔한 톤
   - Stability: 0.75
   - Similarity: 0.85
   - Style: 0.3
   - Speaking rate: 0.85

## SSML 마크업 예시
<speak>
  <prosody rate="90%" pitch="-2st">
    처음 너를 만난 <break time="0.5s"/> 그 카페에서
  </prosody>
  <break time="0.8s"/>
  <prosody rate="85%" pitch="-1st">
    우리의 이야기가 <emphasis level="moderate">시작</emphasis>됐어
  </prosody>
</speak>
```

### 5단계: 배경 음악 생성 프롬프트 (Suno AI용)

```
[SYSTEM PROMPT - MUSIC GENERATION]

## 분위기별 음악 프롬프트

### 로맨틱/감성
```
soft acoustic guitar, gentle piano melody, warm strings,
emotional cinematic underscore, 80 BPM, key of G major,
nostalgic feel, subtle crescendo, indie folk influence
```

### 희망/밝음
```
uplifting piano arpeggios, light percussion, warm synth pads,
inspirational background music, 100 BPM, key of C major,
hopeful atmosphere, gentle build-up, acoustic elements
```

### 그리움/애틋함
```
melancholic piano solo, soft cello accompaniment,
bittersweet melody, 70 BPM, key of A minor,
emotional depth, minimal arrangement, cinematic atmosphere
```

### 가족/따뜻함
```
gentle acoustic ensemble, soft woodwinds, warm harmonies,
heartwarming background score, 85 BPM, key of F major,
cozy feel, nostalgic undertones, home video aesthetic
```

## 출력 요구사항
- Duration: 65초 (여유분 포함)
- Format: MP3/WAV
- Quality: High (320kbps)
- Vocals: Instrumental only
```

---

## 📊 데이터 모델

### 사용자 (Users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(100),
    created_at TIMESTAMP,
    subscription_tier VARCHAR(20), -- free, premium, pro
    credits_remaining INT
);
```

### 프로젝트 (Projects)
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(200),
    narrative_text TEXT,
    style_preference JSONB,
    status VARCHAR(20), -- draft, processing, completed, failed
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 사진 (Photos)
```sql
CREATE TABLE photos (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    storage_url VARCHAR(500),
    analysis_result JSONB,
    sequence_order INT,
    uploaded_at TIMESTAMP
);
```

### 생성 영상 (Generated Videos)
```sql
CREATE TABLE generated_videos (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    storage_url VARCHAR(500),
    duration_seconds INT,
    resolution VARCHAR(20),
    script_data JSONB,
    generation_cost DECIMAL,
    created_at TIMESTAMP
);
```

---

## 💰 비용 구조 (추정)

### API 비용 (영상 1개 생성 기준)
| 서비스 | 사용량 | 예상 비용 |
|--------|--------|-----------|
| Google Gemini 1.5 Flash | 10장 분석 | **$0 (무료)** |
| Groq (Qwen-2.5-72B) | 스크립트 생성 | **$0 (무료)** |
| Replicate (Minimax video-01) | 60초 영상 (6초 × 10씬) | **$0 (무료)** |
| **총 비용** | | **$0 (무료)** |

> ⚡ **완전 무료**: 모든 AI 서비스 무료 티어 활용, 카드 등록 불필요
> 📹 **Minimax video-01**: 720p, 25fps, 6초/씬, 고품질 영상 생성

### 가격 정책 (제안)
| 플랜 | 가격 | 영상 생성 |
|------|------|-----------|
| Free | $0 | 1개/월 (워터마크) |
| Basic | $9.99/월 | 5개/월 |
| Pro | $24.99/월 | 20개/월 + 고급 기능 |
| Enterprise | 문의 | 무제한 + API |

---

## 🚀 개발 로드맵

### Phase 1: MVP (핵심 기능)
- [ ] 웹 앱 기본 UI 구현
- [ ] 사진 업로드 및 저장
- [ ] 서사 입력 인터페이스
- [ ] 이미지 분석 파이프라인
- [ ] 기본 영상 생성 (5개 스타일)
- [ ] 결과물 다운로드

### Phase 2: 고도화
- [ ] 모바일 앱 출시
- [ ] 실시간 미리보기
- [ ] 사용자 음성 녹음 옵션
- [ ] 커스텀 음악 업로드
- [ ] 다국어 지원

### Phase 3: 확장
- [ ] 소셜 공유 기능
- [ ] 템플릿 마켓플레이스
- [ ] 협업 편집 기능
- [ ] B2B API 제공

---

## 🔒 보안 및 개인정보

### 개인정보 보호
1. **데이터 암호화**: 저장/전송 시 AES-256 암호화
2. **자동 삭제**: 30일 후 원본 사진 자동 삭제 (옵션)
3. **접근 제어**: 본인만 프로젝트 접근 가능
4. **얼굴 인식 동의**: 명시적 동의 후 처리

### 콘텐츠 정책
1. **부적절 콘텐츠 필터링**: AI 기반 자동 감지
2. **저작권 보호**: 사용자 소유권 명확화
3. **이용약관**: 생성물 사용 범위 명시

---

## 📝 API 엔드포인트

### 핵심 API
```
POST   /api/v1/projects                    # 새 프로젝트 생성
POST   /api/v1/projects/{id}/photos        # 사진 업로드
PUT    /api/v1/projects/{id}/narrative     # 서사 입력
POST   /api/v1/projects/{id}/analyze       # AI 분석 시작
POST   /api/v1/projects/{id}/generate      # 영상 생성 시작
GET    /api/v1/projects/{id}/status        # 생성 상태 확인
GET    /api/v1/projects/{id}/result        # 결과물 조회
DELETE /api/v1/projects/{id}               # 프로젝트 삭제
```

### WebSocket (실시간 진행상황)
```
WS     /ws/projects/{id}/progress          # 생성 진행률 스트림
```

---

## 🎯 성공 지표 (KPI)

| 지표 | 목표 |
|------|------|
| 영상 생성 완료율 | > 95% |
| 평균 생성 시간 | < 3분 |
| 사용자 만족도 | > 4.5/5 |
| 재방문율 | > 40% |
| 유료 전환율 | > 5% |

---

## 📞 참고 리소스

### AI 서비스 문서
- [Google Gemini API](https://aistudio.google.com/app/apikey) - 이미지 분석 (무료)
- [Groq API](https://console.groq.com/keys) - 스크립트 생성 (무료)
- [Replicate](https://replicate.com/account/api-tokens) - 영상 생성 (카드 없이 무료)

### 유사 서비스 벤치마킹
- Lumen5, Pictory, Synthesia, D-ID, HeyGen

---

*문서 버전: 1.0*
*최종 수정: 2025년 1월*
