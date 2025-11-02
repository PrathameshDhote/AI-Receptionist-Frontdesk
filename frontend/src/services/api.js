import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Methods
export const apiService = {
  // Health check
  async checkHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Help Requests
  async getHelpRequests() {
    const response = await api.get('/api/help-requests/');
    return response.data;
  },

  async getHelpRequest(id) {
    const response = await api.get(`/api/help-requests/${id}`);
    return response.data;
  },

  async answerHelpRequest(id, answer, supervisorName) {
    const response = await api.put(`/api/help-requests/${id}/answer`, null, {
      params: {
        answer,
        supervisor_name: supervisorName,
      },
    });
    return response.data;
  },

  async getStats() {
    const response = await api.get('/api/help-requests/stats/summary');
    return response.data;
  },

  // Knowledge Base
  async getKnowledgeBase() {
    const response = await api.get('/api/knowledge-base/');
    return response.data;
  },

  async createKnowledgeEntry(question, answer) {
    const response = await api.post('/api/knowledge-base/', null, {
      params: { question, answer },
    });
    return response.data;
  },
};

export default api;
