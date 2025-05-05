// API 구성
export const API_BASE_URL = 'http://localhost:8001';

// 기본 요청 옵션
export const DEFAULT_OPTIONS = {
    credentials: 'include' as RequestCredentials,
    headers: {
        'Accept': 'application/json',
    },
};

// API 엔드포인트
export const ENDPOINTS = {
    ESTIMATE_TIME: `${API_BASE_URL}/estimate-processing-time/`,
    UPLOAD_IMAGE_MUSIC: `${API_BASE_URL}/upload-image-music/`,
    UPLOAD_VIDEO: `${API_BASE_URL}/upload-video/`,
} as const;
