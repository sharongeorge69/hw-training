import requests
from parsel import Selector
from playwright.sync_api import sync_playwright

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

url = "https://www.jcpenney.com/p/adidas-tricot-mens-big-and-tall-lightweight-track-jacket/ppr5008524658?pTmplType=regular"
response = requests.get(url, headers=headers)
selector = Selector(text=response.text)

productname = selector.xpath('//h1[@data-automation-id="product-title"]/text()').getall()

brand = selector.xpath('//p[@data-automation-id="at-brand-link-block"]//a[@data-automation-id="at-brand-link-btn"]//text()').get()

with sync_playwright() as p:
        browser = p.firefox.launch(headless=True) # use firefox
        context = browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        unique_id = re.search(r'ppr\d+', url)
        product_name= page.locator('h1[data-automation-id="product-title"]').inner_text().strip()
        brand = page.locator('[data-automation-id="at-brand-link-btn"]').inner_text().strip()
        desc= page.locator('[id="productDescriptionContainer"]')
        description = desc.inner_text().strip()
        image_url= page.locator('img[data-automation-id="ProductImageZoom"]')
        image = image_url.first.get_attribute('src')


        content = page.content()
        sel = Selector(text=content)
        selling_price = sel.xpath('//span[@data-automation-id="at-price-value"]/text()').get()
        regular_price = sel.xpath('//span[@data-automation-id="price-original-price"]/text()').get()
        discount = sel.xpath('//span[@data-automation-id="price-percent-off"]/text()').get()
        color_text = sel.xpath('string(//div[@data-automation-id="color"])').get()


            

        


        







