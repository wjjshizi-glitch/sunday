#!/usr/bin/env python3
"""
火山方舟 temperature 参数自动化验证脚本

用法:
    python validate_temperature.py --api-key YOUR_KEY --endpoint YOUR_ENDPOINT_ID

可选参数:
    --base-url     API 基础地址（默认: https://ark.cn-beijing.volces.com/api/v3）
    --prompt       测试用 prompt（默认: 用一句话描述春天的早晨，要求包含意象和感受，不超过30字。）
    --rounds       每组测试轮次（默认: 5）
    --low-temp     低 temperature 值（默认: 0）
    --high-temp    高 temperature 值（默认: 1.5）
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


def call_model(api_key, endpoint, base_url, prompt, temperature):
    """调用模型并返回回答"""
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": endpoint,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        return f"[HTTP错误 {e.response.status_code}] {e.response.text[:200]}"
    except Exception as e:
        return f"[请求失败] {str(e)}"


def diversity_score(answers):
    """计算回答多样性评分"""
    total = len(answers)
    unique = len(set(answers))
    # 计算两两相似度（简单的字符级比较）
    if total < 2:
        return unique, total, 0.0

    diff_count = 0
    pair_count = 0
    for i in range(total):
        for j in range(i + 1, total):
            pair_count += 1
            if answers[i] != answers[j]:
                diff_count += 1

    diff_ratio = diff_count / pair_count if pair_count > 0 else 0
    return unique, total, diff_ratio


def main():
    parser = argparse.ArgumentParser(description="火山方舟 temperature 参数验证工具")
    parser.add_argument("--api-key", required=True, help="API Key")
    parser.add_argument("--endpoint", required=True, help="推理接入点 ID (ep-xxxx)")
    parser.add_argument("--base-url", default="https://ark.cn-beijing.volces.com/api/v3",
                        help="API 基础地址")
    parser.add_argument("--prompt", default="用一句话描述春天的早晨，要求包含意象和感受，不超过30字。",
                        help="测试用 prompt")
    parser.add_argument("--rounds", type=int, default=5, help="每组测试轮次")
    parser.add_argument("--low-temp", type=float, default=0.0, help="低 temperature 值")
    parser.add_argument("--high-temp", type=float, default=1.5, help="高 temperature 值")
    args = parser.parse_args()

    print("=" * 60)
    print("火山方舟 temperature 参数验证")
    print("=" * 60)
    print(f"接入点: {args.endpoint}")
    print(f"测试 prompt: {args.prompt}")
    print(f"每轮次数: {args.rounds}")
    print()

    # 低 temperature 测试
    print(f"--- 测试 1: temperature = {args.low_temp} ---")
    low_answers = []
    for i in range(args.rounds):
        print(f"  第 {i+1}/{args.rounds} 次调用...", end=" ", flush=True)
        answer = call_model(args.api_key, args.endpoint, args.base_url,
                            args.prompt, args.low_temp)
        low_answers.append(answer)
        print(f"完成: {answer[:50]}{'...' if len(answer) > 50 else ''}")
        time.sleep(0.5)

    print()

    # 高 temperature 测试
    print(f"--- 测试 2: temperature = {args.high_temp} ---")
    high_answers = []
    for i in range(args.rounds):
        print(f"  第 {i+1}/{args.rounds} 次调用...", end=" ", flush=True)
        answer = call_model(args.api_key, args.endpoint, args.base_url,
                            args.prompt, args.high_temp)
        high_answers.append(answer)
        print(f"完成: {answer[:50]}{'...' if len(answer) > 50 else ''}")
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("验证结果")
    print("=" * 60)

    low_unique, low_total, low_diff = diversity_score(low_answers)
    high_unique, high_total, high_diff = diversity_score(high_answers)

    print(f"\n低 temperature ({args.low_temp}):")
    print(f"  去重后: {low_unique}/{low_total} 条不同")
    print(f"  两两差异率: {low_diff:.1%}")
    for i, ans in enumerate(low_answers, 1):
        print(f"  [{i}] {ans}")

    print(f"\n高 temperature ({args.high_temp}):")
    print(f"  去重后: {high_unique}/{high_total} 条不同")
    print(f"  两两差异率: {high_diff:.1%}")
    for i, ans in enumerate(high_answers, 1):
        print(f"  [{i}] {ans}")

    print()
    print("-" * 60)
    print("结论:")
    if low_diff < high_diff:
        print(f"  ✅ temperature 参数生效！低温度({low_diff:.1%})明显比高温度({high_diff:.1%})更确定。")
    elif low_diff == high_diff:
        print(f"  ⚠️  两组差异率相同({low_diff:.1%})，temperature 可能未生效或测试次数不足。")
    else:
        print(f"  ❌ 异常：低温度({low_diff:.1%})反而比高温度({high_diff:.1%})更随机，请检查参数传递是否正确。")
    print("-" * 60)


if __name__ == "__main__":
    main()
