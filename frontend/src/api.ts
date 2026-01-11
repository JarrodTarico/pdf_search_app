import axios from 'axios';
import type { UploadResponse, SearchResponse } from './types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function uploadPDFs(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function searchPDFs(query: string): Promise<SearchResponse> {
  const response = await api.post<SearchResponse>('/search', { query });
  return response.data;
}

export async function getPDFMetadata(pdfId: string) {
  const response = await api.get(`/pdf/${pdfId}`);
  return response.data;
}
