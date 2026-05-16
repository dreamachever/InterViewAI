import { Button, Form, Input, Modal, Select, Space, Switch, Table, Tag, Typography, message } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { createLLMConfig, deleteLLMConfig, listLLMConfigs, setDefaultLLMConfig, testLLMConfig, updateLLMConfig } from '../api/llmConfigs';
import { getApiError } from '../api/client';
import type { LLMConfig, LLMConfigPayload, LLMProvider } from '../types/llmConfig';

const providerOptions: { label: string; value: LLMProvider }[] = [
  { label: 'Mock', value: 'mock' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '通义千问', value: 'tongyi' },
  { label: '豆包', value: 'doubao' },
  { label: 'OpenAI Compatible', value: 'custom_openai_compatible' },
];

export function LLMSettingsPage() {
  const [form] = Form.useForm<LLMConfigPayload>();
  const [editing, setEditing] = useState<LLMConfig | null>(null);
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({ queryKey: ['llm-configs'], queryFn: listLLMConfigs });

  const refresh = () => queryClient.invalidateQueries({ queryKey: ['llm-configs'] });
  const saveMutation = useMutation({
    mutationFn: (values: LLMConfigPayload) => (editing ? updateLLMConfig(editing.id, values) : createLLMConfig(values)),
    onSuccess: () => {
      message.success('模型配置已保存');
      setOpen(false);
      setEditing(null);
      form.resetFields();
      refresh();
    },
    onError: (error) => message.error(getApiError(error)),
  });
  const actionMutation = useMutation({
    mutationFn: async (action: { type: 'delete' | 'default' | 'test'; id: string }) => {
      if (action.type === 'delete') return deleteLLMConfig(action.id);
      if (action.type === 'default') return setDefaultLLMConfig(action.id);
      return testLLMConfig(action.id);
    },
    onSuccess: (result, action) => {
      if (action.type === 'test' && result && 'message' in result) {
        message.success(result.message);
      } else {
        message.success('操作成功');
      }
      refresh();
    },
    onError: (error) => message.error(getApiError(error)),
  });

  const openEditor = (record?: LLMConfig) => {
    setEditing(record || null);
    form.setFieldsValue(
      record
        ? {
            display_name: record.display_name,
            provider: record.provider,
            base_url: record.base_url,
            model: record.model,
            is_active: record.is_active,
            is_default: record.is_default,
          }
        : { provider: 'mock', is_active: true, is_default: !data.length }
    );
    setOpen(true);
  };

  return (
    <div className="page-container">
      <div className="page-title-row">
        <Typography.Title level={2}>模型设置</Typography.Title>
        <Button type="primary" onClick={() => openEditor()}>
          新增配置
        </Button>
      </div>
      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={data}
        columns={[
          { title: '名称', dataIndex: 'display_name' },
          { title: 'Provider', dataIndex: 'provider' },
          { title: '模型', dataIndex: 'model', render: (value) => value || '-' },
          { title: 'API Key', dataIndex: 'has_api_key', render: (value) => (value ? <Tag color="green">已配置</Tag> : <Tag>无</Tag>) },
          { title: '状态', render: (_, record) => <Space>{record.is_active ? <Tag color="blue">启用</Tag> : <Tag>停用</Tag>}{record.is_default && <Tag color="gold">默认</Tag>}</Space> },
          { title: '测试', render: (_, record) => record.last_test_status ? <Tag color={record.last_test_status === 'success' ? 'green' : 'red'}>{record.last_test_status}</Tag> : '-' },
          {
            title: '操作',
            render: (_, record) => (
              <Space>
                <Button size="small" onClick={() => openEditor(record)}>编辑</Button>
                <Button size="small" onClick={() => actionMutation.mutate({ type: 'test', id: record.id })}>测试</Button>
                <Button size="small" disabled={record.is_default} onClick={() => actionMutation.mutate({ type: 'default', id: record.id })}>设默认</Button>
                <Button size="small" danger onClick={() => actionMutation.mutate({ type: 'delete', id: record.id })}>删除</Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editing ? '编辑模型配置' : '新增模型配置'} open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()} confirmLoading={saveMutation.isPending}>
        <Form form={form} layout="vertical" onFinish={(values) => saveMutation.mutate(values)}>
          <Form.Item name="display_name" label="配置名称" rules={[{ required: true, message: '请输入配置名称' }]}>
            <Input placeholder="例如：我的 DeepSeek" />
          </Form.Item>
          <Form.Item name="provider" label="Provider" rules={[{ required: true, message: '请选择 Provider' }]}>
            <Select options={providerOptions} />
          </Form.Item>
          <Form.Item name="base_url" label="Base URL">
            <Input placeholder="OpenAI-compatible 接口地址，mock 可留空" />
          </Form.Item>
          <Form.Item name="model" label="模型">
            <Input placeholder="例如 deepseek-chat / gpt-4o-mini" />
          </Form.Item>
          <Form.Item name="api_key" label="API Key">
            <Input.Password placeholder={editing?.has_api_key ? '留空表示不修改已有 API Key' : 'mock 可留空'} />
          </Form.Item>
          <Form.Item name="is_active" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="is_default" label="设为默认" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
