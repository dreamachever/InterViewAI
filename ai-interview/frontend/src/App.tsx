import { Button, Layout, Space, Typography } from 'antd';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from './store/authStore';

export function App() {
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Layout className="app-layout">
      <Layout.Header className="app-header">
        <Typography.Text className="app-brand" onClick={() => navigate('/')}>
          保研 AI 模拟面试系统
        </Typography.Text>
        <Space>
          {isAuthenticated ? (
            <>
              <Typography.Text className="app-user">{user?.nickname || user?.email}</Typography.Text>
              <Link to="/interviews">我的面试</Link>
              <Link to="/resumes">简历中心</Link>
              <Link to="/settings/llm">模型设置</Link>
              <Button type="link" onClick={handleLogout}>
                退出登录
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">登录</Link>
              <Link to="/register">注册</Link>
            </>
          )}
        </Space>
      </Layout.Header>
      <Layout.Content>
        <Outlet />
      </Layout.Content>
    </Layout>
  );
}
