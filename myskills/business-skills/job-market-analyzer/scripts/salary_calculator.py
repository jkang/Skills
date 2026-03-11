#!/usr/bin/env python3
"""
薪资调研数据分析脚本 (Salary Research Data Analyzer)

处理来自 Levels.fyi 和脉脉(Maimai)的薪资数据，执行统计分析。
支持中文薪资黑话解析（如 "30k*16", "总包80w"）。

用法:
    python salary_calculator.py data.json
    echo '{"entries": [...]}' | python salary_calculator.py
"""

import json
import math
import re
import statistics
import sys
from collections import defaultdict


# ============================================================
# 薪资黑话解析器 (Chinese Salary Slang Parser)
# ============================================================

def parse_salary_slang(raw_text: str) -> dict | None:
    """
    从一段非结构化的中文薪资描述中提取结构化数据。

    支持的格式示例:
      - "30k*16" / "30k×16薪" → base_monthly=30, bonus_months=16
      - "总包80w" / "tc 80" → tc_annual=80
      - "base 25k, 年终3个月" → base_monthly=25, bonus_months=15 (12+3)
      - "月薪3万" → base_monthly=30
      - "年薪50万" → tc_annual=50

    Returns dict with keys: base_monthly(k), bonus_months, stock_annual(万), tc_annual(万)
    Returns None if no salary info could be extracted.
    """
    if not raw_text:
        return None

    text = raw_text.lower().replace('，', ',').replace('×', '*')
    result = {}

    # --- Pattern 1: 总包 / TC ---
    # "总包80w", "tc 80万", "总包大概70-80", "tc80"
    tc_match = re.search(r'(?:总包|tc|total\s*comp)[约大概\s]*(\d+(?:\.\d+)?)\s*[-~到]?\s*(\d+(?:\.\d+)?)?\s*[wW万]?', text)
    if tc_match:
        tc_low = float(tc_match.group(1))
        tc_high = float(tc_match.group(2)) if tc_match.group(2) else tc_low
        # 如果数字 < 200，假设单位是万；如果 >= 200，假设单位是 k (千)
        if tc_low < 200:
            result['tc_annual'] = (tc_low + tc_high) / 2
        else:
            result['tc_annual'] = (tc_low + tc_high) / 2 / 10  # k → 万

    # --- Pattern 2: Base 月薪 ---
    # "base 30k", "base30k", "月薪3万", "base 25000"
    base_match = re.search(r'(?:base|月薪|基本工资)[约大概\s]*(\d+(?:\.\d+)?)\s*[kK千]?', text)
    if base_match:
        base_val = float(base_match.group(1))
        if base_val >= 1000:
            result['base_monthly'] = base_val / 1000  # 元 → k
        elif base_val > 100:
            result['base_monthly'] = base_val / 10  # 可能单位是百? 不太常见，保守处理
        else:
            result['base_monthly'] = base_val  # 已经是 k

    # --- Pattern 3: Nk * N薪 格式 ---
    # "30k*16", "25k*15薪", "28K16薪"
    kn_match = re.search(r'(\d+(?:\.\d+)?)\s*[kK]\s*[*×x·]\s*(\d+)\s*薪?', text)
    if kn_match:
        result['base_monthly'] = float(kn_match.group(1))
        result['bonus_months'] = int(kn_match.group(2))
        result['bonus_fixed_months'] = result['bonus_months'] - 12
        if 'tc_annual' not in result:
            result['tc_annual'] = result['base_monthly'] * result['bonus_months'] / 10  # k*months → 万

    # --- Pattern 4: N薪 (年终奖月数) ---
    # "16薪", "15薪", "14薪"
    if 'bonus_months' not in result:
        month_match = re.search(r'(\d{2})\s*薪', text)
        if month_match:
            result['bonus_months'] = int(month_match.group(1))
            result['bonus_fixed_months'] = result['bonus_months'] - 12

    # --- Pattern 5: 年终奖 N个月 (固定) ---
    # "年终3个月", "年终奖4个月"
    bonus_match = re.search(r'年终[奖金]?\s*(\d+(?:\.\d+)?)\s*个月', text)
    if bonus_match:
        bonus_extra = float(bonus_match.group(1))
        result['bonus_fixed_months'] = bonus_extra
        if 'bonus_months' not in result:
            result['bonus_months'] = 12 + bonus_extra

    # --- Pattern 6: 固定N个月 + 绩效M个月 ---
    # "固定3个月+绩效1-3个月", "3.5+绩效"
    perf_match = re.search(r'(?:固定|保底)(\d+(?:\.\d+)?)\s*个?月?\s*[+＋]\s*(?:绩效|performance)\s*(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)\s*个?月?', text)
    if perf_match:
        fixed = float(perf_match.group(1))
        perf_low = float(perf_match.group(2))
        perf_high = float(perf_match.group(3))
        result['bonus_fixed_months'] = fixed
        result['bonus_performance_months_low'] = perf_low
        result['bonus_performance_months_high'] = perf_high
        if 'bonus_months' not in result:
            result['bonus_months'] = 12 + fixed + (perf_low + perf_high) / 2

    # --- Pattern 7: 年终0-N个月 (浮动范围) ---
    # "年终0-6个月", "年终奖2-4个月"
    range_bonus_match = re.search(r'年终[奖金]?\s*(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)\s*个月', text)
    if range_bonus_match and 'bonus_performance_months_low' not in result:
        low = float(range_bonus_match.group(1))
        high = float(range_bonus_match.group(2))
        result['bonus_performance_months_low'] = low
        result['bonus_performance_months_high'] = high
        if 'bonus_months' not in result:
            result['bonus_months'] = 12 + (low + high) / 2

    # --- Pattern 8: 签字费/Sign-on ---
    # "签字费10w", "sign-on 15万", "入职奖金20w"
    signon_match = re.search(r'(?:签字费|sign[\-\s]?on|入职奖金)[约大概\s]*(\d+(?:\.\d+)?)\s*[wW万]?', text)
    if signon_match:
        result['sign_on_bonus'] = float(signon_match.group(1))

    # --- Pattern 9: 股票/期权 ---
    # "股票一年20w", "期权折合年化15万", "rsu 每年 10万"
    stock_match = re.search(r'(?:股票|期权|rsu|stock)[^\d]*(\d+(?:\.\d+)?)\s*[wW万]', text)
    if stock_match:
        result['stock_annual'] = float(stock_match.group(1))

    # --- Pattern 10: 年薪 ---
    # "年薪50万", "年薪50w"
    annual_match = re.search(r'年薪\s*(\d+(?:\.\d+)?)\s*[wW万]?', text)
    if annual_match and 'tc_annual' not in result:
        val = float(annual_match.group(1))
        result['tc_annual'] = val if val < 200 else val / 10

    return result if result else None


def compute_tc(entry: dict) -> float | None:
    """
    从一条数据记录中计算年度 TC (总包)，单位：万。

    优先使用已有的 tc_annual，否则自行推算。
    """
    # 如果直接提供了 TC
    if entry.get('tc_annual') and entry['tc_annual'] > 0:
        return float(entry['tc_annual'])

    # 从 base + bonus + stock 推算
    base = entry.get('base_monthly')
    if not base or base <= 0:
        return None

    months = entry.get('bonus_months', 12)
    stock = entry.get('stock_annual', 0)

    # base(k) * months / 10 → 万  +  stock(万)
    tc = (base * months) / 10 + stock
    return round(tc, 1)


# ============================================================
# 分位数计算
# ============================================================

def percentile(data: list[float], p: float) -> float:
    """计算百分位数 (线性插值法)"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    k = (n - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


# ============================================================
# 主分析流程
# ============================================================

def analyze_entries(entries: list[dict]) -> dict:
    """
    分析薪资数据条目列表，输出统计结果。

    每条 entry 的字段:
      - base_monthly (float, k): 月薪，单位千
      - bonus_months (int): 总月数 (含年终)，如 16
      - stock_annual (float, 万): 年化股票/期权价值，单位万
      - tc_annual (float, 万): 年度总包，单位万
      - source (str): "levels.fyi" 或 "maimai"
      - raw_text (str, optional): 原始文本
      - post_date (str, optional): 数据发布时间
    """
    all_tc = []
    by_source = defaultdict(list)
    valid_entries = []
    parse_errors = []

    for i, entry in enumerate(entries):
        # 如果有 raw_text 但缺少结构化字段，尝试自动解析
        if entry.get('raw_text') and not entry.get('tc_annual') and not entry.get('base_monthly'):
            parsed = parse_salary_slang(entry['raw_text'])
            if parsed:
                entry.update(parsed)

        tc = compute_tc(entry)
        if tc is None or tc <= 0:
            parse_errors.append({"index": i, "reason": "无法计算 TC", "raw": entry.get('raw_text', '')})
            continue

        # 异常值检测 (TC < 5万 或 > 500万 视为异常)
        if tc < 5 or tc > 500:
            parse_errors.append({"index": i, "reason": f"TC={tc}万 超出合理范围 [5, 500]", "raw": entry.get('raw_text', '')})
            continue

        source = entry.get('source', 'unknown').lower()
        all_tc.append(tc)
        by_source[source].append(tc)
        valid_entries.append({**entry, '_computed_tc': tc})

    # --- 总体统计 ---
    overall = {}
    if all_tc:
        overall = {
            "sample_count": len(all_tc),
            "min": round(min(all_tc), 1),
            "max": round(max(all_tc), 1),
            "mean": round(statistics.mean(all_tc), 1),
            "median": round(statistics.median(all_tc), 1),
            "p25": round(percentile(all_tc, 25), 1),
            "p75": round(percentile(all_tc, 75), 1),
        }

    # --- 按来源统计 ---
    source_stats = {}
    for src, tcs in by_source.items():
        source_stats[src] = {
            "sample_count": len(tcs),
            "min": round(min(tcs), 1),
            "max": round(max(tcs), 1),
            "median": round(statistics.median(tcs), 1),
            "range": f"{round(min(tcs), 1)}-{round(max(tcs), 1)}万",
        }

    # --- Base 月薪统计 ---
    base_values = [e.get('base_monthly') for e in valid_entries if e.get('base_monthly')]
    base_stats = {}
    if base_values:
        base_stats = {
            "sample_count": len(base_values),
            "min": round(min(base_values), 1),
            "max": round(max(base_values), 1),
            "median": round(statistics.median(base_values), 1),
            "unit": "k/月",
        }

    # --- 年终奖统计 ---
    bonus_months_values = [e.get('bonus_months') for e in valid_entries if e.get('bonus_months')]
    bonus_fixed_values = [e.get('bonus_fixed_months') for e in valid_entries if e.get('bonus_fixed_months') is not None]
    perf_low_values = [e.get('bonus_performance_months_low') for e in valid_entries if e.get('bonus_performance_months_low') is not None]
    perf_high_values = [e.get('bonus_performance_months_high') for e in valid_entries if e.get('bonus_performance_months_high') is not None]
    sign_on_values = [e.get('sign_on_bonus') for e in valid_entries if e.get('sign_on_bonus')]

    bonus_stats = {}
    if bonus_months_values:
        bonus_stats["total_months"] = {
            "sample_count": len(bonus_months_values),
            "min": round(min(bonus_months_values), 1),
            "max": round(max(bonus_months_values), 1),
            "median": round(statistics.median(bonus_months_values), 1),
            "common": f"{round(min(bonus_months_values))}-{round(max(bonus_months_values))}薪",
        }
    if bonus_fixed_values:
        bonus_stats["fixed_months"] = {
            "sample_count": len(bonus_fixed_values),
            "min": round(min(bonus_fixed_values), 1),
            "max": round(max(bonus_fixed_values), 1),
            "median": round(statistics.median(bonus_fixed_values), 1),
        }
    if perf_low_values and perf_high_values:
        bonus_stats["performance_months"] = {
            "sample_count": len(perf_low_values),
            "range_low": round(min(perf_low_values), 1),
            "range_high": round(max(perf_high_values), 1),
        }
    if sign_on_values:
        bonus_stats["sign_on_bonus"] = {
            "sample_count": len(sign_on_values),
            "min": round(min(sign_on_values), 1),
            "max": round(max(sign_on_values), 1),
            "median": round(statistics.median(sign_on_values), 1),
            "unit": "万",
        }

    return {
        "overall_tc": overall,
        "by_source": source_stats,
        "base_monthly": base_stats,
        "bonus": bonus_stats,
        "valid_entries": len(valid_entries),
        "parse_errors": parse_errors,
        "entries_detail": [
            {
                "base_monthly": e.get('base_monthly'),
                "bonus_months": e.get('bonus_months'),
                "bonus_fixed_months": e.get('bonus_fixed_months'),
                "bonus_performance_months_low": e.get('bonus_performance_months_low'),
                "bonus_performance_months_high": e.get('bonus_performance_months_high'),
                "sign_on_bonus": e.get('sign_on_bonus'),
                "stock_annual": e.get('stock_annual'),
                "tc_annual": e['_computed_tc'],
                "source": e.get('source', 'unknown'),
            }
            for e in valid_entries
        ],
    }


# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    entries = data.get("entries", data if isinstance(data, list) else [])
    results = analyze_entries(entries)
    print(json.dumps(results, indent=2, ensure_ascii=False))
