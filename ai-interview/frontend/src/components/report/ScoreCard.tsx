import { Card, Progress, Statistic } from 'antd';

interface Props {
  totalScore: number;
}

export function ScoreCard({ totalScore }: Props) {
  return (
    <Card>
      <Statistic title="总分" value={totalScore} suffix="/ 100" />
      <Progress percent={totalScore} status={totalScore >= 80 ? 'success' : 'normal'} />
    </Card>
  );
}
