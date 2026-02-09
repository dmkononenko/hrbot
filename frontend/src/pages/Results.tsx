import { Card } from '../components/ui/Card';
import { Table } from '../components/ui/Table';
import { responseApi } from '../services/api';
import { useQuery } from '@tanstack/react-query';
import { SurveyResponse } from '../types';
import { Status } from '../components/ui/Status';

export const Results = () => {
  const { data: responses = [], isLoading } = useQuery({
    queryKey: ['responses'],
    queryFn: () => responseApi.getResponses(),
  });

  const completedResponses = responses.filter((r: SurveyResponse) => r.is_completed);
  const pendingResponses = responses.filter((r: SurveyResponse) => !r.is_completed);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Результаты опросов</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Завершенные">
          <div className="text-3xl font-bold text-green-600">{completedResponses.length}</div>
        </Card>
        <Card title="В процессе">
          <div className="text-3xl font-bold text-yellow-600">{pendingResponses.length}</div>
        </Card>
        <Card title="Всего ответов">
          <div className="text-3xl font-bold text-blue-600">{responses.length}</div>
        </Card>
      </div>

      <Card title="Все ответы">
        {responses.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Нет ответов</p>
        ) : (
          <Table
            headers={['ID', 'Сотрудник', 'Ответов', 'Статус', 'Дата']}
            data={responses as SurveyResponse[]}
            renderRow={(response: SurveyResponse) => (
              <tr key={response.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {response.id?.slice(0, 8)}...
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">Сотрудник</div>
                  <div className="text-sm text-gray-600">
                    {new Date(response.started_at || '').toLocaleDateString('ru-RU')}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {response.answers.length}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Status type={response.is_completed ? 'completed' : 'pending'} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {response.completed_at
                    ? new Date(response.completed_at).toLocaleDateString('ru-RU')
                    : '-'}
                </td>
              </tr>
            )}
          />
        )}
      </Card>
    </div>
  );
};
