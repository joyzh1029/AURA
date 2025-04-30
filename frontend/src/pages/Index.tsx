import React, { useState, useEffect } from 'react';
import { ChatProvider, useChat } from '@/contexts/ChatContext';
import ChatContainer from '@/components/Chat/ChatContainer';
import { Sparkles, Music, Image as ImageIcon, Video, Upload, RefreshCw } from 'lucide-react';
import FileUploader from '@/components/FileUpload/FileUploader';
import { Button } from '@/components/ui/button';

// Main component
const Index = () => {
  return (
    <ChatProvider>
      <FileUploadHandler />
    </ChatProvider>
  );
};

// Internal component for file upload handling.
const FileUploadHandler = () => {
  const { setUploadedImage, setUploadedVideo, setUploadedMusic } = useChat();
  const [selectedImageFile, setSelectedImageFile] = useState<File | null>(null);
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null);
  const [selectedMusicFile, setSelectedMusicFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [resetTrigger, setResetTrigger] = useState(0);
  
  // Track if any file has been uploaded, used to disable other uploaders
  const hasFileUploaded = selectedImageFile !== null || selectedVideoFile !== null || selectedMusicFile !== null;
  
  // Function to reset all selections
  const resetAll = () => {
    setSelectedImageFile(null);
    setSelectedVideoFile(null);
    setSelectedMusicFile(null);
    setUploadResult(null);
    setResetTrigger(prev => prev + 1);
    setUploadedImage(null);
    setUploadedVideo(null);
    setUploadedMusic(null);
  };
  return (
    <ChatProvider>
      <div className="min-h-screen bg-background flex flex-col">
        <header className="bg-card border-b shadow-sm py-4 px-6">
          <div className="container flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-10 w-10 rounded-lg bg-music-gradient flex items-center justify-center">
                <Music className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">AURA</h1>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 container py-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left side: Chat container */}
            <div className="col-span-1">
              <div className="bg-card border rounded-xl shadow-sm h-[700px] flex flex-col">
                <ChatContainer />
              </div>
            </div>
            
            {/* Right side: Operation area */}
            <div className="col-span-1 h-[700px] flex flex-col justify-between">
              <div className="space-y-6">
                {/* Upper section with wave animation */}
                <div className="relative h-[160px] rounded-xl overflow-hidden bg-music-gradient animate-gradient-move mx-auto">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center p-6 text-white">
                      <Sparkles className="h-8 w-8 mx-auto mb-2" />
                    </div>
                  </div>
                  <div className="absolute inset-0 flex justify-center">
                    <div className="wave-animation wave-1 w-[240px] h-[240px] mt-[-60px]"></div>
                    <div className="wave-animation wave-2 w-[400px] h-[400px] mt-[-140px]"></div>
                    <div className="wave-animation wave-3 w-[600px] h-[600px] mt-[-240px]"></div>
                  </div>
                </div>
                
                {/* Two operation cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Image/Video to Music card */}
                  <div className="bg-card border rounded-xl p-6 flex flex-col items-center text-center h-[280px]">
                    <div className="flex flex-col items-center space-y-4">
                      <div className="flex items-center space-x-1">
                        <ImageIcon className="h-6 w-6 text-primary" />
                        <Video className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold">이미지,영상에서 음악으로</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        이미지의 분위기와 색감을 분석해 어울리는 음악을 생성합니다.
                      </p>
                      <div className="grid grid-cols-2 gap-2 w-full">
                        <FileUploader 
                          type="image"
                          onFileSelect={(file, result) => {
                            setSelectedImageFile(file);
                            setUploadResult(result);
                            console.log('Image file selected', file, result);
                          }}
                          resetTrigger={resetTrigger}
                          disabled={hasFileUploaded && !selectedImageFile}
                        />
                        <FileUploader 
                          type="video"
                          onFileSelect={(file, result) => {
                            setSelectedVideoFile(file);
                            if (result && result.file_url) {
                              setUploadedVideo(result.file_url);
                            } else if (file) {
                              // If no URL is returned, use the local URL
                              setUploadedVideo(URL.createObjectURL(file));
                            }
                            console.log('Video file selected', file, result);
                          }}
                          resetTrigger={resetTrigger}
                          disabled={hasFileUploaded && !selectedVideoFile}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Music to Image card */}
                  <div className="bg-card border rounded-xl p-6 flex flex-col items-center text-center h-[280px]">
                    <div className="flex flex-col items-center space-y-5">
                      <div className="flex items-center space-x-1">
                        <Music className="h-6 w-6 text-primary" />
                        <Music className="h-6 w-6 text-primary opacity-0" />
                      </div>
                      <h3 className="text-lg font-semibold">음악에서 이미지로</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        음악의 분위기와 감정을 분석해 이를 시각화한 이미지를 생성합니다.
                      </p>
                      <FileUploader 
                        type="music"
                        onFileSelect={(file) => {
                          setSelectedMusicFile(file);
                          if (file) {
                            setUploadedMusic(URL.createObjectURL(file));
                          }
                          console.log('Music file selected', file);
                        }}
                        resetTrigger={resetTrigger}
                        disabled={hasFileUploaded && !selectedMusicFile}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Results or preview section */}
              <div className="bg-card border rounded-xl p-6 h-[200px] flex flex-col items-center justify-center relative">
                {(selectedImageFile || selectedVideoFile || selectedMusicFile) ? (
                  <div className="absolute top-4 right-4">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={resetAll}
                      title="Reset"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                ) : null}
                
                {selectedImageFile && uploadResult ? (
                  <div className="text-center">
                    <h4 className="font-medium mb-2">업로드된 이미지</h4>
                    <div className="flex items-center justify-center">
                      <img 
                        src={URL.createObjectURL(selectedImageFile)} 
                        alt="Uploaded image" 
                        className="max-h-[120px] max-w-full rounded-md object-contain" 
                      />
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      파일명: {uploadResult.original_filename}<br/>
                      저장 경로: {uploadResult.file_path}
                    </p>
                  </div>
                ) : selectedVideoFile ? (
                  <div className="text-center">
                    <h4 className="font-medium mb-2">업로드된 영상</h4>
                    <div className="flex items-center justify-center">
                      <video 
                        src={URL.createObjectURL(selectedVideoFile)} 
                        controls 
                        className="max-h-[120px] max-w-full rounded-md" 
                      />
                    </div>
                  </div>
                ) : selectedMusicFile ? (
                  <div className="text-center">
                    <h4 className="font-medium mb-2">업로드된 음악</h4>
                    <div className="flex items-center justify-center">
                      <audio 
                        src={URL.createObjectURL(selectedMusicFile)} 
                        controls 
                        className="max-w-full" 
                      />
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground">
                    <Upload className="h-10 w-10 mx-auto mb-2" />
                    <p>이미지나 동영상,음악 파일을 업로드하면 결과가 여기에 표시됩니다</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </ChatProvider>
  );
};

export default Index;
