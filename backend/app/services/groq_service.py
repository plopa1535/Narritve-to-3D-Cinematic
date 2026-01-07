import httpx
import json
from ..config import get_settings

settings = get_settings()

SCRIPT_GENERATION_PROMPT = """당신은 감성적인 숏폼 영상 스크립트 작가입니다.
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

## 출력 형식 (반드시 이 JSON 형식으로만 응답, 다른 텍스트 없이)
{{
  "title": "영상 제목",
  "total_duration": 60,
  "scenes": [
    {{
      "scene_id": 1,
      "start_time": 0,
      "end_time": 10,
      "photo_id": "photo_1",
      "transition": "fade_in",
      "camera_movement": "slow_zoom_in",
      "emotion": "nostalgic",
      "video_prompt": "Cinematic slow zoom, soft lighting, emotional atmosphere"
    }}
  ],
  "overall_mood": "감성적, 따뜻한",
  "color_grading": "warm_vintage"
}}

## 작성 원칙
1. 사용자의 서사를 존중하되, 영상에 맞게 압축
2. 감정의 흐름을 자연스럽게 설계
3. 각 사진의 특성을 최대한 활용
4. video_prompt는 영어로 작성 (Pika AI용)
5. 각 씬은 5-15초 사이로 구성
6. 사진 수에 맞춰 씬 개수 조정"""


class GroqService:
    """Groq API 서비스 (스크립트 생성용) - 무료"""

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "qwen-2.5-72b"  # 무료 Qwen 모델

    async def generate_script(
        self, image_analysis: dict, narrative: str, style: str
    ) -> dict:
        """영상 스크립트 생성"""
        prompt = SCRIPT_GENERATION_PROMPT.format(
            image_analysis=json.dumps(image_analysis, ensure_ascii=False),
            user_narrative=narrative,
            style_preference=style,
        )

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Groq API error: {response.text}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # JSON 파싱 (마크다운 코드 블록 제거)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())


groq_service = GroqService()
