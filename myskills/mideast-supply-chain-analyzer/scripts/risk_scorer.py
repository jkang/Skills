#!/usr/bin/env python3
"""
risk_scorer.py — 中东地缘政治风险评分引擎

用途:
  接收结构化的地缘政治事件数据（JSON），根据多维度评分模型
  计算每个事件的综合风险评分，并输出汇总统计。

用法:
  python risk_scorer.py events.json
  echo '{"events": [...]}' | python risk_scorer.py

输出:
  JSON 格式的评分结果（stdout），包含每个事件的综合评分、
  整体风险指数、风险分布统计和 Top N 高风险事件。
"""

import json
import math
import statistics
import sys


# ============================================================
# 默认配置 (Default Configuration)
# ============================================================

DEFAULT_ROUTE_WEIGHTS = {
    "红海-苏伊士运河航线": 5,
    "霍尔木兹海峡航线": 5,
    "曼德海峡": 5,
    "亚丁湾航线": 4,
    "波斯湾内航线": 4,
}

TIME_SENSITIVITY_SCORES = {
    "紧急": 5,
    "短期": 4,
    "中期": 3,
    "长期": 2,
}

IMPACT_TYPE_WEIGHTS = {
    "直接": 1.0,
    "间接": 0.7,
    "潜在": 0.4,
}

RISK_LEVEL_THRESHOLDS = [
    (4.0, "高危", "#FF4D4F", "#FFF1F0"),
    (3.0, "中等", "#FAAD14", "#FFFBE6"),
    (0.0, "低",   "#52C41A", "#F6FFED"),
]

# 评分权重
WEIGHT_SEVERITY       = 0.35
WEIGHT_PROBABILITY    = 0.25
WEIGHT_URGENCY        = 0.20
WEIGHT_ROUTE_IMPORTANCE = 0.20


# ============================================================
# 风险评分核心逻辑 (Risk Scoring Engine)
# ============================================================

def get_risk_level(score: float) -> tuple:
    """根据综合评分返回 (等级名称, 文字色, 背景色)"""
    for threshold, name, color, bg_color in RISK_LEVEL_THRESHOLDS:
        if score >= threshold:
            return name, color, bg_color
    return "低", "#52C41A", "#F6FFED"


def compute_source_bonus(source_count: int) -> float:
    """
    多源验证加成：多个独立来源报道同一事件，可信度更高。
    3个来源以上给予加成，上限1.0分。
    """
    if source_count >= 5:
        return 1.0
    if source_count >= 3:
        return 0.5
    return 0.0


def compute_route_importance(affected_routes: list, route_weights: dict) -> float:
    """
    计算受影响航线的最高重要性权重。
    如果事件影响多条航线，取最高值（因为最关键的那条航线决定了风险上限）。
    """
    if not affected_routes:
        return 2.0  # 默认中等权重（事件可能间接影响航运）

    max_weight = 0
    for route in affected_routes:
        # 精确匹配
        if route in route_weights:
            max_weight = max(max_weight, route_weights[route])
            continue
        # 模糊匹配（部分包含）
        for key, weight in route_weights.items():
            if route in key or key in route:
                max_weight = max(max_weight, weight)
                break

    return max_weight if max_weight > 0 else 2.0


def score_event(event: dict, route_weights: dict) -> dict:
    """
    对单个事件进行多维度评分。

    综合评分公式:
      composite = severity × 0.35 + probability × 0.25
                + urgency × 0.20 + route_importance × 0.20
                + source_bonus

    评分上限为 5.0 + source_bonus（最高6.0）。
    """
    severity = min(float(event.get("severity", 3)), 5.0)
    probability = min(float(event.get("probability", 3)), 5.0)

    time_sens = event.get("time_sensitivity", "中期")
    urgency = float(TIME_SENSITIVITY_SCORES.get(time_sens, 3))

    affected_routes = event.get("affected_routes", [])
    route_imp = compute_route_importance(affected_routes, route_weights)

    source_count = int(event.get("source_count", 1))
    source_bonus = compute_source_bonus(source_count)

    # 影响类型权重调整
    impact_type = event.get("supply_chain_impact", "直接")
    impact_multiplier = IMPACT_TYPE_WEIGHTS.get(impact_type, 0.7)

    # 基础综合评分
    base_score = (
        severity       * WEIGHT_SEVERITY +
        probability    * WEIGHT_PROBABILITY +
        urgency        * WEIGHT_URGENCY +
        route_imp      * WEIGHT_ROUTE_IMPORTANCE
    )

    # 应用影响类型调节：间接和潜在影响会降低评分
    adjusted_score = base_score * (0.6 + 0.4 * impact_multiplier)

    # 加上多源验证加成
    composite = adjusted_score + source_bonus

    # 限制上限
    composite = min(composite, 6.0)

    risk_level, risk_color, risk_bg = get_risk_level(composite)

    return {
        "event_id": event.get("event_id", "unknown"),
        "title": event.get("title", ""),
        "composite_score": round(composite, 2),
        "severity_score": severity,
        "probability_score": probability,
        "urgency_score": urgency,
        "route_importance_score": route_imp,
        "impact_multiplier": impact_multiplier,
        "source_bonus": source_bonus,
        "source_count": source_count,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_bg_color": risk_bg,
        "event_type": event.get("event_type", ""),
        "event_type_name": event.get("event_type_name", ""),
        "countries": event.get("countries", []),
        "affected_routes": affected_routes,
        "time_sensitivity": time_sens,
        "supply_chain_impact": impact_type,
        "summary": event.get("summary", ""),
        "source_urls": event.get("source_urls", []),
    }


# ============================================================
# 汇总统计 (Aggregate Statistics)
# ============================================================

def aggregate_results(scored_events: list) -> dict:
    """
    汇总所有事件的评分结果，生成整体风险报告。
    """
    if not scored_events:
        return {
            "overall_risk_index": 0,
            "risk_level": "低",
            "risk_level_color": "#52C41A",
            "total_events": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "events": [],
            "risk_distribution": {"高危": 0, "中等": 0, "低": 0},
            "affected_routes_summary": [],
            "top_risks": [],
            "trend_summary": "无可分析的事件数据",
        }

    scores = [e["composite_score"] for e in scored_events]

    # 整体风险指数：使用加权平均，高分事件权重更大（突出最严重风险）
    if len(scores) >= 2:
        # 排序后取前50%的均值，避免大量低危事件稀释整体风险感知
        sorted_scores = sorted(scores, reverse=True)
        top_half = sorted_scores[:max(len(sorted_scores) // 2, 1)]
        overall_index = round(statistics.mean(top_half), 2)
    else:
        overall_index = round(scores[0], 2)

    overall_level, overall_color, _ = get_risk_level(overall_index)

    # 风险分布统计
    distribution = {"高危": 0, "中等": 0, "低": 0}
    for e in scored_events:
        distribution[e["risk_level"]] = distribution.get(e["risk_level"], 0) + 1

    # 受影响航线汇总
    route_risks = {}
    for e in scored_events:
        for route in e.get("affected_routes", []):
            if route not in route_risks:
                route_risks[route] = {"name": route, "event_count": 0, "max_score": 0, "events": []}
            route_risks[route]["event_count"] += 1
            route_risks[route]["max_score"] = max(route_risks[route]["max_score"], e["composite_score"])
            route_risks[route]["events"].append(e["event_id"])

    routes_summary = sorted(route_risks.values(), key=lambda x: x["max_score"], reverse=True)

    # Top N 高风险事件
    top_risks = sorted(scored_events, key=lambda x: x["composite_score"], reverse=True)[:5]

    # 趋势摘要
    trend_parts = []
    if distribution["高危"] > 0:
        trend_parts.append("{}个高危事件需要立即关注".format(distribution["高危"]))
    if distribution["中等"] > 0:
        trend_parts.append("{}个中等风险事件需持续监控".format(distribution["中等"]))
    if len(routes_summary) > 0:
        trend_parts.append("共{}条航线受到影响".format(len(routes_summary)))
    trend_summary = "；".join(trend_parts) if trend_parts else "当前风险态势总体可控"

    return {
        "overall_risk_index": overall_index,
        "risk_level": overall_level,
        "risk_level_color": overall_color,
        "total_events": len(scored_events),
        "high_risk_count": distribution["高危"],
        "medium_risk_count": distribution["中等"],
        "low_risk_count": distribution["低"],
        "events": scored_events,
        "risk_distribution": distribution,
        "affected_routes_summary": routes_summary,
        "top_risks": top_risks,
        "trend_summary": trend_summary,
        "statistics": {
            "mean_score": round(statistics.mean(scores), 2),
            "max_score": round(max(scores), 2),
            "min_score": round(min(scores), 2),
            "stdev": round(statistics.stdev(scores), 2) if len(scores) >= 2 else 0,
        },
    }


# ============================================================
# CLI 入口 (CLI Entry Point)
# ============================================================

if __name__ == "__main__":
    # 读取输入: 文件路径 或 stdin
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("错误: 文件不存在 — {}".format(sys.argv[1]), file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print("错误: JSON 解析失败 — {}".format(e), file=sys.stderr)
            sys.exit(1)
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print("错误: stdin JSON 解析失败 — {}".format(e), file=sys.stderr)
            sys.exit(1)

    # 解析输入数据
    if isinstance(data, list):
        events = data
        route_weights = DEFAULT_ROUTE_WEIGHTS
    else:
        events = data.get("events", [])
        route_weights = data.get("route_weights", DEFAULT_ROUTE_WEIGHTS)

    if not events:
        print("警告: 输入事件列表为空", file=sys.stderr)

    print("[评分] 开始处理 {} 个事件...".format(len(events)), file=sys.stderr)

    # 逐个评分
    scored_events = []
    for i, event in enumerate(events):
        scored = score_event(event, route_weights)
        scored_events.append(scored)
        level_tag = scored["risk_level"]
        print("[评分] 事件 {}/{}: {} — {} (评分: {})".format(
            i + 1, len(events), scored["event_id"], level_tag, scored["composite_score"]
        ), file=sys.stderr)

    # 汇总统计
    result = aggregate_results(scored_events)

    print("[完成] 整体风险指数: {} ({})".format(
        result["overall_risk_index"], result["risk_level"]
    ), file=sys.stderr)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
