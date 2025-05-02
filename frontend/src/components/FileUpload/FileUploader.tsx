import React, { useState, useRef, useEffect } from 'react';
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Upload, Image as ImageIcon, Music, Video, Loader2 } from 'lucide-react';
import { useChat } from '@/contexts/ChatContext';
import { uploadImage, uploadVideo, uploadAudio } from '@/services/api';

interface FileUploaderProps {
  type: 'image' | 'video' | 'music';
  onFileSelect: (file: File, uploadResult?: any) => void;
  resetTrigger?: number;
  disabled?: boolean;
}

const FileUploader: React.FC<FileUploaderProps> = ({ type, onFileSelect, resetTrigger = 0, disabled = false }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const { isLoading } = useChat();

  useEffect(() => {
    if (resetTrigger > 0) {
      setUploadedFile(null);
      setVideoBlob(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [resetTrigger]);

  const validateVideoDuration = (file: File): Promise<boolean> => {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        window.URL.revokeObjectURL(video.src);
        if (video.duration > 30) {
          toast.error('영상은 30초 이하만 업로드 가능합니다.');
          resolve(false);
        } else {
          resolve(true);
        }
      };
      video.src = URL.createObjectURL(file);
    });
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      e.target.value = '';
      validateAndProcessFile(file);
    }
  };

  const validateAndProcessFile = async (file: File) => {
    if (type === 'image') {
      const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
      if (!validTypes.includes(file.type)) {
        toast.error('지원하지 않는 이미지 형식입니다.');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        toast.error('이미지 크기가 너무 큽니다.');
        return;
      }
      try {
        setIsUploading(true);
        const result = await uploadImage(file);
        toast.success('이미지 업로드 성공');
        setUploadedFile(file);
        onFileSelect(file, result);
      } catch (error) {
        toast.error('이미지 업로드 실패');
      } finally {
        setIsUploading(false);
      }
    } else if (type === 'video') {
      const validTypes = ['video/mp4', 'video/webm', 'video/quicktime'];
      if (!validTypes.includes(file.type)) {
        toast.error('지원하지 않는 영상 형식입니다.');
        return;
      }
      if (file.size > 100 * 1024 * 1024) {
        toast.error('파일 크기가 너무 큽니다.');
        return;
      }
      const isValidDuration = await validateVideoDuration(file);
      if (!isValidDuration) return;
      try {
        setIsUploading(true);
        // 영상 처리 결과 - Blob URL 반환
        const videoUrl = await uploadVideo(file);
        toast.success('영상이 성공적으로 처리되었습니다.');
        console.log('Video URL:', videoUrl);
        setUploadedFile(file);
        // 영상 URL을 결과로 전달
        onFileSelect(file, { url: videoUrl });
      } catch (error) {
        console.error('Upload error:', error);
        toast.error('영상 처리 중 오류가 발생했습니다.');
        toast.error('영상 업로드 실패');
      } finally {
        setIsUploading(false);
      }
    } else if (type === 'music') {
      const validTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3', 'audio/m4a'];
      if (!validTypes.includes(file.type)) {
        toast.error('지원하지 않는 음악 형식입니다.');
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        toast.error('음악 파일이 너무 큽니다.');
        return;
      }
      try {
        setIsUploading(true);
        const result = await uploadAudio(file);
        toast.success('음악 업로드 성공');
        setUploadedFile(file);
        onFileSelect(file, result);
      } catch (error) {
        toast.error('음악 업로드 실패');
      } finally {
        setIsUploading(false);
      }
    }
  };

  const handleDownloadClick = () => {
    if (!videoBlob) return;
    const url = URL.createObjectURL(videoBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated_${Date.now()}.mp4`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const triggerFileInput = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div>
      <div
        className={`border-2 border-dashed p-2 rounded-xl transition-all ${isUploading ? 'cursor-wait' : disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'} flex flex-col items-center justify-center h-full max-h-full overflow-hidden w-full ${
          isDragging && !disabled
            ? 'border-primary bg-primary/10'
            : disabled
              ? 'border-muted'
              : 'border-muted hover:border-primary/50 hover:bg-muted/50'
        }`}
        onDragOver={disabled ? undefined : (e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={disabled ? undefined : () => setIsDragging(false)}
        onDrop={disabled ? undefined : (e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files.length) {
            validateAndProcessFile(e.dataTransfer.files[0]);
          }
        }}
        onClick={disabled || isUploading || uploadedFile ? undefined : triggerFileInput}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept={type === 'image' ? 'image/*' : type === 'video' ? 'video/*' : 'audio/*'}
          disabled={disabled || isLoading || isUploading}
        />
        <div className="flex flex-col items-center justify-center text-center gap-1 py-1 max-h-full overflow-hidden">
          {isUploading ? (
            <>
              <Loader2 className="h-4 w-4 text-primary animate-spin" />
              <div className="text-xs font-medium">업로드 중...</div>
            </>
          ) : uploadedFile ? (
            <>
              {type === 'image' ? <ImageIcon className="h-4 w-4 text-primary" /> : type === 'video' ? <Video className="h-4 w-4 text-primary" /> : <Music className="h-4 w-4 text-primary" />}
              <div className="text-xs font-medium truncate w-full">
                {uploadedFile.name.length > 15 ? `${uploadedFile.name.substring(0, 12)}...` : uploadedFile.name}
              </div>
              <Button variant="ghost" size="sm" className="text-xs p-1 h-auto min-h-0" onClick={(e) => {
                e.stopPropagation();
                setUploadedFile(null);
                setVideoBlob(null);
                if (fileInputRef.current) fileInputRef.current.value = '';
                triggerFileInput();
              }}>다른 파일</Button>
            </>
          ) : (
            <>
              {type === 'image' ? <ImageIcon className="h-4 w-4 text-muted-foreground" /> : type === 'video' ? <Video className="h-4 w-4 text-muted-foreground" /> : <Music className="h-4 w-4 text-muted-foreground" />}
              <div className="text-xs font-medium">
                {disabled ? (
                  <span className="text-red-500">업로드 불가</span>
                ) : (
                  type === 'image' ? '이미지 업로드' : type === 'video' ? '영상 (30초 이하) 업로드' : '음악 업로드'
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {videoBlob && (
        <div className="mt-4 space-y-2">
          <video controls src={URL.createObjectURL(videoBlob)} className="w-full rounded shadow" />
          <Button onClick={handleDownloadClick}>결과 영상 다운로드</Button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
