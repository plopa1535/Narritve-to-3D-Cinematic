import { Loader2, CheckCircle, AlertCircle, ImageIcon, Sparkles, Film } from 'lucide-react';

interface ProgressIndicatorProps {
  status: string;
  progress: number;
  message: string;
}

const STEPS = [
  { key: 'upload', label: '사진 업로드', icon: ImageIcon },
  { key: 'analyze', label: 'AI 분석', icon: Sparkles },
  { key: 'generate', label: '영상 생성', icon: Film },
];

export default function ProgressIndicator({ status, progress, message }: ProgressIndicatorProps) {
  const getStepStatus = (stepKey: string) => {
    if (status === 'completed') return 'completed';
    if (status === 'failed') return 'failed';

    const statusMap: Record<string, number> = {
      draft: 0,
      analyzing: 1,
      generating: 2,
      completed: 3,
    };

    const stepMap: Record<string, number> = {
      upload: 0,
      analyze: 1,
      generate: 2,
    };

    const currentStep = statusMap[status] || 0;
    const stepIndex = stepMap[stepKey];

    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className="space-y-6">
      {/* 진행 바 */}
      <div className="relative">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="absolute -top-1 left-0 right-0 flex justify-between">
          {[0, 33, 66, 100].map((pos, idx) => (
            <div
              key={idx}
              className={`w-4 h-4 rounded-full border-2 transition-colors
                ${progress >= pos
                  ? 'bg-blue-500 border-blue-500'
                  : 'bg-white border-gray-300'
                }
              `}
            />
          ))}
        </div>
      </div>

      {/* 단계 표시 */}
      <div className="flex justify-between">
        {STEPS.map((step) => {
          const stepStatus = getStepStatus(step.key);
          const Icon = step.icon;

          return (
            <div key={step.key} className="flex flex-col items-center gap-2">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all
                  ${stepStatus === 'completed' ? 'bg-green-100 text-green-600' : ''}
                  ${stepStatus === 'active' ? 'bg-blue-100 text-blue-600' : ''}
                  ${stepStatus === 'pending' ? 'bg-gray-100 text-gray-400' : ''}
                  ${stepStatus === 'failed' ? 'bg-red-100 text-red-600' : ''}
                `}
              >
                {stepStatus === 'completed' ? (
                  <CheckCircle className="w-6 h-6" />
                ) : stepStatus === 'active' ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : stepStatus === 'failed' ? (
                  <AlertCircle className="w-6 h-6" />
                ) : (
                  <Icon className="w-6 h-6" />
                )}
              </div>
              <span
                className={`text-sm font-medium
                  ${stepStatus === 'active' ? 'text-blue-600' : ''}
                  ${stepStatus === 'completed' ? 'text-green-600' : ''}
                  ${stepStatus === 'pending' ? 'text-gray-400' : ''}
                  ${stepStatus === 'failed' ? 'text-red-600' : ''}
                `}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* 현재 상태 메시지 */}
      <div className="text-center py-4">
        {status === 'generating' && (
          <div className="flex items-center justify-center gap-2 text-blue-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="font-medium">{message}</span>
          </div>
        )}
        {status === 'analyzing' && (
          <div className="flex items-center justify-center gap-2 text-purple-600">
            <Sparkles className="w-5 h-5 animate-pulse" />
            <span className="font-medium">{message}</span>
          </div>
        )}
        {status === 'completed' && (
          <div className="flex items-center justify-center gap-2 text-green-600">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">{message}</span>
          </div>
        )}
        {status === 'failed' && (
          <div className="flex items-center justify-center gap-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">{message}</span>
          </div>
        )}
      </div>
    </div>
  );
}
