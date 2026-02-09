import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Table } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import { AnswerViewer } from '../components/results/AnswerViewer';
import { surveyApi, employeeApi } from '../services/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Survey, Employee } from '../types';
import { SurveyResults as SurveyResultsType } from '../types';
import { Status } from '../components/ui/Status';

export const SurveyResults = () => {
  const { surveyId } = useParams<{ surveyId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: survey, isLoading: surveyLoading } = useQuery({
    queryKey: ['surveys', surveyId],
    queryFn: () => surveyApi.getSurvey(surveyId!),
    enabled: !!surveyId,
  });

  const { data: results, isLoading: resultsLoading } = useQuery({
    queryKey: ['surveyResults', surveyId],
    queryFn: () => surveyApi.getSurveyResults(surveyId!),
    enabled: !!surveyId,
  });

  const { data: employees = [] } = useQuery({
    queryKey: ['employees'],
    queryFn: employeeApi.getEmployees,
  });

  const { data: eligibleEmployees = [] } = useQuery({
    queryKey: ['eligibleEmployees', surveyId],
    queryFn: () => surveyApi.getEligibleEmployees(surveyId!),
    enabled: !!surveyId,
  });

  const initiateMutation = useMutation({
    mutationFn: (employeeId: string) => surveyApi.sendInvite(surveyId!, employeeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveyResults', surveyId] });
    },
  });

  const handleInitiateSurvey = async (employeeId: string) => {
    try {
      await initiateMutation.mutateAsync(employeeId);
      alert('Приглашение отправлено сотруднику');
    } catch (error) {
      console.error('Error initiating survey:', error);
      alert('Ошибка при отправке приглашения');
    }
  };

  if (surveyLoading || resultsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!survey || !results) {
    return <div className="text-center py-8">Опрос не найден</div>;
  }

  const getEmployeeName = (employeeId: string) => {
    const employee = employees.find((e) => e.id === employeeId);
    return employee?.full_name || 'Неизвестный сотрудник';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <button
            onClick={() => navigate('/surveys')}
            className="text-blue-600 hover:text-blue-700 mb-2 inline-block"
          >
            ← Назад к опросам
          </button>
          <h1 className="text-2xl font-semibold text-gray-900">{survey.title}</h1>
          {survey.description && (
            <p className="text-gray-600">{survey.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Badge variant="blue">
            {results.total_responses} ответов
          </Badge>
          <Badge variant="green">
            {results.completion_rate}% завершено
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="Результаты по сотрудникам">
            {results.responses.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                Нет ответов на этот опрос
              </p>
            ) : (
              <Table
                headers={['Сотрудник', 'Ответов', 'Статус', 'Дата']}
                data={results.responses}
                renderRow={(response) => (
                  <tr key={response.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">
                        {getEmployeeName(response.employee_id)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {response.answers.length} / {results.questions.length}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Status
                        type={response.is_completed ? 'completed' : 'pending'}
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {response.completed_at
                        ? new Date(response.completed_at).toLocaleDateString('ru-RU')
                        : new Date(response.started_at || '').toLocaleDateString('ru-RU')}
                    </td>
                  </tr>
                )}
              />
            )}
          </Card>

          <Card title="Детальные ответы">
            {results.responses.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Нет ответов</p>
            ) : (
              <div className="space-y-4">
                {results.responses.map((response: SurveyResultsType['responses'][0]) => (
                  <div key={response.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-4">
                      <h4 className="font-semibold text-gray-900">
                        {getEmployeeName(response.employee_id)}
                      </h4>
                      <Status
                        type={response.is_completed ? 'completed' : 'pending'}
                      />
                    </div>
                    {response.answers.map((answer: any, index) => (
                      <AnswerViewer key={index} answer={answer} />
                    ))}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Вопросы опроса">
            <div className="space-y-4">
              {results.questions.map((question: any, index) => (
                <div key={question.id || index} className="bg-gray-50 rounded-lg p-4">
                  <div className="font-medium text-gray-900 mb-2">
                    {index + 1}. {question.text}
                  </div>
                  {question.type === 'text' && (
                    <p className="text-sm text-gray-600">
                      Текстовый ответ
                    </p>
                  )}
                  {question.type === 'single_choice' && question.options && (
                    <ul className="text-sm text-gray-600 space-y-1">
                      {question.options.map((option: any) => (
                        <li key={option.id}>• {option.text}</li>
                      ))}
                    </ul>
                  )}
                  {question.type === 'multiple_choice' && question.options && (
                    <ul className="text-sm text-gray-600 space-y-1">
                      {question.options.map((option: any) => (
                        <li key={option.id}>• {option.text}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card title="Пригласить сотрудников">
            <p className="text-sm text-gray-600 mb-4">
              Отправить приглашение на прохождение опроса
            </p>
            <div className="space-y-2">
              {eligibleEmployees.length === 0 ? (
                <p className="text-sm text-gray-500">Нет доступных сотрудников</p>
              ) : (
                eligibleEmployees.map((employee) => (
                  <div
                    key={employee.id}
                    className="flex justify-between items-center bg-gray-50 rounded-lg p-3"
                  >
                    <div>
                      <div className="font-medium text-gray-900 text-sm">
                        {employee.full_name}
                      </div>
                      <div className="text-xs text-gray-600">
                        {employee.position}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleInitiateSurvey(employee.id!)}
                      className="px-3 py-1.5 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 text-sm"
                    >
                      Пригласить
                    </button>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
