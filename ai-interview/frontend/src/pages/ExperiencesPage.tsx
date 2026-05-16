import { Button, Card, Empty, Form, Input, Popconfirm, Select, Space, Table, Tag, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { deleteExperience, extractExperience, listExperiences } from '../api/experiences';
import { getApiError } from '../api/client';
import type { ExperienceListItem } from '../types/experience';

const statusColorMap = { success: 'green', pending: 'gold', failed: 'red' } as const;

export function ExperiencesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const filters = Form.useWatch([], form) ?? {};
  const queryFilters = useMemo(
    () => ({
      target_school: filters.target_school || undefined,
      target_major: filters.target_major || undefined,
      interview_type: filters.interview_type || undefined,
      source_type: filters.source_type || undefined,
    }),
    [filters.interview_type, filters.source_type, filters.target_major, filters.target_school],
  );
  const { data = [], isLoading, error } = useQuery({
    queryKey: ['experiences', queryFilters],
    queryFn: () => listExperiences(queryFilters),
  });
  const deleteMutation = useMutation({
    mutationFn: deleteExperience,
    onSuccess: async () => {
      message.success('面经已删除');
      await queryClient.invalidateQueries({ queryKey: ['experiences'] });
    },
    onError: (deleteError) => message.error(getApiError(deleteError)),
  });
  const extractMutation = useMutation({
    mutationFn: (experienceId: string) => extractExperience(experienceId),
    onSuccess: async () => {
      message.success('已重新提取面经要点');
      await queryClient.invalidateQueries({ queryKey: ['experiences'] });
    },
    onError: (extractError) => message.error(getApiError(extractError)),
  });

  if (error) {
    message.error(getApiError(error));
  }

  return (
    <div className="page-container">
      <div className="page-title-row">
        <Typography.Title level={2} style={{ margin: 0 }}>面经库</Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/experiences/new')}>
          新增面经
        </Button>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline">
          <Form.Item name="target_school" label="学校">
            <Input placeholder="筛选学校" allowClear />
          </Form.Item>
          <Form.Item name="target_major" label="专业">
            <Input placeholder="筛选专业" allowClear />
          </Form.Item>
          <Form.Item name="interview_type" label="面试类型">
            <Select
              allowClear
              style={{ width: 160 }}
              options={['保研综合面', '保研科研面', '保研专业面'].map((item) => ({ label: item, value: item }))}
            />
          </Form.Item>
          <Form.Item name="source_type" label="来源">
            <Select
              allowClear
              style={{ width: 140 }}
              options={['manual', 'web', 'mock'].map((item) => ({ label: item, value: item }))}
            />
          </Form.Item>
        </Form>
      </Card>

      <Card>
        <Table<ExperienceListItem>
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          locale={{ emptyText: <Empty description="暂无面经数据" /> }}
          onRow={(record) => ({ onClick: () => navigate(`/experiences/${record.id}`) })}
          rowClassName="clickable-row"
          columns={[
            { title: '标题', dataIndex: 'title' },
            { title: '学校', dataIndex: 'target_school', render: (value) => value || '-' },
            { title: '专业', dataIndex: 'target_major', render: (value) => value || '-' },
            { title: '年份', dataIndex: 'year', render: (value) => value || '-' },
            { title: '来源', dataIndex: 'source_type' },
            {
              title: '提取状态',
              dataIndex: 'extract_status',
              render: (value: keyof typeof statusColorMap) => <Tag color={statusColorMap[value] || 'default'}>{value}</Tag>,
            },
            { title: '问题数量', dataIndex: 'real_question_count' },
            {
              title: '重点方向',
              dataIndex: 'focus_preview',
              render: (value: string[]) => value.length ? <Space wrap>{value.map((item) => <Tag key={item}>{item}</Tag>)}</Space> : '-',
            },
            {
              title: '操作',
              render: (_, record) => (
                <Space>
                  <Button type="link" onClick={(event) => { event.stopPropagation(); navigate(`/experiences/${record.id}`); }}>查看</Button>
                  <Button type="link" loading={extractMutation.isPending} onClick={(event) => { event.stopPropagation(); extractMutation.mutate(record.id); }}>
                    重新提取
                  </Button>
                  <Popconfirm
                    title="确认删除这条面经？"
                    description="会同步删除 AI 提取结果以及关联关系。"
                    okText="删除"
                    cancelText="取消"
                    okButtonProps={{ danger: true }}
                    onConfirm={(event) => {
                      event?.stopPropagation();
                      deleteMutation.mutate(record.id);
                    }}
                    onCancel={(event) => event?.stopPropagation()}
                  >
                    <Button type="link" danger loading={deleteMutation.isPending} onClick={(event) => event.stopPropagation()}>
                      删除
                    </Button>
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
