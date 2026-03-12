import sys
import json
import asyncio
import os
from playwright.async_api import async_playwright

async def scrape(company, job_title, target_count=50):
    print(f"Starting 51job scrape for {company} {job_title}...", flush=True)
    results = []
    
    async with async_playwright() as p:
        browser = None
        context = None
        try:
            print("Trying to connect to an existing Chrome instance on port 9222...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            print("Successfully connected to existing Chrome!")
        except Exception as e:
            print(f"Could not connect to existing Chrome ({e}). Starting a new browser instance...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
        
        url = f"https://we.51job.com/pc/search?keyword={company} {job_title}"
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            for page_num in range(10): # increased arbitrarily to safely hit dynamic counts
                # 51job is known to be a bit slow, ensure cards are loaded
                await page.wait_for_timeout(2000)
                cards = await page.query_selector_all(".joblist-item")
                if not cards and page_num == 0:
                    raise Exception("Could not find Job cards on 51job. UI might have changed or blocked.")
                    
                for card in cards:
                    if len(results) >= target_count:
                        break
                    title_elem = await card.query_selector(".jname.text-cut")
                    salary_elem = await card.query_selector(".sal")
                    exp_elem = await card.query_selector(".d.icon-work.text-cut")
                    edu_elem = await card.query_selector(".d.icon-edu.text-cut")
                    
                    title = await title_elem.inner_text() if title_elem else "未知岗位"
                    salary = await salary_elem.inner_text() if salary_elem else "薪资面议"
                    exp = await exp_elem.inner_text() if exp_elem else ""
                    edu = await edu_elem.inner_text() if edu_elem else ""
                    
                    results.append({
                        "platform": "51job",
                        "job_name": title,
                        "salary_range": salary,
                        "req_experience": exp,
                        "req_education": edu
                    })
                
                print(f"51job page {page_num+1} scraped. Total records so far: {len(results)}")
                
                if len(results) >= target_count:
                    break
                    
                # try click next page
                try:
                    next_btn = await page.query_selector(".btn-next")
                    if next_btn:
                        is_disabled = await next_btn.get_attribute("disabled")
                        if is_disabled is not None:
                            break
                        await next_btn.click()
                        await page.wait_for_timeout(3000)
                    else:
                        break
                except Exception as e:
                    print(f"Could not go to next page: {e}")
                    break
            
            print(f"Successfully scraped {len(results)} records from 51job.")

        except Exception as e:
            print(f"51job scraping failed. Error: {e}")
            # CRITICAL: No more fallback fake data here!
            
        await browser.close()
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(script_dir, "../../reports/raw")
    os.makedirs(reports_dir, exist_ok=True)
    
    file_path = os.path.join(reports_dir, "51job.json")
    existing_data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except:
            pass
            
    combined_data = existing_data + results
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "OPPO"
    job_title = sys.argv[2] if len(sys.argv) > 2 else "算法工程师"
    target_count = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    asyncio.run(scrape(company, job_title, target_count))
