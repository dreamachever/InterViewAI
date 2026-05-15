import { Button, Card, Form, Input, Typography, message } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { getApiError } from '../api/client';
import { getCurrentUser } from '../api/users';
import { useAuth } from '../store/authStore';
import type { LoginRequest } from '../types/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setToken, setUser } = useAuth();
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/interviews';

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: async (data) => {
      setToken(data.access_token);
      const user = await getCurrentUser();
      setUser(user);
      message.success('登录成功');
      navigate(from, { replace: true });
    },
    onError: (error) => message.error(getApiError(error) || '账号或密码错误'),
  });

  return (
    <div className="page-container auth-container">
      <Card>
        <Typography.Title level={2}>登录</Typography.Title>
        <Form layout="vertical" onFinish={(values: LoginRequest) => mutation.mutate(values)}>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }]}>
            <Input placeholder="test@example.com" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, min: 8, message: '请输入至少 8 位密码' }]}>
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={mutation.isPending} block size="large">
            登录
          </Button>
        </Form>
        <Typography.Paragraph className="auth-link">
          还没有账号？<Link to="/register">去注册</Link>
        </Typography.Paragraph>
      </Card>
    </div>
  );
}
