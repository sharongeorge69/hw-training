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
subcategory_xpath = sel.xpath('//div[@role="list"]//a[@data-auid="subCategoryLinks_LP"]/@href').getall()


#############  C R A W L E R ############

CATEGORY_ID = "15054"
BASE_CATEGORY_URL = "https://www.academy.com/c/mens/mens-apparel"

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'channel': 'web',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'cookie': '_vuid=78632572-d83c-4dfa-a21a-4caff8b17765; USERTYPE=G; enablePriceRangeAttributes=true; enableShowPriceSwatch=true; ACADEMY_PLCC_USER=true; rxVisitor=177570782430014JBC4DOJALOQ623M502C59UV47C0A32; mt.v=2.567925382.1775707824308; _ALGOLIA=anonymous-d56d8667-6d1f-40ad-b158-52cb0652ecdd; c_uuid=250118664537361460005373651080192024; utag_main_v_id=019d706f251b0001e6510d0a60e905065001805d00bd0; utag_main_vapi_domain=academy.com; AMCVS_606441B5546CD33C0A4C98A7%40AdobeOrg=1; _gcl_au=1.1.584548683.1775707826; cscv=default; crl8.fpcuid=8e06243f-f632-4749-ab90-7b2cf89407bd; s_ecid=MCMID%7C64440751200181166660663997108339536929; s_cc=true; _pxvid=099dc5da-33ca-11f1-bd40-500daf94171b; pxcts=099dcde3-33ca-11f1-bd40-04805287997c; _fbp=fb.1.1775707826558.586288965600559795; ltkSubscriber-Signup=eyJsdGtDaGFubmVsIjoiZW1haWwiLCJsdGtUcmlnZ2VyIjoibG9hZCJ9; ltkSubscriber-GXPMonetate=eyJsdGtDaGFubmVsIjoiZW1haWwiLCJsdGtUcmlnZ2VyIjoibG9hZCJ9; __pxvid=09e2c5f4-33ca-11f1-9689-36131c18288c; GSIDc6dmlqeqKI30=ba9205cb-b5b0-4e79-a91f-5f85f2ee4328; STSIDc6dmlqeqKI30=996988d2-c8e6-493f-a8ff-6677f2122170; xdVisitorId=1186IBKg_lxxcuyt_5-1Vgs4UxjNZq_ufOuWm2XGbXQyWXY0B4F; atgRecVisitorId=1186IBKg_lxxcuyt_5-1Vgs4UxjNZq_ufOuWm2XGbXQyWXY0B4F; QuantumMetricUserID=60d1f167777ec9abf160e088f932fc8d; academy_clarip_consent=0,1,2,3; contentstack=true; dtCookie=v_4_srv_7_sn_PT5O7LF6BJA5N3FMEVI6EOPGGRR8LUIK_app-3Ac941cf92b69f2e35_1_ol_0_perc_100000_mul_1; sddStoreId=; styliticsWidgetSession=32f4582c-8671-4f87-b267-f1fc7195bc9a; BVBRANDID=9edd4158-7715-4fff-b256-e869d0bd55d9; s_fid=78183744D9D36940-1153298497B034A0; s_vi=[CS]v1|34EB9BA830DF67BC-4000115A4032F221[CE]; klarnaTender=true; dMOnQV=true; atClEn=false; guestFavorite=true; ecp=Y:Y:Y; enableXCCPromotion=true; _pxhd=S5Wd2y1PebEbu26Q/UKXfPFt58SodKvkujPRhcxUM2nF9GF4eEYkXm80z/DmpTD/muHL/skA0kFT7E3/Y1as6Q==:bUt30GeCV-rIlm7rYFo4nuxF0sWoG986ucqxbz6wpQXXfW4Zs0CoNBs3oT5yFgsT1xVkDmZ4rPyWTYV6bU1GjXFt8TewdsW3G2avwZjPYzA=; LAT_LONG=46.06,14.51; utag_main__sn=2; utag_main_ses_id=1775721389991%3Bexp-session; utag_main_academy_visitorId=guest%3Bexp-session; utag_main__ss=0%3Bexp-session; s_inv=7678; s_vnc365=1807257392581%26vn%3D2; s_ivc=true; utag_main_dc_visit=2; utag_main_dc_region=eu-central-1%3Bexp-session; AMCV_606441B5546CD33C0A4C98A7%40AdobeOrg=179643557%7CMCIDTS%7C20553%7CMCMID%7C64440751200181166660663997108339536929%7CMCAAMLH-1776326193%7C6%7CMCAAMB-1776326193%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1775728593s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0; utag_main_qm_replay_sent=1775721389991%3Bexp-session; QuantumMetricSessionID=42904ce83327c8b465374d564ae53741; akamai_ch=A; enableCheckoutSignInOtp=true; s_ips=993; lcontentstack=ckt|ord|act; kount360Enabled=false; stack=400; akaalb_Default-ALB-production=1775727347~op=wwwDefaultALB:PROD1EAST|~rv=16~m=PROD1EAST:0|~os=b7cd39262b6e2f76bba2f46a7a88a486~id=d4153a6ae4b785d341f449eae0816bf1; correlationId=AA-vNNnMiO2aNX7IDaAP98VhxCpAmxuyhkJ; utag_main__pn=13%3Bexp-session; BVBRANDSID=7da592e3-82a8-4253-8e53-270fa55e8532; atgRecSessionId=isFxfaf3v1SCD5Vz9Lf5_nBgJ3zYPBoxV_7xnGXz7BHZTpqgtulR!1869869958!-1909555317; fw_se={%22value%22:%22fws2.0cbbb42b-4dda-49c4-95ed-158899ee8ea0.4.1775725560236%22%2C%22createTime%22:%222026-04-09T09:06:00.236Z%22}; fw_uid={%22value%22:%226b3d8a9e-9b61-4a51-9593-4fb2ca3d7f19%22%2C%22createTime%22:%222026-04-09T09:06:00.240Z%22}; _px3=d2c9de4683d5b350bd1b169c109b14953c36f091a5a41634cc6faee8493d37c3:emLL81XF1KGotzSdx2i9s5RHOr8BJw7xVVvzQTmd7jb21ZbdeMn17loqjhx+KOPBAF+lryCY0iUU7pqbUzoYRw==:1000:lkLfnSC/u00in8VDgDELgMIXy6HBQure9ACoYkcMRZP1nyH8M28cJSyrPPmy3Lslak0sgOhHUWdSFm/CxM5kLDSm7dT2NseoWQQJpOeWg9KR18hoTOanIrsjJBEzxjEITQiJaKEac8ZodfMtvJORqnHVFJz78qZhyZnjNJDH58d/lOWu/xFG3wDaz5vIOWCe8EDwxnGgj1Fjy7z63pEKgypxySpKzmmOD7T2oBw7Qloxez0hBY/tI5u+dPCNXDIuy9gzJia6giEKNHCvPGca1Wojdck1W6/SZN1WZyjx5T9LL5Yq8VIx0WB28u7x6LNTWeU2m+0wamI+e2SEAu2KvS3N/XIrxxr0ZXk0CaTSnT11eCTLllVYjl/e8TFAxLpheRtJPO+l65y8K9NVZZJjztSbS2+Qp+QOuTR/D0rZCrkzsjA6vPzwCUJpvuFQFelcAtQLBIWk7PpvvWWQMSnlFUMxotmHkYFuvRgQWxAAkeY=; _uetsid=09b9013033ca11f18c7ba7d2b4a934fc; _uetvid=09b90d8033ca11f189f2dbf2b4827473; fw_bid={%22value%22:%225LNmzk%22%2C%22createTime%22:%222026-04-09T09:06:01.325Z%22}; ltk-product-QOH=0; rxvt=1775727365135|1775720921460; s_tp=3616; s_ppv=heydude%2520mens%2520wally%2520holiday%2520print%2520warmth%2520slip-on%2520shoes%2520%257C%2520academy%2C27%2C27%2C993%2C1%2C3; dtPC=7$325548693_953h-vJFETSVQFIPHIPIJAPCCMMCUFUMHRIULP-0e0; _br_uid_2=uid%3D1142251380776%3Av%3D17.1%3Ats%3D1775707828148%3Ahc%3D68; utag_main__se=73%3Bexp-session; utag_main__st=1775727367139%3Bexp-session; s_nr30=1775725567146-Repeat; s_nr365=1775725567146-Repeat; s_tslv=1775725567148; utag_main_dc_event=19%3Bexp-session; utag_main__prevpage=https://www.academy.com/p/heydude-mens-wally-holiday-print-warmth-slip-on-shoes?sku; s_sq=academyglobal%3D%2526c.%2526a.%2526activitymap.%2526page%253Dheydude%252520mens%252520wally%252520holiday%252520print%252520warmth%252520slip-on%252520shoes%252520%25257C%252520academy%2526link%253D%25252F%25252Facademy.scene7.com%25252Fis%25252Fimage%25252Facademy%25252F21310634%25253F%252524pdp-gallery-ng%252524%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dheydude%252520mens%252520wally%252520holiday%252520print%252520warmth%252520slip-on%252520shoes%252520%25257C%252520academy%2526pidt%253D1%2526oid%253DfunctionDr%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DBUTTON; akavpau_wd=1775726176~id=03a36a01b095cf27d09c164ce8e39757',
}
pageno = 1
api_url = (
            f"https://www.academy.com/api/category/v3/{CATEGORY_ID}"
            f"?web=true&displayFacets=true&recordsPerPage=29"
            f"&categoryPageId={BASE_CATEGORY_URL.replace('https://www.academy.com', '')}"
            f"&orderBy=mostRelevant&pageNumber={pageno}&enableInventoryFacetCheck=true"
        )
response = requests.get(api_url, headers=headers, timeout=30)




############# P A R S E R ###################

import requests
from parsel import Selector
import json
headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
pdp_url = "https://www.academy.com/p/magellan-outdoors-mens-laguna-madre-solid-short-sleeve-fishing-shirt-109383201?sku=beach-glass-x-small"

response = requests.get(pdp_url, headers=headers, timeout=30)

JSON_XPATH = '//div[@data-compId="comp-blt51a442da3d780eaa"]//script[@type="application/ld+json"]/text()'

json_text = sel.xpath(JSON_XPATH).get()
product_data = json.loads(json_text)
