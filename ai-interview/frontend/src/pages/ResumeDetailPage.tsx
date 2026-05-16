import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Input,
  List,
  Popconfirm,
  Progress,
  Row,
  Select,
  Space,
  Tag,
  Typography,
  message,
} from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CopyOutlined } from '@ant-design/icons';
import { diagnoseResume, getResume, listResumeDiagnostics, reparseResume, updateResume } from '../api/resumes';
import { listLLMConfigs } from '../api/llmConfigs';
import { createInterview } from '../api/interviews';
import { getApiError } from '../api/client';
import type { ResumeDiagnostic, ResumeSuggestion } from '../types/resume';

type RiskLevel = 'high' | 'medium' | 'low';

const riskMeta: Record<RiskLevel, { label: string; color: string }> = {
  high: { label: '高风险', color: 'red' },
  medium: { label: '中风险', color: 'orange' },
  low: { label: '低风险', color: 'blue' },
};

export function ResumeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm<{ title: string }>();
  const [isEditingText, setIsEditingText] = useState(false);
  const [draftText, setDraftText] = useState('');
  const resumeId = id || '';
  const { data: resume } = useQuery({ queryKey: ['resume', resumeId], queryFn: () => getResume(resumeId), enabled: Boolean(resumeId) });
  const { data: diagnostics = [] } = useQuery({ queryKey: ['resume-diagnostics', resumeId], queryFn: () => listResumeDiagnostics(resumeId), enabled: Boolean(resumeId) });
  const { data: llmConfigs = [] } = useQuery({ queryKey: ['llm-configs'], queryFn: listLLMConfigs });
  const latest = diagnostics[0];
  const questions = latest?.likely_interview_questions || latest?.follow_up_questions_json || [];

  const groupedRisks = useMemo(() => {
    const groups: Record<RiskLevel, ResumeSuggestion[]> = { high: [], medium: [], low: [] };
    latest?.suggestions_json.forEach((item) => {
      const level = (['high', 'medium', 'low'].includes(item.priority) ? item.priority : 'medium') as RiskLevel;
      groups[level].push(item);
    });
    return groups;
  }, [latest]);

  useEffect(() => {
    if (resume?.title) form.setFieldsValue({ title: resume.title });
    if (resume?.parsed_text && !isEditingText) setDraftText(resume.parsed_text);
  }, [form, isEditingText, resume?.parsed_text, resume?.title]);

  const refreshResume = () => {
    queryClient.invalidateQueries({ queryKey: ['resume', resumeId] });
    queryClient.invalidateQueries({ queryKey: ['resumes'] });
  };

  const diagnoseMutation = useMutation({
    mutationFn: (llmConfigId?: string | null) => diagnoseResume(resumeId, llmConfigId),
    onSuccess: (diagnostic) => {
      queryClient.setQueryData<ResumeDiagnostic[]>(['resume-diagnostics', resumeId], (current = []) => [
        diagnostic,
        ...current.filter((item) => item.id !== diagnostic.id),
      ]);
      if (diagnostic.fallback_used) {
        message.warning(`真实模型调用失败，已使用 mock 结果：${diagnostic.fallback_reason || '请检查模型配置'}`);
      } else {
        message.success(`简历诊断已生成：${diagnostic.provider}${diagnostic.model ? ` / ${diagnostic.model}` : ''}，${diagnostic.overall_score} 分`);
      }
      queryClient.invalidateQueries({ queryKey: ['resume-diagnostics', resumeId] });
      refreshResume();
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const saveTitleMutation = useMutation({
    mutationFn: (title: string) => updateResume(resumeId, { title }),
    onSuccess: () => {
      message.success('标题已更新');
      refreshResume();
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const saveTextMutation = useMutation({
    mutationFn: () => updateResume(resumeId, { parsed_text: draftText }),
    onSuccess: () => {
      message.success('解析文本已保存，建议重新分析');
      setIsEditingText(false);
      refreshResume();
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const reparseMutation = useMutation({
    mutationFn: () => reparseResume(resumeId),
    onSuccess: () => {
      message.success('重新解析完成');
      refreshResume();
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const startMutation = useMutation({
    mutationFn: () =>
      createInterview({
        type: '保研科研面',
        interviewer_style: '严谨导师',
        resume_id: resumeId,
      }),
    onSuccess: (data) => navigate(`/interviews/${data.interview_id}`),
    onError: (error) => message.error(getApiError(error)),
  });

  const copyQuestion = async (question: string) => {
    await navigator.clipboard.writeText(question);
    message.success('已复制问题');
  };

  return (
    <div className="page-container">
      <div className="page-title-row">
        <Typography.Title level={2}>{resume?.title || '简历详情'}</Typography.Title>
        <Space>
          <Button onClick={() => startMutation.mutate()} loading={startMutation.isPending}>用这份简历开始面试</Button>
          <Popconfirm title="确认重新解析 PDF？" description="会用原始 PDF 覆盖当前解析文本。" onConfirm={() => reparseMutation.mutate()}>
            <Button loading={reparseMutation.isPending}>重新解析</Button>
          </Popconfirm>
          <Button type="primary" onClick={() => diagnoseMutation.mutate(null)} loading={diagnoseMutation.isPending}>
            {diagnoseMutation.isPending ? '正在分析...' : '重新分析'}
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={8}>
          <Card>
            <Typography.Text type="secondary">AI 简历总分</Typography.Text>
            <Progress percent={latest?.overall_score || 0} status={(latest?.overall_score || 0) >= 80 ? 'success' : 'normal'} />
            <Typography.Title level={2} style={{ margin: 0 }}>{latest?.overall_score ?? '--'} / 100</Typography.Title>
          </Card>
        </Col>
        <Col xs={24} md={16}>
          <Card>
            <Space wrap>
              <Tag color={resume?.parse_status === 'success' ? 'green' : 'red'}>解析：{resume?.parse_status || '-'}</Tag>
              <Tag color={resume?.analysis_status === 'success' ? 'green' : resume?.analysis_status === 'outdated' ? 'orange' : 'default'}>
                分析：{resume?.analysis_status || 'none'}
              </Tag>
              {latest && (
                <Tag color={latest.fallback_used ? 'orange' : latest.provider === 'mock' ? 'default' : 'blue'}>
                  {latest.fallback_used ? 'mock fallback' : `${latest.provider}${latest.model ? ` / ${latest.model}` : ''}`}
                </Tag>
              )}
            </Space>
            <Typography.Paragraph style={{ marginTop: 12 }}>{latest?.summary || '还没有诊断报告。点击重新分析生成 AI 简历诊断。'}</Typography.Paragraph>
            {latest?.fallback_used && (
              <Alert
                type="warning"
                showIcon
                message="真实模型调用失败，本次结果来自 mock，仅用于流程演示。"
                description={latest.fallback_reason || '请检查 API Key、Base URL、模型名称或网络连接。'}
                style={{ marginBottom: 12 }}
              />
            )}
            {latest && (
              <Typography.Text type="secondary">
                最近分析时间：{new Date(latest.created_at).toLocaleString()}
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      {resume?.analysis_status === 'outdated' && <Alert type="warning" showIcon message="解析文本已修改，当前诊断可能已过期，建议重新分析。" style={{ marginBottom: 16 }} />}

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={11}>
          <Card title="解析文本">
            <Form form={form} layout="inline" onFinish={(values) => saveTitleMutation.mutate(values.title)}>
              <Form.Item name="title" rules={[{ required: true, message: '请输入标题' }]}>
                <Input placeholder="简历标题" />
              </Form.Item>
              <Button htmlType="submit" loading={saveTitleMutation.isPending}>保存标题</Button>
            </Form>

            {isEditingText ? (
              <Space direction="vertical" style={{ width: '100%', marginTop: 18 }}>
                <Input.TextArea rows={18} value={draftText} onChange={(event) => setDraftText(event.target.value)} />
                <Space>
                  <Button type="primary" onClick={() => saveTextMutation.mutate()} loading={saveTextMutation.isPending}>保存修改</Button>
                  <Button onClick={() => { setDraftText(resume?.parsed_text || ''); setIsEditingText(false); }}>取消编辑</Button>
                </Space>
              </Space>
            ) : (
              <>
                <Typography.Paragraph className="resume-text">{resume?.parsed_text}</Typography.Paragraph>
                <Button onClick={() => setIsEditingText(true)}>编辑解析文本</Button>
              </>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={13}>
          <Card
            title="AI 简历诊断"
            extra={
              <Select
                allowClear
                placeholder="选择模型重新分析"
                style={{ width: 220 }}
                loading={diagnoseMutation.isPending}
                disabled={diagnoseMutation.isPending}
                onSelect={(value) => diagnoseMutation.mutate(value)}
                options={llmConfigs.map((item) => ({ label: `${item.display_name}${item.is_default ? '（默认）' : ''}`, value: item.id }))}
              />
            }
          >
            {latest ? (
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Section title="优势" items={latest.strengths_json} color="green" />
                <Typography.Title level={4}>风险点</Typography.Title>
                {(Object.keys(riskMeta) as RiskLevel[]).map((level) => (
                  <RiskGroup key={level} title={riskMeta[level].label} color={riskMeta[level].color} items={groupedRisks[level]} />
                ))}
                <Typography.Title level={4}>可能追问</Typography.Title>
                <List
                  dataSource={questions}
                  renderItem={(item) => (
                    <List.Item actions={[<Button icon={<CopyOutlined />} size="small" onClick={() => copyQuestion(item)}>复制</Button>]}>
                      {item}
                    </List.Item>
                  )}
                />
              </Space>
            ) : (
              <Typography.Paragraph type="secondary">还没有诊断报告，点击右上角按钮生成。</Typography.Paragraph>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}

function Section({ title, items, color }: { title: string; items: string[]; color: string }) {
  return (
    <div>
      <Typography.Title level={4}>{title}</Typography.Title>
      <Space wrap>{items.map((item) => <Tag color={color} key={item}>{item}</Tag>)}</Space>
    </div>
  );
}

function RiskGroup({ title, color, items }: { title: string; color: string; items: ResumeSuggestion[] }) {
  if (!items.length) {
    return <Typography.Text type="secondary">{title}：暂无</Typography.Text>;
  }
  return (
    <div>
      <Typography.Text strong>{title}</Typography.Text>
      <List
        size="small"
        dataSource={items}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              title={<Space><Tag color={color}>{item.priority}</Tag>{item.problem}</Space>}
              description={`${item.advice}${item.example ? ` 示例：${item.example}` : ''}`}
            />
          </List.Item>
        )}
      />
    </div>
  );
}
