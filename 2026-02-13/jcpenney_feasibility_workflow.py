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
#######################CATEGORY#######################

#main category (womens, mens, juniors, kids, jewelry & watches, handbags)
CATEGORY_XPATH = '//a[@class="deptLink PTZFD"]'
category_nodes = selector.xpath(CATEGORY_XPATH)
CATEGORY_LINKFARMS = {
                "Women": ["2", "4"],
                "Men": ["2", "3"],
                "Juniors": ["1", "5"],
                "Kids": ["1", "2"],
                "Jewelry & Watches": ["1", "2", "3", "5"],
                "Handbags": ["0", "1"]
            }

#sub category(dresses, shoes, etc)
xpath = f'//div[@id="comp_linkfarm_{lf_id}"]//li/a'
links = selector.xpath(xpath)
subcategory_href = link.xpath('./@href').extract_first()

#######################PARSER#######################
url = "https://www.jcpenney.com/p/adidas-tricot-mens-big-and-tall-lightweight-track-jacket/ppr5008524658?pTmplType=regular"
response = requests.get(url, headers=headers)
data = json.loads(match.group(1).replace("undefined", "null"))
pd = data.get('productDetails', {})
lots = pd.get('lots', [])
brand_data = pd.get('brand')
description = ""
fit = ""
colors = []
sizes = set()

#description
if lots:
    lot = lots[0]
    raw_desc = lot.get('description', '')
#fit
for attr in lot.get('bulletedAttributes', []):
    desc = attr.get('description', '')
    if desc.lower().startswith("fit:"):
        fit = desc.split(':', 1)[1].strip()
#colour
color_seq = pd.get('colorSequences') or lot.get('colorSequences', [])

#size
for item in lot.get('items', []):
    for ov in item.get('optionValues', []):
        if ov.get('name', '').lower() == 'size' and ov.get('value'):
            sizes.add(ov.get('value').title())
    if item.get('size'):
        sizes.add(item.get('size').title())

#images
images = [img['url'] for img in pd.get('images', []) if isinstance(img, dict) and 'url' in img]

#rating and reviews
rating = valuation.get('rating')
reviews = valuation.get('reviews', {}).get('count', 0)

#price_api            
price_url = f"https://browse-api.jcpenney.com/v2/product-aggregator/{pd.get('id')}/additional-details?deliveryAvailabilityCheckRequired=false&GPA=false"


#################FINDINGS#######################

#the site has pagination cap issues
#There is not prices for some products it shows add to cart for the prices to be visible


        







