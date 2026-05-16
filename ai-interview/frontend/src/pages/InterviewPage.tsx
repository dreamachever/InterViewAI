import { Card, Space, Spin, Tag, Typography, message } from 'antd';
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
      if (result.action === 'end_interview') message.info('面试轮次已接近上限，可以生成报告了。');
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
      {data.experiences.length > 0 && (
        <Card style={{ marginBottom: 16 }} title="已启用的面经增强">
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            {data.experiences.map((item) => (
              <div key={item.id}>
                <Typography.Text strong>{item.title}</Typography.Text>
                <div>
                  <Space wrap>
                    <Tag>{item.target_school || '未填写院校'}</Tag>
                    <Tag>{item.target_major || '未填写专业'}</Tag>
                    <Tag>{item.interview_type || '未填写类型'}</Tag>
                    <Tag>{item.year || '未知年份'}</Tag>
                    <Tag color="blue">问题数 {item.real_question_count}</Tag>
                  </Space>
                </div>
              </div>
            ))}
          </Space>
        </Card>
      )}
      <InterviewChat
        messages={data.messages}
        sending={sendMutation.isPending}
        voiceEnabled={data.voice_enabled}
        onSend={(answer) => sendMutation.mutate(answer)}
      />
    </div>
  );
}
