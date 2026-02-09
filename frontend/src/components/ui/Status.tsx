import React from 'react';

type StatusType = 'active' | 'inactive' | 'pending' | 'completed' | 'failed';

interface StatusProps {
  type: StatusType;
}

export const Status: React.FC<StatusProps> = ({ type }) => {
  const statusStyles = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-blue-100 text-blue-800',
    failed: 'bg-red-100 text-red-800',
  };

  const statusLabels: Record<StatusType, string> = {
    active: 'Активен',
    inactive: 'Неактивен',
    pending: 'Ожидает',
    completed: 'Завершен',
    failed: 'Ошибка',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[type]}`}
    >
      {statusLabels[type]}
    </span>
  );
};
