#!/usr/bin/env python3
"""
猎聘网 AI 产品经理职位数据抓取脚本
使用 Playwright 自动化浏览器获取动态渲染的职位信息
"""

import json
import re
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# 目标公司和搜索关键词
TARGET_COMPANIES = [
    ("腾讯", "AI产品经理"),
    ("阿里巴巴", "AI产品经理"),
    ("字节跳动", "AI产品经理"),
    ("华为", "AI产品经理"),
    ("小米", "AI产品经理"),
    ("美团", "AI产品经理"),
]

async def scrape_liepin_jobs(company, keyword):
    """抓取猎聘网指定公司的 AI 产品经理职位"""
    
    jobs = []
    search_query = f"{company} {keyword}"
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # 构造搜索 URL
            search_url = f"https://www.liepin.com/zhaopin/?key={search_query.replace(' ', '+')}&dqs=010"
            print(f"🔍 正在抓取: {company} - {search_url}")
            
            # 访问页面并等待加载
            await page.goto(search_url, wait_until='networkidle', timeout=30000)
            
            # 等待职位列表加载
            await page.wait_for_selector('.job-list-box, .list-item-box, [data-selector="job-list"]')
            
            # 提取职位数据
            job_cards = await page.query_selector_all('.job-list-box .list-item, .list-item-box, .job-card')
            
            print(f"  ✅ 找到 {len(job_cards)} 个职位卡片")
            
            for card in job_cards[:10]:  # 只取前 10 条
                try:
                    # 提取职位名称
                    title_elem = await card.query_selector('.job-title, .ellipsis-1, h3, .job-name')
                    title = await title_elem.inner_text() if title_elem else "未知职位"
                    
                    # 提取薪资
                    salary_elem = await card.query_selector('.job-salary, .salary, .text-warning')
                    salary_text = await salary_elem.inner_text() if salary_elem else ""
                    
                    # 提取公司名
                    company_elem = await card.query_selector('.company-name, .company-title, .name')
                    company_name = await company_elem.inner_text() if company_elem else company
                    
                    # 提取工作年限要求
                    exp_elem = await card.query_selector('.job-exp, .exp, .experience')
                    experience = await exp_elem.inner_text() if exp_elem else ""
                    
                    # 提取学历要求
                    edu_elem = await card.query_selector('.job-edu, .edu, .education')
                    education = await edu_elem.inner_text() if edu_elem else ""
                    
                    # 提取地点
                    loc_elem = await card.query_selector('.job-area, .area, .location')
                    location = await loc_elem.inner_text() if loc_elem else ""
                    
                    # 提取标签
                    tag_elems = await card.query_selector_all('.job-tags span, .tags span, .tag')
                    tags = [await tag.inner_text() for tag in tag_elems[:5]]
                    
                    # 解析薪资数据
                    salary_data = parse_salary(salary_text)
                    
                    job = {
                        "company": company_name.strip(),
                        "job_title": title.strip(),
                        "salary_raw": salary_text.strip(),
                        "salary_parsed": salary_data,
                        "experience": experience.strip(),
                        "education": education.strip(),
                        "location": location.strip(),
                        "tags": tags,
                        "source": "liepin",
                        "data_type": "employer_posted",
                        "crawl_time": datetime.now().isoformat(),
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    print(f"  ⚠️ 解析职位卡片失败: {e}")
                    continue
            
        except Exception as e:
            print(f"  ❌ 抓取失败: {e}")
        
        finally:
            await browser.close()
    
    return jobs

def parse_salary(salary_text):
    """解析猎聘网薪资格式"""
    if not salary_text:
        return None
    
    result = {}
    text = salary_text.lower().replace('·', '').replace('薪', '').strip()
    
    # 匹配 "30-50k·16薪" 格式
    match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*[kK]', text)
    if match:
        result['base_low_k'] = float(match.group(1))
        result['base_high_k'] = float(match.group(2))
        result['base_median_k'] = (result['base_low_k'] + result['base_high_k']) / 2
    
    # 匹配月数 (如 16薪)
    month_match = re.search(r'(\d{2})', text)
    if month_match:
        result['bonus_months'] = int(month_match.group(1))
    else:
        result['bonus_months'] = 12  # 默认 12 薪
    
    # 计算年度总包
    if 'base_median_k' in result:
        result['tc_annual'] = result['base_median_k'] * result['bonus_months'] / 10  # 万
    
    return result

async def main():
    """主函数：抓取所有目标公司的数据"""
    
    all_jobs = []
    
    print("=" * 60)
    print("🚀 开始抓取猎聘网 AI 产品经理职位数据")
    print("=" * 60)
    
    for company, keyword in TARGET_COMPANIES:
        jobs = await scrape_liepin_jobs(company, keyword)
        all_jobs.extend(jobs)
        print(f"  📊 {company}: 成功抓取 {len(jobs)} 条职位\n")
        await asyncio.sleep(2)  # 避免请求过快
    
    # 保存结果
    output = {
        "source": "liepin",
        "crawl_time": datetime.now().isoformat(),
        "total_jobs": len(all_jobs),
        "jobs": all_jobs
    }
    
    # 写入文件
    output_path = "/Users/superkkk/MyCoding/Skills/myskills/business-skills/job-market-analyzer/reports/liepin_ai_pm_jobs.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print(f"✅ 抓取完成！共 {len(all_jobs)} 条职位数据")
    print(f"📁 数据已保存至: {output_path}")
    print("=" * 60)
    
    return output

if __name__ == "__main__":
    result = asyncio.run(main())
    print(json.dumps(result, ensure_ascii=False, indent=2))
