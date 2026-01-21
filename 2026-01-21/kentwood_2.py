import json
import time
from curl_cffi import requests
from parsel import Selector

# Configuration
URL = "https://www.kentwood.com/CMS/CmsRoster/RosterSearchResults"
OUTPUT_FILE = "kentwood_agents.json"
PAGE_SIZE = 10

# Headers for API List (Use the ones that worked for list)
# Note: The user provided diff headers for list vs bio, but let's try to use the FRESH ones for both if possible, 
# or keep separate if needed. The list headers in kentwood_2.py worked fine. 
# Let's use the BIO headers for the bio requests specifically since they are proven for that endpoint.

# New Headers for BIO (PROFILE) Scanning - Using these for LIST too as they are fresh
BIO_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': 'subsiteID=278950; subsiteDirectory=; culture=en; ASP.NET_SessionId=ehj5hdkcmfzu3tamdzozw2sj; currencyAbbr=USD; currencyCulture=en-US; _gid=GA1.2.990041556.1768970341; OptanonAlertBoxClosed=2026-01-21T04:39:05.102Z; _hjSessionUser_2481254=eyJpZCI6ImFkMDcwMjZlLTc4NGQtNWI4NS04MTY1LTM3MGY1NDMyNTM4YiIsImNyZWF0ZWQiOjE3Njg5NzAzNDE2MzYsImV4aXN0aW5nIjp0cnVlfQ==; _cfuvid=Qpwegm2bPTrGwsR4uIGx9IW62PJabeSHFLE2ftuJUp0-1768986326444-0.0.1.1-604800000; rnSessionID=662124604422120032; _hjSession_2481254=eyJpZCI6IjZlYzY0MDExLTU1YjYtNGJmZS04MDRmLTRkYzRiZTYyZTUxYiIsImMiOjE3Njg5OTA4MTUwMjgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; __cf_bm=D_CZmzg.pETM4_53ky8g_L2Wj6g.OmSabJHwzgpVFHE-1768995258-1.0.1.1-7wTRJWi.rYaElLs6kmRlKRmqEx3tASFszA73LGd5h4TSUTVEga1pQbUwC1qL4ilOdzpKMSvOQrsXsKGZHtq2RXjDJs8V.qgAJN18AFMcbic; cf_clearance=P2KUzTU1uFeK33fU67kxhDCqyAvoO9Qrif3FIRldizY-1768995263-1.2.1.1-2_6RV0y59c0jppHPsm2KBSRiQvTB1cCpN6Rwc.VSkcnpWSbkT3SRLqOmNC7epNp71gfEJVgIGFc6jqEjE3SmnK_ij3aCxsTs1m0TaknwVBsGhcKzMEwA0H26.7fmfboWgIPVCQMmpxrVeX2ly0n0uP3wK756CtLIzz__7i_kxIsEKneHHrqwb3FllaR6xX8ikrWbDNWWubTKs1pKPEhPLfcGX7MRbOwh..ihUq9BSjKRcCH0XvSOJcvn6u_ZKOWC; _ga=GA1.1.812340961.1768970341; _ga_X66CHF3N5R=GS2.1.s1768989700$o4$g1$t1768995469$j59$l0$h0; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jan+21+2026+17%3A07%3A49+GMT%2B0530+(India+Standard+Time)&version=202509.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0003%3A1%2CC0001%3A1%2CC0005%3A1%2CC0002%3A1%2CC0004%3A1%2COSSTA_BG%3A1&geolocation=IN%3BKL&AwaitingReconsent=false',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"143.0.7499.169"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="143.0.7499.169", "Chromium";v="143.0.7499.169", "Not A(Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-ua-platform-version': '""',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
}

LIST_HEADERS = BIO_HEADERS.copy()
LIST_HEADERS["referer"] = "https://www.kentwood.com/roster/agents/"

# New Headers for BIO (PROFILE) Scanning
BIO_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': 'subsiteID=278950; subsiteDirectory=; culture=en; ASP.NET_SessionId=ehj5hdkcmfzu3tamdzozw2sj; currencyAbbr=USD; currencyCulture=en-US; _gid=GA1.2.990041556.1768970341; OptanonAlertBoxClosed=2026-01-21T04:39:05.102Z; _hjSessionUser_2481254=eyJpZCI6ImFkMDcwMjZlLTc4NGQtNWI4NS04MTY1LTM3MGY1NDMyNTM4YiIsImNyZWF0ZWQiOjE3Njg5NzAzNDE2MzYsImV4aXN0aW5nIjp0cnVlfQ==; _cfuvid=Qpwegm2bPTrGwsR4uIGx9IW62PJabeSHFLE2ftuJUp0-1768986326444-0.0.1.1-604800000; rnSessionID=662124604422120032; _hjSession_2481254=eyJpZCI6IjZlYzY0MDExLTU1YjYtNGJmZS04MDRmLTRkYzRiZTYyZTUxYiIsImMiOjE3Njg5OTA4MTUwMjgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; __cf_bm=D_CZmzg.pETM4_53ky8g_L2Wj6g.OmSabJHwzgpVFHE-1768995258-1.0.1.1-7wTRJWi.rYaElLs6kmRlKRmqEx3tASFszA73LGd5h4TSUTVEga1pQbUwC1qL4ilOdzpKMSvOQrsXsKGZHtq2RXjDJs8V.qgAJN18AFMcbic; cf_clearance=P2KUzTU1uFeK33fU67kxhDCqyAvoO9Qrif3FIRldizY-1768995263-1.2.1.1-2_6RV0y59c0jppHPsm2KBSRiQvTB1cCpN6Rwc.VSkcnpWSbkT3SRLqOmNC7epNp71gfEJVgIGFc6jqEjE3SmnK_ij3aCxsTs1m0TaknwVBsGhcKzMEwA0H26.7fmfboWgIPVCQMmpxrVeX2ly0n0uP3wK756CtLIzz__7i_kxIsEKneHHrqwb3FllaR6xX8ikrWbDNWWubTKs1pKPEhPLfcGX7MRbOwh..ihUq9BSjKRcCH0XvSOJcvn6u_ZKOWC; _ga=GA1.1.812340961.1768970341; _ga_X66CHF3N5R=GS2.1.s1768989700$o4$g1$t1768995469$j59$l0$h0; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jan+21+2026+17%3A07%3A49+GMT%2B0530+(India+Standard+Time)&version=202509.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0003%3A1%2CC0001%3A1%2CC0005%3A1%2CC0002%3A1%2CC0004%3A1%2COSSTA_BG%3A1&geolocation=IN%3BKL&AwaitingReconsent=false',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"143.0.7499.169"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="143.0.7499.169", "Chromium";v="143.0.7499.169", "Not A(Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-ua-platform-version': '""',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
}

def clean_text(text):
    if not text:
        return ""
    return text.replace("\r", " ").replace("\n", " ").strip()

def parse_name(full_name):
    if not full_name:
        return "", "", ""
    parts = full_name.split()
    first_name = parts[0] if parts else ""
    middle_name = ""
    last_name = ""
    if len(parts) > 2:
        middle_name = parts[1]
        last_name = " ".join(parts[2:])
    elif len(parts) == 2:
        last_name = parts[1]
    return first_name, middle_name, last_name

def scrape_agents():
    agents = []
    
    # Check if we already have the list (to save time/requests)
    # But user asked to write code that returns the data, assuming full run.
    # We will reuse the list fetching logic.
    
    page_number = 1
    total_count = None

    print("--- Phase 1: Scraping Agent List ---")
    
    # To reduce risk of spamming getting blocked, maybe limit for test? 
    # But we want 197 agents.
    
    while True:
        print(f"Fetching page {page_number}...")
        params = {
            "layoutID": "956",
            "pageSize": str(PAGE_SIZE),
            "pageNumber": str(page_number),
            "sortBy": "firstname"
        }

        try:
            response = requests.get(URL, params=params, headers=LIST_HEADERS, impersonate="chrome120")
            
            if response.status_code != 200:
                print(f"Failed to fetch page {page_number}: {response.status_code}")
                break

            data = response.json()
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            if total_count is None:
                total_count = data.get("TotalCount", 0)
                print(f"Total Agents: {total_count}")

            html_content = data.get("Html", "")
            if not html_content:
                print("No HTML content found. Stopping.")
                break

            sel = Selector(text=html_content)
            cards = sel.css('article.rng-agent-roster-agent-card')
            if not cards: cards = sel.css('.rn-agent-roster-item')
            
            if not cards:
                print("No agents found on this page. Stopping.")
                break

            for card in cards:
                # Basic Info
                name_text = card.css('h1.rn-agent-roster-name::text').get()
                full_name = clean_text(name_text)
                first, middle, last = parse_name(full_name)
                
                profile_path = card.css('a.btn.button.hollow::attr(href)').get()
                profile_url = f"https://www.kentwood.com{profile_path}" if profile_path else "N/A"

                image_url = card.css('img::attr(src)').get()
                if image_url and not image_url.startswith("http"):
                    image_url = f"https://www.kentwood.com{image_url}"

                # Office & Address
                office_name = clean_text(card.css('p strong::text').get())
                p_text_nodes = card.xpath('.//p//text()').getall()
                address_cleaned = " ".join([clean_text(t) for t in p_text_nodes if clean_text(t) and clean_text(t) != office_name and "Directions" not in t])
                address_cleaned = address_cleaned.rstrip(" |")

                # Phones
                office_phone_xp = card.xpath('.//i[contains(@class, "fa-building")]/parent::*/text()').getall() 
                office_phone = "".join([clean_text(t) for t in office_phone_xp])
                
                agent_phone_xp = card.xpath('.//i[contains(@class, "fa-user")]/following-sibling::text()').get()
                agent_phone = clean_text(agent_phone_xp) if agent_phone_xp else ""
                if not agent_phone and agent_phone_xp is None:
                     agent_phone_xp = card.xpath('.//i[contains(@class, "fa-user")]/parent::*/text()').getall()
                     agent_phone = "".join([clean_text(t) for t in agent_phone_xp])
                
                office_phone = office_phone if office_phone else "N/A"
                agent_phone = agent_phone if agent_phone else "N/A"

                # Social Media
                social_links = []
                social_elements = card.css('li.rng-agent-profile-contact-social a::attr(href)').getall()
                for link in social_elements:
                    if link:
                        social_links.append(link)

                agent = {
                    "first_name": first,
                    "middle_name": middle,
                    "last_name": last,
                    "profile_url": profile_url,
                    "image_url": image_url,
                    "office_name": office_name,
                    "address": address_cleaned,
                    "agent_phone_numbers": [agent_phone] if agent_phone != "N/A" else [],
                    "office_phone_numbers": [office_phone] if office_phone != "N/A" else [],
                    "social": social_links,
                    "description": "N/A", 
                    "mail_id": "N/A"      
                }
                agents.append(agent)

            print(f"Collected {len(agents)} agents so far.")

            if len(agents) >= total_count:
                print("Reached total count.")
                break
            
            page_number += 1

        except Exception as e:
            print(f"Error on page {page_number}: {e}")
            break


    print("\n--- Phase 2: Secondary Mining (Descriptions) ---")
    
    # We use BIO_HEADERS here.
    # Be careful with rate limiting
    
    count = 0
    for agent in agents:
        p_url = agent["profile_url"]
        if p_url == "N/A":
             continue
        
        count += 1
        print(f"[{count}/{len(agents)}] Visiting {p_url}...")
        
        try:
             # Add referer dynamically? Or stick to static?
             # User's curl had a specific tk in referer, might be important or might expire.
             # We'll try just the base url as referer or the previous one
             headers = BIO_HEADERS.copy()
             headers["referer"] = p_url # Self-referencing sometimes works or just domain
             
             resp_bio = requests.get(p_url, headers=headers, impersonate="chrome120")
             
             if resp_bio.status_code == 200:
                 sel = Selector(text=resp_bio.text)
                 xpath = "//div[starts-with(@id, 'widget-text-1-preview-5503-')]"
                 desc_node = sel.xpath(xpath)
                 if desc_node:
                     text_content = desc_node.xpath(".//text()").getall()
                     desc_text = " ".join([t.strip() for t in text_content if t.strip()])
                     agent["description"] = desc_text
                     print("  > Description Found!")
                 else:
                     print("  > No description text found (Selector mismatch).")
             else:
                 print(f"  > Failed: {resp_bio.status_code}")
        
        except Exception as e:
            print(f"  > Error: {e}")
            
        # Sleep to avoid rapid bans
        time.sleep(1.0)
        
        # Save incrementally or check? 
        # For now, we wait till end or interrupt.

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(agents)} agents to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_agents()
