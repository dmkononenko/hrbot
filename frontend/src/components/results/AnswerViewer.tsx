import React from 'react';
import { Answer } from '../../types';

interface AnswerViewerProps {
  answer: Answer;
}

export const AnswerViewer: React.FC<AnswerViewerProps> = ({ answer }) => {
  const displayAnswer = Array.isArray(answer.answer)
    ? answer.answer.join(', ')
    : answer.answer;

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h4 className="font-semibold text-gray-900 mb-2">{answer.question_text}</h4>
      <p className="text-gray-700">{displayAnswer}</p>
    </div>
  );
};
