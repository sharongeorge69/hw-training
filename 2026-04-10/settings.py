import requests
from parsel import Selector

# Use standard browser headers for HTML page request
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,ml;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://mercatoronline.si/brskaj',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

url = 'https://mercatoronline.si/brskaj'

print(f"Fetching {url}...")
try:
    response = requests.get(url, headers=headers, timeout=20)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        sel = Selector(text=response.text)
        category_names = sel.xpath('//li[contains(@class, "lib-category-menu-top")]/a/@data-analytics-label').getall()
        category_ids = sel.xpath('//li[contains(@class, "lib-category-menu-top")]/@data-category-id').getall()
        
        print(f"\nFound {len(category_names)} categories:")
        for name, cid in zip(category_names, category_ids):
            print(f"ID: {cid} | Name: {name}")
            
    else:
        print("Failed to fetch page.")
        # Print a snippet of the response if it's an error
        print("\nResponse snippet:")
        print(response.text[:500])

except Exception as e:
    print(f"Error: {e}")
