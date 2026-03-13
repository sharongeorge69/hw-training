######################  CRAWLER  ######################

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}
cookies = {
        'TS0113bcfc': '016303f95522b86a6a52be2e196f06b189f358610d64b968c52cd52c41da63d0489084c922acddb63ea037dc30f217a0527cdf62a8',
        'reese84': '3:pTr4TW2l3yhR+7Ek4xc/7g==:ccMe0thMYchmBALl1L3xskEcVTaCLCF8UwbnR2pSTSdyM0RqVbfafGsBLNdh+soMPzXIdeuaMICro+9owEiVKZ+o4+t3yHSEyoWCqiaZ/wRR5RQGnTQOltgmp5qoNTNLmFrB6HIeq8q1sPxSjwcWe4XgL+nCXU4qaw8Si4Q+6qiiHIjEnxpEWngzPin5OvG08PWZA+yO5Tmg9qccvO2op6qPhHPazpFF7CqmLPRLqHK/ZKRYM8QjNOdWL/Z+hWJwdziBbFobEq2EjwgN2qFxY/8AQYornN6OROJAVxkFR6VTOGl2ITohY53SVY23TXGbeebIodqon8j35wnTbuTAzLqGs0OWd37MOsHjrf5svM0ih9tdSmz3CtJ1zWy643d4utkyGYlzDv1ZbJjnpIBYQnl/hBb4Y8iq1+vx7JTgTL5MCN5ads+eWd88tz++hScm+VEbGjKytSJaIvOF2noY4w==:IW+o8roYHTi9ywvtA/iMO5ppPq6bqVzVwJEmj+sqeVY=',
        'TS01ea2401': '016303f95543e2876d6b6078e7397eb87e70c2dd428588536ebfb891b1ff86a875a41773103c18098a345a375b3de6a463dd238137',
        'OptanonAlertBoxClosed': '2026-03-11T06:11:55.946Z',
        '_fbp': 'fb.1.1773209516648.826884414131233127',
        '_gcl_au': '1.1.257700418.1773209517',
        'AMCV_FA4C56F358B81A660A495DE5%40AdobeOrg': 'MCMID|38126559327142789600315638631472783660',
        'tms_storeperma': 'eyJhZG9iZV9lY2lkIjoiMzgxMjY1NTkzMjcxNDI3ODk2MDAzMTU2Mzg2MzE0NzI3ODM2NjAifQ%3D%3D',
        '_hjSessionUser_137278': 'eyJpZCI6IjhmMjY1ZjY4LTA5ZGYtNTAyYi1iY2FjLTMyOTkxNDc0ZWY4MiIsImNyZWF0ZWQiOjE3NzMyMDk1MTcxNjksImV4aXN0aW5nIjp0cnVlfQ==',
        '_hjSession_137278': 'eyJpZCI6IjMyMDU3MDVjLTk1YzgtNDI4MS05NmNiLTJmMTdjNzU3YzM4NSIsImMiOjE3NzMyMDk1MTcxNzAsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=',
        '_pin_unauth': 'dWlkPU5qRXdaamM1TnpjdE5tSm1OaTAwWXpRNUxXSXdZamt0WTJFM1pXRTJOams0TkRKag',
        'tfpsi': 'dd4504ab-4d9f-4717-a0af-fcb3faef45e9',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Mar+11+2026+11%3A48%3A45+GMT%2B0530+(India+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=e6301ae2-efd5-4f40-8a89-52d41ec2d98d&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&geolocation=%3B&AwaitingReconsent=false',
        'dtCookie4ik80me8': 'v_4_srv_5_sn_6F6F529871E6B59EC09B1223D92FE0AF_perc_100000_ol_0_mul_1_app-3A8907cbcdb73fbef3_1',
        '_uetsid': '351813e01d1111f1a8a31579d7d99750',
        '_uetvid': '351828b01d1111f18ea3c9702d6e0056',
        'utag_main': 'v_id:019cdb85ba4f0022d00e1906bd6005065004805d00bd0$_sn:1$_se:65$_ss:0$_st:1773211785096$ses_id:1773209500239%3Bexp-session$_pn:4%3Bexp-session$dc_visit:1$dc_event:11%3Bexp-session$dc_region:eu-central-1%3Bexp-session',
    }
base_url = "https://apip.colruyt.be/gateway/emec.colruyt.protected.bffsvc/cg/nl/api/product-search-prs"

from curl_cffi import requests
skip = 0
total_found = None
page_size = 22
all_products = []
params = {
            'placeId': 604,
            'skip': skip,
            'size': page_size,
            'sort': 'relevancy asc',
            'isAvailable': 'true'
        }
response = requests.get(base_url,headers=headers,cookies = cookies,impersonate="chrome120", params=params)
data = response.json()
products = data.get('products', [])
art_num = products.get('commercialArticleNumber')
pdp_url = f"https://www.colruyt.be/nl/producten/{art_num}" if art_num else None


######################  PARSER  ######################


from curl_cffi import requests
url = "https://apip.colruyt.be/gateway/emec.cust.prdretr.extsvcv3/v3/nl/api/products/detail"
params = {
            'placeId': '604',
            'clientCode': 'CLP',
            'ensignCountryCode': '8_BE',
            'technicalArtNo': tech_art_no,
            'dataGroup': 'ALL',
        }
        
resp = requests.get(url, params=params, impersonate="chrome110", timeout=20)
product_details = resp.json()
brand = product_details.get('brand', '')
name = product_details.get('name', '')
product_name = f"{brand} {name}"
competitor_name = "colruyt"

grammage_quantity = ""
grammage_unit = ""
match = re.match(r'([\d,\.]+)([a-zA-Z]+)', content)
if match:
    grammage_quantity = match.group(1) 
    grammage_unit = match.group(2)

#producthierarchy
categories = product_details.get("categories", [])
name = product_details.get("name", "") 
brand = product_details.get("brand", "")

levels = []              

node = categories[0] if categories else None
levels.append(node.get("name"))
children = node.get("children")         
node = children[0] if children else None
levels.append(f"{brand} {name}")   
breadcrumb = " > ".join(levels) if levels else ""

price = product_details.get('price')
if isinstance(price, dict):
    basicPrice = price.get('basicPrice')
    quantityPrice = price.get('quantityPrice') if price.get('quantityPrice') else ""
    quantityPriceQuantity = price.get('quantityPriceQuantity') if price.get('quantityPriceQuantity') else ""
regular_price = str(basicPrice)
selling_price = regular_price

promotion_valid_from = str(product_details.get('publicationStartDate', ''))
promotion_valid_upto = str(product_details.get('publicationEndDate', ''))
price_valid_from = promotion_valid_from
price_per_unit = str(product_details.get('measurementUnitPrice', ''))
description_raw = product_details.get("description", "")
image_url_1 = str(product_details.get('fullImage', ''))
allergens_data = product_details.get("allergenAttributes", {})

promotion_description = ""
if quantityPrice:
    promotion_description = f"{quantityPrice} vanaf {quantityPriceQuantity} st"

product_unique_key = f"{unique_id}P"


######################## FINDINGS #############################

#1. Crawler api works locally(not in server) but has blocking issues
#2.Promotion api as blocking issues
 
