// Question types
export type QuestionType = 'text' | 'single_choice' | 'multiple_choice'

export interface QuestionOption {
  id: number
  question_id: number
  option_text: string
  order_index: number
}

export interface Question {
  id: number
  survey_id: number
  question_text: string
  question_type: QuestionType
  order_index: number
  is_required: boolean
  options?: QuestionOption[]
}

export interface QuestionCreate {
  question_text: string
  question_type: QuestionType
  order_index: number
  is_required: boolean
  options?: { option_text: string; order_index: number }[]
}

// Survey types
export interface Survey {
  id: number
  title: string
  description: string
  days_after_start: number
  is_active: boolean
  created_at: string
  updated_at: string
  questions: Question[]
}

export interface SurveyCreate {
  title: string
  description: string
  days_after_start: number
  is_active: boolean
  questions: QuestionCreate[]
}

export interface SurveyUpdate {
  title?: string
  description?: string
  days_after_start?: number
  is_active?: boolean
}

export interface SurveysListResponse {
  surveys: Survey[]
  total: number
}

// Employee types
export interface Employee {
  id: number
  telegram_id: number
  telegram_username: string | null
  first_name: string
  last_name: string
  start_date: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EmployeeCreate {
  telegram_id: number
  telegram_username?: string
  first_name: string
  last_name: string
  start_date: string
  is_active?: boolean
}

export interface EmployeeUpdate {
  telegram_username?: string
  first_name?: string
  last_name?: string
  start_date?: string
  is_active?: boolean
}

export interface EmployeesListResponse {
  employees: Employee[]
  total: number
}

// Response types
export type ResponseStatus = 'pending' | 'completed'

export interface Answer {
  id: number
  survey_response_id: number
  question_id: number
  answer_text: string | null
  answer_options: number[] | null
}

export interface SurveyResponse {
  id: number
  survey_id: number
  employee_id: number
  status: ResponseStatus
  completed_at: string | null
  answers: Answer[]
  employee: Employee
}

export interface ResponsesListResponse {
  responses: SurveyResponse[]
  total: number
}

// Survey Results
export interface AnswerDetail {
  question_id: number
  question_text: string
  question_type: QuestionType
  answer_text: string | null
  answer_options: string[] | null
}

export interface ResponseResult {
  response_id: number
  employee: {
    id: number
    telegram_id: number
    telegram_username: string | null
    first_name: string
    last_name: string
  }
  completed_at: string | null
  answers: AnswerDetail[]
}

export interface SurveyResultsResponse {
  survey_id: number
  survey_title: string
  responses: ResponseResult[]
  total_responses: number
  completion_rate: number
}

// Eligible Employee
export interface EligibleEmployee {
  id: number
  telegram_id: number
  first_name: string
  last_name: string
  start_date: string
  days_since_start: number
}

export interface EligibleEmployeesResponse {
  survey_id: number
  days_after_start: number
  eligible_employees: EligibleEmployee[]
  total: number
}

// Bot API types
export interface InitiateSurveyRequest {
  employee_telegram_id: number
  survey_id: number
}

export interface InitiateSurveyResponse {
  message: string
  response_id: number
  employee_telegram_id: number
  survey_id: number
  invite_sent: boolean
  invite_error: string | null
}
