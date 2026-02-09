import { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Table } from '../components/ui/Table';
import { employeeApi } from '../services/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Employee } from '../types';
import { Status } from '../components/ui/Status';

export const Employees = () => {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);

  const { data: employees = [], isLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: employeeApi.getEmployees,
  });

  const createMutation = useMutation({
    mutationFn: (data: Omit<Employee, 'id' | 'created_at' | 'updated_at'>) =>
      employeeApi.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setShowModal(false);
      setEditingEmployee(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Employee> }) =>
      employeeApi.updateEmployee(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setShowModal(false);
      setEditingEmployee(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: employeeApi.deleteEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
  });


  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee);
    setShowModal(true);
  };

  const handleDelete = (employee: Employee) => {
    if (window.confirm(`Вы уверены, что хотите удалить сотрудника "${employee.full_name}"?`)) {
      deleteMutation.mutate(employee.id!);
    }
  };

  const handleSubmit = (employeeData: Omit<Employee, 'id' | 'created_at' | 'updated_at'>) => {
    if (editingEmployee) {
      updateMutation.mutate({ id: editingEmployee.id!, data: employeeData });
    } else {
      createMutation.mutate(employeeData);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Управление сотрудниками</h1>
        <Button onClick={() => setShowModal(true)}>
          + Добавить сотрудника
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : employees.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Нет сотрудников</p>
        ) : (
          <Table
            headers={['ФИО', 'Должность', 'Отдел', 'Email', 'Статус', 'Действия']}
            data={employees}
            renderRow={(employee) => (
              <tr key={employee.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{employee.full_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {employee.position}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {employee.department}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {employee.email || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Status type={employee.is_active ? 'active' : 'inactive'} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex gap-2">
                    <Button variant="secondary" size="sm" onClick={() => handleEdit(employee)}>
                      Редактировать
                    </Button>
                    <Button variant="danger" size="sm" onClick={() => handleDelete(employee)}>
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
          setEditingEmployee(null);
        }}
        title={editingEmployee ? 'Редактировать сотрудника' : 'Добавить сотрудника'}
        size="md"
      >
        <EmployeeForm
          employee={editingEmployee || {}}
          onChange={(data) => setEditingEmployee({ ...editingEmployee!, ...data })}
          onSubmit={handleSubmit}
          onCancel={() => {
            setShowModal(false);
            setEditingEmployee(null);
          }}
          isEditing={!!editingEmployee}
        />
      </Modal>
    </div>
  );
};

const EmployeeForm: React.FC<{
  employee: Omit<Employee, 'id' | 'created_at' | 'updated_at'>;
  onChange: (data: Omit<Employee, 'id' | 'created_at' | 'updated_at'>) => void;
  onSubmit: (data: Omit<Employee, 'id' | 'created_at' | 'updated_at'>) => void;
  onCancel: () => void;
  isEditing?: boolean;
}> = ({ employee, onChange, onSubmit, onCancel, isEditing = false }) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(employee);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          ФИО сотрудника *
        </label>
        <input
          type="text"
          value={employee.full_name || ''}
          onChange={(e) => onChange({ ...employee, full_name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Иванов Иван Иванович"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Должность *
        </label>
        <input
          type="text"
          value={employee.position || ''}
          onChange={(e) => onChange({ ...employee, position: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Разработчик"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Отдел *
        </label>
        <input
          type="text"
          value={employee.department || ''}
          onChange={(e) => onChange({ ...employee, department: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="IT Отдел"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email (необязательно)
        </label>
        <input
          type="email"
          value={employee.email || ''}
          onChange={(e) => onChange({ ...employee, email: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="ivanov@example.com"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Телефон (необязательно)
        </label>
        <input
          type="text"
          value={employee.phone || ''}
          onChange={(e) => onChange({ ...employee, phone: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="+7 (999) 123-45-67"
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
