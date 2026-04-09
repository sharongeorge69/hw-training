########### C A T E G O R Y #############

import requests
from parsel import Selector

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"e62d1-G1hfUiVx7ovHoi4NgrlA7xFF4ko:dtagent10331260218130851/00F:dtagent10331260218130851/00F"',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
}

response = requests.get('https://www.academy.com/', headers=headers)

sel = Selector(text=response.text)
main_category_links = sel.xpath('//ul[@class="listContainer--xTWe4 bm24--S2oVK"]//li/a/@href').getall()

