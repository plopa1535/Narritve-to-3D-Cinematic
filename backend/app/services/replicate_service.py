import httpx
import base64
import asyncio
from typing import Optional
from ..config import get_settings

settings = get_settings()


class ReplicateService:
    """Replicate 영상 생성 서비스

    Minimax video-01 (Hailuo) 모델 사용
    - 해상도: 720p
    - FPS: 25
    - 영상 길이: 6초
    - 무료: 카드 없이 제한된 횟수 무료 사용 가능
    """

    def __init__(self):
        self.api_key = settings.replicate_api_key
        self.base_url = "https://api.replicate.com/v1"
        self.model_version = "minimax/video-01"

    async def generate_video_from_image(
        self,
        image_data: bytes,
        prompt: str,
    ) -> dict:
        """이미지에서 영상 생성 (Image-to-Video)

        Args:
            image_data: 원본 이미지 바이트 데이터
            prompt: 영상 생성 프롬프트 (영어)

        Returns:
            생성된 영상 정보 (prediction_id 등)
        """
        # 이미지를 base64 data URL로 변환
        base64_image = base64.b64encode(image_data).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{base64_image}"

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model_version}/predictions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Prefer": "wait",  # 동기 방식으로 결과 대기
                },
                json={
                    "input": {
                        "prompt": prompt,
                        "first_frame_image": image_url,
                        "prompt_optimizer": True,
                    }
                },
            )

            if response.status_code not in [200, 201, 202]:
                raise Exception(f"Replicate API error: {response.text}")

            result = response.json()
            return {
                "prediction_id": result.get("id"),
                "status": result.get("status"),
                "video_url": result.get("output"),
            }

    async def generate_video_from_prompt(
        self,
        prompt: str,
    ) -> dict:
        """텍스트 프롬프트로 영상 생성 (Text-to-Video)

        Args:
            prompt: 영상 생성 프롬프트 (영어)

        Returns:
            생성된 영상 정보
        """
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model_version}/predictions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": {
                        "prompt": prompt,
                        "prompt_optimizer": True,
                    }
                },
            )

            if response.status_code not in [200, 201, 202]:
                raise Exception(f"Replicate API error: {response.text}")

            result = response.json()
            return {
                "prediction_id": result.get("id"),
                "status": result.get("status"),
                "video_url": result.get("output"),
            }

    async def get_prediction_status(self, prediction_id: str) -> dict:
        """영상 생성 상태 조회"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/predictions/{prediction_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code != 200:
                raise Exception(f"Replicate API error: {response.text}")

            result = response.json()
            status = result.get("status")

            if status == "succeeded":
                return {
                    "status": "completed",
                    "video_url": result.get("output"),
                }
            elif status == "failed":
                return {
                    "status": "failed",
                    "error": result.get("error"),
                }
            else:
                return {"status": status}

    async def wait_for_completion(
        self, prediction_id: str, max_wait: int = 600, poll_interval: int = 10
    ) -> dict:
        """영상 생성 완료까지 대기

        Args:
            prediction_id: 예측 ID
            max_wait: 최대 대기 시간 (초)
            poll_interval: 폴링 간격 (초)
        """
        elapsed = 0
        while elapsed < max_wait:
            status = await self.get_prediction_status(prediction_id)

            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                raise Exception(f"Video generation failed: {status.get('error')}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise Exception("Video generation timeout")

    async def generate_scene_videos(
        self, scenes: list[dict], images: dict[str, bytes]
    ) -> list[dict]:
        """여러 씬의 영상 생성

        Args:
            scenes: 스크립트의 씬 목록
            images: photo_id -> image_data 매핑

        Returns:
            생성된 영상 정보 목록
        """
        results = []

        for scene in scenes:
            photo_id = scene.get("photo_id")
            video_prompt = scene.get("video_prompt", "")

            # 이미지가 있으면 image-to-video, 없으면 text-to-video
            if photo_id and photo_id in images:
                image_data = images[photo_id]
                generation = await self.generate_video_from_image(
                    image_data=image_data,
                    prompt=video_prompt,
                )
            else:
                generation = await self.generate_video_from_prompt(
                    prompt=video_prompt,
                )

            # 이미 완료된 경우 (Prefer: wait 사용 시)
            if generation.get("video_url"):
                result = {
                    "status": "completed",
                    "video_url": generation.get("video_url"),
                    "scene_id": scene.get("scene_id"),
                }
            else:
                # 완료 대기 필요
                result = await self.wait_for_completion(generation["prediction_id"])
                result["scene_id"] = scene.get("scene_id")

            results.append(result)

        return results


class MockReplicateService:
    """테스트용 Mock Replicate 서비스"""

    async def generate_video_from_image(
        self,
        image_data: bytes,
        prompt: str,
    ) -> dict:
        await asyncio.sleep(2)
        return {
            "prediction_id": "mock_replicate_123",
            "status": "succeeded",
            "video_url": "https://example.com/mock_replicate_video.mp4",
        }

    async def generate_video_from_prompt(
        self,
        prompt: str,
    ) -> dict:
        await asyncio.sleep(2)
        return {
            "prediction_id": "mock_replicate_123",
            "status": "succeeded",
            "video_url": "https://example.com/mock_replicate_video.mp4",
        }

    async def get_prediction_status(self, prediction_id: str) -> dict:
        return {
            "status": "completed",
            "video_url": "https://example.com/mock_replicate_video.mp4",
        }

    async def wait_for_completion(
        self, prediction_id: str, max_wait: int = 600, poll_interval: int = 10
    ) -> dict:
        await asyncio.sleep(3)
        return {
            "status": "completed",
            "video_url": "https://example.com/mock_replicate_video.mp4",
        }

    async def generate_scene_videos(
        self, scenes: list[dict], images: dict[str, bytes]
    ) -> list[dict]:
        results = []
        for scene in scenes:
            await asyncio.sleep(1)
            results.append({
                "scene_id": scene.get("scene_id"),
                "status": "completed",
                "video_url": f"https://example.com/replicate_scene_{scene.get('scene_id')}.mp4",
            })
        return results


def get_replicate_service():
    """Replicate API 키가 있으면 실제 서비스, 없으면 Mock 서비스"""
    if settings.replicate_api_key:
        return ReplicateService()
    return MockReplicateService()


replicate_service = get_replicate_service()
