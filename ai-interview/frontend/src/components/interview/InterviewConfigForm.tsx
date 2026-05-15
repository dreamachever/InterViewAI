import { Button, Form, Input, Select } from 'antd';
import type { InterviewConfig } from '../../types/interview';

const interviewTypes = ['保研综合面', '保研科研面', '保研专业面'];
const interviewerStyles = ['和善导师', '严肃导师', '压力导师', '专业导师', '科研导师'];

interface Props {
  loading?: boolean;
  onSubmit: (values: InterviewConfig) => void;
}

export function InterviewConfigForm({ loading, onSubmit }: Props) {
  return (
    <Form layout="vertical" onFinish={onSubmit} initialValues={{ type: '保研科研面', interviewer_style: '严肃导师' }}>
      <Form.Item name="type" label="面试类型" rules={[{ required: true, message: '请选择面试类型' }]}>
        <Select options={interviewTypes.map((item) => ({ label: item, value: item }))} />
      </Form.Item>
      <Form.Item name="interviewer_style" label="面试官风格" rules={[{ required: true, message: '请选择面试官风格' }]}>
        <Select options={interviewerStyles.map((item) => ({ label: item, value: item }))} />
      </Form.Item>
      <Form.Item name="target_school" label="目标院校">
        <Input placeholder="例如：浙江大学" />
      </Form.Item>
      <Form.Item name="target_major" label="目标专业">
        <Input placeholder="例如：计算机科学与技术" />
      </Form.Item>
      <Form.Item name="resume_text" label="简历文本" rules={[{ required: true, min: 10, message: '请粘贴至少 10 个字符的简历文本' }]}>
        <Input.TextArea rows={10} placeholder="粘贴你的简历文本、课程背景、科研经历、竞赛经历或项目经历..." />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={loading} block size="large">
        开始面试
      </Button>
    </Form>
  );
}
