import { Button, Card, Col, Empty, Popconfirm, Row, Space, Tag, Typography, Upload, message } from 'antd';
import type { UploadProps } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { deleteResume, listResumes, updateResume, uploadResume } from '../api/resumes';
import { getApiError } from '../api/client';
import type { Resume } from '../types/resume';

const parseStatusColor: Record<string, string> = {
  success: 'green',
  pending: 'blue',
  failed: 'red',
};

const analysisStatusColor: Record<string, string> = {
  success: 'green',
  none: 'default',
  failed: 'red',
  outdated: 'orange',
};

const analysisStatusLabel: Record<string, string> = {
  success: '已分析',
  none: '未分析',
  failed: '分析失败',
  outdated: '需重新分析',
};

function formatSize(size: number) {
  return `${(size / 1024 / 1024).toFixed(2)} MB`;
}

export function ResumeCenterPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['resumes'], queryFn: listResumes });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ['resumes'] });

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: (resume) => {
      message.success('简历上传并解析成功');
      refresh();
      navigate(`/resumes/${resume.id}`);
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const actionMutation = useMutation({
    mutationFn: async (action: { type: 'delete' | 'default'; resume: Resume }) => {
      if (action.type === 'delete') return deleteResume(action.resume.id);
      return updateResume(action.resume.id, { is_default: true });
    },
    onSuccess: () => {
      message.success('操作成功');
      refresh();
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const customRequest: UploadProps['customRequest'] = (options) => {
    const file = options.file as File;
    uploadMutation.mutate(file, {
      onSuccess: () => options.onSuccess?.({}, file),
      onError: (error) => options.onError?.(error as Error),
    });
  };

  const uploader = (
    <Upload accept="application/pdf,.pdf" showUploadList={false} customRequest={customRequest}>
      <Button type="primary" loading={uploadMutation.isPending}>上传 PDF 简历</Button>
    </Upload>
  );

  return (
    <div className="page-container">
      <div className="page-title-row">
        <Typography.Title level={2}>简历中心</Typography.Title>
        {uploader}
      </div>

      {!isLoading && data.length === 0 ? (
        <Card>
          <Empty
            description={
              <Space direction="vertical" size={4}>
                <Typography.Text>还没有简历。上传一份 PDF，系统会解析文本并生成保研面试向的 AI 诊断。</Typography.Text>
                <Typography.Text type="secondary">建议上传可复制文字的 PDF，扫描件暂不支持 OCR。</Typography.Text>
              </Space>
            }
          >
            {uploader}
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {data.map((resume) => (
            <Col xs={24} md={12} xl={8} key={resume.id}>
              <Card
                title={<Typography.Text ellipsis>{resume.title}</Typography.Text>}
                extra={resume.is_default ? <Tag color="gold">默认</Tag> : null}
                actions={[
                  <Button type="link" onClick={() => navigate(`/resumes/${resume.id}`)}>查看</Button>,
                  <Button type="link" disabled={resume.is_default} onClick={() => actionMutation.mutate({ type: 'default', resume })}>设默认</Button>,
                  <Popconfirm title="确认删除这份简历？" description="删除后文件和诊断记录都会移除。" onConfirm={() => actionMutation.mutate({ type: 'delete', resume })}>
                    <Button type="link" danger>删除</Button>
                  </Popconfirm>,
                ]}
              >
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <Typography.Text type="secondary" ellipsis>{resume.original_filename}</Typography.Text>
                  <Typography.Text type="secondary">{formatSize(resume.file_size)}</Typography.Text>
                  <Space wrap>
                    <Tag color={parseStatusColor[resume.parse_status] || 'default'}>解析：{resume.parse_status}</Tag>
                    <Tag color={analysisStatusColor[resume.analysis_status] || 'default'}>分析：{analysisStatusLabel[resume.analysis_status] || resume.analysis_status}</Tag>
                    {typeof resume.latest_overall_score === 'number' && <Tag color="blue">AI 分数：{resume.latest_overall_score}</Tag>}
                  </Space>
                  {resume.high_risks.length > 0 && (
                    <div>
                      <Typography.Text type="secondary">高风险点</Typography.Text>
                      <Space wrap style={{ marginTop: 6 }}>
                        {resume.high_risks.map((risk) => <Tag color="red" key={risk}>{risk}</Tag>)}
                      </Space>
                    </div>
                  )}
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
