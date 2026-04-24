import json
import os
import time
import asyncio
from camoufox.async_api import AsyncCamoufox
import requests

COOKIES_FILE = "msc_cookies.json"

class MSCSessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.load_cookies()

    def load_cookies(self):
        if os.path.exists(COOKIES_FILE):
            try:
                with open(COOKIES_FILE, "r") as f:
                    saved = json.load(f)
                    self.session.cookies.update(saved.get("cookies", {}))
                    self.headers['user-agent'] = saved.get("user_agent", self.headers['user-agent'])
            except Exception as e:
                print(f"Error loading cookies: {e}")

    def save_cookies(self, cookies_dict, user_agent):
        print(f"Saving new session to {COOKIES_FILE}...")
        with open(COOKIES_FILE, "w") as f:
            json.dump({
                "cookies": cookies_dict, 
                "user_agent": user_agent,
                "timestamp": time.time()
            }, f, indent=4)

    def is_session_valid(self):
        """Test if current cookies work on a product page."""
        test_url = "https://www.mscdirect.com/"
        try:
            # We check the home page for a simpler footprint
            res = self.session.get(test_url, headers=self.headers, timeout=15)
            if res.status_code == 200 and "Pardon Our Interruption" not in res.text:
                return True
        except Exception:
            pass
        return False

    async def _refresh_via_browser(self):
        """Launches Camoufox to solve the WAF and grab new cookies."""
        print("\n[!] Session expired. Refreshing via Camoufox...")
        async with AsyncCamoufox(headless=False, humanize=True) as browser:
            page = await browser.new_page()
            await page.goto("https://www.mscdirect.com/")
            
            # Wait for the "Pardon Our Interruption" to go away
            success = False
            for _ in range(15):
                title = await page.title()
                content = await page.content()
                if "Pardon Our Interruption" not in title and "msc-logo" in content:
                    success = True
                    break
                await asyncio.sleep(5)
            
            if not success:
                print("Failed to clear WAF in time.")
                return False

            browser_cookies = await page.context.cookies()
            cookies_dict = {c['name']: c['value'] for c in browser_cookies}
            user_agent = await page.evaluate("navigator.userAgent")
            
            self.save_cookies(cookies_dict, user_agent)
            self.session.cookies.update(cookies_dict)
            self.headers['user-agent'] = user_agent
            return True

    def get_session(self):
        if not self.is_session_valid():
            asyncio.run(self._refresh_via_browser())
        return self.session, self.headers

if __name__ == "__main__":
    manager = MSCSessionManager()
    session, headers = manager.get_session()
    res = session.get("https://www.mscdirect.com/product/details/44533321", headers=headers)
    print(f"Verification Results - Status: {res.status_code}")
    if res.status_code == 200 and "Pardon Our Interruption" not in res.text:
        print("Success: Session is valid and data is accessible.")
    else:
        print("Failure: Session is still blocked.")
