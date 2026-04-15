
import requests
from parsel import Selector
cookies = {
    '_gid': 'GA1.2.1050393973.1776159681',
    '__kla_id': 'eyJjaWQiOiJPR1E0T0dZM1l6QXRORFk1WVMwMFl6RmpMV0V6T0RBdE1UTTFOek5rTkdVM1ptTm0ifQ==',
    '_gcl_au': '1.1.25886331.1776159682',
    '_fbp': 'fb.1.1776159682265.968210421434899477',
    'csrftoken': '0FjAq1BY5KWjJ5NxioeQaD37EcTdigYp',
    'product-list-type': 'horizontal',
    '_clck': 'hh44uh%5E2%5Eg58%5E0%5E2295',
    '_nb_sp_ses.6daf': '*',
    'ssUserId': 'abfee844-f6f8-4949-9fb3-de3b0c3c87ce',
    'ssSessionId': 'dcb42e8c-ad1f-47d1-89df-c20c7b3a5eee',
    'ssViewedProducts': '173632%2C392476%2C34469%2C523101%2C85687%2C832824%2C266087%2C19',
    '_ga': 'GA1.1.1736128707.1776159681',
    '_ga_MNNV0SMJQH': 'GS2.1.s1776221888$o3$g1$t1776225716$j60$l0$h0',
    '_uetsid': '188aa64037e611f1bdf7bdec46383a5e',
    '_uetvid': '188ac9e037e611f182f3530a75d5543b',
    '_rdt_uuid': '1776159680855.791d8c8f-df70-4ac6-a783-d03745507632',
    '_ga_M8TWSNS3RE': 'GS2.1.s1776225267$o5$g1$t1776225716$j60$l0$h0',
    '_clsk': 'drjn3k%5E1776225717550%5E5%5E1%5Ev.clarity.ms%2Fcollect',
    'recent_products': '"[266087\\054 832824\\054 85687\\054 523101\\054 34469\\054 392476\\054 172525\\054 173632]:1wCrVB:bR4yE1q9eyAbYwOscDzu6ak5HAz6-8tW_8JzkIQShAA"',
    '_nb_sp_id.6daf': '370974be-6f66-481b-89b5-e03e3274f237.1776159682.5.1776225977.1776222169.45b5c589-967a-42c2-a8f9-3d9096d88ae2',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.mrosupply.com/timing-belt-pulleys/',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    # 'cookie': '_gid=GA1.2.1050393973.1776159681; __kla_id=eyJjaWQiOiJPR1E0T0dZM1l6QXRORFk1WVMwMFl6RmpMV0V6T0RBdE1UTTFOek5rTkdVM1ptTm0ifQ==; _gcl_au=1.1.25886331.1776159682; _fbp=fb.1.1776159682265.968210421434899477; csrftoken=0FjAq1BY5KWjJ5NxioeQaD37EcTdigYp; product-list-type=horizontal; _clck=hh44uh%5E2%5Eg58%5E0%5E2295; _nb_sp_ses.6daf=*; ssUserId=abfee844-f6f8-4949-9fb3-de3b0c3c87ce; ssSessionId=dcb42e8c-ad1f-47d1-89df-c20c7b3a5eee; ssViewedProducts=173632%2C392476%2C34469%2C523101%2C85687%2C832824%2C266087%2C19; _ga=GA1.1.1736128707.1776159681; _ga_MNNV0SMJQH=GS2.1.s1776221888$o3$g1$t1776225716$j60$l0$h0; _uetsid=188aa64037e611f1bdf7bdec46383a5e; _uetvid=188ac9e037e611f182f3530a75d5543b; _rdt_uuid=1776159680855.791d8c8f-df70-4ac6-a783-d03745507632; _ga_M8TWSNS3RE=GS2.1.s1776225267$o5$g1$t1776225716$j60$l0$h0; _clsk=drjn3k%5E1776225717550%5E5%5E1%5Ev.clarity.ms%2Fcollect; recent_products="[266087\\054 832824\\054 85687\\054 523101\\054 34469\\054 392476\\054 172525\\054 173632]:1wCrVB:bR4yE1q9eyAbYwOscDzu6ak5HAz6-8tW_8JzkIQShAA"; _nb_sp_id.6daf=370974be-6f66-481b-89b5-e03e3274f237.1776159682.5.1776225977.1776222169.45b5c589-967a-42c2-a8f9-3d9096d88ae2',
}

response = requests.get(
    'https://www.mrosupply.com/timing-belt-pulleys/173632_78821022_gates-rubber/',
    cookies=cookies,
    headers=headers,
)


sel = Selector(response.text)

description = sel.xpath('//div[@class="m-accordion--item--body"]//text()').getall()
item_name =  sel.xpath('//meta[@property="og:title"]/@content').get()

