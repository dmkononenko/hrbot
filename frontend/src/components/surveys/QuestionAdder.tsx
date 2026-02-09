import React from 'react';
import { Button } from '../ui/Button';

interface QuestionAdderProps {
  onAdd: () => void;
}

export const QuestionAdder: React.FC<QuestionAdderProps> = ({ onAdd }) => {
  return (
    <Button variant="secondary" onClick={onAdd} className="w-full">
      + Добавить вопрос
    </Button>
  );
};
