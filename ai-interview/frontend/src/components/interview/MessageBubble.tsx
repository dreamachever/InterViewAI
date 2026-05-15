import { Avatar, Space, Typography } from 'antd';
import { RobotOutlined, UserOutlined } from '@ant-design/icons';
import type { Message } from '../../types/interview';

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isCandidate = message.role === 'candidate';
  return (
    <div className={`message-row ${isCandidate ? 'message-row-right' : 'message-row-left'}`}>
      {!isCandidate && <Avatar icon={<RobotOutlined />} />}
      <div className={`message-bubble ${isCandidate ? 'candidate-bubble' : 'interviewer-bubble'}`}>
        <Space direction="vertical" size={4}>
          <Typography.Text strong>{isCandidate ? '候选人' : 'AI 面试官'}</Typography.Text>
          <Typography.Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{message.content}</Typography.Paragraph>
        </Space>
      </div>
      {isCandidate && <Avatar icon={<UserOutlined />} />}
    </div>
  );
}
