import httpx
import base64
import json
from ..config import get_settings

settings = get_settings()

IMAGE_ANALYSIS_PROMPT = """당신은 사진 분석 전문가입니다. 업로드된 사진을 분석하여 다음 정보를 JSON 형식으로 추출해주세요.

## 분석 항목
1. **인물 정보**: 등장인물 수, 추정 관계, 표정, 포즈
2. **장소/배경**: 실내/실외, 장소 유형, 시간대, 계절
3. **감정 톤**: 행복, 슬픔, 평화, 설렘, 그리움 등
4. **시각적 요소**: 주요 색상, 조명, 구도
5. **특별한 요소**: 특별한 이벤트, 상징적 물체

## 출력 형식 (반드시 이 JSON 형식으로만 응답, 다른 텍스트 없이)
{
  "people": {"count": 0, "relationship": "", "emotions": []},
  "setting": {"type": "", "indoor": true, "time": "", "season": ""},
  "mood": "",
  "colors": [],
  "key_elements": []
}"""


class GeminiService:
    """Groq LLaVA API 서비스 (이미지 분석용) - 무료"""

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.2-90b-vision-preview"

    async def analyze_image(self, image_data: bytes, photo_id: str) -> dict:
        """단일 이미지 분석"""
        base64_image = base64.b64encode(image_data).decode("utf-8")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": IMAGE_ANALYSIS_PROMPT
                                }
                            ]
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1024,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Groq LLaVA API error: {response.text}")

            result = response.json()
            text_content = result["choices"][0]["message"]["content"]

            # JSON 파싱 (마크다운 코드 블록 제거)
            if "```json" in text_content:
                text_content = text_content.split("```json")[1].split("```")[0]
            elif "```" in text_content:
                text_content = text_content.split("```")[1].split("```")[0]

            try:
                analysis = json.loads(text_content.strip())
            except json.JSONDecodeError:
                # JSON 파싱 실패시 기본값 반환
                analysis = {
                    "people": {"count": 0, "relationship": "unknown", "emotions": []},
                    "setting": {"type": "unknown", "indoor": True, "time": "unknown", "season": "unknown"},
                    "mood": "neutral",
                    "colors": [],
                    "key_elements": []
                }

            analysis["photo_id"] = photo_id
            return analysis

    async def analyze_all_images(self, images: list[tuple[str, bytes]]) -> dict:
        """여러 이미지 분석 및 전체 테마 추출"""
        analyses = []

        for photo_id, image_data in images:
            analysis = await self.analyze_image(image_data, photo_id)
            analyses.append(analysis)

        # 전체 분석 요약
        overall_analysis = await self._summarize_analyses(analyses)
        overall_analysis["photos"] = analyses

        return overall_analysis

    async def _summarize_analyses(self, analyses: list[dict]) -> dict:
        """분석 결과들을 종합하여 전체 테마 추출"""
        summary_prompt = f"""다음 사진 분석 결과들을 종합하여 전체 스토리 테마를 추출해주세요.

분석 결과: {json.dumps(analyses, ensure_ascii=False)}

## 출력 형식 (반드시 이 JSON 형식으로만 응답, 다른 텍스트 없이)
{{
  "overall_theme": "전체 테마",
  "suggested_narrative_arc": "시작 → 전개 → 결말",
  "emotional_journey": ["감정1", "감정2", "감정3"]
}}"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",  # 텍스트 요약은 LLaMA 사용
                    "messages": [{"role": "user", "content": summary_prompt}],
                    "temperature": 0.1,
                    "max_tokens": 512,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Groq API error: {response.text}")

            result = response.json()
            text_content = result["choices"][0]["message"]["content"]

            # JSON 파싱
            if "```json" in text_content:
                text_content = text_content.split("```json")[1].split("```")[0]
            elif "```" in text_content:
                text_content = text_content.split("```")[1].split("```")[0]

            try:
                return json.loads(text_content.strip())
            except json.JSONDecodeError:
                return {
                    "overall_theme": "개인 스토리",
                    "suggested_narrative_arc": "시작 → 전개 → 결말",
                    "emotional_journey": ["기대", "경험", "회상"]
                }


gemini_service = GeminiService()
