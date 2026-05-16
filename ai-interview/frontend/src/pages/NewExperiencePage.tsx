import { Alert, Button, Card, Form, Input, InputNumber, Select, Space, Tabs, Tag, Typography, message } from 'antd';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { importExperienceText, importExperienceWeb, searchExperienceWeb } from '../api/experiences';
import { getApiError } from '../api/client';
import { listLLMConfigs } from '../api/llmConfigs';
import type { ExperienceSearchResultItem } from '../types/experience';

interface ManualFormValues {
  title: string;
  target_school?: string;
  target_major?: string;
  target_lab?: string;
  target_teacher?: string;
  interview_type?: string;
  year?: number;
  source_url?: string;
  raw_content: string;
  llm_config_id?: string;
}

interface SearchFormValues {
  keyword?: string;
  target_school?: string;
  target_major?: string;
  target_lab?: string;
  target_teacher?: string;
  interview_type?: string;
  year?: number;
  llm_config_id?: string;
}

export function NewExperiencePage() {
  const navigate = useNavigate();
  const [manualForm] = Form.useForm<ManualFormValues>();
  const [searchForm] = Form.useForm<SearchFormValues>();
  const { data: llmConfigs = [] } = useQuery({ queryKey: ['llm-configs'], queryFn: listLLMConfigs });

  const importTextMutation = useMutation({
    mutationFn: importExperienceText,
    onSuccess: (data) => {
      message.success('面经已保存，并开始提取结构化要点');
      navigate(`/experiences/${data.experience_id}`);
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const searchMutation = useMutation({
    mutationFn: searchExperienceWeb,
    onError: (error) => message.error(getApiError(error)),
  });

  const importWebMutation = useMutation({
    mutationFn: importExperienceWeb,
    onSuccess: (data) => {
      message.success('已从搜索结果导入面经，并开始提取结构化要点');
      navigate(`/experiences/${data.experience_id}`);
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const onManualFinish = (values: ManualFormValues) => {
    importTextMutation.mutate({
      ...values,
      source_url: values.source_url || null,
      target_school: values.target_school || null,
      target_major: values.target_major || null,
      target_lab: values.target_lab || null,
      target_teacher: values.target_teacher || null,
      interview_type: values.interview_type || null,
      year: values.year || null,
      llm_config_id: values.llm_config_id || null,
    });
  };

  const onSearchFinish = (values: SearchFormValues) => {
    searchMutation.mutate({
      keyword: values.keyword || undefined,
      target_school: values.target_school || undefined,
      target_major: values.target_major || undefined,
      target_lab: values.target_lab || undefined,
      target_teacher: values.target_teacher || undefined,
      interview_type: values.interview_type || undefined,
      year: values.year || undefined,
      max_results: 5,
    });
  };

  const handleImportSearchResult = (result: ExperienceSearchResultItem) => {
    const values = searchForm.getFieldsValue();
    importWebMutation.mutate({
      title: result.title,
      source_url: result.url,
      source_site: result.source_site || null,
      snippet: result.snippet,
      raw_content: result.raw_content || result.snippet,
      target_school: values.target_school || null,
      target_major: values.target_major || null,
      target_lab: values.target_lab || null,
      target_teacher: values.target_teacher || null,
      interview_type: values.interview_type || null,
      year: values.year || null,
      llm_config_id: values.llm_config_id || null,
    });
  };

  return (
    <div className="page-container narrow-container">
      <Typography.Title level={2}>新增面经</Typography.Title>
      <Card>
        <Tabs
          items={[
            {
              key: 'manual',
              label: '手动粘贴',
              children: (
                <Form form={manualForm} layout="vertical" onFinish={onManualFinish} initialValues={{ interview_type: '保研科研面' }}>
                  <ExperienceMetaFields llmConfigs={llmConfigs} />
                  <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
                    <Input placeholder="例如：浙大计算机保研复试面经" />
                  </Form.Item>
                  <Form.Item name="source_url" label="来源 URL">
                    <Input placeholder="可选，例如论坛链接" />
                  </Form.Item>
                  <Form.Item name="raw_content" label="经验贴正文" rules={[{ required: true, min: 20, message: '请粘贴至少 20 个字符的面经正文' }]}>
                    <Input.TextArea rows={14} placeholder="粘贴真实经验贴内容，AI 会自动提取面试流程、高频问题、风险点和准备策略。" />
                  </Form.Item>
                  <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                    <Button onClick={() => navigate('/experiences')}>取消</Button>
                    <Button type="primary" htmlType="submit" loading={importTextMutation.isPending}>保存并提取</Button>
                  </Space>
                </Form>
              ),
            },
            {
              key: 'search',
              label: '网络搜索',
              children: (
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <Alert
                    type="info"
                    showIcon
                    message="已接入搜索 API。建议至少填写学校或专业，再配合关键词搜索，这样命中面经结果会更稳定。"
                  />
                  <Form form={searchForm} layout="vertical" onFinish={onSearchFinish} initialValues={{ interview_type: '保研科研面' }}>
                    <ExperienceMetaFields llmConfigs={llmConfigs} />
                    <Form.Item name="keyword" label="补充关键词">
                      <Input placeholder="例如：导师面 / 机试 / 英语问答 / 预推免" />
                    </Form.Item>
                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Typography.Text type="secondary">搜索后可直接把结果导入为面经，并自动触发 AI 提取。</Typography.Text>
                      <Button type="primary" htmlType="submit" loading={searchMutation.isPending}>搜索面经</Button>
                    </Space>
                  </Form>

                  {searchMutation.data && (
                    <Card size="small" title={`搜索结果 · ${searchMutation.data.provider}`}>
                      <Space direction="vertical" size="large" style={{ width: '100%' }}>
                        <Typography.Text type="secondary">实际检索词：{searchMutation.data.query_used}</Typography.Text>
                        {searchMutation.data.message && <Alert type="warning" showIcon message={searchMutation.data.message} />}
                        {searchMutation.data.results.map((result) => (
                          <Card key={result.url} size="small">
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                              <Typography.Text strong>{result.title}</Typography.Text>
                              <Space wrap>
                                <Tag>{result.source_site || '未知站点'}</Tag>
                                {result.published_date && <Tag>{result.published_date}</Tag>}
                                {typeof result.score === 'number' && <Tag color="blue">score {result.score.toFixed(2)}</Tag>}
                              </Space>
                              <Typography.Paragraph style={{ marginBottom: 0 }}>{result.snippet || '无摘要'}</Typography.Paragraph>
                              <Typography.Link href={result.url} target="_blank" rel="noreferrer">{result.url}</Typography.Link>
                              <Space>
                                <Button
                                  type="primary"
                                  loading={importWebMutation.isPending}
                                  disabled={!result.raw_content && !result.snippet}
                                  onClick={() => handleImportSearchResult(result)}
                                >
                                  导入为面经
                                </Button>
                                <Typography.Text type="secondary">
                                  正文长度：{(result.raw_content || result.snippet).length} 字符
                                </Typography.Text>
                              </Space>
                            </Space>
                          </Card>
                        ))}
                      </Space>
                    </Card>
                  )}
                </Space>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}

function ExperienceMetaFields({ llmConfigs }: { llmConfigs: Array<{ id: string; display_name: string; is_default: boolean }> }) {
  return (
    <>
      <Form.Item name="target_school" label="目标院校">
        <Input placeholder="例如：浙江大学" />
      </Form.Item>
      <Form.Item name="target_major" label="目标专业">
        <Input placeholder="例如：计算机科学与技术" />
      </Form.Item>
      <Form.Item name="target_lab" label="目标实验室">
        <Input placeholder="可选" />
      </Form.Item>
      <Form.Item name="target_teacher" label="目标导师">
        <Input placeholder="可选" />
      </Form.Item>
      <Form.Item name="interview_type" label="面试类型">
        <Select options={['保研综合面', '保研科研面', '保研专业面'].map((item) => ({ label: item, value: item }))} />
      </Form.Item>
      <Form.Item name="year" label="年份">
        <InputNumber min={2000} max={2100} style={{ width: '100%' }} placeholder="例如：2025" />
      </Form.Item>
      <Form.Item name="llm_config_id" label="提取所用模型">
        <Select
          allowClear
          placeholder="默认模型"
          options={llmConfigs.map((item) => ({
            label: `${item.display_name}${item.is_default ? '（默认）' : ''}`,
            value: item.id,
          }))}
        />
      </Form.Item>
    </>
  );
}
