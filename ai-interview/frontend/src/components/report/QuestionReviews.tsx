import { Card, Collapse, Tag, Typography } from 'antd';
import type { QuestionReview } from '../../types/report';

interface Props {
  reviews: QuestionReview[];
}

export function QuestionReviews({ reviews }: Props) {
  return (
    <Card title="逐题点评">
      <Collapse
        items={reviews.map((review, index) => ({
          key: String(index),
          label: (
            <span>
              {review.question} <Tag color="blue">{review.score}/10</Tag>
            </span>
          ),
          children: (
            <>
              <Typography.Paragraph>
                <Typography.Text strong>回答摘要：</Typography.Text>
                {review.answer_summary}
              </Typography.Paragraph>
              <Typography.Paragraph>
                <Typography.Text strong>点评：</Typography.Text>
                {review.comment}
              </Typography.Paragraph>
              <Typography.Paragraph>
                <Typography.Text strong>优化建议：</Typography.Text>
                {review.improved_answer_suggestion}
              </Typography.Paragraph>
            </>
          ),
        }))}
      />
    </Card>
  );
}
