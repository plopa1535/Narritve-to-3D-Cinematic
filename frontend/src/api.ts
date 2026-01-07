import axios from 'axios';

// 같은 도메인에서 서빙되므로 상대 경로 사용
const api = axios.create({
  baseURL: '/api/v1',
});

export interface Project {
  id: string;
  title: string | null;
  status: 'draft' | 'analyzing' | 'generating' | 'completed' | 'failed';
  photo_count: number;
  narrative: string | null;
  video_url: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface PhotoAnalysis {
  photo_id: string;
  people: { count: number; relationship: string; emotions: string[] };
  setting: { type: string; indoor: boolean; time: string; season: string };
  mood: string;
  colors: string[];
  key_elements: string[];
}

export interface AnalysisResult {
  project_id: string;
  photos: PhotoAnalysis[];
  overall_theme: string;
  suggested_narrative_arc: string;
  emotional_journey: string[];
}

export interface GenerationStatus {
  project_id: string;
  status: string;
  progress: number;
  message: string;
  video_url: string | null;
}

// API 함수들
export const createProject = async (title?: string): Promise<Project> => {
  const response = await api.post('/projects', { title });
  return response.data;
};

export const getProject = async (projectId: string): Promise<Project> => {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
};

export const uploadPhotos = async (projectId: string, files: File[]): Promise<{ photos: { id: string; filename: string }[] }> => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  const response = await api.post(`/projects/${projectId}/photos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const setNarrative = async (projectId: string, narrative: string, style: string): Promise<void> => {
  await api.put(`/projects/${projectId}/narrative`, { narrative, style });
};

export const analyzePhotos = async (projectId: string): Promise<AnalysisResult> => {
  const response = await api.post(`/projects/${projectId}/analyze`);
  return response.data;
};

export const startGeneration = async (projectId: string): Promise<void> => {
  await api.post(`/projects/${projectId}/generate`);
};

export const getGenerationStatus = async (projectId: string): Promise<GenerationStatus> => {
  const response = await api.get(`/projects/${projectId}/status`);
  return response.data;
};

export const deleteProject = async (projectId: string): Promise<void> => {
  await api.delete(`/projects/${projectId}`);
};

export default api;
