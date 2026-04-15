import requests
from parsel import Selector
import gzip
import io
cookies = {
    'BRC': 'B',
    'sitetype': 'full',
    'AB1': 'G',
    'AD1': 'B',
    'geo': '|CALICUT|KL|IN',
    'TLTSID': '7F2E327A8CB3B788F8856BAF128F0502',
    'signin': 'C',
    'reg': 'A',
    'LDC': '7F2E327A8CB3B788F8856BAF128F0502',
    'CIP': '169.197.85.174',
    'O': '2p',
    'at_check': 'true',
    '__wwgmui': '9a94da63-6af6-4a10-a2ed-01c166e471b8',
    'JSESSIONID': '19573F329A65B1AF11020AC4FB255FF1.7383125b',
    'AMCVS_FC80403D53C3ED6C0A490D4C%40AdobeOrg': '1',
    's_ecid': 'MCMID%7C64833927038269199410694304929591633438',
    'AMCV_FC80403D53C3ED6C0A490D4C%40AdobeOrg': '1176715910%7CMCIDTS%7C20558%7CMCMID%7C64833927038269199410694304929591633438%7CMCAAMLH-1776764592%7C7%7CMCAAMB-1776764592%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776166993s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.4.0',
    's_vnc30': '1778751795041%26vn%3D1',
    's_ivc': 'true',
    'ttc': '1776159795245',
    's_cc': 'true',
    '_gcl_au': '1.1.588932221.1776159795',
    '_ga': 'GA1.1.341260612.1776159795',
    'kndctr_FC80403D53C3ED6C0A490D4C_AdobeOrg_identity': 'CiY2NDgzMzkyNzAzODI2OTE5OTQxMDY5NDMwNDkyOTU5MTYzMzQzOFIQCLHW_trYMxgBKgNWQTYwA_ABsdb-2tgz',
    'kndctr_FC80403D53C3ED6C0A490D4C_AdobeOrg_cluster': 'va6',
    'O': '2p',
    '_fbp': 'fb.1.1776160319371.391725146266805492',
    'isPickup': 'false',
    'guestRTA': 'true',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Apr+14+2026+15%3A33%3A21+GMT%2B0530+(India+Standard+Time)&version=202211.2.0&isIABGlobal=false&hosts=&consentId=e37f0ee3-fbea-4ee6-aa85-50d91c04bd68&interactionCount=1&landingPath=NotLandingPage&groups=C0004%3A1%2CC0007%3A1%2CC0003%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false',
    'mbox': 'session#6f470fe60a544d0fa4fef8be19dd00a6#1776162894|PC#6f470fe60a544d0fa4fef8be19dd00a6.34_0#1839405800',
    '_uetsid': '5d3b186037e611f1a6d785976c961dbf',
    '_uetvid': '5d3b17f037e611f1acfa8596d3852d96',
    '_ga_94DBLXKMHK': 'GS2.1.s1776159795$o1$g1$t1776161037$j19$l0$h0$dm33V7MxbGLSO9wv2lC0td2peIQHmAj4-wA',
    'datadome': '1VQiY9SV~vwfP_Ck5iwoVuWsTunioSRUTNhGcQriSvEThMOD7IaOXBtERr5L_k1cpmiHIvICqJn4Ly~9iWVfK2Vwkaz37aq_TD_iPDudqXFPd_jwEss_8n97uGdwGY7n',
    's_nr30': '1776161038337-New',
    '_dd_s': 'rum=1&id=9a154ad5-ac02-42fc-89aa-650725f1a895&created=1776159988636&expire=1776161940426',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.grainger.com/',
    'sec-ch-device-memory': '16',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="147.0.7727.55", "Not.A/Brand";v="8.0.0.0", "Chromium";v="147.0.7727.55"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    # 'cookie': 'BRC=B; sitetype=full; AB1=G; AD1=B; geo=|CALICUT|KL|IN; TLTSID=7F2E327A8CB3B788F8856BAF128F0502; signin=C; reg=A; LDC=7F2E327A8CB3B788F8856BAF128F0502; CIP=169.197.85.174; O=2p; at_check=true; __wwgmui=9a94da63-6af6-4a10-a2ed-01c166e471b8; JSESSIONID=19573F329A65B1AF11020AC4FB255FF1.7383125b; AMCVS_FC80403D53C3ED6C0A490D4C%40AdobeOrg=1; s_ecid=MCMID%7C64833927038269199410694304929591633438; AMCV_FC80403D53C3ED6C0A490D4C%40AdobeOrg=1176715910%7CMCIDTS%7C20558%7CMCMID%7C64833927038269199410694304929591633438%7CMCAAMLH-1776764592%7C7%7CMCAAMB-1776764592%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1776166993s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.4.0; s_vnc30=1778751795041%26vn%3D1; s_ivc=true; ttc=1776159795245; s_cc=true; _gcl_au=1.1.588932221.1776159795; _ga=GA1.1.341260612.1776159795; kndctr_FC80403D53C3ED6C0A490D4C_AdobeOrg_identity=CiY2NDgzMzkyNzAzODI2OTE5OTQxMDY5NDMwNDkyOTU5MTYzMzQzOFIQCLHW_trYMxgBKgNWQTYwA_ABsdb-2tgz; kndctr_FC80403D53C3ED6C0A490D4C_AdobeOrg_cluster=va6; O=2p; _fbp=fb.1.1776160319371.391725146266805492; isPickup=false; guestRTA=true; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Apr+14+2026+15%3A33%3A21+GMT%2B0530+(India+Standard+Time)&version=202211.2.0&isIABGlobal=false&hosts=&consentId=e37f0ee3-fbea-4ee6-aa85-50d91c04bd68&interactionCount=1&landingPath=NotLandingPage&groups=C0004%3A1%2CC0007%3A1%2CC0003%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false; mbox=session#6f470fe60a544d0fa4fef8be19dd00a6#1776162894|PC#6f470fe60a544d0fa4fef8be19dd00a6.34_0#1839405800; _uetsid=5d3b186037e611f1a6d785976c961dbf; _uetvid=5d3b17f037e611f1acfa8596d3852d96; _ga_94DBLXKMHK=GS2.1.s1776159795$o1$g1$t1776161037$j19$l0$h0$dm33V7MxbGLSO9wv2lC0td2peIQHmAj4-wA; datadome=1VQiY9SV~vwfP_Ck5iwoVuWsTunioSRUTNhGcQriSvEThMOD7IaOXBtERr5L_k1cpmiHIvICqJn4Ly~9iWVfK2Vwkaz37aq_TD_iPDudqXFPd_jwEss_8n97uGdwGY7n; s_nr30=1776161038337-New; _dd_s=rum=1&id=9a154ad5-ac02-42fc-89aa-650725f1a895&created=1776159988636&expire=1776161940426',
}

 ############ C R A W L E R #####################
url = "https://www.grainger.com/product-items-sitemap2.xml.gz"

response = requests.get(url, headers=headers, cookies= cookies , timeout=30)
 # Decompress gzip
with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
    xml_content = f.read().decode('utf-8')
selector = Selector(text=xml_content, type='xml')
urls = selector.xpath('//*[local-name()="loc"]/text()').getall()


############## P A R S E R ##################

import json
response = requests.get(
    'https://www.grainger.com/product/TOUCH-N-SEAL-Insulating-Spray-Foam-Sealant-801V27',
    cookies=cookies,
    headers=headers,
)
selector = Selector(text=response.text)
script_data = selector.css('script#__PRELOADED_STATE__::text').get()
data = json.loads(script_data)

product = data.get("product", {})
category = product.get("category", {})
product_details = product.get("productDetails", {})
gcom_products = product.get("gcomProducts", {})
config_all = product.get("configData", {})
digital_data = config_all.get("digitalData", {})

sku = category.get("lastVisitedProductSku")
gcom_product = gcom_products.get(sku, {})
config_data = config_all.get(sku, {})
Manufacturer_Name = product_details.get("external", {}).get("brandName")
Brand_Name = product_details.get("external", {}).get("brandName")
Manufacturer_Part_Number = product_details.get("manufacturerPartNumber")
Grainger_Item_Number = product_details.get("sku")
Item_Name = product_details.get("primaryNoun")
Full_Product_Description = product_details.get("description")
Price = (
        gcom_product.get("hybrisProductInfo", {})
        .get("price", {})
        .get("sell", {})
        .get("formattedPrice")
    )
Country_of_Origin = config_data.get("productData", {}).get("countryOfOrigin")
Unit_of_Issue = gcom_product.get("hybrisProductInfo", {}).get("uomLabel")
QTY_Per_UOI = gcom_product.get("sellPackQty")
Model_Number= gcom_product.get("hybrisProductInfo", {}).get("manufactureModelNo")

Product_Category = config_data.get("productData", {}).get("categoryName")
Stock_Status = digital_data.get("product")[0].get("productInfo", {}).get("stockStatus")
