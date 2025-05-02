import React, { useState } from 'react';
import { ChatProvider, useChat } from '@/contexts/ChatContext';
import ChatContainer from '@/components/Chat/ChatContainer';
import { Sparkles, Music, Image as ImageIcon, Video, Upload, RefreshCw } from 'lucide-react';
import FileUploader from '@/components/FileUpload/FileUploader';
import { Button } from '@/components/ui/button';

const Index = () => {
  return (
    <ChatProvider>
      <FileUploadHandler />
    </ChatProvider>
  );
};

const FileUploadHandler = () => {
  const { setUploadedImage, setUploadedVideo } = useChat();
  const [selectedImageFile, setSelectedImageFile] = useState<File | null>(null);
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [videoURL, setVideoURL] = useState<string | null>(null);
  // 새 상태: 생성된 음악 파일 URL (audio 스트림)
  const [uploadedAudio, setUploadedAudio] = useState<string | null>(null);
  // 새 상태: 이미지 업로드 후 음악 생성 요청이 진행 중임을 표시하는 플래그
  const [isConverting, setIsConverting] = useState(false);
  const [resetTrigger, setResetTrigger] = useState(0);

  const hasFileUploaded = selectedImageFile !== null || selectedVideoFile !== null;

  const resetAll = () => {
    setSelectedImageFile(null);
    setSelectedVideoFile(null);
    setUploadedAudio(null);
    setVideoBlob(null);
    setVideoURL(null);
    setIsConverting(false);
    setResetTrigger((prev) => prev + 1);
    setUploadedImage(null);
    setUploadedVideo(null);
  };

  // 오디오 다운로드 기능
  const downloadAudio = () => {
    if (uploadedAudio) {
      const a = document.createElement("a");
      a.href = uploadedAudio;
      a.download = "generated_music.wav";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
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
            <div className="col-span-1">
              <div className="bg-card border rounded-xl shadow-sm h-[700px] flex flex-col">
                <ChatContainer />
              </div>
            </div>

            <div className="col-span-1 h-[700px] flex flex-col justify-between">
              <div className="space-y-6">
                {/* 상단 영역: 영상 업로드이면 영상, 이미지 업로드이면 상태에 따라 변환중 or 오디오 플레이어 표시 */}
                <div className="relative h-[160px] rounded-xl overflow-hidden bg-music-gradient animate-gradient-move mx-auto">
                  {videoURL && selectedVideoFile ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-black">
                      <video
                        src={videoURL}
                        controls
                        autoPlay
                        className="h-full w-full object-contain"
                      />
                    </div>
                  ) : selectedImageFile ? (
                    <>
                      {isConverting ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black">
                          <div className="text-white text-xl font-medium">
                            음악 생성중입니다...
                          </div>
                        </div>
                      ) : uploadedAudio ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black">
                          <audio
                            src={uploadedAudio}
                            controls
                            autoPlay
                            className="w-full"
                          >
                            Your browser does not support the audio element.
                          </audio>
                          <Button variant="outline" size="sm" className="mt-2" onClick={downloadAudio}>
                            Download Music
                          </Button>
                        </div>
                      ) : null}
                    </>
                  ) : (
                    <>
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
                    </>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* 이미지 -> 음악: 업로드 후 자동으로 음악 생성 요청 */}
                  <div className="bg-card border rounded-xl p-6 flex flex-col items-center text-center h-[280px]">
                    <div className="flex flex-col items-center space-y-4">
                      <div className="flex items-center space-x-1">
                        <ImageIcon className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold">이미지에서 음악으로</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        이미지의 분위기와 색감을 분석해 어울리는 음악을 생성합니다.
                      </p>
                      <FileUploader
                        type="image"
                        onFileSelect={async (file) => {
                          setSelectedImageFile(file);
                          setIsConverting(true);
                          try {
                            const formData = new FormData();
                            formData.append("file", file);
                            // /upload-image-music/ 엔드포인트 호출
                            const response = await fetch("/upload-image-music/", {
                              method: "POST",
                              body: formData,
                            });
                            if (!response.ok) {
                              throw new Error("음악 생성 요청 실패");
                            }
                            const blob = await response.blob();
                            const audioUrl = URL.createObjectURL(blob);
                            setUploadedAudio(audioUrl);
                          } catch (error) {
                            console.error("Error generating music:", error);
                          } finally {
                            setIsConverting(false);
                          }
                        }}
                        resetTrigger={resetTrigger}
                        disabled={hasFileUploaded && !selectedImageFile}
                      />
                    </div>
                  </div>

                  {/* 영상 -> 음악 */}
                  <div className="bg-card border rounded-xl p-6 flex flex-col items-center text-center h-[280px]">
                    <div className="flex flex-col items-center space-y-5">
                      <div className="flex items-center space-x-1">
                        <Video className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold">영상에서 음악으로</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        영상을 분석해 분위기와 어울리는 음악을 생성합니다.
                      </p>
                      <FileUploader
                        type="video"
                        onFileSelect={(file, blob) => {
                          setSelectedVideoFile(file);
                          setVideoBlob(blob);
                          const url = URL.createObjectURL(blob);
                          setVideoURL(url);
                        }}
                        resetTrigger={resetTrigger}
                        disabled={hasFileUploaded && !selectedVideoFile}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* 하단 영역: 업로드한 영상은 영상 미리보기, 업로드한 이미지는 이미지 미리보기만 */}
              <div className="bg-card border rounded-xl p-6 h-[200px] flex flex-col items-center justify-center relative">
                {selectedVideoFile ? (
                  <div className="text-center">
                    <h4 className="font-medium mb-2">업로드된 영상</h4>
                    <div className="flex items-center justify-center">
                      <video
                        src={videoURL ?? URL.createObjectURL(selectedVideoFile)}
                        controls
                        className="max-h-[120px] max-w-full rounded-md"
                      />
                    </div>
                  </div>
                ) : selectedImageFile ? (
                  <div className="text-center">
                    <h4 className="font-medium mb-2">업로드된 이미지</h4>
                    <div className="flex items-center justify-center">
                      <img
                        src={URL.createObjectURL(selectedImageFile)}
                        alt="Uploaded image"
                        className="max-h-[120px] max-w-full rounded-md object-contain"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground">
                    <Upload className="h-10 w-10 mx-auto mb-2" />
                    <p>이미지나 동영상 파일을 업로드하면 결과가 여기에 표시됩니다</p>
                  </div>
                )}
                {(selectedImageFile || selectedVideoFile) && (
                  <div className="absolute top-4 right-4">
                    <Button variant="ghost" size="icon" onClick={resetAll} title="Reset">
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>

        <footer className="py-4 text-center text-sm text-muted-foreground border-t mt-auto">
          <p>© 2025 AURA. 이미지,영상과 음악의 교차점.</p>
        </footer>
      </div>
    </ChatProvider>
  );
};

export default Index;
