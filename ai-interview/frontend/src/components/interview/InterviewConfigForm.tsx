import { Button, Form, Input, Select } from 'antd';
import type { InterviewConfig } from '../../types/interview';

const interviewTypes = ['保研综合面', '保研科研面', '保研专业面', '求职技术面', '求职 HR 面'];
const interviewerStyles = ['和善导师', '严肃导师', '压力导师', '技术专家', 'HR 面试官'];

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
      <Form.Item name="target_company" label="目标公司">
        <Input placeholder="例如：字节跳动" />
      </Form.Item>
      <Form.Item name="target_major" label="目标专业">
        <Input placeholder="例如：计算机科学与技术" />
      </Form.Item>
      <Form.Item name="target_position" label="目标岗位">
        <Input placeholder="例如：后端开发工程师" />
      </Form.Item>
      <Form.Item name="resume_text" label="简历文本" rules={[{ required: true, min: 10, message: '请粘贴至少 10 个字符的简历文本' }]}>
        <Input.TextArea rows={10} placeholder="粘贴你的简历文本、项目经历、科研经历或实习经历..." />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={loading} block size="large">
        开始面试
      </Button>
    </Form>
  );
}
