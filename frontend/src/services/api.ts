// API service for handling backend requests

const API_BASE_URL = 'http://localhost:8000';

/**
 * Upload a single image file to the backend
 * @param file The file to upload
 * @returns Response data from the server
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
 * @param files Array of files to upload
 * @returns Response data from the server
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
 * @returns Response data from the server
 */
export const uploadVideo = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-video/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload video');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading video:', error);
    throw error;
  }
};
