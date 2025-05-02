const API_BASE_URL = 'http://localhost:8001';

/**
 * Upload a single image file to the backend
 */
export const uploadImage = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload image');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

/**
 * Upload multiple image files to the backend
 */
export const uploadMultipleImages = async (files: File[]) => {
  try {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/upload-multiple/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload images');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading multiple images:', error);
    throw error;
  }
};

/**
 * Upload a video file to the backend
 * @param file The video file to upload
 * @returns Blob URL to the processed video
 */
export const uploadVideo = async (file: File): Promise<Blob> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-video/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      // 영상 업로드 시도 중 JSON 형식의 오류 메시지 파싱
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload video');
      } catch (jsonError) {
        // JSON 형식이 아닌 경우, 상태 텍스트 사용
        throw new Error(`Failed to upload video: ${response.statusText}`);
      }
    }

    // 영상 처리 성공 응답 - 영상 스트림을 가져와 Blob URL 생성
    const videoBlob = await response.blob();
    return URL.createObjectURL(videoBlob);
  } catch (error) {
    console.error('Error uploading video:', error);
    throw error;
  }
};

/**
 * Upload an audio file to the backend
 */
export const uploadAudio = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-audio/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload audio');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading audio:', error);
    throw error;
  }
};

/**
 * Interface for chat message request
 */
interface ChatMessageRequest {
  message: string;
  image_url?: string;
  audio_url?: string;
  video_url?: string;
}

/**
 * Send a chat message to the LangChain-powered backend
 * @param messageData The message data including text and any media URLs
 * @returns The AI response
 */
export const sendChatMessage = async (messageData: ChatMessageRequest) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(messageData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to process chat message');
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};
