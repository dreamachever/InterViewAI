import { Spin, message } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { finishInterview, getInterview, sendAnswer } from '../api/interviews';
import { getApiError } from '../api/client';
import { InterviewChat } from '../components/interview/InterviewChat';
import { InterviewHeader } from '../components/interview/InterviewHeader';

export function InterviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const interviewId = id ?? '';

  const { data, isLoading } = useQuery({
    queryKey: ['interview', interviewId],
    queryFn: () => getInterview(interviewId),
    enabled: Boolean(interviewId),
  });

  const sendMutation = useMutation({
    mutationFn: (answer: string) => sendAnswer(interviewId, answer),
    onSuccess: async (result) => {
      await queryClient.invalidateQueries({ queryKey: ['interview', interviewId] });
      if (result.action === 'end_interview') message.info('面试轮次已接近上限，可以生成报告了');
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const finishMutation = useMutation({
    mutationFn: () => finishInterview(interviewId),
    onSuccess: () => navigate(`/interviews/${interviewId}/report`),
    onError: (error) => message.error(getApiError(error)),
  });

  if (isLoading || !data) {
    return (
      <div className="center-page">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="page-container">
      <InterviewHeader interview={data} finishing={finishMutation.isPending} onFinish={() => finishMutation.mutate()} />
      <InterviewChat messages={data.messages} sending={sendMutation.isPending} onSend={(answer) => sendMutation.mutate(answer)} />
    </div>
  );
}
