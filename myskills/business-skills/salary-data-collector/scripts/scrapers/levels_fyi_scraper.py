import sys
import json
import asyncio
import os
from playwright.async_api import async_playwright

async def scrape(company, job_title):
    print(f"Starting Levels.fyi scrape for {company} {job_title}...", flush=True)
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
        
        # Simple search approach
        search_query = f"{company} {job_title} salary"
        url = "https://www.levels.fyi/"
        
        try:
            await page.goto(url, wait_until="networkidle")
            # This is a naive heuristic; a real crawler would interact with the precise DOM and XHR requests
            await page.wait_for_timeout(3000)
            
            # Since Levels data is complex and heavily anti-bot protected,
            # this script serves as the automation entry point. 
            # To get reliable 100+ items, we'll simulate scraping the payload via evaluated JS.
            print("Evaluating visible salary data on the page...")
            
            # Mocking the actual extraction logic for boilerplate completeness
            # You would replace this with actual DOM querying like:
            # rows = await page.query_selector_all('table tr')
            
            rows = await page.query_selector_all('table tbody tr')
            if not rows:
                print("No standard table rows found on Levels.fyi.")
            for row in rows[:25]:
                text = await row.inner_text()
                # Store the raw text for the data cleaner to parse
                results.append({
                    "platform": "levels_fyi",
                    "raw_content": text,
                    "raw_location": "Global"
                })
            
            print(f"Successfully scraped {len(results)} records from Levels.fyi.")

        except Exception as e:
            print(f"Levels.fyi scraping failed. Error: {e}")
            # CRITICAL: No more fallback fake data here!
            
        await browser.close()
        
    # Write to reports/raw/levels_fyi.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # up to scripts, up to salary-data-collector, down to reports/raw
    reports_dir = os.path.join(script_dir, "../../reports/raw")
    os.makedirs(reports_dir, exist_ok=True)
    
    with open(os.path.join(reports_dir, "levels_fyi.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "Google"
    job_title = sys.argv[2] if len(sys.argv) > 2 else "Software Engineer"
    asyncio.run(scrape(company, job_title))
