import { Layout } from 'antd';
import { Outlet, useNavigate } from 'react-router-dom';

export function App() {
  const navigate = useNavigate();
  return (
    <Layout className="app-layout">
      <Layout.Header className="app-header" onClick={() => navigate('/')}>
        AI 文字版模拟面试系统
      </Layout.Header>
      <Layout.Content>
        <Outlet />
      </Layout.Content>
    </Layout>
  );
}
