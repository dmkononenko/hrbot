// Survey Types
export type QuestionType = 'text' | 'single_choice' | 'multiple_choice';

export interface QuestionOption {
  id: string;
  text: string;
  order: number;
}

export interface Question {
  id?: string;
  type: QuestionType;
  text: string;
  options?: QuestionOption[];
  required: boolean;
  order: number;
}

export interface Survey {
  id?: string;
  title: string;
  description?: string;
  questions: Question[];
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// Employee Types
export interface Employee {
  id?: string;
  telegram_id?: number;
  full_name: string;
  position: string;
  department: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// Response Types
export interface Answer {
  question_id: string;
  question_text: string;
  answer: string | string[];
}

export interface SurveyResponse {
  id?: string;
  survey_id: string;
  employee_id: string;
  answers: Answer[];
  is_completed: boolean;
  completed_at?: string;
  started_at?: string;
}

// Survey Results Types
export interface SurveyResults {
  survey_id: string;
  survey_title: string;
  total_responses: number;
  completion_rate: number;
  responses: SurveyResponse[];
  questions: Question[];
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Notification Types
export interface Notification {
  id?: string;
  employee_id: string;
  type: 'invite' | 'reminder' | 'completed';
  status: 'pending' | 'sent' | 'failed';
  sent_at?: string;
  error_message?: string;
}
