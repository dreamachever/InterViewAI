import { Button, Result, Spin, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { getReport } from '../api/interviews';
import { ReportView } from '../components/report/ReportView';

export function ReportPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const interviewId = id ?? '';
  const { data, isLoading, isError } = useQuery({
    queryKey: ['report', interviewId],
    queryFn: () => getReport(interviewId),
    enabled: Boolean(interviewId),
  });

  if (isLoading) {
    return (
      <div className="center-page">
        <Spin size="large" />
      </div>
    );
  }

  if (isError || !data) {
    return <Result status="warning" title="报告暂不可用" extra={<Button onClick={() => navigate(`/interviews/${interviewId}`)}>返回面试</Button>} />;
  }

  return (
    <div className="page-container">
      <Typography.Title level={2}>面试评分报告</Typography.Title>
      <ReportView report={data} />
    </div>
  );
}
