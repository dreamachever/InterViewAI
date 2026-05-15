import { Button, Card, Form, Input, Typography, message } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/auth';
import { getApiError } from '../api/client';
import type { RegisterRequest } from '../types/auth';

export function RegisterPage() {
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: register,
    onSuccess: () => {
      message.success('注册成功，请登录');
      navigate('/login');
    },
    onError: (error) => message.error(getApiError(error)),
  });

  return (
    <div className="page-container auth-container">
      <Card>
        <Typography.Title level={2}>注册</Typography.Title>
        <Form layout="vertical" onFinish={(values: RegisterRequest) => mutation.mutate(values)}>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }]}>
            <Input placeholder="test@example.com" />
          </Form.Item>
          <Form.Item name="nickname" label="昵称">
            <Input placeholder="例如：张三" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, min: 8, message: '请输入至少 8 位密码' }]}>
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={mutation.isPending} block size="large">
            注册
          </Button>
        </Form>
        <Typography.Paragraph className="auth-link">
          已有账号？<Link to="/login">去登录</Link>
        </Typography.Paragraph>
      </Card>
    </div>
  );
}
