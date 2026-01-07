from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class StylePreference(str, Enum):
    ROMANTIC = "romantic"
    NOSTALGIC = "nostalgic"
    HAPPY = "happy"
    EMOTIONAL = "emotional"
    CINEMATIC = "cinematic"


# Request Models
class ProjectCreate(BaseModel):
    title: Optional[str] = None


class NarrativeInput(BaseModel):
    narrative: str
    style: StylePreference = StylePreference.EMOTIONAL


# Response Models
class PhotoAnalysis(BaseModel):
    photo_id: str
    people: dict
    setting: dict
    mood: str
    colors: list[str]
    key_elements: list[str]


class SceneScript(BaseModel):
    scene_id: int
    start_time: float
    end_time: float
    photo_id: str
    transition: str
    camera_movement: str
    emotion: str
    video_prompt: str


class VideoScript(BaseModel):
    title: str
    total_duration: int
    scenes: list[SceneScript]
    overall_mood: str
    color_grading: str


class ProjectResponse(BaseModel):
    id: str
    title: Optional[str]
    status: ProjectStatus
    photo_count: int
    narrative: Optional[str]
    video_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class AnalysisResponse(BaseModel):
    project_id: str
    photos: list[PhotoAnalysis]
    overall_theme: str
    suggested_narrative_arc: str
    emotional_journey: list[str]


class GenerationStatusResponse(BaseModel):
    project_id: str
    status: ProjectStatus
    progress: int  # 0-100
    message: str
    video_url: Optional[str] = None
