import { Button, Card, Empty, Popconfirm, Space, Table, Tag, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getApiError } from '../api/client';
import { deleteInterview, listInterviews } from '../api/interviews';
import type { InterviewListItem } from '../types/interview';

export function InterviewHistoryPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ['interviews'],
    queryFn: listInterviews,
  });
  const deleteMutation = useMutation({
    mutationFn: deleteInterview,
    onSuccess: () => {
      message.success('面试记录已删除');
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
    },
    onError: (deleteError) => message.error(getApiError(deleteError)),
  });

  if (error) {
    message.error(getApiError(error));
  }

  return (
    <div className="page-container">
      <div className="page-title-row">
        <Typography.Title level={2} style={{ margin: 0 }}>
          我的面试
        </Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/interviews/new')}>
          创建新面试
        </Button>
      </div>
      <Card>
        <Table<InterviewListItem>
          rowKey="id"
          loading={isLoading}
          dataSource={data ?? []}
          locale={{ emptyText: <Empty description="暂无面试记录" /> }}
          onRow={(record) => ({ onClick: () => navigate(`/interviews/${record.id}`) })}
          rowClassName="clickable-row"
          columns={[
            { title: '面试类型', dataIndex: 'type' },
            { title: '面试官风格', dataIndex: 'interviewer_style' },
            { title: '目标院校', dataIndex: 'target_school', render: (value) => value || '-' },
            { title: '目标专业', dataIndex: 'target_major', render: (value) => value || '-' },
            {
              title: '状态',
              dataIndex: 'status',
              render: (value) => <Tag color={value === 'FINISHED' ? 'green' : 'blue'}>{value}</Tag>,
            },
            { title: '总分', dataIndex: 'total_score', render: (value) => value ?? '-' },
            {
              title: '创建时间',
              dataIndex: 'created_at',
              render: (value) => new Date(value).toLocaleString(),
            },
            {
              title: '操作',
              render: (_, record) => (
                <Space>
                  <Button
                    type="link"
                    onClick={(event) => {
                      event.stopPropagation();
                      navigate(`/interviews/${record.id}`);
                    }}
                  >
                    进入
                  </Button>
                  {record.status === 'FINISHED' && (
                    <Button
                      type="link"
                      onClick={(event) => {
                        event.stopPropagation();
                        navigate(`/interviews/${record.id}/report`);
                      }}
                    >
                      报告
                    </Button>
                  )}
                  <Popconfirm
                    title="确认删除这条面试记录？"
                    description="删除后会同步移除对话消息和报告。"
                    okText="删除"
                    cancelText="取消"
                    okButtonProps={{ danger: true }}
                    onConfirm={(event) => {
                      event?.stopPropagation();
                      deleteMutation.mutate(record.id);
                    }}
                    onCancel={(event) => event?.stopPropagation()}
                  >
                    <Button
                      type="link"
                      danger
                      loading={deleteMutation.isPending}
                      onClick={(event) => event.stopPropagation()}
                    >
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
