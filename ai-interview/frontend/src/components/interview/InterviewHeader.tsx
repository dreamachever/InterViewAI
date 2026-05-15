import { Button, Space, Tag, Typography } from 'antd';
import type { InterviewDetail } from '../../types/interview';

interface Props {
  interview: InterviewDetail;
  finishing?: boolean;
  onFinish: () => void;
}

export function InterviewHeader({ interview, finishing, onFinish }: Props) {
  return (
    <div className="interview-header">
      <Space direction="vertical" size={6}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          {interview.type}
        </Typography.Title>
        <Space wrap>
          <Tag color="blue">{interview.interviewer_style}</Tag>
          <Tag color="purple">{interview.current_stage}</Tag>
          {interview.target_school && <Tag>{interview.target_school}</Tag>}
          {interview.target_company && <Tag>{interview.target_company}</Tag>}
        </Space>
      </Space>
      <Button danger loading={finishing} onClick={onFinish}>
        结束面试并生成报告
      </Button>
    </div>
  );
}
