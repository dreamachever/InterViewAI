import { Card, message, Typography } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { createInterview } from '../api/interviews';
import { getApiError } from '../api/client';
import { InterviewConfigForm } from '../components/interview/InterviewConfigForm';
import type { InterviewConfig } from '../types/interview';

export function NewInterviewPage() {
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: createInterview,
    onSuccess: (data) => navigate(`/interviews/${data.interview_id}`),
    onError: (error) => message.error(getApiError(error)),
  });

  const onSubmit = (values: InterviewConfig) => {
    mutation.mutate({
      ...values,
      target_school: values.target_school || null,
      target_major: values.target_major || null,
    });
  };

  return (
    <div className="page-container narrow-container">
      <Typography.Title level={2}>创建模拟面试</Typography.Title>
      <Card>
        <InterviewConfigForm loading={mutation.isPending} onSubmit={onSubmit} />
      </Card>
    </div>
  );
}
