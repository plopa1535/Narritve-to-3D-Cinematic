import httpx
import base64
import json
import asyncio
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
    """Google Gemini API 서비스 (이미지 분석용)"""

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash"

    async def analyze_image(self, image_data: bytes, photo_id: str) -> dict:
        """단일 이미지 분석"""
        base64_image = base64.b64encode(image_data).decode("utf-8")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": base64_image,
                                    }
                                },
                                {"text": IMAGE_ANALYSIS_PROMPT},
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1024,
                    },
                },
            )

            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.text}")

            result = response.json()

            # 응답에서 텍스트 추출
            text_content = result["candidates"][0]["content"]["parts"][0]["text"]

            # JSON 파싱 (마크다운 코드 블록 제거)
            if "```json" in text_content:
                text_content = text_content.split("```json")[1].split("```")[0]
            elif "```" in text_content:
                text_content = text_content.split("```")[1].split("```")[0]

            analysis = json.loads(text_content.strip())
            analysis["photo_id"] = photo_id

            return analysis

    async def analyze_all_images(self, images: list[tuple[str, bytes]]) -> dict:
        """여러 이미지 분석 및 전체 테마 추출 (rate limit 대응)"""
        analyses = []

        for i, (photo_id, image_data) in enumerate(images):
            # 첫 번째 이후 요청은 5초 대기 (rate limit 방지)
            if i > 0:
                await asyncio.sleep(5)

            analysis = await self.analyze_image(image_data, photo_id)
            analyses.append(analysis)

        # 5초 대기 후 요약 요청
        await asyncio.sleep(5)

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
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": summary_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 512,
                    },
                },
            )

            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.text}")

            result = response.json()
            text_content = result["candidates"][0]["content"]["parts"][0]["text"]

            # JSON 파싱
            if "```json" in text_content:
                text_content = text_content.split("```json")[1].split("```")[0]
            elif "```" in text_content:
                text_content = text_content.split("```")[1].split("```")[0]

            return json.loads(text_content.strip())


gemini_service = GeminiService()
