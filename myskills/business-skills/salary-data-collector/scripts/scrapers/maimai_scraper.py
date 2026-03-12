import sys
import json
import asyncio
import os
from playwright.async_api import async_playwright

async def scrape(company, job_title):
    print(f"Starting Maimai scrape for {company} {job_title}...", flush=True)
    results = []
    
    async with async_playwright() as p:
        # Try to connect to an existing Chrome instance running with --remote-debugging-port=9222
        # This allows reusing an already logged-in session.
        browser = None
        context = None
        try:
            print("Trying to connect to an existing Chrome instance on port 9222...")
            # Use connect_over_cdp to attach to an existing Chrome
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            # When connecting over CDP, contexts are already present
            context = browser.contexts[0]
            page = await context.new_page()
            print("Successfully connected to existing Chrome!")
        except Exception as e:
            print(f"Could not connect to existing Chrome ({e}). Starting a new browser instance...")
            # Fallback to launching a new non-headless browser
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
        
        try:
            import urllib.parse
            search_term = f"{company} {job_title} 爆料"
            encoded_query = urllib.parse.quote(search_term)
            target_url = f"https://maimai.cn/web/search_center?highlight=true&query={encoded_query}&type=feed"
            
            print(f"Navigating to accurate search URL: {target_url}")
            await page.goto(target_url)
            print("Waiting up to 60 seconds for page to load. Please scan QR code to log in if required...")
            
            # Wait for feed items to appear, which indicates both login success and data loaded
            await page.wait_for_selector(".feed-item", timeout=60000)
            print("Login success and results loaded! Proceeding to extract.")
            
            await page.wait_for_timeout(2000) # Buffer to let images/dom settle
            
            # Simulated scroll and extract
            # Maimai feeds require scrolling
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                
            posts = await page.query_selector_all(".feed-item")
            print(f"Found {len(posts)} posts. Extracting data...")
            
            for post in posts[:30]:
                content = await post.inner_text()
                # Basic extraction
                results.append({
                    "platform": "maimai",
                    "post_title": f"{company} {job_title} 爆料",
                    "post_content": content.replace('\n', ' '),
                    "extracted_numbers": "", # Extracted via regex or data-cleaner later
                    "post_date": "2024-03-12"
                })

            # If no actual posts due to UI changes, use fallback to prevent pipeline failure
            if not results:
                raise Exception("No posts found with selector .feed-item")

        except Exception as e:
            print(f"Maimai scraping encountered an issue: {e}")
            # CRITICAL: No more fallback fake data here!
        finally:
            await browser.close()
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(script_dir, "../../reports/raw")
    os.makedirs(reports_dir, exist_ok=True)
    
    with open(os.path.join(reports_dir, "maimai.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "ByteDance"
    job_title = sys.argv[2] if len(sys.argv) > 2 else "算法"
    asyncio.run(scrape(company, job_title))
