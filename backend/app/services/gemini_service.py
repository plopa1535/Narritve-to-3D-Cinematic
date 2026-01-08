import httpx
import base64
import json
from ..config import get_settings

settings = get_settings()


class VisionService:
    """Google Cloud Vision API 서비스 (이미지 분석용)"""

    def __init__(self):
        self.api_key = settings.google_vision_api_key
        self.base_url = "https://vision.googleapis.com/v1"

    async def analyze_image(self, image_data: bytes, photo_id: str) -> dict:
        """단일 이미지 분석 - Vision API로 라벨, 얼굴, 색상 등 추출"""
        base64_image = base64.b64encode(image_data).decode("utf-8")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/images:annotate",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "requests": [
                        {
                            "image": {"content": base64_image},
                            "features": [
                                {"type": "LABEL_DETECTION", "maxResults": 10},
                                {"type": "FACE_DETECTION", "maxResults": 10},
                                {"type": "IMAGE_PROPERTIES"},
                                {"type": "LANDMARK_DETECTION", "maxResults": 5},
                                {"type": "OBJECT_LOCALIZATION", "maxResults": 10},
                            ],
                        }
                    ]
                },
            )

            if response.status_code != 200:
                raise Exception(f"Vision API error: {response.text}")

            result = response.json()
            response_data = result.get("responses", [{}])[0]

            # Vision API 결과를 우리 형식으로 변환
            analysis = self._parse_vision_response(response_data)
            analysis["photo_id"] = photo_id

            return analysis

    def _parse_vision_response(self, response: dict) -> dict:
        """Vision API 응답을 분석 형식으로 변환"""
        # 라벨 추출
        labels = [label.get("description", "") for label in response.get("labelAnnotations", [])]

        # 얼굴 분석
        faces = response.get("faceAnnotations", [])
        face_count = len(faces)
        emotions = []
        for face in faces:
            if face.get("joyLikelihood") in ["LIKELY", "VERY_LIKELY"]:
                emotions.append("happy")
            if face.get("sorrowLikelihood") in ["LIKELY", "VERY_LIKELY"]:
                emotions.append("sad")
            if face.get("surpriseLikelihood") in ["LIKELY", "VERY_LIKELY"]:
                emotions.append("surprised")

        # 색상 추출
        colors = []
        image_props = response.get("imagePropertiesAnnotation", {})
        dominant_colors = image_props.get("dominantColors", {}).get("colors", [])
        for color_info in dominant_colors[:5]:
            color = color_info.get("color", {})
            r, g, b = color.get("red", 0), color.get("green", 0), color.get("blue", 0)
            colors.append(f"rgb({int(r)},{int(g)},{int(b)})")

        # 랜드마크 추출
        landmarks = [lm.get("description", "") for lm in response.get("landmarkAnnotations", [])]

        # 객체 추출
        objects = [obj.get("name", "") for obj in response.get("localizedObjectAnnotations", [])]

        # 실내/실외 판단
        indoor_keywords = ["room", "interior", "indoor", "furniture", "ceiling"]
        outdoor_keywords = ["sky", "outdoor", "nature", "tree", "building", "street"]
        indoor = any(kw in " ".join(labels).lower() for kw in indoor_keywords)
        outdoor = any(kw in " ".join(labels).lower() for kw in outdoor_keywords)

        # 분위기 추정
        mood = "neutral"
        if emotions:
            if "happy" in emotions:
                mood = "joyful"
            elif "sad" in emotions:
                mood = "melancholy"
        elif any(kw in " ".join(labels).lower() for kw in ["sunset", "beach", "nature"]):
            mood = "peaceful"

        return {
            "people": {
                "count": face_count,
                "relationship": "unknown",
                "emotions": list(set(emotions)) if emotions else ["neutral"],
            },
            "setting": {
                "type": landmarks[0] if landmarks else (objects[0] if objects else "unknown"),
                "indoor": indoor and not outdoor,
                "time": "unknown",
                "season": "unknown",
            },
            "mood": mood,
            "colors": colors,
            "key_elements": labels[:5] + objects[:3],
        }

    async def analyze_all_images(self, images: list[tuple[str, bytes]]) -> dict:
        """여러 이미지 분석 및 전체 테마 추출"""
        analyses = []

        for photo_id, image_data in images:
            analysis = await self.analyze_image(image_data, photo_id)
            analyses.append(analysis)

        # 전체 분석 요약 (Groq 사용)
        overall_analysis = await self._summarize_with_groq(analyses)
        overall_analysis["photos"] = analyses

        return overall_analysis

    async def _summarize_with_groq(self, analyses: list[dict]) -> dict:
        """Groq를 사용하여 분석 결과 요약"""
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
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": summary_prompt}],
                    "temperature": 0.1,
                    "max_tokens": 512,
                },
            )

            if response.status_code != 200:
                # Groq 실패시 기본값 반환
                return {
                    "overall_theme": "개인 스토리",
                    "suggested_narrative_arc": "시작 → 전개 → 결말",
                    "emotional_journey": ["기대", "경험", "회상"],
                }

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
                    "emotional_journey": ["기대", "경험", "회상"],
                }


# 기존 코드 호환성을 위해 이름 유지
gemini_service = VisionService()
GeminiService = VisionService
