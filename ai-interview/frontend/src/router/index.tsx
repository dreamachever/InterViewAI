import { createBrowserRouter } from 'react-router-dom';
import { App } from '../App';
import { ExperienceDetailPage } from '../pages/ExperienceDetailPage';
import { ExperiencesPage } from '../pages/ExperiencesPage';
import { HomePage } from '../pages/HomePage';
import { InterviewHistoryPage } from '../pages/InterviewHistoryPage';
import { InterviewPage } from '../pages/InterviewPage';
import { LLMSettingsPage } from '../pages/LLMSettingsPage';
import { LoginPage } from '../pages/LoginPage';
import { NewExperiencePage } from '../pages/NewExperiencePage';
import { NewInterviewPage } from '../pages/NewInterviewPage';
import { RegisterPage } from '../pages/RegisterPage';
import { ReportPage } from '../pages/ReportPage';
import { ResumeCenterPage } from '../pages/ResumeCenterPage';
import { ResumeDetailPage } from '../pages/ResumeDetailPage';
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
          { path: 'resumes', element: <ResumeCenterPage /> },
          { path: 'resumes/:id', element: <ResumeDetailPage /> },
          { path: 'experiences', element: <ExperiencesPage /> },
          { path: 'experiences/new', element: <NewExperiencePage /> },
          { path: 'experiences/:id', element: <ExperienceDetailPage /> },
          { path: 'settings/llm', element: <LLMSettingsPage /> },
        ],
      },
    ],
  },
]);
