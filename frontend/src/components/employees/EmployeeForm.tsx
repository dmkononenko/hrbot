import React from 'react';
import { Employee } from '../../types';
import { Input } from '../ui/Input';

interface EmployeeFormProps {
  employee: Partial<Employee>;
  onChange: (employee: Partial<Employee>) => void;
  onSubmit: (e: React.FormEvent) => void;
  onCancel: () => void;
  isEditing?: boolean;
}

export const EmployeeForm: React.FC<EmployeeFormProps> = ({
  employee,
  onChange,
  onSubmit,
  onCancel,
  isEditing = false,
}) => {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <Input
          label="ФИО сотрудника"
          value={employee.full_name || ''}
          onChange={(e) => onChange({ ...employee, full_name: e.target.value })}
          required
        />
      </div>
      <div>
        <Input
          label="Должность"
          value={employee.position || ''}
          onChange={(e) => onChange({ ...employee, position: e.target.value })}
          required
        />
      </div>
      <div>
        <Input
          label="Отдел"
          value={employee.department || ''}
          onChange={(e) => onChange({ ...employee, department: e.target.value })}
          required
        />
      </div>
      <div>
        <Input
          label="Email (необязательно)"
          type="email"
          value={employee.email || ''}
          onChange={(e) => onChange({ ...employee, email: e.target.value })}
        />
      </div>
      <div>
        <Input
          label="Телефон (необязательно)"
          value={employee.phone || ''}
          onChange={(e) => onChange({ ...employee, phone: e.target.value })}
        />
      </div>
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
