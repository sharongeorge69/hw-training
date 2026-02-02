


#=======================================
#Settings
#=======================================

BASE_URL = "https://styleunion.in/"

# Network Settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Request Settings
TIMEOUT = 20
RETRY_COUNT = 3
INITIAL_DELAY = 5


#=======================================
#Category Extraction
#=======================================

  def get_category_urls(self):
    response = requests.get(self.base_url, headers=self.headers)
    sel = Selector(text=response.text)
     # Xpath for Category Links
    category_links = sel.xpath("//div[contains(@class,'list-menu-dropdown')]//div[contains(@class,'menu__dropdown-grandchild-container')]//li/a/@href").getall()

 #========================================
 #PDP url Extraction - Crawler
 #========================================

def crawl_category(self, category_url):
    all_product_urls = []
    current_url = category_url
        

    response = requests.get(current_url, headers=self.headers, timeout=settings.TIMEOUT)
    #extract product links on current page
    product_links = set(sel.xpath('//div[contains(@id, "ProductGridContainer")]//a[contains(@href, "/products/")]/@href').getall()) # Process links - to remove duplicate links
    #Process links - to remove duplicate links
    #because same product is repeated under multiple urls for example
    #https://styleunion.in/collections/kids-bag/products/boys-printed-backpack-nkbb0002?variant=46935028990201
    #https://styleunion.in/products/boys-printed-backpack-nkbb0002?variant=46935028990201
    for link in product_links:
        full_url = urljoin(self.base_url, link)
        if "/products/" in full_url:
            prod_idx = full_url.find("/products/")
            if prod_idx != -1:
                path_and_query = full_url[prod_idx:]
                full_url = "https://styleunion.in" + path_and_query
            
            all_product_urls.append(full_url)
    #xpath for next page
    next_page_path = sel.xpath('//infinite-scroll/@data-url').get()
    if next_page_path:
        current_url = urljoin(self.base_url, next_page_path)


 #========================================
 #PDP field Extraction - parser
 #========================================

 def parse_product(self, url):
    response = requests.get(url, headers=self.headers, timeout=settings.TIMEOUT)
    sel = Selector(text=response.text)
    #xpaths for fields
    title= sel.xpath("//h1[contains(@class,'product__title')]")
    breadcrumbs_list = sel.xpath("//nav[@aria-label='breadcrumbs']//li[contains(@class, 'breadcrumbs__item')]//a[normalize-space(text())]/text()").getall()
    if breadcrumbs_list:
        breadcrumbs= " > ".join([b.strip() for b in breadcrumbs_list if b.strip()])

    price_xpaths = ["//span[contains(@class,'regular-price')]", 
                    "//div[contains(@class,'price__regular')]//span"]

    sku = sel.xpath("//p[contains(@class,'product__sku')]//b", "//p[contains(@id,'sku-')]//b")

    description = sel.xpath("//div[contains(@class,'accordion__content')]//div[contains(@class,'desc_inner')][2]//div[@class='acc__panel']")
    dim_nodes = sel.xpath("//div[contains(@class, 'form__variants')]//span[@class='color__swatch-name']")
    net_qty = sel.xpath("//input[contains(@class,'quantity__input')]/@value").get()
    fit = sel.xpath("//strong[contains(text(),'Fit')]/following-sibling::text()",
                                        "//b[contains(text(),'Fit')]/following-sibling::text()")
    care_instruction = sel.xpath("//h3[text()='Wash and Care']/following::div[@class='acc__panel'][1]")

    fabric_composition= sel.xpath("//strong[contains(text(),'Fabric')]/following-sibling::text()",
                                                        "//b[contains(text(),'Fabric')]/following-sibling::text()"])


##############################FINDINGS##############################

# URL Structure & Duplication
#    - Products appear under nested collection paths (e.g., /collections/kids-bag/products/...) 
#      AND standard paths (/products/...).

# Pagination (Infinite Scroll)
#    - The site uses infinite scroll mechanism instead of standard numbered pagination.
#    - XPATH: `//infinite-scroll/@data-url`

#  Antibot / Blocking (Feasibility)
#    - Tested with randomized User-Agents and 2-4s delays.
#    - 429 (Too Many Requests) is potential risk. Logic added to backoff (sleep * 2) if 429 encountered.

