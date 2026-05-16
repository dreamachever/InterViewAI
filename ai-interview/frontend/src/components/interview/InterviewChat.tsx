import { Alert, Button, Empty, Input, Space, Switch, Typography } from 'antd';
import { AudioMutedOutlined, AudioOutlined, SendOutlined, StopOutlined } from '@ant-design/icons';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { Message } from '../../types/interview';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { MessageBubble } from './MessageBubble';

interface Props {
  messages: Message[];
  sending?: boolean;
  voiceEnabled?: boolean;
  onSend: (answer: string) => void;
}

export function InterviewChat({ messages, sending, voiceEnabled = false, onSend }: Props) {
  const [answer, setAnswer] = useState('');
  const [autoSpeak, setAutoSpeak] = useState(voiceEnabled);
  const lastSpokenMessageId = useRef<string | null>(null);
  const speech = useSpeechSynthesis();
  const recognition = useSpeechRecognition((text) => setAnswer(text));
  const canSend = useMemo(() => answer.trim().length > 0 && !sending, [answer, sending]);

  const latestInterviewerMessage = useMemo(
    () => [...messages].reverse().find((message) => message.role === 'interviewer'),
    [messages]
  );

  useEffect(() => {
    setAutoSpeak(voiceEnabled);
  }, [voiceEnabled]);

  useEffect(() => {
    if (!voiceEnabled || !autoSpeak || !latestInterviewerMessage || !speech.supported) return;
    if (lastSpokenMessageId.current === latestInterviewerMessage.id) return;
    lastSpokenMessageId.current = latestInterviewerMessage.id;
    speech.speak(latestInterviewerMessage.content);
  }, [autoSpeak, latestInterviewerMessage, speech, voiceEnabled]);

  const submit = () => {
    if (!canSend) return;
    recognition.stop();
    speech.stop();
    onSend(answer);
    setAnswer('');
    recognition.reset();
  };

  const startListening = useCallback(() => {
    speech.stop();
    recognition.start();
  }, [recognition, speech]);

  return (
    <div className="chat-shell">
      {voiceEnabled && (
        <div className="voice-toolbar">
          <Space wrap>
            <Typography.Text strong>语音面试模式</Typography.Text>
            <Switch checked={autoSpeak} onChange={setAutoSpeak} checkedChildren="自动朗读" unCheckedChildren="手动朗读" />
            <Button icon={<StopOutlined />} disabled={!speech.supported} onClick={speech.stop}>
              停止朗读
            </Button>
            <Typography.Text type="secondary">
              {speech.supported ? 'AI 问题可朗读' : '当前浏览器不支持语音播报'}
              {' / '}
              {recognition.supported ? '麦克风可转文字' : '当前浏览器不支持语音识别'}
            </Typography.Text>
          </Space>
          {recognition.error && <Alert type="warning" showIcon message={recognition.error} style={{ marginTop: 8 }} />}
        </div>
      )}
      <div className="message-list">
        {messages.length === 0 ? (
          <Empty description="暂无消息" />
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              voiceEnabled={voiceEnabled}
              speechSupported={speech.supported}
              onSpeak={speech.speak}
            />
          ))
        )}
      </div>
      <div className="chat-input">
        {voiceEnabled && recognition.interimText && (
          <Typography.Paragraph type="secondary" className="voice-interim">
            正在识别：{recognition.interimText}
          </Typography.Paragraph>
        )}
        <Space.Compact style={{ width: '100%' }}>
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
          {voiceEnabled && (
            recognition.listening ? (
              <Button icon={<AudioMutedOutlined />} onClick={recognition.stop}>
                停止
              </Button>
            ) : (
              <Button icon={<AudioOutlined />} disabled={!recognition.supported || sending} onClick={startListening}>
                语音
              </Button>
            )
          )}
          <Button type="primary" icon={<SendOutlined />} loading={sending} disabled={!canSend} onClick={submit}>
            发送
          </Button>
        </Space.Compact>
      </div>
    </div>
  );
}
