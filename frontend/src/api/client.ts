import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Surveys API
export const surveysApi = {
  getAll: (params?: { skip?: number; limit?: number; active_only?: boolean }) =>
    api.get('/surveys', { params }),

  getById: (id: number) =>
    api.get(`/surveys/${id}`),

  create: (data: any) =>
    api.post('/surveys', data),

  update: (id: number, data: any) =>
    api.put(`/surveys/${id}`, data),

  delete: (id: number) =>
    api.delete(`/surveys/${id}`),

  getResults: (id: number) =>
    api.get(`/surveys/${id}/results`),
}

// Employees API
export const employeesApi = {
  getAll: (params?: { skip?: number; limit?: number }) =>
    api.get('/employees', { params }),

  getById: (id: number) =>
    api.get(`/employees/${id}`),

  getByTelegramId: (telegramId: number) =>
    api.get(`/employees/telegram/${telegramId}`),

  create: (data: any) =>
    api.post('/employees', data),

  update: (id: number, data: any) =>
    api.put(`/employees/${id}`, data),

  delete: (id: number) =>
    api.delete(`/employees/${id}`),
}

// Responses API
export const responsesApi = {
  getAll: (params?: { skip?: number; limit?: number; survey_id?: number }) =>
    api.get('/responses', { params }),

  getById: (id: number) =>
    api.get(`/responses/${id}`),
}

// Bot API
export const botApi = {
  initiateSurvey: (data: { employee_telegram_id: number; survey_id: number }) =>
    api.post('/bot/initiate-survey', data),

  getEligibleEmployees: (surveyId: number) =>
    api.get(`/bot/eligible-employees/${surveyId}`),

  sendInvite: (data: { employee_id: number; survey_id: number }) =>
    api.post('/bot/send-invite', data),

  sendReminder: (data: { employee_id: number; survey_id: number; days_remaining?: number }) =>
    api.post('/bot/send-reminder', data),
}
