import { Card, Col, List, Row, Space, Typography } from 'antd';
import type { Report } from '../../types/report';
import { DimensionScores } from './DimensionScores';
import { QuestionReviews } from './QuestionReviews';
import { ScoreCard } from './ScoreCard';

interface Props {
  report: Report;
}

export function ReportView({ report }: Props) {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <ScoreCard totalScore={report.total_score} />
        </Col>
        <Col xs={24} md={16}>
          <Card title="整体评价">
            <Typography.Paragraph>{report.overall_comment}</Typography.Paragraph>
          </Card>
        </Col>
      </Row>
      <DimensionScores scores={report.dimension_scores} />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card title="优点">
            <List dataSource={report.strengths} renderItem={(item) => <List.Item>{item}</List.Item>} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card title="问题">
            <List dataSource={report.weaknesses} renderItem={(item) => <List.Item>{item}</List.Item>} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card title="简历风险">
            <List dataSource={report.resume_risks} renderItem={(item) => <List.Item>{item}</List.Item>} />
          </Card>
        </Col>
      </Row>
      <QuestionReviews reviews={report.question_reviews} />
      <Card title="下一次训练计划">
        <List dataSource={report.next_training_plan} renderItem={(item) => <List.Item>{item}</List.Item>} />
      </Card>
    </Space>
  );
}
