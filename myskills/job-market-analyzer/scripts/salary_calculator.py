#!/usr/bin/env python3
import json
import re
import statistics
import sys
from collections import Counter

def parse_salary(salary_str):
    """
    Parses a Chinese salary string (e.g. "20-40k", "15-30k·16薪") into estimated annual and monthly ranges.
    Returns (min_monthly, max_monthly, min_annual, max_annual) in thousands (k).
    """
    salary_str = salary_str.lower().replace('K', 'k').replace('W', 'w')
    
    # Try to extract base range (e.g. 20-40k or 20-40)
    range_match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)(k|w|)', salary_str)
    if not range_match:
        return None
        
    min_val = float(range_match.group(1))
    max_val = float(range_match.group(2))
    unit = range_match.group(3)
    
    if unit == 'w' or (not unit and min_val < 200 and '年' in salary_str):
        # Likely Annual in 10k (wan)
        min_monthly = (min_val * 10) / 12
        max_monthly = (max_val * 10) / 12
        min_annual = min_val * 10
        max_annual = max_val * 10
    else:
        # Default to Monthly in k
        min_monthly = min_val
        max_monthly = max_val
        
        # Check for multiplier (e.g., 14薪, 16薪)
        months_match = re.search(r'(\d{2})薪', salary_str)
        months = float(months_match.group(1)) if months_match else 12.0
        
        min_annual = min_monthly * months
        max_annual = max_monthly * months

    return {
        "min_monthly": min_monthly,
        "max_monthly": max_monthly,
        "avg_monthly": (min_monthly + max_monthly) / 2,
        "min_annual": min_annual,
        "max_annual": max_annual,
        "avg_annual": (min_annual + max_annual) / 2
    }

def analyze_jobs(jobs):
    valid_salaries = []
    hard_skills = Counter()
    soft_skills = Counter()
    
    for job in jobs:
        # Process Salary
        if "salary" in job:
            parsed = parse_salary(job["salary"])
            if parsed:
                valid_salaries.append(parsed)
                
        # Process Skills
        if "hard_skills" in job:
            for skill in job["hard_skills"]:
                hard_skills[skill] += 1
                
        if "soft_skills" in job:
            for skill in job["soft_skills"]:
                soft_skills[skill] += 1
                
    # Calculate Stats
    stats = {}
    if valid_salaries:
        avg_month_mins = [s["min_monthly"] for s in valid_salaries]
        avg_month_maxs = [s["max_monthly"] for s in valid_salaries]
        avg_month_avgs = [s["avg_monthly"] for s in valid_salaries]
        
        stats["salary"] = {
            "valid_samples": len(valid_salaries),
            "monthly": {
                "absolute_min": round(min(avg_month_mins), 1),
                "absolute_max": round(max(avg_month_maxs), 1),
                "market_average": round(statistics.mean(avg_month_avgs), 1),
                "median_average": round(statistics.median(avg_month_avgs), 1),
            }
        }
    
    stats["top_hard_skills"] = hard_skills.most_common(10)
    stats["top_soft_skills"] = soft_skills.most_common(5)
    
    return stats

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
        
    results = analyze_jobs(data.get("jobs", data))
    print(json.dumps(results, indent=2, ensure_ascii=False))
