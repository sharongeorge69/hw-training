PROJECT_NAME = "colruyt"
BASE_URL = "https://www.colruyt.be"

# Mongo db and collections
MONGO_DB = f"{PROJECT_NAME}_db_1"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_RAW_RESPONSE = f"{PROJECT_NAME}_raw_response"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"


MONGO_URI = "mongodb://127.0.0.1:27017/"
# MONGO_URI = "mongodb://mongotraining:a4892e52373844dc4862e6c468d11b6df7938e16@209.97.183.63:27017/?authSource=admin"

import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME_FULLDUMP = os.path.join(BASE_DIR, f"{PROJECT_NAME}_{datetime.now().strftime('%Y_%m_%d')}_{'sample'}.csv")
EXTRACTION_DATE = datetime.now().strftime('%Y_%m_%d')

headers_crawler = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.1',
    'origin': 'https://www.colruyt.be',
    'priority': 'u=1, i',
    'referer': 'https://www.colruyt.be/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'x-cg-apikey': 'a8ylmv13-b285-4788-9e14-0f79b7ed2411',
}


headers_api = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'origin': 'https://www.colruyt.be',
    'priority': 'u=1, i',
    'referer': 'https://www.colruyt.be/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'x-cg-apikey': 'a8ylmv13-b285-4788-9e14-0f79b7ed2411'
}

cookies = {
    'TS0113bcfc': '016303f95508964e2facf8746a5208432cb603d15bc20313cd0865b1c67712dca6f653b38abfc13c4bf6e1970fa1d47dbdcabf2f68',
    'TS01ea2401': '016303f95524aa4d4896a2a2476cf2ef72f01134544b1f4fd09af51dd3b2fdbc98ba3adea0231e5b586dc6702700790c092d1cdcfd',
    'OptanonAlertBoxClosed': '2026-03-12T06:38:59.527Z',
    '_fbp': 'fb.1.1773297539946.448520699994207020',
    '_gcl_au': '1.1.1424166131.1773297540',
    'kndctr_FA4C56F358B81A660A495DE5_AdobeOrg_identity': 'CiY2NDIyMzkzNzYyNzgxOTM4NTU2MDY4MzM5MTQ4MTM4NzkwMjgyM1ITCPO3lIbOMxABGAEqBElORDEwAPAB87eUhs4z',
    'AMCV_FA4C56F358B81A660A495DE5%40AdobeOrg': 'MCMID|64223937627819385560683391481387902823',
    'tms_storeperma': 'eyJhZG9iZV9lY2lkIjoiNjQyMjM5Mzc2Mjc4MTkzODU1NjA2ODMzOTE0ODEzODc5MDI4MjMifQ%3D%3D',
    '_pin_unauth': 'dWlkPU56ZzFOR0prTTJJdE5qUTVPQzAwWmpsakxXRTJaakF0WXpVNFpEUm1ORFl6WkRnMA',
    '_hjSessionUser_137278': 'eyJpZCI6IjNiYTdjM2U0LTEzNTMtNTQ2Yy1hOTNmLTM3YWEwMTZhNzg2YyIsImNyZWF0ZWQiOjE3NzMyOTc1NDA1MjIsImV4aXN0aW5nIjp0cnVlfQ==',
    'rxVisitor4ik80me8': '1773308562680JM1VBBK9SP1TCAU6D9116QO55IM0BIGG',
    'dtSa4ik80me8': '-',
    'rxvt4ik80me8': '1773316115584|1773314315130',
    'dtPC4ik80me8': '3$314315129_697h-vJCHVJBKDOPHECMGHMACNSJEDFAOMGKMM-0e0',
    'reese84': '3:nxU5QViuK75AqEjGoxGWXg==:U09m0GIgVCkScAj6G2wwEawb4SHYXlV3214+arKEfK36KmBj5yslMlutuTsRdSpxI/KBM/mxLY2Wv+YNq1GPg02YkmTuYf2mPt7ERJ5tMmwoYt8M9XwBv39KaIR4uyk/ZtNTBor37mr765r1Y+K21dwOqIr/OOmUa1Fo91vfZBAI6z8jJ7UEshi0IfLJldrEKJcKp8koR+IRRTNb+Xm8DoeuAzL6YMHGFrqlsuy1YVszxkpqMtGDz9Ry6lz1ZtWYpE3kKrFaYKAcEfo24mZ8GH52wkSTK0PCK0mtLkO9DYDyrio7ipAZ3axM8dqYsqVzs6akD1za7YU47e+qtQGq0+WrKcXFFsb1701YLBkiw463azrhczKEY8j0G6Y+tTJPiK4mvJN2nqpUnTKYZGRemdN3sE4AfCMOQxa8/zHPNzWaQtAcXwCRRKLMXjgC8oUxjgc8soiQ9vXaBh1rwjCyZQ==:AGj2dqV/lrY3h7xQZ5HrUHUToZgDMZal0VPZzS80H3o=',
    'kndctr_FA4C56F358B81A660A495DE5_AdobeOrg_cluster': 'ind1',
    'tfpsi': '053df7c5-dffd-4cef-9621-3b8d98b992ff',
    '_hjSession_137278': 'eyJpZCI6ImNmZjkwNDEwLTZjNGEtNDg3YS05OGQzLThkNTQzMjM4NmE0ZSIsImMiOjE3NzMzMjgwNDczMDksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=',
    '_uetsid': '2718e5a01dde11f1a02b538804ad2593',
    '_uetvid': '2718d9401dde11f1b3475fac9e2ced59',
    'tms_storevisit': 'eyJ0aW1lRXZlbnRfbXNGb2N1c291dCI6MjUzMDgyNDEsInRpbWVFdmVudF9zdGFydFRpbWUiOjE3NzMzMjgwMzc4NTMsImFkYmxvY2tfc3RhdHVzIjoibm90YWN0aXZlIiwicGFnZV9kZXB0aCI6NCwidXNlcl92aXNpdF9pZCI6Ijc3MjQzOS4xNzczMzI4MDQyMzkyIiwibGFzdF9sb2dpbl9zdGF0ZSI6Im5vIn0%3D',
    'utag_main': 'v_id:019ce0c50de2002048f2e92fc2c005065003905d00bd0$_sn:4$_se:36$_ss:0$_st:1773330310758$dc_visit:4$ses_id:1773328038167%3Bexp-session$_pn:5%3Bexp-session$dc_event:7%3Bexp-session$dc_region:eu-central-1%3Bexp-session',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Thu+Mar+12+2026+20%3A45%3A10+GMT%2B0530+(India+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=c85e8369-5805-47f7-ba17-b3d77b56a436&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&geolocation=%3B&AwaitingReconsent=false',
    'dtCookie4ik80me8': 'v_4_srv_1_sn_9FF8B053C265F9B72BAD0E070B5474B3_perc_100000_ol_0_mul_1_app-3A8907cbcdb73fbef3_0',
}

