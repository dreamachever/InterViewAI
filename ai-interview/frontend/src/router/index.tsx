import { createBrowserRouter } from 'react-router-dom';
import { HomePage } from '../pages/HomePage';
import { InterviewHistoryPage } from '../pages/InterviewHistoryPage';
import { InterviewPage } from '../pages/InterviewPage';
import { LoginPage } from '../pages/LoginPage';
import { NewInterviewPage } from '../pages/NewInterviewPage';
import { RegisterPage } from '../pages/RegisterPage';
import { ReportPage } from '../pages/ReportPage';
import { App } from '../App';
import { ProtectedRoute } from './ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'interviews', element: <InterviewHistoryPage /> },
          { path: 'interviews/new', element: <NewInterviewPage /> },
          { path: 'interviews/:id', element: <InterviewPage /> },
          { path: 'interviews/:id/report', element: <ReportPage /> },
        ],
      },
    ],
  },
]);
