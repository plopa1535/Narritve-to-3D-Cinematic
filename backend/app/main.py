from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .api import api_router
from .config import get_settings

settings = get_settings()

app = FastAPI(
    title="Personal Shorts Service",
    description="개인화된 1분 숏츠 영화 생성 서비스 API",
    version="1.0.0",
)

# CORS 설정 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)

# 로컬 스토리지 정적 파일 서빙
storage_path = Path(__file__).parent.parent / "storage"
storage_path.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# 프론트엔드 정적 파일 경로
static_path = Path(__file__).parent.parent / "static"


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# 프론트엔드 정적 파일 서빙 (SPA)
if static_path.exists():
    app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # API 경로는 제외
        if full_path.startswith("api/") or full_path.startswith("storage/"):
            return {"detail": "Not Found"}

        # 정적 파일 확인
        file_path = static_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # SPA fallback - index.html 반환
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return {"detail": "Not Found"}
