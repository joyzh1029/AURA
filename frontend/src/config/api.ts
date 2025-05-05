// API configuration
export const API_BASE_URL = 'http://localhost:8001';

// API endpoints
export const ENDPOINTS = {
    ESTIMATE_TIME: `${API_BASE_URL}/estimate-processing-time/`,
    UPLOAD_IMAGE_MUSIC: `${API_BASE_URL}/upload-image-music/`,
    UPLOAD_VIDEO: `${API_BASE_URL}/upload-video/`,
} as const;
