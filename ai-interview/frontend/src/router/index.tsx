import { createBrowserRouter } from 'react-router-dom';
import { HomePage } from '../pages/HomePage';
import { InterviewPage } from '../pages/InterviewPage';
import { NewInterviewPage } from '../pages/NewInterviewPage';
import { ReportPage } from '../pages/ReportPage';
import { App } from '../App';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'interviews/new', element: <NewInterviewPage /> },
      { path: 'interviews/:id', element: <InterviewPage /> },
      { path: 'interviews/:id/report', element: <ReportPage /> },
    ],
  },
]);
