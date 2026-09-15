# 常见 HTTP 错误码排查手册

## 概述

调用火山方舟 API 或访问控制台时，可能遇到各种 HTTP 错误码。本手册列出常见错误码的原因和排查方法。

## 4xx 客户端错误

### 400 Bad Request

**原因**：请求格式错误，参数不合法

**常见场景**：
- 请求体 JSON 格式错误
- 缺少必填参数
- 参数取值超出范围（如 temperature=3）
- model/endpoint_id 不存在

**排查方法**：
1. 检查请求体是否为合法 JSON
2. 对照 API 文档检查必填参数
3. 检查参数取值范围
4. 确认 endpoint_id 正确且已创建

### 401 Unauthorized

**原因**：凭证无效，无法通过身份认证

**常见场景**：
- API Key 错误、过期或被吊销
- API Key 复制时带有多余空格
- 认证方式错误（应该用 Bearer Token 却用了 AK/SK）
- stg 环境缺少小流量头 `x-maas-env`

**排查方法**：
1. 重新生成 API Key，确保完整复制
2. 检查 Authorization header 格式：`Bearer <API_KEY>`
3. 确认 Key 未过期（在控制台查看状态）
4. stg 环境确认已配置小流量头
5. 使用 curl 直接测试，排除代码问题

**curl 测试示例**：
```bash
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"model":"ep-xxxx","messages":[{"role":"user","content":"hi"}]}'
```

### 403 Forbidden

**原因**：凭证有效但无权限访问该资源

**常见场景**：
- 账号未开通对应服务
- IAM 用户/角色缺少所需权限策略
- 企业账号未被管理员授权
- 访问了无权限的区域或项目
- API 网关侧的应用未授权访问该 API 分组

**排查方法**：
1. 确认服务已开通（在控制台查看服务状态）
2. 检查 IAM 策略是否包含 `MachineLearning` 相关权限
3. 企业账号联系管理员确认授权
4. 确认访问的区域（region）正确
5. API 网关场景：确认应用已绑定到对应 API 分组

### 404 Not Found

**原因**：请求的资源不存在

**常见场景**：
- URL 路径错误
- endpoint_id 不存在或已删除
- API 版本不正确
- MCP Server URL 缺少 `/mcp` 后缀

**排查方法**：
1. 对照文档检查 URL 路径
2. 确认 endpoint_id 正确且存在
3. 检查 API 版本号（如 `/api/v3/`）
4. MCP 场景确认 URL 以 `/mcp` 结尾

### 429 Too Many Requests

**原因**：请求频率超过限流阈值

**常见场景**：
- 短时间内发送过多请求
- 并发数超过限制
- 账号的 QPS 配额不足

**排查方法**：
1. 降低请求频率，添加重试间隔
2. 检查账号的 QPS/并发配额
3. 实现指数退避重试机制
4. 联系技术支持提升配额

## 5xx 服务端错误

### 500 Internal Server Error

**原因**：服务端内部错误

**排查方法**：
1. 记录 RequestId，提交工单
2. 检查请求体是否有异常内容
3. 稍后重试（可能是临时故障）
4. 确认是否为已知的服务端问题

### 502 Bad Gateway

**原因**：网关从上游服务收到无效响应

**排查方法**：
1. 稍后重试
2. 检查请求是否过大
3. 确认服务状态是否正常

### 503 Service Unavailable

**原因**：服务暂时不可用

**排查方法**：
1. 稍后重试
2. 检查服务状态页
3. 确认是否在维护时间窗口

### 504 Gateway Timeout

**原因**：网关等待上游响应超时

**常见场景**：
- 模型推理时间过长
- 请求的 max_tokens 过大
- MCP Server 响应超时

**排查方法**：
1. 减少 max_tokens
2. 简化 prompt，降低推理复杂度
3. MCP 场景检查 MCP Server 响应速度
4. 增加客户端超时时间

## 错误排查通用流程

1. **记录 RequestId**：每次错误响应中都包含 RequestId，这是排查的关键
2. **复现问题**：用 curl 或最小化代码复现，排除业务代码干扰
3. **检查凭证**：确认 API Key 有效且有权限
4. **检查参数**：对照文档检查所有参数
5. **检查网络**：确认网络可达，无代理干扰
6. **提交工单**：带上 RequestId 和复现步骤，联系技术支持

## 工单提交模板

```
问题描述：[简要描述遇到的问题]
RequestId：[从错误响应中获取]
请求时间：[YYYY-MM-DD HH:MM:SS]
请求 URL：[完整的 API 端点]
请求体：[脱敏后的请求体]
错误响应：[完整的错误响应]
已尝试的排查：[已经做过哪些排查操作]
```
