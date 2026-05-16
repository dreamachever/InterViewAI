import { Alert, Button, Card, Form, Input, Progress, Radio, Select, Space, Switch, Tag, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { listExperiences } from '../../api/experiences';
import { listLLMConfigs } from '../../api/llmConfigs';
import { listResumes } from '../../api/resumes';
import type { InterviewConfig } from '../../types/interview';
import type { Resume } from '../../types/resume';

const interviewTypes = ['保研综合面', '保研科研面', '保研专业面'];
const interviewerStyles = ['和善导师', '严谨导师', '压力导师', '专业导师', '科研导师'];

interface Props {
  loading?: boolean;
  onSubmit: (values: InterviewConfig) => void;
}

interface FormValues extends InterviewConfig {
  resume_source: 'existing' | 'paste';
  use_experiences: 'none' | 'selected';
}

export function InterviewConfigForm({ loading, onSubmit }: Props) {
  const [form] = Form.useForm<FormValues>();
  const resumeSource = Form.useWatch('resume_source', form);
  const useExperiences = Form.useWatch('use_experiences', form);
  const selectedResumeId = Form.useWatch('resume_id', form);
  const selectedExperienceIds = Form.useWatch('experience_ids', form) ?? [];
  const { data: resumes = [] } = useQuery({ queryKey: ['resumes'], queryFn: listResumes });
  const { data: llmConfigs = [] } = useQuery({ queryKey: ['llm-configs'], queryFn: listLLMConfigs });
  const { data: experiences = [] } = useQuery({ queryKey: ['experiences', 'selectable'], queryFn: () => listExperiences() });
  const defaultResume = resumes.find((item) => item.is_default);
  const defaultConfig = llmConfigs.find((item) => item.is_default);
  const selectedResume = resumes.find((item) => item.id === selectedResumeId);
  const selectedExperiences = experiences.filter((item) => selectedExperienceIds.includes(item.id));

  useEffect(() => {
    if (defaultResume && !form.getFieldValue('resume_id')) {
      form.setFieldsValue({ resume_source: 'existing', resume_id: defaultResume.id });
    }
    if (defaultConfig && !form.getFieldValue('llm_config_id')) {
      form.setFieldsValue({ llm_config_id: defaultConfig.id });
    }
  }, [defaultConfig, defaultResume, form]);

  const handleFinish = (values: FormValues) => {
    const payload: InterviewConfig = {
      type: values.type,
      interviewer_style: values.interviewer_style,
      target_school: values.target_school || null,
      target_major: values.target_major || null,
      llm_config_id: values.llm_config_id || null,
      voice_enabled: Boolean(values.voice_enabled),
      experience_ids: values.use_experiences === 'selected' ? values.experience_ids ?? [] : [],
    };
    if (values.resume_source === 'existing') {
      payload.resume_id = values.resume_id || defaultResume?.id || null;
    } else {
      payload.resume_text = values.resume_text || '';
    }
    onSubmit(payload);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      initialValues={{
        type: '保研科研面',
        interviewer_style: '严谨导师',
        resume_source: defaultResume ? 'existing' : 'paste',
        resume_id: defaultResume?.id,
        llm_config_id: defaultConfig?.id,
        voice_enabled: false,
        use_experiences: 'none',
        experience_ids: [],
      }}
    >
      <Form.Item name="type" label="面试类型" rules={[{ required: true, message: '请选择面试类型' }]}>
        <Select options={interviewTypes.map((item) => ({ label: item, value: item }))} />
      </Form.Item>
      <Form.Item name="interviewer_style" label="面试官风格" rules={[{ required: true, message: '请选择面试官风格' }]}>
        <Select options={interviewerStyles.map((item) => ({ label: item, value: item }))} />
      </Form.Item>
      <Form.Item name="target_school" label="目标院校">
        <Input placeholder="例如：浙江大学" />
      </Form.Item>
      <Form.Item name="target_major" label="目标专业">
        <Input placeholder="例如：计算机科学与技术" />
      </Form.Item>
      <Form.Item name="llm_config_id" label="模型配置">
        <Select
          allowClear
          placeholder="系统默认模型"
          options={llmConfigs.map((item) => ({
            label: `${item.display_name}${item.is_default ? '（默认）' : ''}`,
            value: item.id,
          }))}
        />
      </Form.Item>
      <Form.Item name="resume_source" label="简历来源">
        <Radio.Group>
          <Radio.Button value="existing" disabled={!resumes.length}>选择已有简历</Radio.Button>
          <Radio.Button value="paste">粘贴简历文本</Radio.Button>
        </Radio.Group>
      </Form.Item>
      <Form.Item name="voice_enabled" label="语音面试模式" valuePropName="checked">
        <Switch checkedChildren="开启" unCheckedChildren="关闭" />
      </Form.Item>
      <Typography.Paragraph type="secondary">
        开启后，AI 面试官会自动朗读问题；你也可以用麦克风把回答转成文字后再提交。
      </Typography.Paragraph>
      {resumeSource === 'existing' && (
        <>
          <Form.Item name="resume_id" label="选择简历" rules={[{ required: true, message: '请选择一份简历' }]}>
            <Select
              placeholder="选择简历"
              options={resumes.map((item) => ({
                label: `${item.title}${item.is_default ? '（默认）' : ''}`,
                value: item.id,
              }))}
            />
          </Form.Item>
          {selectedResume && <SelectedResumePreview resume={selectedResume} />}
        </>
      )}
      {resumeSource !== 'existing' && (
        <Form.Item name="resume_text" label="简历文本" rules={[{ required: true, min: 10, message: '请粘贴至少 10 个字符的简历文本' }]}>
          <Input.TextArea rows={10} placeholder="粘贴你的简历文本、课程背景、科研经历、竞赛经历或项目经历..." />
        </Form.Item>
      )}
      {!resumes.length && (
        <Typography.Paragraph type="secondary">你还没有上传 PDF 简历，也可以先粘贴文本创建面试。</Typography.Paragraph>
      )}

      <Card size="small" title="面经增强" style={{ marginBottom: 16 }}>
        <Form.Item name="use_experiences" label="是否使用面经">
          <Radio.Group>
            <Radio value="none">不使用面经</Radio>
            <Radio value="selected">选择已有面经</Radio>
          </Radio.Group>
        </Form.Item>
        {useExperiences === 'selected' && (
          <>
            <Form.Item
              name="experience_ids"
              label="选择面经（最多 3 条）"
              rules={[{ validator: (_, value: string[] = []) => value.length <= 3 ? Promise.resolve() : Promise.reject(new Error('最多选择 3 条面经')) }]}
            >
              <Select
                mode="multiple"
                maxCount={3}
                placeholder="按学校、专业、年份选择面经"
                optionFilterProp="label"
                options={experiences.map((item) => ({
                  label: `${item.title} ｜ ${item.target_school || '未填写院校'} ｜ ${item.target_major || '未填写专业'} ｜ ${item.year || '未知年份'}`,
                  value: item.id,
                }))}
              />
            </Form.Item>
            <Space direction="vertical" style={{ width: '100%' }}>
              {selectedExperiences.map((item) => (
                <Card key={item.id} size="small">
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Typography.Text strong>{item.title}</Typography.Text>
                    <Space wrap>
                      <Tag>{item.target_school || '未填写院校'}</Tag>
                      <Tag>{item.target_major || '未填写专业'}</Tag>
                      <Tag>{item.interview_type || '未填写类型'}</Tag>
                      <Tag>{item.year || '未知年份'}</Tag>
                    </Space>
                    <Typography.Text type="secondary">高频/真实问题数：{item.real_question_count}</Typography.Text>
                    {item.focus_preview.length > 0 && (
                      <Space wrap>{item.focus_preview.map((point) => <Tag color="blue" key={point}>{point}</Tag>)}</Space>
                    )}
                    {item.high_risk_preview.length > 0 && (
                      <Space wrap>{item.high_risk_preview.map((point) => <Tag color="red" key={point}>{point}</Tag>)}</Space>
                    )}
                  </Space>
                </Card>
              ))}
              {!experiences.length && (
                <Alert type="info" showIcon message="你还没有面经数据，可以先去面经库新增，再回来创建增强面试。" />
              )}
            </Space>
          </>
        )}
      </Card>

      <Space direction="vertical" style={{ width: '100%' }}>
        <Button type="primary" htmlType="submit" loading={loading} block size="large">开始面试</Button>
      </Space>
    </Form>
  );
}

function SelectedResumePreview({ resume }: { resume: Resume }) {
  const shouldWarn = resume.analysis_status === 'failed' || resume.analysis_status === 'outdated';
  return (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Space wrap>
          <Tag color={resume.parse_status === 'success' ? 'green' : 'red'}>解析：{resume.parse_status}</Tag>
          <Tag color={resume.analysis_status === 'success' ? 'green' : resume.analysis_status === 'outdated' ? 'orange' : resume.analysis_status === 'failed' ? 'red' : 'default'}>
            分析：{resume.analysis_status}
          </Tag>
        </Space>
        {typeof resume.latest_overall_score === 'number' ? (
          <div>
            <Typography.Text type="secondary">AI 简历分数</Typography.Text>
            <Progress percent={resume.latest_overall_score} size="small" />
          </div>
        ) : (
          <Typography.Text type="secondary">这份简历还没有 AI 分数。</Typography.Text>
        )}
        {resume.high_risks.length > 0 && (
          <Space wrap>
            {resume.high_risks.slice(0, 3).map((risk) => <Tag color="red" key={risk}>{risk}</Tag>)}
          </Space>
        )}
        {shouldWarn && (
          <Alert
            type="warning"
            showIcon
            message={resume.analysis_status === 'failed' ? '这份简历上次分析失败，仍可继续创建面试。' : '这份简历的分析可能已过期，仍可继续创建面试。'}
          />
        )}
      </Space>
    </Card>
  );
}
