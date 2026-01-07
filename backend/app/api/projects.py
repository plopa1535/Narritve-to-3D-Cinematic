import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional

from ..models.schemas import (
    ProjectCreate,
    NarrativeInput,
    ProjectResponse,
    ProjectStatus,
    AnalysisResponse,
    GenerationStatusResponse,
)
from ..services import gemini_service, groq_service, replicate_service, storage_service

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory 프로젝트 저장소 (실제로는 DB 사용)
projects_db: dict = {}


@router.post("", response_model=ProjectResponse)
async def create_project(project: ProjectCreate = None):
    """새 프로젝트 생성"""
    project_id = str(uuid.uuid4())

    projects_db[project_id] = {
        "id": project_id,
        "title": project.title if project else None,
        "status": ProjectStatus.DRAFT,
        "photos": [],
        "photo_analyses": [],
        "narrative": None,
        "style": None,
        "script": None,
        "video_url": None,
        "created_at": datetime.now(),
        "completed_at": None,
    }

    return ProjectResponse(
        id=project_id,
        title=projects_db[project_id]["title"],
        status=ProjectStatus.DRAFT,
        photo_count=0,
        narrative=None,
        video_url=None,
        created_at=projects_db[project_id]["created_at"],
        completed_at=None,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """프로젝트 조회"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    return ProjectResponse(
        id=project_id,
        title=project["title"],
        status=project["status"],
        photo_count=len(project["photos"]),
        narrative=project["narrative"],
        video_url=project["video_url"],
        created_at=project["created_at"],
        completed_at=project["completed_at"],
    )


@router.post("/{project_id}/photos")
async def upload_photos(project_id: str, files: list[UploadFile] = File(...)):
    """사진 업로드 (여러 장)"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 photos allowed")

    uploaded_photos = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")

        photo_data = await file.read()
        photo_id = await storage_service.upload_photo(project_id, photo_data, file.filename)

        projects_db[project_id]["photos"].append({
            "id": photo_id,
            "filename": file.filename,
        })
        uploaded_photos.append({"id": photo_id, "filename": file.filename})

    return {
        "message": f"{len(uploaded_photos)} photos uploaded",
        "photos": uploaded_photos,
    }


@router.put("/{project_id}/narrative")
async def set_narrative(project_id: str, narrative_input: NarrativeInput):
    """서사 입력"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    projects_db[project_id]["narrative"] = narrative_input.narrative
    projects_db[project_id]["style"] = narrative_input.style.value

    return {"message": "Narrative saved", "narrative": narrative_input.narrative}


@router.post("/{project_id}/analyze", response_model=AnalysisResponse)
async def analyze_photos(project_id: str):
    """사진 분석 시작"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    if not project["photos"]:
        raise HTTPException(status_code=400, detail="No photos uploaded")

    # 상태 업데이트
    project["status"] = ProjectStatus.ANALYZING

    # 모든 사진 로드
    images = []
    all_photos = await storage_service.get_all_photos(project_id)

    for photo in project["photos"]:
        photo_id = photo["id"]
        if photo_id in all_photos:
            images.append((photo_id, all_photos[photo_id]))

    # Gemini로 분석 (무료)
    try:
        analysis_result = await gemini_service.analyze_all_images(images)
        project["photo_analyses"] = analysis_result
        project["status"] = ProjectStatus.DRAFT  # 분석 완료, 생성 대기

        return AnalysisResponse(
            project_id=project_id,
            photos=analysis_result["photos"],
            overall_theme=analysis_result["overall_theme"],
            suggested_narrative_arc=analysis_result["suggested_narrative_arc"],
            emotional_journey=analysis_result["emotional_journey"],
        )
    except Exception as e:
        project["status"] = ProjectStatus.FAILED
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def _generate_video_task(project_id: str):
    """백그라운드 영상 생성 태스크"""
    project = projects_db[project_id]

    try:
        # 1. 스크립트 생성 (Groq - 무료)
        script = await groq_service.generate_script(
            image_analysis=project["photo_analyses"],
            narrative=project["narrative"],
            style=project["style"],
        )
        project["script"] = script

        # 2. 이미지 로드
        images = await storage_service.get_all_photos(project_id)

        # 3. 각 씬별 영상 생성 (Replicate - Minimax video-01)
        scene_videos = await replicate_service.generate_scene_videos(
            scenes=script["scenes"],
            images=images,
        )

        # 4. 최종 영상 URL 저장 (실제로는 영상 병합 필요)
        # 여기서는 첫 번째 씬 영상을 대표로 사용
        if scene_videos:
            project["video_url"] = scene_videos[0].get("video_url")

        project["status"] = ProjectStatus.COMPLETED
        project["completed_at"] = datetime.now()

    except Exception as e:
        project["status"] = ProjectStatus.FAILED
        project["error"] = str(e)


@router.post("/{project_id}/generate")
async def start_generation(project_id: str, background_tasks: BackgroundTasks):
    """영상 생성 시작"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    if not project["photos"]:
        raise HTTPException(status_code=400, detail="No photos uploaded")

    if not project["narrative"]:
        raise HTTPException(status_code=400, detail="Narrative not set")

    if not project.get("photo_analyses"):
        raise HTTPException(status_code=400, detail="Photos not analyzed yet")

    # 상태 업데이트
    project["status"] = ProjectStatus.GENERATING

    # 백그라운드에서 영상 생성
    background_tasks.add_task(_generate_video_task, project_id)

    return {"message": "Video generation started", "project_id": project_id}


@router.get("/{project_id}/status", response_model=GenerationStatusResponse)
async def get_generation_status(project_id: str):
    """영상 생성 상태 조회"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    # 진행률 계산 (간단한 예시)
    progress_map = {
        ProjectStatus.DRAFT: 0,
        ProjectStatus.ANALYZING: 25,
        ProjectStatus.GENERATING: 50,
        ProjectStatus.COMPLETED: 100,
        ProjectStatus.FAILED: 0,
    }

    status_messages = {
        ProjectStatus.DRAFT: "Ready to generate",
        ProjectStatus.ANALYZING: "Analyzing photos...",
        ProjectStatus.GENERATING: "Generating video...",
        ProjectStatus.COMPLETED: "Video ready!",
        ProjectStatus.FAILED: f"Failed: {project.get('error', 'Unknown error')}",
    }

    return GenerationStatusResponse(
        project_id=project_id,
        status=project["status"],
        progress=progress_map.get(project["status"], 0),
        message=status_messages.get(project["status"], "Unknown status"),
        video_url=project.get("video_url"),
    )


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """프로젝트 삭제"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    # 파일 삭제
    await storage_service.delete_project_files(project_id)

    # DB에서 삭제
    del projects_db[project_id]

    return {"message": "Project deleted"}
