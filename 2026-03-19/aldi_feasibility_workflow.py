################## C R A W L E R ##################
import requests
from parsel import Selector

url = "https://www.aldi.be/nl/producten/assortiment/alcoholvrije-dranken.html","https://www.aldi.be/nl/producten/assortiment/alcoholvrije-dranken/energy-drinks-sportdrank.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

response = requests.get(url, headers=headers, timeout=5)
selector = Selector(text=response.text)
snippet_url = selector.xpath("//div[@data-tile-url]/@data-tile-url").getall()

base = "https://www.aldi.be"
category_hash = url.split("aldi.be")[1].replace(".html", "")

match = re.search(r"snippet-(.*)\.shoppinglisttile", snippet_url)
product_id = match.group(1)
final_url = f"{base}/nl/p/artikel-{product_id}.article.html#{category_hash}"

################## P A R S E R ##################
import requests
from parsel import Selector
sel = Selector(text=response.text)
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }
url = "https://www.aldi.be/nl/p/energydrink-120-1-0.article.html#/nl/producten/assortiment/alcoholvrije-dranken/energy-drinks-sportdrank"
response = requests.get(url, headers=headers)
brand = sel.xpath(
    "//span[contains(@class,'mod-article-intro__header-headline-small')]/text()"
).get()


product_name = sel.xpath(
    "normalize-space(//div[contains(@class,'mod-article-intro__header-headline')]//h1/text()[normalize-space()])"
).get()

product_description = sel.xpath(
    "normalize-space(//div[contains(@class,'rte')]//p)"
).get()

regular_price = sel.xpath(
    "normalize-space(//div[contains(@class,'price')]//span[contains(@class,'price__wrapper')])"
).get()
selling_price = sel.xpath(
    "normalize-space(//div[contains(@class,'price')]//span[contains(@class,'price__wrapper')])"
).get()

grammage_quantity = sel.xpath(
    "normalize-space(//span[contains(@class,'price__unit')])"
).get()
grammage_unit = sel.xpath(
    "normalize-space(//span[contains(@class,'price__unit')])"
).get()
breadcrumbs = sel.xpath(
    "//ol[contains(@class,'mod-breadcrumb__nav')]//li//span/text()"
).getall()
currency = "EUR"
image = sel.xpath(
    "//div[contains(@class,'mod-gallery-article__stage')]//a[contains(@class,'has-lightbox')]/@href"
).get()