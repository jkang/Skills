import json
import os
import re

def clean_salary(salary_str):
    if not salary_str or "面议" in salary_str:
        return 0, 0, 0
    # Generic regex for numbers like 20-30k, 3-5万
    numbers = re.findall(r'(\d+\.?\d*)', salary_str)
    if not numbers:
        return 0, 0, 0
    
    # Try to find multiplier like 15薪
    multiplier = 12
    mult_match = re.search(r'(\d+)薪', salary_str)
    if mult_match:
        multiplier = int(mult_match.group(1))
    
    # Unit detection
    unit = 1000 # Default k
    if "万" in salary_str or "W" in salary_str.upper():
        unit = 10000
    
    low = float(numbers[0]) * unit
    high = float(numbers[1]) * unit if len(numbers) > 1 else low
    avg_monthly = (low + high) / 2
    
    base_annual = avg_monthly * 12
    bonus_annual = avg_monthly * (multiplier - 12) if multiplier > 12 else 0
    tc = avg_monthly * multiplier
    
    return int(base_annual), int(bonus_annual), int(tc)

def main():
    raw_dir = "reports/raw"
    merged = []
    cleaned = []
    
    for filename in os.listdir(raw_dir):
        if filename.endswith(".json"):
            with open(os.path.join(raw_dir, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                merged.extend(data)
                
                source = filename.replace(".json", "")
                for item in data:
                    # Generic cleaning
                    title = item.get("job_name", item.get("post_title", "Unknown"))
                    salary_raw = item.get("salary_range", item.get("post_content", ""))
                    
                    if "未知岗位" in title or "面议" in salary_raw:
                        continue
                        
                    base, bonus, tc = clean_salary(salary_raw)
                    
                    if base == 0 and tc == 0:
                        continue
                        
                    cleaned.append({
                        "company": "华为",
                        "job_title": title,
                        "base_salary": f"{base:,}",
                        "stock_value": "0",
                        "bonus_value": f"{bonus:,}",
                        "tc": f"{tc:,}",
                        "source": source,
                        "data_type": "employer_posted" if source in ["liepin", "51job"] else "employee_reported"
                    })

    os.makedirs("reports", exist_ok=True)
    with open("reports/raw_data_merged.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    with open("reports/cleaned_data.json", "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
        
    print(f"Merged {len(merged)} records. Cleaned {len(cleaned)} records.")
    
    # Enforce at least 50 valid records per platform
    counts_by_source = {}
    for r in cleaned:
        src = r.get("source", "unknown")
        counts_by_source[src] = counts_by_source.get(src, 0) + 1
        
    print(f"Valid records per source: {counts_by_source}")
    failed_sources = [src for src, count in counts_by_source.items() if count < 50]
    
    if failed_sources:
        raise Exception(f"Validation Error: The following platforms failed to gather at least 50 valid records: {failed_sources}. Please check scrapers or login status.")
        
if __name__ == "__main__":
    main()
