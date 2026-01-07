import { useState } from 'react';
import { PenLine, Sparkles } from 'lucide-react';

interface NarrativeInputProps {
  narrative: string;
  setNarrative: (value: string) => void;
  style: string;
  setStyle: (value: string) => void;
}

const STYLE_OPTIONS = [
  { value: 'romantic', label: '로맨틱', emoji: '💕', desc: '사랑스럽고 따뜻한' },
  { value: 'nostalgic', label: '추억', emoji: '📷', desc: '그리운 옛 기억' },
  { value: 'happy', label: '행복', emoji: '🌟', desc: '밝고 즐거운' },
  { value: 'emotional', label: '감성', emoji: '🌙', desc: '잔잔하고 깊은' },
  { value: 'cinematic', label: '시네마틱', emoji: '🎬', desc: '영화같은 웅장함' },
];

const EXAMPLE_NARRATIVES = [
  "우리가 처음 만난 날부터 지금까지, 함께한 모든 순간들이 소중해요.",
  "엄마와 함께한 제주도 여행. 평생 잊지 못할 추억이 되었어요.",
  "졸업 후 친구들과 마지막 여행. 우리의 청춘을 담았습니다.",
  "반려견과 함께한 4년간의 일상. 너는 나의 가족이야.",
];

export default function NarrativeInput({
  narrative,
  setNarrative,
  style,
  setStyle,
}: NarrativeInputProps) {
  const [showExamples, setShowExamples] = useState(false);

  return (
    <div className="space-y-6">
      {/* 스타일 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          영상 스타일
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
          {STYLE_OPTIONS.map(option => (
            <button
              key={option.value}
              onClick={() => setStyle(option.value)}
              className={`p-3 rounded-xl border-2 transition-all text-center
                ${style === option.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <span className="text-2xl">{option.emoji}</span>
              <p className="font-medium mt-1">{option.label}</p>
              <p className="text-xs text-gray-500">{option.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* 서사 입력 */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="block text-sm font-medium text-gray-700">
            <PenLine className="w-4 h-4 inline mr-1" />
            나의 이야기
          </label>
          <button
            onClick={() => setShowExamples(!showExamples)}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            <Sparkles className="w-4 h-4" />
            예시 보기
          </button>
        </div>

        {showExamples && (
          <div className="mb-3 p-3 bg-gray-50 rounded-lg space-y-2">
            <p className="text-xs text-gray-500 mb-2">클릭하여 예시 사용</p>
            {EXAMPLE_NARRATIVES.map((example, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setNarrative(example);
                  setShowExamples(false);
                }}
                className="block w-full text-left p-2 text-sm text-gray-600 hover:bg-white rounded transition-colors"
              >
                "{example}"
              </button>
            ))}
          </div>
        )}

        <textarea
          value={narrative}
          onChange={(e) => setNarrative(e.target.value)}
          placeholder="사진에 담긴 당신의 이야기를 자유롭게 적어주세요.
AI가 당신의 서사를 바탕으로 감성적인 영상을 만들어드립니다."
          className="w-full h-40 p-4 border border-gray-300 rounded-xl resize-none
            focus:ring-2 focus:ring-blue-500 focus:border-transparent
            placeholder:text-gray-400"
        />
        <div className="flex justify-between mt-2 text-sm text-gray-500">
          <span>최소 20자 이상 작성해주세요</span>
          <span className={narrative.length >= 20 ? 'text-green-600' : ''}>
            {narrative.length}자
          </span>
        </div>
      </div>
    </div>
  );
}
