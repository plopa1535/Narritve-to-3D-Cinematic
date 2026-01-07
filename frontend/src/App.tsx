import { useState, useEffect } from 'react';
import { Film, ChevronRight, ChevronLeft } from 'lucide-react';
import PhotoUploader from './components/PhotoUploader';
import NarrativeInput from './components/NarrativeInput';
import ProgressIndicator from './components/ProgressIndicator';
import VideoPlayer from './components/VideoPlayer';
import * as api from './api';

type Step = 'upload' | 'narrative' | 'processing' | 'complete';

export default function App() {
  const [step, setStep] = useState<Step>('upload');
  const [photos, setPhotos] = useState<File[]>([]);
  const [narrative, setNarrative] = useState('');
  const [style, setStyle] = useState('emotional');
  const [projectId, setProjectId] = useState<string | null>(null);
  const [status, setStatus] = useState({ status: 'draft', progress: 0, message: '' });
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 상태 폴링
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (projectId && (status.status === 'analyzing' || status.status === 'generating')) {
      interval = setInterval(async () => {
        try {
          const statusData = await api.getGenerationStatus(projectId);
          setStatus(statusData);

          if (statusData.status === 'completed' && statusData.video_url) {
            setVideoUrl(statusData.video_url);
            setStep('complete');
          } else if (statusData.status === 'failed') {
            setError(statusData.message);
          }
        } catch (err) {
          console.error('Status polling error:', err);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [projectId, status.status]);

  const handleNext = async () => {
    if (step === 'upload' && photos.length >= 3) {
      setStep('narrative');
    } else if (step === 'narrative' && narrative.length >= 20) {
      await startProcessing();
    }
  };

  const handleBack = () => {
    if (step === 'narrative') {
      setStep('upload');
    }
  };

  const startProcessing = async () => {
    setError(null);
    setStep('processing');

    try {
      // 1. 프로젝트 생성
      const project = await api.createProject('My Shorts');
      setProjectId(project.id);

      // 2. 사진 업로드
      setStatus({ status: 'analyzing', progress: 10, message: '사진 업로드 중...' });
      await api.uploadPhotos(project.id, photos);

      // 3. 서사 설정
      setStatus({ status: 'analyzing', progress: 20, message: '서사 저장 중...' });
      await api.setNarrative(project.id, narrative, style);

      // 4. 분석 시작
      setStatus({ status: 'analyzing', progress: 30, message: 'AI가 사진을 분석하고 있어요...' });
      await api.analyzePhotos(project.id);

      // 5. 영상 생성 시작
      setStatus({ status: 'generating', progress: 50, message: '영상을 생성하고 있어요...' });
      await api.startGeneration(project.id);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '오류가 발생했습니다.');
      setStatus({ status: 'failed', progress: 0, message: '생성 실패' });
    }
  };

  const handleReset = () => {
    setStep('upload');
    setPhotos([]);
    setNarrative('');
    setStyle('emotional');
    setProjectId(null);
    setStatus({ status: 'draft', progress: 0, message: '' });
    setVideoUrl(null);
    setError(null);
  };

  const canProceed = () => {
    if (step === 'upload') return photos.length >= 3;
    if (step === 'narrative') return narrative.length >= 20;
    return false;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* 헤더 */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Film className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-gray-900">Personal Shorts</h1>
              <p className="text-xs text-gray-500">나만의 숏츠 영화</p>
            </div>
          </div>

          {/* 스텝 인디케이터 */}
          {step !== 'complete' && (
            <div className="hidden sm:flex items-center gap-2 text-sm">
              <span className={step === 'upload' ? 'text-blue-600 font-medium' : 'text-gray-400'}>
                1. 사진
              </span>
              <ChevronRight className="w-4 h-4 text-gray-300" />
              <span className={step === 'narrative' ? 'text-blue-600 font-medium' : 'text-gray-400'}>
                2. 서사
              </span>
              <ChevronRight className="w-4 h-4 text-gray-300" />
              <span className={step === 'processing' ? 'text-blue-600 font-medium' : 'text-gray-400'}>
                3. 생성
              </span>
            </div>
          )}
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Step 1: 사진 업로드 */}
        {step === 'upload' && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">사진을 올려주세요</h2>
            <p className="text-gray-600 mb-6">
              영상에 담고 싶은 사진을 3~10장 선택해주세요.
              <br />
              <span className="text-sm text-gray-400">순서대로 영상이 구성됩니다.</span>
            </p>

            <PhotoUploader photos={photos} setPhotos={setPhotos} maxPhotos={10} />
          </div>
        )}

        {/* Step 2: 서사 입력 */}
        {step === 'narrative' && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">이야기를 들려주세요</h2>
            <p className="text-gray-600 mb-6">
              사진에 담긴 당신의 이야기를 자유롭게 적어주세요.
              <br />
              <span className="text-sm text-gray-400">AI가 이를 바탕으로 감성적인 영상을 만들어드립니다.</span>
            </p>

            <NarrativeInput
              narrative={narrative}
              setNarrative={setNarrative}
              style={style}
              setStyle={setStyle}
            />
          </div>
        )}

        {/* Step 3: 처리 중 */}
        {step === 'processing' && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">영상을 만들고 있어요</h2>
            <p className="text-gray-600 mb-8 text-center">
              AI가 당신의 이야기를 영상으로 만들고 있습니다.
              <br />
              <span className="text-sm text-gray-400">잠시만 기다려주세요...</span>
            </p>

            <ProgressIndicator
              status={status.status}
              progress={status.progress}
              message={status.message}
            />

            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-center">
                <p className="text-red-600">{error}</p>
                <button
                  onClick={handleReset}
                  className="mt-3 text-sm text-red-600 hover:text-red-700 underline"
                >
                  처음부터 다시 시작
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 4: 완료 */}
        {step === 'complete' && videoUrl && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">영상이 완성됐어요!</h2>
            <p className="text-gray-600 mb-8 text-center">
              당신만의 숏츠 영화가 준비되었습니다.
            </p>

            <VideoPlayer videoUrl={videoUrl} onReset={handleReset} />
          </div>
        )}

        {/* 네비게이션 버튼 */}
        {(step === 'upload' || step === 'narrative') && (
          <div className="flex justify-between mt-6">
            {step === 'narrative' ? (
              <button
                onClick={handleBack}
                className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
                이전
              </button>
            ) : (
              <div />
            )}

            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className={`flex items-center gap-2 px-8 py-3 rounded-xl font-medium transition-all
                ${canProceed()
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-200'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              {step === 'narrative' ? '영상 만들기' : '다음'}
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </main>

      {/* 푸터 */}
      <footer className="text-center py-8 text-sm text-gray-400">
        <p>Powered by Qwen + Pika AI</p>
      </footer>
    </div>
  );
}
