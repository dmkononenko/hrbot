import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { Surveys } from './pages/Surveys';
import { Employees } from './pages/Employees';
import { Results } from './pages/Results';
import { SurveyResults } from './pages/SurveyResults';

const Navigation = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-white shadow-md mb-6">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-xl font-bold text-blue-600">
              HR Bot Admin
            </Link>
            <div className="flex gap-4">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isActive('/')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Панель
              </Link>
              <Link
                to="/surveys"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isActive('/surveys')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Опросы
              </Link>
              <Link
                to="/employees"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isActive('/employees')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Сотрудники
              </Link>
              <Link
                to="/results"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isActive('/results')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Результаты
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

const AppContent = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/surveys" element={<Surveys />} />
          <Route path="/surveys/:surveyId/results" element={<SurveyResults />} />
          <Route path="/employees" element={<Employees />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </div>
    </div>
  );
};

export const App = () => {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
};
