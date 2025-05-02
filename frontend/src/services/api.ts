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
 * @returns Blob (not URL string)
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
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload video');
      } catch (jsonError) {
        throw new Error(`Failed to upload video: ${response.statusText}`);
      }
    }

    return await response.blob(); // ← Blob 객체 반환
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
