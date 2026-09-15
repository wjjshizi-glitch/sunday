# MCP 连接详细排错指南

## 概述

MCP（Model Context Protocol）是用于扩展模型能力的协议。连接 MCP Server 时常见的问题包括凭证错误、网络不通、工具加载失败等。

## 连接流程

1. **配置 MCP Server**：填写 URL、认证方式（API Key / Bearer Token / 无认证）
2. **探测连接**：平台向 MCP Server 发送探测请求，验证凭证和连通性
3. **加载工具列表**：连接成功后，加载 MCP Server 暴露的工具列表
4. **工具调用**：在对话中触发工具调用

## 错误码对照表

| 状态码 | 错误信息 | 原因 | 解决方案 |
|---|---|---|---|
| 401 | rejected credentials at probe | API Key 无效或格式错误 | 重新生成 Key，确认无空格 |
| 403 | forbidden | 账号无权限 | 联系管理员授权 |
| 404 | not found | URL 路径错误 | 检查 URL 是否包含 `/mcp` 后缀 |
| 500 | internal error | MCP Server 内部错误 | 检查 MCP Server 日志 |
| timeout | request timeout | 网络不通或服务未启动 | 检查网络和服务状态 |

## 分步排查

### 第 1 步：验证 URL 可达性

```bash
curl -v "https://your-mcp-server.com/mcp"
```

- 如果返回连接拒绝：检查服务是否启动、端口是否正确
- 如果返回 DNS 错误：检查域名是否正确
- 如果返回 401/403：URL 可达，问题在凭证或权限

### 第 2 步：验证凭证

```bash
curl -X POST "https://your-mcp-server.com/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

- 返回 200 且包含 `serverInfo`：凭证正确
- 返回 401：API Key 错误
- 返回 403：Key 有效但无权限

### 第 3 步：验证工具列表

```bash
curl -X POST "https://your-mcp-server.com/mcp/tools/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

- 返回工具列表：工具加载正常
- 返回空列表：MCP Server 未暴露任何工具
- 返回错误：检查 MCP Server 实现

### 第 4 步：验证工具调用

选择一个工具，发送调用请求：

```bash
curl -X POST "https://your-mcp-server.com/mcp/tools/call" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"name":"tool_name","arguments":{"param1":"value1"}}'
```

- 返回正常结果：工具调用正常
- 返回参数错误：检查工具参数定义
- 返回执行错误：检查工具实现逻辑

## 火山引擎 API 网关 MCP 特别注意

如果 MCP Server 部署在火山引擎 API 网关上（域名包含 `apigateway-cn-beijing.volceapi.com`）：

1. **确认 API 分组**：你的 Key 需要绑定到该 API 分组
2. **确认应用授权**：在 API 网关控制台，确认应用已授权访问该 API
3. **确认环境**：stg 环境可能需要额外的小流量头
4. **确认地域**：网关在 `cn-beijing`，确认请求未被代理篡改

## 常见陷阱

1. **API Key 有空格**：复制时容易带上前后空格，导致 401
2. **URL 缺少 /mcp 后缀**：MCP 端点通常需要 `/mcp` 路径
3. **混淆 AK/SK 和 API Key**：API 网关可能需要 AK/SK 签名而非简单的 Bearer Token
4. **小流量头未启用**：stg 环境必须携带 `x-maas-env` 请求头
5. **工具名称不匹配**：调用时工具名称必须与 MCP Server 暴露的完全一致（大小写敏感）
