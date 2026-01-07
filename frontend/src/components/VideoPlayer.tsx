import { Download, Share2, RotateCcw, Play } from 'lucide-react';

interface VideoPlayerProps {
  videoUrl: string;
  onReset: () => void;
}

export default function VideoPlayer({ videoUrl, onReset }: VideoPlayerProps) {
  const handleDownload = async () => {
    try {
      const response = await fetch(videoUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `my-shorts-${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: '나만의 숏츠 영상',
          text: 'Personal Shorts로 만든 영상을 확인해보세요!',
          url: videoUrl,
        });
      } catch (error) {
        console.error('Share failed:', error);
      }
    } else {
      // 클립보드에 URL 복사
      await navigator.clipboard.writeText(videoUrl);
      alert('링크가 클립보드에 복사되었습니다!');
    }
  };

  return (
    <div className="space-y-6">
      {/* 영상 플레이어 */}
      <div className="relative bg-black rounded-2xl overflow-hidden aspect-[9/16] max-w-sm mx-auto shadow-2xl">
        <video
          src={videoUrl}
          controls
          autoPlay
          loop
          playsInline
          className="w-full h-full object-contain"
        >
          브라우저가 비디오를 지원하지 않습니다.
        </video>
      </div>

      {/* 액션 버튼들 */}
      <div className="flex justify-center gap-4">
        <button
          onClick={handleDownload}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl
            hover:bg-blue-700 transition-colors font-medium"
        >
          <Download className="w-5 h-5" />
          다운로드
        </button>

        <button
          onClick={handleShare}
          className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl
            hover:bg-gray-200 transition-colors font-medium"
        >
          <Share2 className="w-5 h-5" />
          공유하기
        </button>
      </div>

      {/* 새로 만들기 */}
      <div className="text-center pt-4">
        <button
          onClick={onReset}
          className="flex items-center gap-2 mx-auto text-gray-500 hover:text-gray-700 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          새 영상 만들기
        </button>
      </div>
    </div>
  );
}
