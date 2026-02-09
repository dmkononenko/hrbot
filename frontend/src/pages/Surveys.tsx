import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Table } from '../components/ui/Table';
import { surveyApi } from '../services/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Survey } from '../types';
import { Status } from '../components/ui/Status';

export const Surveys = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingSurvey, setEditingSurvey] = useState<Survey | null>(null);

  const { data: surveys = [], isLoading } = useQuery({
    queryKey: ['surveys'],
    queryFn: () => surveyApi.getSurveys(),
  });

  const createMutation = useMutation({
    mutationFn: (data: Omit<Survey, 'id' | 'created_at' | 'updated_at'>) =>
      surveyApi.createSurvey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveys'] });
      setShowModal(false);
      setEditingSurvey(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Omit<Survey, 'id' | 'created_at' | 'updated_at'> }) =>
      surveyApi.updateSurvey(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveys'] });
      setShowModal(false);
      setEditingSurvey(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: surveyApi.deleteSurvey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['surveys'] });
    },
  });


  const handleEdit = (survey: Survey) => {
    setEditingSurvey(survey);
    setShowModal(true);
  };

  const handleDelete = (survey: Survey) => {
    if (window.confirm(`Вы уверены, что хотите удалить опрос "${survey.title}"?`)) {
      deleteMutation.mutate(survey.id!);
    }
  };

  const handleSubmit = (surveyData: Partial<Survey>) => {
    if (editingSurvey) {
      updateMutation.mutate({ id: editingSurvey.id!, data: surveyData });
    } else {
      createMutation.mutate(surveyData);
    }
  };

  const handleViewResults = (surveyId: string) => {
    navigate(`/surveys/${surveyId}/results`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Управление опросами</h1>
        <Button onClick={() => setShowModal(true)}>
          + Создать опрос
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : surveys.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Нет опросов</p>
        ) : (
          <Table
            headers={['Название', 'Вопросы', 'Статус', 'Действия']}
            data={surveys}
            renderRow={(survey) => (
              <tr key={survey.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{survey.title}</div>
                  {survey.description && (
                    <div className="text-sm text-gray-600">{survey.description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {survey.questions.length}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Status type={survey.is_active ? 'active' : 'inactive'} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex gap-2">
                    <Button variant="secondary" size="sm" onClick={() => handleViewResults(survey.id!)}>
                      Результаты
                    </Button>
                    <Button variant="secondary" size="sm" onClick={() => handleEdit(survey)}>
                      Редактировать
                    </Button>
                    <Button variant="danger" size="sm" onClick={() => handleDelete(survey)}>
                      Удалить
                    </Button>
                  </div>
                </td>
              </tr>
            )}
          />
        )}
      </Card>

      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setEditingSurvey(null);
        }}
        title={editingSurvey ? 'Редактировать опрос' : 'Создать опрос'}
        size="lg"
      >
        <SurveyForm
          survey={editingSurvey || { title: '', description: '', questions: [], is_active: false }}
          onSubmit={handleSubmit}
          onCancel={() => {
            setShowModal(false);
            setEditingSurvey(null);
          }}
          isEditing={!!editingSurvey}
        />
      </Modal>
    </div>
  );
};

const SurveyForm: React.FC<{
  survey: Omit<Survey, 'id' | 'created_at' | 'updated_at'>;
  onSubmit: (data: Omit<Survey, 'id' | 'created_at' | 'updated_at'>) => void;
  onCancel: () => void;
  isEditing?: boolean;
}> = ({ survey, onSubmit, onCancel, isEditing = false }) => {
  const [title, setTitle] = useState(survey.title || '');
  const [description, setDescription] = useState(survey.description || '');
  const [questions, setQuestions] = useState<Survey['questions']>(
    survey.questions || []
  );
  const [isActive, setIsActive] = useState(survey.is_active || false);

  const handleAddQuestion = () => {
    setQuestions([
      ...questions,
      {
        id: Date.now().toString(),
        type: 'text',
        text: '',
        options: [],
        required: false,
        order: questions.length,
      },
    ]);
  };

  const handleUpdateQuestion = (index: number, updatedQuestion: any) => {
    const newQuestions = [...questions];
    newQuestions[index] = updatedQuestion;
    setQuestions(newQuestions);
  };

  const handleRemoveQuestion = (index: number) => {
    const newQuestions = questions.filter((_, i) => i !== index);
    setQuestions(newQuestions);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('Введите название опроса');
      return;
    }

    onSubmit({
      title,
      description,
      questions,
      is_active: isActive,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Название опроса *
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите название опроса"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Описание
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите описание опроса"
          rows={3}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="isActive"
          checked={isActive}
          onChange={(e) => setIsActive(e.target.checked)}
          className="mr-2"
        />
        <label htmlFor="isActive" className="text-sm text-gray-700">
          Активный опрос
        </label>
      </div>

      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Вопросы</h3>
        {questions.map((question, index) => (
          <QuestionEditor
            key={question.id || index}
            question={question}
            onChange={(updated) => handleUpdateQuestion(index, updated)}
            onRemove={() => handleRemoveQuestion(index)}
            index={index}
          />
        ))}
      </div>

      <QuestionAdder onAdd={handleAddQuestion} />

      <div className="flex gap-2 pt-4">
        <button type="submit" className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          {isEditing ? 'Сохранить' : 'Создать'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 bg-gray-200 text-gray-900 px-4 py-2 rounded-lg hover:bg-gray-300"
        >
          Отмена
        </button>
      </div>
    </form>
  );
};

const QuestionEditor: React.FC<{
  question: any;
  onChange: (question: any) => void;
  onRemove: () => void;
  index: number;
}> = ({ question, onChange, onRemove, index }) => {
  const [showOptions, setShowOptions] = useState(
    question.type === 'single_choice' || question.type === 'multiple_choice'
  );

  const handleTypeChange = (type: any) => {
    onChange({
      ...question,
      type,
      options: type === 'text' ? undefined : question.options,
    });
    setShowOptions(type === 'single_choice' || type === 'multiple_choice');
  };

  const handleOptionChange = (optionIndex: number, field: 'text', value: string) => {
    const newOptions = question.options?.map((opt: any, idx: number) =>
      idx === optionIndex ? { ...opt, [field]: value } : opt
    );
    onChange({ ...question, options: newOptions });
  };

  const addOption = () => {
    if (!question.options) return;
    const newOption = {
      id: Date.now().toString(),
      text: '',
      order: question.options.length,
    };
    onChange({
      ...question,
      options: [...question.options, newOption],
    });
  };

  const removeOption = (optionIndex: number) => {
    if (!question.options) return;
    const newOptions = question.options.filter((_: any, idx: number) => idx !== optionIndex);
    onChange({
      ...question,
      options: newOptions.map((opt: any, idx: number) => ({ ...opt, order: idx })),
    });
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 mb-4">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Вопрос #{index + 1}
          </label>
          <input
            type="text"
            value={question.text}
            onChange={(e) => onChange({ ...question, text: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Введите текст вопроса"
          />
        </div>
        <button
          type="button"
          onClick={onRemove}
          className="text-red-600 hover:text-red-700"
        >
          Удалить
        </button>
      </div>

      <div className="flex gap-4 mb-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Тип вопроса
          </label>
          <select
            value={question.type}
            onChange={(e) => handleTypeChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="text">Текстовый</option>
            <option value="single_choice">Один вариант</option>
            <option value="multiple_choice">Несколько вариантов</option>
          </select>
        </div>
        <div className="flex items-end">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={question.required}
              onChange={(e) => onChange({ ...question, required: e.target.checked })}
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Обязательный</span>
          </label>
        </div>
      </div>

      {showOptions && question.options && (
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Варианты ответа
          </label>
          {question.options.map((option: any, optIndex: number) => (
            <div key={option.id} className="flex gap-2 mb-2">
              <input
                type="text"
                value={option.text}
                onChange={(e) => handleOptionChange(optIndex, 'text', e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={`Вариант ${optIndex + 1}`}
              />
              <button
                type="button"
                onClick={() => removeOption(optIndex)}
                className="text-red-600 hover:text-red-700 px-3"
                disabled={question.options.length <= 2}
              >
                Удалить
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addOption}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            + Добавить вариант
          </button>
        </div>
      )}
    </div>
  );
};
