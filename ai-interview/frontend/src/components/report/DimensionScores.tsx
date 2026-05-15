import { Card, Progress, Space, Typography } from 'antd';
import type { DimensionScore } from '../../types/report';

interface Props {
  scores: Record<string, DimensionScore>;
}

export function DimensionScores({ scores }: Props) {
  return (
    <Card title="分项评分">
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {Object.entries(scores).map(([name, item]) => (
          <div key={name}>
            <Typography.Text strong>{name}</Typography.Text>
            <Progress percent={Math.round((item.score / item.max) * 100)} format={() => `${item.score}/${item.max}`} />
            <Typography.Text type="secondary">{item.comment}</Typography.Text>
          </div>
        ))}
      </Space>
    </Card>
  );
}
