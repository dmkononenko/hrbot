import axios, { AxiosError } from 'axios';
import type {
  Survey,
  Employee,
  SurveyResponse,
  SurveyResults,
  ApiResponse,
  Notification,
} from '../types';

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL?: string;
  }
}

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse<unknown>>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Survey API
export const surveyApi = {
  getSurveys: async (): Promise<Survey[]> => {
    const response = await apiClient.get<ApiResponse<Survey[]>>('/surveys');
    return response.data.data || [];
  },

  getSurvey: async (id: string): Promise<Survey> => {
    const response = await apiClient.get<ApiResponse<Survey>>(`/surveys/${id}`);
    return response.data.data!;
  },

  createSurvey: async (survey: Omit<Survey, 'id' | 'created_at' | 'updated_at'>): Promise<Survey> => {
    const response = await apiClient.post<ApiResponse<Survey>>('/surveys', survey);
    return response.data.data!;
  },

  updateSurvey: async (id: string, survey: Partial<Survey>): Promise<Survey> => {
    const response = await apiClient.put<ApiResponse<Survey>>(`/surveys/${id}`, survey);
    return response.data.data!;
  },

  deleteSurvey: async (id: string): Promise<void> => {
    await apiClient.delete<ApiResponse<void>>(`/surveys/${id}`);
  },

  toggleSurveyStatus: async (id: string): Promise<Survey> => {
    const response = await apiClient.patch<ApiResponse<Survey>>(`/surveys/${id}/toggle`);
    return response.data.data!;
  },

  getSurveyResults: async (id: string): Promise<SurveyResults> => {
    const response = await apiClient.get<ApiResponse<SurveyResults>>(`/surveys/${id}/results`);
    return response.data.data!;
  },

  getEligibleEmployees: async (surveyId: string): Promise<Employee[]> => {
    const response = await apiClient.get<ApiResponse<Employee[]>>(
      `/surveys/${surveyId}/eligible-employees`
    );
    return response.data.data || [];
  },

  initiateSurvey: async (surveyId: string, employeeIds: string[]): Promise<Notification[]> => {
    const response = await apiClient.post<ApiResponse<Notification[]>>(
      `/surveys/${surveyId}/initiate`,
      { employee_ids: employeeIds }
    );
    return response.data.data || [];
  },

  sendInvite: async (surveyId: string, employeeId: string): Promise<Notification> => {
    const response = await apiClient.post<ApiResponse<Notification>>(
      `/surveys/${surveyId}/send-invite`,
      { employee_id: employeeId }
    );
    return response.data.data!;
  },

  sendReminder: async (surveyId: string, employeeId: string): Promise<Notification> => {
    const response = await apiClient.post<ApiResponse<Notification>>(
      `/surveys/${surveyId}/send-reminder`,
      { employee_id: employeeId }
    );
    return response.data.data!;
  },
};

// Employee API
export const employeeApi = {
  getEmployees: async (): Promise<Employee[]> => {
    const response = await apiClient.get<ApiResponse<Employee[]>>('/employees');
    return response.data.data || [];
  },

  getEmployee: async (id: string): Promise<Employee> => {
    const response = await apiClient.get<ApiResponse<Employee>>(`/employees/${id}`);
    return response.data.data!;
  },

  createEmployee: async (employee: Omit<Employee, 'id' | 'created_at' | 'updated_at'>): Promise<Employee> => {
    const response = await apiClient.post<ApiResponse<Employee>>('/employees', employee);
    return response.data.data!;
  },

  updateEmployee: async (id: string, employee: Partial<Employee>): Promise<Employee> => {
    const response = await apiClient.put<ApiResponse<Employee>>(`/employees/${id}`, employee);
    return response.data.data!;
  },

  deleteEmployee: async (id: string): Promise<void> => {
    await apiClient.delete<ApiResponse<void>>(`/employees/${id}`);
  },

  toggleEmployeeStatus: async (id: string): Promise<Employee> => {
    const response = await apiClient.patch<ApiResponse<Employee>>(`/employees/${id}/toggle`);
    return response.data.data!;
  },
};

// Response API
export const responseApi = {
  getResponses: async (surveyId?: string): Promise<SurveyResponse[]> => {
    const url = surveyId ? `/responses?survey_id=${surveyId}` : '/responses';
    const response = await apiClient.get<ApiResponse<SurveyResponse[]>>(url);
    return response.data.data || [];
  },

  getResponse: async (id: string): Promise<SurveyResponse> => {
    const response = await apiClient.get<ApiResponse<SurveyResponse>>(`/responses/${id}`);
    return response.data.data!;
  },
};

export default apiClient;
