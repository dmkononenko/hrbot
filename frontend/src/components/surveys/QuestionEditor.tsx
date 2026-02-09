import React, { useState } from 'react';
import { QuestionType } from '../../types';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Select } from '../ui/Select';

interface QuestionEditorProps {
  question: any;
  onChange: (question: any) => void;
  onRemove: () => void;
  index: number;
}

export const QuestionEditor: React.FC<QuestionEditorProps> = ({
  question,
  onChange,
  onRemove,
  index,
}) => {
  const [showOptions, setShowOptions] = useState(question.type === 'single_choice' || question.type === 'multiple_choice');

  const handleTypeChange = (type: QuestionType) => {
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
    ) || [];
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
          <Input
            value={question.text}
            onChange={(e) => onChange({ ...question, text: e.target.value })}
            placeholder="Введите текст вопроса"
          />
        </div>
        <Button variant="danger" size="sm" onClick={onRemove}>
          Удалить
        </Button>
      </div>

      <div className="flex gap-4 mb-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Тип вопроса
          </label>
          <Select
            value={question.type}
            onChange={(e) => handleTypeChange(e.target.value as QuestionType)}
            options={[
              { value: 'text', label: 'Текстовый' },
              { value: 'single_choice', label: 'Один вариант' },
              { value: 'multiple_choice', label: 'Несколько вариантов' },
            ]}
          />
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
              <Input
                value={option.text}
                onChange={(e) => handleOptionChange(optIndex, 'text', e.target.value)}
                placeholder={`Вариант ${optIndex + 1}`}
              />
              <Button
                variant="danger"
                size="sm"
                onClick={() => removeOption(optIndex)}
                disabled={question.options.length <= 2}
              >
                Удалить
              </Button>
            </div>
          ))}
          <Button variant="secondary" size="sm" onClick={addOption}>
            + Добавить вариант
          </Button>
        </div>
      )}
    </div>
  );
};
