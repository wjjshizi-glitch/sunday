#!/usr/bin/env python3
"""
MCP Server 连接检测脚本

用法:
    python check_mcp_connection.py --url https://your-mcp-server.com/mcp --api-key YOUR_KEY

可选参数:
    --timeout      请求超时时间（秒，默认: 10）
    --tool-name    指定要测试调用的工具名称（不指定则只列工具）
    --tool-args    工具调用参数（JSON 格式）
"""

import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库，请运行: pip install requests")
    sys.exit(1)


def check_url_reachable(url, timeout):
    """检查 URL 是否可达"""
    print(f"[1/4] 检查 URL 可达性: {url}")
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
        print(f"  ✅ URL 可达，状态码: {resp.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 连接失败：无法建立连接，请检查服务是否启动、URL 是否正确")
        return False
    except requests.exceptions.Timeout:
        print(f"  ❌ 连接超时：服务响应超过 {timeout} 秒")
        return False
    except Exception as e:
        print(f"  ❌ 连接异常: {str(e)}")
        return False


def check_credentials(url, api_key, timeout):
    """检查凭证是否有效"""
    print(f"\n[2/4] 检查凭证有效性")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-checker", "version": "1.0.0"}
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            server_info = data.get("result", {}).get("serverInfo", {})
            print(f"  ✅ 凭证有效！Server: {server_info.get('name', 'unknown')} v{server_info.get('version', 'unknown')}")
            return True
        elif resp.status_code == 401:
            print(f"  ❌ 凭证无效（401）：API Key 错误或过期")
            print(f"     响应: {resp.text[:200]}")
            return False
        elif resp.status_code == 403:
            print(f"  ❌ 无权限（403）：凭证有效但无权访问该资源")
            print(f"     响应: {resp.text[:200]}")
            return False
        else:
            print(f"  ⚠️  非预期状态码: {resp.status_code}")
            print(f"     响应: {resp.text[:200]}")
            return resp.status_code < 500
    except Exception as e:
        print(f"  ❌ 请求异常: {str(e)}")
        return False


def list_tools(url, api_key, timeout):
    """列出 MCP Server 的工具"""
    print(f"\n[3/4] 获取工具列表")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # 先初始化
    init_payload = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "mcp-checker", "version": "1.0.0"}}
    }
    try:
        requests.post(url, headers=headers, json=init_payload, timeout=timeout)
    except:
        pass

    # 发送 initialized 通知
    notif_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    try:
        requests.post(url, headers=headers, json=notif_payload, timeout=timeout)
    except:
        pass

    # 列出工具
    list_payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    try:
        resp = requests.post(url, headers=headers, json=list_payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            tools = data.get("result", {}).get("tools", [])
            print(f"  ✅ 成功获取 {len(tools)} 个工具:")
            for tool in tools:
                desc = tool.get("description", "无描述")[:60]
                print(f"    - {tool.get('name', 'unknown')}: {desc}")
            return tools
        else:
            print(f"  ❌ 获取工具列表失败，状态码: {resp.status_code}")
            print(f"     响应: {resp.text[:200]}")
            return []
    except Exception as e:
        print(f"  ❌ 请求异常: {str(e)}")
        return []


def test_tool_call(url, api_key, timeout, tool_name, tool_args):
    """测试工具调用"""
    print(f"\n[4/4] 测试工具调用: {tool_name}")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": tool_args or {}}
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", {})
            content = result.get("content", [])
            print(f"  ✅ 工具调用成功！")
            for item in content:
                if item.get("type") == "text":
                    print(f"  结果: {item.get('text', '')[:300]}")
            return True
        else:
            print(f"  ❌ 工具调用失败，状态码: {resp.status_code}")
            print(f"     响应: {resp.text[:300]}")
            return False
    except Exception as e:
        print(f"  ❌ 请求异常: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MCP Server 连接检测工具")
    parser.add_argument("--url", required=True, help="MCP Server URL（通常以 /mcp 结尾）")
    parser.add_argument("--api-key", default=None, help="API Key（Bearer Token）")
    parser.add_argument("--timeout", type=int, default=10, help="请求超时时间（秒）")
    parser.add_argument("--tool-name", default=None, help="要测试调用的工具名称")
    parser.add_argument("--tool-args", default=None, help="工具调用参数（JSON 字符串）")
    args = parser.parse_args()

    print("=" * 60)
    print("MCP Server 连接检测")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"API Key: {'已配置' if args.api_key else '未配置'}")
    print()

    # 1. 检查 URL 可达性
    if not check_url_reachable(args.url, args.timeout):
        print("\n❌ 检测终止：URL 不可达，请检查服务状态和网络连接")
        sys.exit(1)

    # 2. 检查凭证
    if not check_credentials(args.url, args.api_key, args.timeout):
        print("\n❌ 检测终止：凭证验证失败，请检查 API Key")
        sys.exit(1)

    # 3. 列出工具
    tools = list_tools(args.url, args.api_key, args.timeout)

    # 4. 测试工具调用（如果指定了工具名）
    if args.tool_name:
        tool_args = {}
        if args.tool_args:
            try:
                tool_args = json.loads(args.tool_args)
            except json.JSONDecodeError:
                print(f"\n❌ tool-args 不是合法 JSON: {args.tool_args}")
                sys.exit(1)
        test_tool_call(args.url, args.api_key, args.timeout, args.tool_name, tool_args)
    else:
        print(f"\n[4/4] 跳过工具调用测试（未指定 --tool-name）")

    print("\n" + "=" * 60)
    print("检测完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
