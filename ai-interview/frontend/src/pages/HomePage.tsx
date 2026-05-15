import { Button, Space, Typography } from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

export function HomePage() {
  const navigate = useNavigate();
  return (
    <div className="home-page">
      <Space direction="vertical" size="large" className="home-content">
        <Typography.Title>上传简历，生成你的专属 AI 面试官</Typography.Title>
        <Typography.Paragraph className="home-subtitle">
          先从文字版模拟面试开始，帮你提前发现简历风险和回答短板
        </Typography.Paragraph>
        <Button type="primary" size="large" icon={<ArrowRightOutlined />} onClick={() => navigate('/interviews/new')}>
          开始模拟面试
        </Button>
      </Space>
    </div>
  );
}
