import { Card } from '../components/ui/Card';
import { surveyApi, employeeApi, responseApi } from '../services/api';
import { useQuery } from '@tanstack/react-query';
import { Survey, Employee, SurveyResponse } from '../types';
import { Status } from '../components/ui/Status';

export const Dashboard = () => {
  const { data: surveys = [], isLoading: surveysLoading } = useQuery({
    queryKey: ['surveys'],
    queryFn: surveyApi.getSurveys,
  });

  const { data: employees = [], isLoading: employeesLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: employeeApi.getEmployees,
  });

  const { data: responses = [], isLoading: responsesLoading } = useQuery({
    queryKey: ['responses'],
    queryFn: () => responseApi.getResponses(),
  });

  const activeSurveys = surveys.filter((s: Survey) => s.is_active);
  const completedResponses = responses.filter((r: any) => r.is_completed);
  const activeEmployees = employees.filter((e: Employee) => e.is_active);

  if (surveysLoading || employeesLoading || responsesLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Панель управления</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Активные опросы">
          <div className="text-3xl font-bold text-blue-600">{activeSurveys.length}</div>
          <div className="text-sm text-gray-600 mt-1">всего опросов</div>
        </Card>

        <Card title="Активные сотрудники">
          <div className="text-3xl font-bold text-green-600">{activeEmployees.length}</div>
          <div className="text-sm text-gray-600 mt-1">всего сотрудников</div>
        </Card>

        <Card title="Завершенные ответы">
          <div className="text-3xl font-bold text-purple-600">{completedResponses.length}</div>
          <div className="text-sm text-gray-600 mt-1">завершенных опросов</div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Последние опросы">
          {surveys.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Нет опросов</p>
          ) : (
            <div className="space-y-3">
              {surveys.slice(0, 5).map((survey) => (
                <div key={survey.id} className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-gray-900">{survey.title}</div>
                    <div className="text-sm text-gray-600">
                      {survey.questions.length} вопросов
                    </div>
                  </div>
                  <Status type={survey.is_active ? 'active' : 'inactive'} />
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Последние ответы">
          {responses.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Нет ответов</p>
          ) : (
            <div className="space-y-3">
              {responses.slice(0, 5).map((response: SurveyResponse) => (
                <div key={response.id} className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-gray-900">
                      {response.answers.length} ответов
                    </div>
                    <div className="text-sm text-gray-600">
                      {new Date(response.completed_at || response.started_at || '').toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                  <Status type={response.is_completed ? 'completed' : 'pending'} />
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
