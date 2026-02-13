import requests
from parsel import Selector

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}








#######################PARSER#######################

url = "https://www.jcpenney.com/p/stafford-big-and-tall-coolmax-all-season-oxford-mens-button-down-collar-long-sleeve-stretch-fabric-wrinkle-free-dress-shirt/ppr5008282312?pTmplType=regular"
response = requests.get(url, headers=headers)
selector = Selector(text=response.text)

productname = selector.xpath('//h1[@data-automation-id="product-title"]/text()').getall()
cleaned_productname = "".join(productname).strip()

brand = selector.xpath('//p[@data-automation-id="at-brand-link-block"]//a[@data-automation-id="at-brand-link-btn"]//text()').get()
cleaned_brand = "".join(brand).strip()
print(brand)








