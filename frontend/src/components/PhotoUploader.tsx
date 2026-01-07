import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image } from 'lucide-react';

interface PhotoUploaderProps {
  photos: File[];
  setPhotos: (photos: File[]) => void;
  maxPhotos?: number;
}

export default function PhotoUploader({ photos, setPhotos, maxPhotos = 10 }: PhotoUploaderProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newPhotos = [...photos, ...acceptedFiles].slice(0, maxPhotos);
    setPhotos(newPhotos);
  }, [photos, setPhotos, maxPhotos]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
    maxFiles: maxPhotos - photos.length,
  });

  const removePhoto = (index: number) => {
    setPhotos(photos.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
          ${isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
          ${photos.length >= maxPhotos ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} disabled={photos.length >= maxPhotos} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        {isDragActive ? (
          <p className="text-blue-600 font-medium">여기에 놓아주세요</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">사진을 드래그하거나 클릭하여 업로드</p>
            <p className="text-sm text-gray-400 mt-2">JPG, PNG, WEBP (최대 {maxPhotos}장)</p>
          </>
        )}
      </div>

      {photos.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {photos.map((photo, index) => (
            <div key={index} className="relative group aspect-square">
              <img
                src={URL.createObjectURL(photo)}
                alt={`Photo ${index + 1}`}
                className="w-full h-full object-cover rounded-lg"
              />
              <button
                onClick={() => removePhoto(index)}
                className="absolute top-1 right-1 p-1 bg-black/60 rounded-full text-white
                  opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4" />
              </button>
              <div className="absolute bottom-1 left-1 px-2 py-0.5 bg-black/60 rounded text-white text-xs">
                {index + 1}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <Image className="w-4 h-4" />
          <span>{photos.length} / {maxPhotos} 장</span>
        </div>
        {photos.length >= 3 && (
          <span className="text-green-600">준비 완료!</span>
        )}
      </div>
    </div>
  );
}
