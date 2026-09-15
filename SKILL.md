---
name: ark-stg-debug-helper
description: "火山方舟 stg 环境调试与排错助手。提供 stg 环境访问配置（小流量头 x-maas-env）、MCP 连接排错、模型参数验证方法、常见 HTTP 错误（401/403/500）排查指南。当用户遇到火山方舟 stg 环境无法访问、MCP 连接失败、凭证校验错误、模型参数不生效、小流量头配置等问题时使用本 Skill。"
---

# 火山方舟 stg 环境调试助手

## Overview

本 Skill 用于帮助开发者排查和解决火山方舟（Volcano Ark）stg 环境中的常见问题，包括环境访问配置、MCP 连接、模型参数验证、HTTP 错误排查等。

## 快速诊断流程

遇到问题时，按以下顺序排查：

1. **确认环境**：检查访问的是否为 stg 环境（URL 中包含 `ark-stg`）
2. **检查小流量头**：确认请求头 `x-maas-env` 已正确配置并启用
3. **检查凭证**：确认 API Key / Access Key 有效且有权限
4. **检查网络**：确认网络可达，无代理或防火墙拦截
5. **查看错误码**：根据返回的 HTTP 状态码定位具体问题

## stg 环境访问配置

### 小流量头配置

访问火山方舟 stg 环境必须携带小流量头，否则可能返回 401 或 403。

| 配置项 | 值 |
|---|---|
| Header Name | `x-maas-env` |
| Header Value | `ma-0908`（或分配给你的具体环境标识） |
| 启用方式 | 浏览器扩展（ModHeader 等）或代码中手动添加请求头 |

### 浏览器端配置（ModHeader）

1. 安装 ModHeader 扩展
2. 添加 Request Header：`x-maas-env` = `ma-0908`
3. 确保开关处于启用状态
4. 刷新 stg 环境页面

### 代码端配置（curl 示例）

```bash
curl -X POST "https://ark-stg.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "x-maas-env: ma-0908" \
  -d '{
    "model": "your-endpoint-id",
    "messages": [{"role": "user", "content": "hello"}]
  }'
```

## MCP 连接排错

### 常见错误及解决方案

| 错误信息 | 可能原因 | 解决方案 |
|---|---|---|
| `rejected credentials at probe (status 401)` | API Key 错误或过期 | 重新生成 API Key，确认无多余空格 |
| `status 403` | 账号无权限访问该服务 | 联系管理员授权，确认服务已开通 |
| `connection refused` / `timeout` | MCP Server 地址错误或网络不通 | 检查 URL 是否正确，确认服务已启动 |
| `tool not found` | MCP 工具未正确加载 | 检查 MCP Server 的工具列表，确认工具名称匹配 |

### MCP 验证步骤

1. **验证连接**：在控制台查看 MCP Server 状态是否为"已连接"
2. **验证工具列表**：确认 MCP Server 暴露的工具已正确加载
3. **验证工具调用**：触发一个 MCP 工具调用，检查请求和响应
4. **验证凭证**：使用正确的 API Key，确认无 401 错误

详细的 MCP 配置和排错指南见 [references/mcp-troubleshooting.md](references/mcp-troubleshooting.md)。

## 模型参数验证

### temperature 参数验证

temperature 控制输出随机性，取值范围 [0, 2]，默认值 1。

**验证方法：**
1. 设置 `temperature=0`，用相同 prompt 调用 5 次，记录回答
2. 设置 `temperature=1.5`，用相同 prompt 调用 5 次，记录回答
3. 对比：temperature=0 时回答高度一致，temperature=1.5 时回答明显不同

**注意事项：**
- 不要同时调整 top_p，两个参数都会影响随机性
- 使用有创作空间的 prompt（如"写一句话"），不要用有唯一答案的问题
- 至少调用 3 次，建议 5 次

详细的参数验证方法见 [references/model-params-validation.md](references/model-params-validation.md)。

## 常见 HTTP 错误排查

### 401 Unauthorized

- **原因**：凭证无效（API Key 错误、过期、格式不对）
- **排查**：
  1. 确认 API Key 完整复制，无多余空格或换行
  2. 确认 Key 未过期、未被吊销
  3. 确认使用了正确的认证方式（Bearer Token / AK/SK 签名）
  4. 检查是否需要额外的小流量头

### 403 Forbidden

- **原因**：凭证有效但无权限访问该资源
- **排查**：
  1. 确认账号已开通对应服务
  2. 确认 IAM 策略包含所需权限
  3. 确认访问的区域/项目正确
  4. 企业账号需确认管理员已授权

### 500 Internal Server Error

- **原因**：服务端内部错误
- **排查**：
  1. 记录 RequestId，提交工单给技术支持
  2. 检查请求体格式是否正确
  3. 稍后重试，可能是临时故障

## 辅助脚本

本 Skill 包含以下辅助脚本，位于 `scripts/` 目录：

- `validate_temperature.py`：自动化验证 temperature 参数是否生效
- `check_mcp_connection.py`：检查 MCP Server 连接状态和工具列表

使用方法见各脚本顶部注释。

## Resources

### references/
- `mcp-troubleshooting.md` - MCP 连接详细排错指南
- `model-params-validation.md` - 模型参数（temperature/top_p/max_tokens）验证方法
- `http-errors-guide.md` - 常见 HTTP 错误码排查手册

### scripts/
- `validate_temperature.py` - temperature 参数自动化验证脚本
- `check_mcp_connection.py` - MCP 连接检测脚本

### assets/
- `modheader-config-example.json` - ModHeader 扩展配置示例（可直接导入）
