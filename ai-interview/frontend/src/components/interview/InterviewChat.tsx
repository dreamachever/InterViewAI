import { Button, Empty, Input, Space } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { useMemo, useState } from 'react';
import type { Message } from '../../types/interview';
import { MessageBubble } from './MessageBubble';

interface Props {
  messages: Message[];
  sending?: boolean;
  onSend: (answer: string) => void;
}

export function InterviewChat({ messages, sending, onSend }: Props) {
  const [answer, setAnswer] = useState('');
  const canSend = useMemo(() => answer.trim().length > 0 && !sending, [answer, sending]);

  const submit = () => {
    if (!canSend) return;
    onSend(answer);
    setAnswer('');
  };

  return (
    <div className="chat-shell">
      <div className="message-list">
        {messages.length === 0 ? <Empty description="暂无消息" /> : messages.map((message) => <MessageBubble key={message.id} message={message} />)}
      </div>
      <Space.Compact className="chat-input">
        <Input.TextArea
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          onPressEnter={(event) => {
            if (!event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
          autoSize={{ minRows: 2, maxRows: 5 }}
          placeholder="输入你的回答，Enter 发送，Shift + Enter 换行"
        />
        <Button type="primary" icon={<SendOutlined />} loading={sending} disabled={!canSend} onClick={submit}>
          发送
        </Button>
      </Space.Compact>
    </div>
  );
}
