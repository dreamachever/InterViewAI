import { Button, Card, Descriptions, Empty, Popconfirm, Space, Spin, Tag, Typography, message } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { deleteExperience, extractExperience, getExperience } from '../api/experiences';
import { getApiError } from '../api/client';

export function ExperienceDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const experienceId = id ?? '';
  const { data, isLoading } = useQuery({
    queryKey: ['experience', experienceId],
    queryFn: () => getExperience(experienceId),
    enabled: Boolean(experienceId),
  });
  const extractMutation = useMutation({
    mutationFn: () => extractExperience(experienceId),
    onSuccess: async () => {
      message.success('已重新提取面经要点');
      await queryClient.invalidateQueries({ queryKey: ['experience', experienceId] });
      await queryClient.invalidateQueries({ queryKey: ['experiences'] });
    },
    onError: (error) => message.error(getApiError(error)),
  });
  const deleteMutation = useMutation({
    mutationFn: () => deleteExperience(experienceId),
    onSuccess: async () => {
      message.success('面经已删除');
      await queryClient.invalidateQueries({ queryKey: ['experiences'] });
      navigate('/experiences');
    },
    onError: (error) => message.error(getApiError(error)),
  });

  if (isLoading || !data) {
    return <div className="center-page"><Spin size="large" /></div>;
  }

  const insight = data.latest_insight;

  return (
    <div className="page-container">
      <div className="page-title-row">
        <Typography.Title level={2} style={{ margin: 0 }}>{data.title}</Typography.Title>
        <Space>
          <Button onClick={() => navigate('/experiences')}>返回列表</Button>
          <Button loading={extractMutation.isPending} onClick={() => extractMutation.mutate()}>重新提取</Button>
          <Popconfirm
            title="确认删除这条面经？"
            description="会同步删除 AI 提取结果以及关联关系。"
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
            onConfirm={() => deleteMutation.mutate()}
          >
            <Button danger loading={deleteMutation.isPending}>删除</Button>
          </Popconfirm>
        </Space>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Descriptions column={{ xs: 1, md: 2 }}>
          <Descriptions.Item label="学校">{data.target_school || '-'}</Descriptions.Item>
          <Descriptions.Item label="专业">{data.target_major || '-'}</Descriptions.Item>
          <Descriptions.Item label="实验室">{data.target_lab || '-'}</Descriptions.Item>
          <Descriptions.Item label="导师">{data.target_teacher || '-'}</Descriptions.Item>
          <Descriptions.Item label="面试类型">{data.interview_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="年份">{data.year || '-'}</Descriptions.Item>
          <Descriptions.Item label="来源">{data.source_type}</Descriptions.Item>
          <Descriptions.Item label="提取状态"><Tag>{data.extract_status}</Tag></Descriptions.Item>
          <Descriptions.Item label="来源链接" span={2}>
            {data.source_url ? <a href={data.source_url} target="_blank" rel="noreferrer">{data.source_url}</a> : '-'}
          </Descriptions.Item>
        </Descriptions>
        {data.summary && (
          <>
            <Typography.Title level={5} style={{ marginTop: 16 }}>摘要</Typography.Title>
            <Typography.Paragraph>{data.summary}</Typography.Paragraph>
          </>
        )}
      </Card>

      <Card title="原文内容" style={{ marginBottom: 16 }}>
        <div className="resume-text" style={{ marginTop: 0 }}>{data.raw_content}</div>
      </Card>

      <Card title="AI 提取结果">
        {!insight ? (
          <Empty description="暂未生成结构化要点" />
        ) : (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <InsightSection title="面试流程" tags={insight.interview_process_json} />
            <InsightSection
              title="高频问题分类"
              items={insight.question_categories_json.map((item) => `${item.category}（${item.frequency}）：${item.questions.join('；')}`)}
            />
            <InsightSection
              title="真实问题"
              items={insight.real_questions_json.map((item) => `${item.question}${item.category ? ` ｜ ${item.category}` : ''}`)}
            />
            <InsightSection title="重点考察方向" tags={insight.focus_points_json} />
            <InsightSection
              title="风险点"
              items={insight.risk_points_json.map((item) => `${item.level.toUpperCase()} ｜ ${item.point}${item.suggestion ? ` ｜ 建议：${item.suggestion}` : ''}`)}
            />
            <InsightSection title="准备策略" items={insight.suggested_strategy_json} />
          </Space>
        )}
      </Card>
    </div>
  );
}

function InsightSection({ title, tags, items }: { title: string; tags?: string[]; items?: string[] }) {
  const values = tags ?? items ?? [];
  return (
    <div>
      <Typography.Title level={5}>{title}</Typography.Title>
      {tags ? (
        <Space wrap>{values.map((item) => <Tag key={item}>{item}</Tag>)}</Space>
      ) : (
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          {values.map((item) => <Typography.Paragraph key={item} style={{ marginBottom: 0 }}>{item}</Typography.Paragraph>)}
        </Space>
      )}
    </div>
  );
}
