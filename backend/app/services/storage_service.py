import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from ..config import get_settings

settings = get_settings()

# 로컬 저장소 경로
LOCAL_STORAGE_PATH = Path(__file__).parent.parent.parent / "storage"
LOCAL_STORAGE_PATH.mkdir(exist_ok=True)


class LocalStorageService:
    """로컬 파일 저장소 서비스 (개발용)"""

    def __init__(self):
        self.base_path = LOCAL_STORAGE_PATH
        (self.base_path / "photos").mkdir(exist_ok=True)
        (self.base_path / "videos").mkdir(exist_ok=True)

    async def upload_photo(self, project_id: str, photo_data: bytes, filename: str) -> str:
        """사진 업로드"""
        photo_id = str(uuid.uuid4())
        ext = Path(filename).suffix or ".jpg"
        file_path = self.base_path / "photos" / f"{project_id}_{photo_id}{ext}"

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(photo_data)

        return photo_id

    async def get_photo(self, project_id: str, photo_id: str) -> Optional[bytes]:
        """사진 조회"""
        # 확장자 모르므로 패턴 매칭
        for file_path in (self.base_path / "photos").glob(f"{project_id}_{photo_id}.*"):
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()
        return None

    async def get_all_photos(self, project_id: str) -> dict[str, bytes]:
        """프로젝트의 모든 사진 조회"""
        photos = {}
        for file_path in (self.base_path / "photos").glob(f"{project_id}_*"):
            photo_id = file_path.stem.split("_", 1)[1]
            async with aiofiles.open(file_path, "rb") as f:
                photos[photo_id] = await f.read()
        return photos

    async def save_video(self, project_id: str, video_data: bytes) -> str:
        """영상 저장"""
        video_id = str(uuid.uuid4())
        file_path = self.base_path / "videos" / f"{project_id}_{video_id}.mp4"

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(video_data)

        return str(file_path)

    async def delete_project_files(self, project_id: str):
        """프로젝트 관련 파일 삭제"""
        # 사진 삭제
        for file_path in (self.base_path / "photos").glob(f"{project_id}_*"):
            file_path.unlink()
        # 영상 삭제
        for file_path in (self.base_path / "videos").glob(f"{project_id}_*"):
            file_path.unlink()

    def get_photo_url(self, project_id: str, photo_id: str) -> str:
        """사진 URL 반환 (로컬)"""
        return f"/api/v1/storage/photos/{project_id}/{photo_id}"

    def get_video_url(self, project_id: str, video_id: str) -> str:
        """영상 URL 반환 (로컬)"""
        return f"/api/v1/storage/videos/{project_id}/{video_id}"


class S3StorageService:
    """AWS S3 저장소 서비스 (프로덕션용)"""

    def __init__(self):
        import boto3
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket = settings.aws_s3_bucket

    async def upload_photo(self, project_id: str, photo_data: bytes, filename: str) -> str:
        """사진 S3 업로드"""
        photo_id = str(uuid.uuid4())
        ext = Path(filename).suffix or ".jpg"
        key = f"photos/{project_id}/{photo_id}{ext}"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=photo_data,
            ContentType="image/jpeg",
        )

        return photo_id

    async def get_photo(self, project_id: str, photo_id: str) -> Optional[bytes]:
        """S3에서 사진 조회"""
        try:
            # 확장자 시도
            for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                try:
                    key = f"photos/{project_id}/{photo_id}{ext}"
                    response = self.s3.get_object(Bucket=self.bucket, Key=key)
                    return response["Body"].read()
                except:
                    continue
        except Exception:
            pass
        return None

    async def get_all_photos(self, project_id: str) -> dict[str, bytes]:
        """프로젝트의 모든 사진 조회"""
        photos = {}
        prefix = f"photos/{project_id}/"

        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        for obj in response.get("Contents", []):
            key = obj["Key"]
            photo_id = Path(key).stem
            photo_response = self.s3.get_object(Bucket=self.bucket, Key=key)
            photos[photo_id] = photo_response["Body"].read()

        return photos

    async def save_video(self, project_id: str, video_data: bytes) -> str:
        """영상 S3 업로드"""
        video_id = str(uuid.uuid4())
        key = f"videos/{project_id}/{video_id}.mp4"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=video_data,
            ContentType="video/mp4",
        )

        return f"https://{self.bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"

    def get_photo_url(self, project_id: str, photo_id: str) -> str:
        """S3 사진 Pre-signed URL"""
        key = f"photos/{project_id}/{photo_id}.jpg"
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=3600,
        )


def get_storage_service():
    """환경에 따른 저장소 서비스 선택"""
    if settings.aws_s3_bucket and settings.aws_access_key_id:
        return S3StorageService()
    return LocalStorageService()


storage_service = get_storage_service()
