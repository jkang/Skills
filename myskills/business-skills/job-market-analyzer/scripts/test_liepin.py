#!/usr/bin/env python3
"""
猎聘网测试抓取脚本 - 简化版
"""

import json
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

async def quick_scrape():
    """快速抓取猎聘网数据"""
    
    jobs = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 直接访问猎聘搜索页
            print("🌐 正在访问猎聘网...")
            await page.goto(
                "https://www.liepin.com/zhaopin/?key=AI产品经理",
                wait_until='domcontentloaded',
                timeout=15000
            )
            
            # 等待职位列表
            print("⏳ 等待页面加载...")
            await page.wait_for_timeout(3000)
            
            # 获取页面内容
            content = await page.content()
            
            # 检查是否有反爬验证
            if "验证码" in content or "captcha" in content.lower():
                print("⚠️ 触发反爬验证，需要手动登录")
                return None
            
            # 提取职位信息（使用简单选择器）
            job_elements = await page.query_selector_all('[class*="job"], [class*="list"]')
            print(f"📊 找到 {len(job_elements)} 个可能的项目")
            
            # 尝试提取文本内容
            titles = await page.eval_on_selector_all('.job-title, .ellipsis-1, h3', 
                'elements => elements.map(e => e.textContent.trim()).slice(0, 10)')
            
            salaries = await page.eval_on_selector_all('.job-salary, .salary, .text-warning',
                'elements => elements.map(e => e.textContent.trim()).slice(0, 10)')
            
            companies = await page.eval_on_selector_all('.company-name, .company-title',
                'elements => elements.map(e => e.textContent.trim()).slice(0, 10)')
            
            print(f"\n✅ 成功提取数据:")
            print(f"  - 职位: {len(titles)} 条")
            print(f"  - 薪资: {len(salaries)} 条")
            print(f"  - 公司: {len(companies)} 条")
            
            # 组装数据
            for i in range(min(len(titles), len(salaries), 5)):
                job = {
                    "job_title": titles[i] if i < len(titles) else "",
                    "salary_raw": salaries[i] if i < len(salaries) else "",
                    "company": companies[i] if i < len(companies) else "",
                    "source": "liepin",
                    "crawl_time": datetime.now().isoformat()
                }
                jobs.append(job)
                print(f"\n  📋 {i+1}. {job['job_title']}")
                print(f"     💰 {job['salary_raw']}")
                print(f"     🏢 {job['company']}")
            
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return None
        
        finally:
            await browser.close()
    
    return jobs

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 猎聘网 AI 产品经理职位快速测试")
    print("=" * 50)
    
    jobs = asyncio.run(quick_scrape())
    
    if jobs:
        output_path = "/Users/superkkk/MyCoding/Skills/myskills/business-skills/job-market-analyzer/reports/liepin_test.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"jobs": jobs, "count": len(jobs)}, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 测试数据已保存: {output_path}")
    else:
        print("\n⚠️ 自动抓取受限，将使用备用数据源")
