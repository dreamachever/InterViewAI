import { Avatar, Button, Space, Tooltip, Typography } from 'antd';
import { RobotOutlined, SoundOutlined, UserOutlined } from '@ant-design/icons';
import type { Message } from '../../types/interview';

interface Props {
  message: Message;
  voiceEnabled?: boolean;
  speechSupported?: boolean;
  onSpeak?: (text: string) => void;
}

export function MessageBubble({ message, voiceEnabled, speechSupported, onSpeak }: Props) {
  const isCandidate = message.role === 'candidate';
  return (
    <div className={`message-row ${isCandidate ? 'message-row-right' : 'message-row-left'}`}>
      {!isCandidate && <Avatar icon={<RobotOutlined />} />}
      <div className={`message-bubble ${isCandidate ? 'candidate-bubble' : 'interviewer-bubble'}`}>
        <Space direction="vertical" size={4}>
          <Space>
            <Typography.Text strong>{isCandidate ? '候选人' : 'AI 面试官'}</Typography.Text>
            {!isCandidate && voiceEnabled && (
              <Tooltip title={speechSupported ? '朗读这条问题' : '当前浏览器不支持语音播报'}>
                <Button
                  size="small"
                  type="text"
                  icon={<SoundOutlined />}
                  disabled={!speechSupported}
                  onClick={() => onSpeak?.(message.content)}
                />
              </Tooltip>
            )}
          </Space>
          <Typography.Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{message.content}</Typography.Paragraph>
        </Space>
      </div>
      {isCandidate && <Avatar icon={<UserOutlined />} />}
    </div>
  );
}
