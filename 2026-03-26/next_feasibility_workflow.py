from curl_cffi import requests
from parsel import Selector

cookies = {
    'ASP.NET_SessionId': 'mqh43q1kqezz3ftmzftvzvbj',
    'NextDeviceType': 'Desktop',
    'NSC_JObpvvqlbx0xcdzbrn3bnhbgejhupbq': 'ffffffff6602d71645525d5f4f58455e445a4a423660',
    'akaas_MEGANAV_2022_PD': '2147483647~rv=97~id=2a4ccc01c5ba24a136944c0d018f8878',
    'ABPersistent_www.next.co.uk': 'a|341',
    'x-next-persona': 'APlatform',
    'RPId': 'ID=7476275754',
    'IdentityReqParams': 'CountryCode=gb&LanguageCode=en&Domain=www.next.co.uk&APDomain=www.next.co.uk/secure/account&Strategy=1&Version=2',
    'Next': 'ID=7f1273f346ee4b5fa4848056a9a59a82',
    'OptanonAlertBoxClosed': '2026-03-25T06:32:37.066Z',
    '_gcl_au': '1.1.1728391654.1774420357',
    '_ga': 'GA1.1.1482600303.1774420357',
    'OptUCMOnsiteConsent': 'true',
    'exponeaRpid': '7476275754',
    'blis_ctid': 'lfu4ftpw18',
    'rxVisitor': '1774420357826OSL6LMLMAEHL7HKSVU2BJTDGBHMNSEER',
    '_tt_enable_cookie': '1',
    '_ttp': '01KMHV3WWF94E5J31WT8W4G5PK_.tt.2',
    '_pin_unauth': 'dWlkPU56ZzFOR0prTTJJdE5qUTVPQzAwWmpsakxXRTJaakF0WXpVNFpEUm1ORFl6WkRnMA',
    'FPID': 'FPID2.3.MB3B1HMlgIOkOeujRpNCBuRAomef0Bli7NndlopItE8%3D.1774420357',
    '__exponea_time2__': '0.022652626037597656',
    '__exponea_etc__': 'cc7bdca2-3533-475f-a989-ab092fe8cc1c',
    'FPAU': '1.1.1728391654.1774420357',
    '_clck': '80hgmn%5E2%5Eg4n%5E0%5E2275',
    'FPLC': 'lSuHA0yMkBCVD3Z7MvOVoUyPxdIJMTq01AyUiEQSlU10dLqXrvF5VpnSeMpmCjAXLpw2PB3rN75OZV4c6WRJOxkDqkh23pgd6SPyZijd31LSM7lUQC8TZJMh8LuKmw%3D%3D',
    '_fbp': 'fb.2.1774420358257.2125544667',
    '_scid': '726e54b4-09a4-4885-8192-0eb62d2be662',
    '__adal_ca': 'so%3Ddirect%26me%3Dnone%26ca%3Ddirect%26co%3D%28not%2520set%29%26ke%3D%28not%2520set%29%26cg%3DDirect',
    '__adal_cw': '1774420358805',
    '_ScCbts': '%5B%5D',
    '_br_mt_search': '_br_var_1',
    '_sctr': '1%7C1774377000000',
    '_fbp': 'fb.3.1774420649172.398960512507903304',
    'NSC_JOg4n15zbh4zrwxelowwfdbdxoadldq': 'ffffffff6602d70245525d5f4f58455e445a4a423662',
    'NextSessionVariables': 'ShowRecentlyViewed=true',
    'MASId': 'ID=PS1_Z',
    '_br_seg_id': 'Z',
    'PIM-SESSION-ID': 'GvkGptMbTnPCCP7U',
    'dtCookie': 'v_4_srv_17_sn_U9R30327MB88STTJCKM7U88RR393M2UN_app-3A5d5b51ec364c93f9_1_ol_0_perc_100000_mul_1_rcs-3Acss_0',
    'x-next-realm-entrypoint': 'next',
    '__adal_ses': '*',
    'QueueITAccepted-SDFrts345E-V3_nextmainsite': 'EventId%3Dnextmainsite%26QueueId%3Ddb9c1a4f-30c3-47a4-a045-9ef862ca29e2%26RedirectType%3Dsafetynet%26IssueTime%3D1774428045%26Hash%3D4004b19990cad54ee3b3a13ac9f58a164416e478fdd5997a2725d7646b88138c',
    '_ga_86YHTTW9QY': 'deleted',
    '_ga_86YHTTW9QY': 'deleted',
    'bm_ss': 'ab8e18ef4e',
    'BVBRANDID': '9425d7f9-c347-406d-b61f-012110fec9d9',
    'BVBRANDSID': 'd5d18db5-d2a4-41b4-b1f6-c1867861fd12',
    'bm_mi': '8310CC188A38926103C56C757EDE97A2~YAAQz0vSF0VGdwOdAQAAo3mtJB8Qh/TCNGFFhRDqbFAT9QgkjkjXf2FjgxA8mV1mKeuOl2tj1PC9/COXEsOIMoqQ/cQ3n4M+BXQw0rxz3LSZsvbxQfMwzAkdhuMlN4pN5lpjFIeCr7IPB5y3yTrh5kclgICtCvmaeYH80jh5DWDqiI5lGM3XlqgQtsMjTOagWAzyLmF/MPzBMSnpLql7lIwVnfiW8+/oKcIB7QN8Y1IgmdXKHyFHcHDO7bWRwsSwCudyV/kRnkNUrlVsuBoyJgZ6rwBwNZq737KXgy9vNPbEn3Lf/pvkVGIcarLB9hsHD2XvXb83LoFFT6TR8kGbJqoOMQ==~1',
    '_tq_id.TV-7290186381-1.4261': '36acb5c8eed32da2.1774420359.0.1774436842..',
    'dtsrVID': '1774436846942',
    'ak_bmsc': 'CB08A5EB3EDBD8341D69C157A8DAEB31~000000000000000000000000000000~YAAQz0vSF3uSdwOdAQAABs6tJB/HKuPOKBgZXB/I/jYQKBhjqNwoL1xlNfl9mHF4afI4ueKgCeSPUhdrmb6mk33lWDKr0oskHY9jOSoXZCcTePc7ee/1iYYimYtWnwUvjLUfN4EagpIClTGpziv2BouqWAEo4Def5ntZNY1lg/G9i9WTDPpyL4yL87JwcgMjt1IUDmI/JoNPdtC8D58RaBkinTfuGkrI2Hj4dxWp2k1JNvMu/d0YCnDoqec3LwXFCE6mGbYXDSbuCOzmwYfzkadYp0+8litCp3pI8l7giknWHSlyOO8zH0BG+tT3sneI/+zdF8TFZi1df09rPWultz+rU58gBqooPJGnjMWfMMwRcChvjWjwJAdj7RDexPoAUvQJoQp9eACdCWt2iid6wk4dqNNrHneKRKtk8XVmyb4YQWiaRbNldbAQC+LItE+VkTimuPcJ',
    'bm_so': '4D14EB175998D20CFE2ED5680F4C9179CDF8A818CF357D0C66B915613FA03258~YAAQz0vSFwuteAOdAQAA4w2vJAf4lqFYn3acCpfGr4/QlW7a5thYRuisve/rrZsEDWNcNZ5g6iF0IOYkIYMM+GdTQ5KPR2LTi5ENytckkyuon2Ee+G1JptDbYd8BiUwzDXLuSrQbaxMhWHLmciWXgk1wsd3m9q721K/yDGhheygLZffPf+vX9YOLWTnKoHRidkP5D0MkLBGOWc5WnWw/FgisHW3VZcfj0q1mwh8b4GgKfxf1lTC7wlZ20d6amQWPCNSPRfyCbGsbIQZCHGf0gl/rvO+1BUZ+vjhrIaHxH4wDXUPnc9qbcapmDNsm9YE/JNz7Pl9mP6sa3MSbErmU0IKsVXMUZRFxL7IpRO7xCbNR0ZdlaWY8a2tA5mIbDXcKDj5AJHtCtjQqEeeNz9h9yuJbEJcPDb3N45nvdkBY2KDKKM6f6nJJ3A6qygZRRLg4/kuFGAn06VV4azxqVhnT',
    'bm_sz': 'D55F9AA81DFC0F3CED02A5AAAFD934B4~YAAQz0vSFwyteAOdAQAA4w2vJB8BYj+JaxpJPz0s0VaLA90oS7lWsmNP5bAZfGk22HxtwN/CrARbeEv0wSTTQ8lQqgmUtzWik0+f8aOfxxBO22GrVHU3j3fMgrk64fLw2N7CLFC/loktssuhNrPG9F2FT0SmJiYPxrYXdmUSnTWswEEd6azNVO1hLfuW7II/iqlG9CdOk5arm8T4wP4HpmM9kK3ubn15UinNKHcfDtybS7hwMeBPENb1jQ70FzUxWD4nG/xfDb7xpqP+zkNci/1w2O5k9UZBoGVoaTlPzvGNCCDtYp1nBejcVj1kqeUQRux75PK0O97tsponQT9vEi5aFA34EwW/VNr18T6o5wBeYHP4kbESBRBzy+8D89bHsOgjkS+Rzv58yH2EY5z04uCkUJ1Zyl8aorS0jCXqa8cLdD1bZPtH5AQA4pCmeIeLWmWsFOMK5VGl7pel8ZUXs4q4SKBZJSJQK9YCxKjRKznV2EXAIXE1sAJKXa6F37jOuKl3Y+Mypk/VvsKvEm6vEMGztZmvFoGOys1w9YZEEFMIRIK5zcc1IOuDHZGMD6701AI6HvY4iM9vLoUNxw==~4473926~3420729',
    'ABSession_www.next.co.uk': 'a|1774436945623',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Mar+25+2026+16%3A39%3A06+GMT%2B0530+(India+Standard+Time)&version=202601.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2016135d-7fb4-40c9-8a78-157687c07418&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=Targt%3A1%2COntgt%3A1%2CPerf%3A1%2CStNec%3A1%2CFunct%3A1&intType=1&crTime=1774420357765&geolocation=IN%3BKL&AwaitingReconsent=false',
    'bm_s': 'YAAQz0vSFwSzeAOdAQAA7BSvJAUYhS0tkKyXAVKdVFBzPKjDk3A4rZhUPRp4MtIaEDQLmIW+zvq/7wIp0gRBjRm1aVty6MHM2T6pKMUDUq8Yj9spcYqwOhkZjvVtCLjmym0t9a+BBKKBADizJ6G02pO5lSOE11QwzczIukuSPOwsvgvqZmYotpzsjn7Whm19WcoNr/IdXV+ZMBxyMY7ONNxU/tOUDGyvo2XoVVMN9BssJS4oMAHmtWZHYdEmpAEAaugUm6A116vdRg7A+14g0nVSeqLz4D2bOQbnW+l0mVrrKuO6Hifw4i9cFMK3duA6G8YPOPZ4BlxR32UwpYBO/I+k/SN3In2GJyNF/VYW7XkTbOh5ULabaTSdTVN9aCyN802+YWPWjzmzdybyATUGTYPX3/GpnY9jPVRfc1B94gdWpohLQUW9hF6sVQJ/4MhDpAYllWhnO50gTmfFz1bqXjcX4MFSBHk/PXOhkZ9UbwEoNTawwwmsaFIej23C/9RBtrW3erLe1/9wEyCFasuwXJbIYtTLpzOcNoijceTbTe7RVAEWwLHskjkXov7QBfBs/YR2plr6Z3R7Ia0iU7Y5eQxLNrf5kNZhf7T6yWqNAR1tb68UV0Bb2AR4p27OFTLcx3r8cKNtq6DyFQGsAFeSrq5YJ9owmARAX5++dgbcFwkw5kPLXOhXqdpibGhqnOLyQ1gfvFpeTobgcyLMlLylQ5Q9NT6EiAB/ITqR0DVJ0L0aDYDcjfEzMkR9As6wImaJRcSdS01Da3xIo8Vbi+O+hyGBMNhyWzJPLdCJkVnU2BDRmy32qTIzPcnxfSUnTTl6Du92+pWqcUCdnhy+Ny+4Xj/yrHImXgbpe1QciOozg0QhRKuWrFP3qrvf3PY3fc2wvz0=',
    '_br_uid_2': 'uid%3D939147309820%3Av%3D13.0%3Ats%3D1774420357671%3Ahc%3D92',
    '_ga_0MCQTK8RLH': 'GS2.1.s1774428043$o2$g1$t1774436948$j60$l1$h1440240704',
    '__adal_id': '2ce5819b-24dc-4491-ade5-88a2a31196bf.1774420359.2.1774436948.1774423120.e26e5e33-b4db-4f12-a083-c078fdc61839',
    '_scid_r': 'NmPU6rCPl0w6Pmb37SqzHRT4kG_gft5ZqBLApQ',
    '_clsk': 'ilbrxj%5E1774436948977%5E139%5E0%5Ey.clarity.ms%2Fcollect',
    'ttcsid': '1774426848435::C-j8CT27dkoy8kjeRQFP.2.1774436949185.0::1.10096718.10100500::9919728.139.756.1088::10091667.724.12132',
    'ttcsid_C0VO58H5A0R73RNS8PEG': '1774428043175::yMX7RsJ1Ad42DElWSUsz.2.1774436949185.1',
    'NextVisitor': 'LatestSessionID=7f1273f346ee4b5fa4848056a9a59a82&LatestSessionTimestamp=25/03/2026 11:09:09&ID=6195568319b04defb4240938a3c5f3cd',
    '_uetsid': '6bd81490281411f1a44a4f9e9aee8b87',
    '_uetvid': '6bd83d30281411f1bfa3bb0718bf3a67',
    'bm_lso': '4D14EB175998D20CFE2ED5680F4C9179CDF8A818CF357D0C66B915613FA03258~YAAQz0vSFwuteAOdAQAA4w2vJAf4lqFYn3acCpfGr4/QlW7a5thYRuisve/rrZsEDWNcNZ5g6iF0IOYkIYMM+GdTQ5KPR2LTi5ENytckkyuon2Ee+G1JptDbYd8BiUwzDXLuSrQbaxMhWHLmciWXgk1wsd3m9q721K/yDGhheygLZffPf+vX9YOLWTnKoHRidkP5D0MkLBGOWc5WnWw/FgisHW3VZcfj0q1mwh8b4GgKfxf1lTC7wlZ20d6amQWPCNSPRfyCbGsbIQZCHGf0gl/rvO+1BUZ+vjhrIaHxH4wDXUPnc9qbcapmDNsm9YE/JNz7Pl9mP6sa3MSbErmU0IKsVXMUZRFxL7IpRO7xCbNR0ZdlaWY8a2tA5mIbDXcKDj5AJHtCtjQqEeeNz9h9yuJbEJcPDb3N45nvdkBY2KDKKM6f6nJJ3A6qygZRRLg4/kuFGAn06VV4azxqVhnT~1774436950058',
    '_ga_86YHTTW9QY': 'GS2.1.s1774428043$o2$g1$t1774436950$j58$l0$h1151395892',
    'rxvt': '1774438750776|1774425800995',
    '_abck': '14CA11F64076AF4E1809D43C8D026A7F~-1~YAAQz0vSFxW/eAOdAQAAYiOvJA/YWonGHmvbA6lNwxqrBcheYjOElxa8NDmtSbTtzkNQtDnXj3trcy4DNkpuiv68sfdq+kzxNgi84hGuWCV9IQdwe9fLhnA2U1WZbYVyJk76ogPEea8Xnui6ORpLkMg1W+dUSCigJXSPcRH7cfNeiIlD9zcR23bhJfgCFHT8VyWuMixLHYR98M2f0EdRwc7pXfQGemQtGfCq1KkLX3yPuITRuSMMIfllUgLj2YbsW1lc7bj+b3haswh358RD4Y0X6upnroAZYbo+nuDpOKa6O9QFpWWUK27q71vFZNHb7HINzSSExcX7VVLJl3Cs5v+giTAkyuws+kjyfUwh+K4/jC0QyTBfj3wKksE4/H3YterXaFAv6P8gWFfRI9lbgSVYpbe4iCAudAV3vbxUmPCYtmGvULWfemuxWXE+TzV4TavrHIjHNTCRxaNwaGnxWu39uDtjHeWk/6o/+HjYrMHsONV8UZjlZinET4rpHhofkpyNjDqSYdmYAXHjkwfsNj9OSRnDcLbcPReCtz659xIm5TvVSK1xlLruaxF5QYY83AYfDpvWJfAXfd1omnZtxN6NbnIuri5joGDvvyl5ClDsnODXSTGxUtoLlHLhm/SUo9MoppS+K4hlQDyC/oOs5/JFZfxC1EzFfJN70rvx/XlZrAQqO8rwwpU+j722MMDM5006UezM2Dt7MpPb4IMTntlI7x1n7oFGPzh5AYpBSKhpAXP5F2pRUlv/fJQbvUM=~-1~-1~1774438275~AAQAAAAF%2f%2f%2f%2f%2f1rYz8mKKdI1xKdqvNeKG7V7oeMjv2OWAQJPgPVauZPBK%2fD2E6291MMPfsK%2f%2fV5twdj4su5EwZMI8h5STeOY6M43lN8KWlD1WlVEBX+AJ4Y+EKbkRvh5aqyc1Q%2fZhNo6c2pQriTAImqeBS2SyF4NGL8PBTwUJXp+wwhLi0BnxmwRMHB9omE8XHp8tsNQswBX4YSjNM1BOvACNBDjLCMULtNo5iSI5aRBt%2fSkwg6roF+wWdU%3d~1774437005',
    'dtPC': '17$236948196_777h-vEVKANUHBGAAJMAFGMBDLDUHGVGCCARPP-0e0',
    'dtSa': 'false%7C_load_%7C15%7C_onload_%7C-%7C1774436949547%7C236948196_777%7Chttps%3A%2F%2Fwww.next.co.uk%2Fshop%2Fgender-women-productaffiliation-clothing-0%3Fp%3D15%7C%7C%7C0.9090908765792847%7C',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}

################## C A T E G O R Y #######################

response = requests.get('https://www.next.co.uk/women', cookies=cookies,headers=headers, impersonate = "chrome110")
sel = Selector(text=response.text)
rating = sel.xpath("//label[text()='CLOTHING']/following-sibling::div//a/@href").getall()




################### C R A W L E R #######################
# change params for pagination
params = {
    'p': '1',
}

response = requests.get(
    'https://www.next.co.uk/shop/gender-women-productaffiliation-clothing-0',
    params=params,
    cookies=cookies,
    headers=headers,
    impersonate="chrome120"

)


sel = Selector(text=response.text)
pdp_url = sel.xpath('//a[@class="MuiCardMedia-root produc-1mup83m"]//@href').getall()





##############PARSER#################
import json
start_url = "https://www.next.co.uk/style/su778665/h63603"
response = requests.get(start_url)
sel = Selector(text=response.text)
json_text = sel.xpath("//script[@id='__NEXT_DATA__']/text()").get()
data = json.loads(json_text)
queries = data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
product_data = queries[0].get("state", {}).get("data", {})

product_name =product_data.get("title")
brand = product_data.get("brand")
product_id = product_data.get("itemNumber")
style_number = product_data.get("styleNumber")
# description
desc = product_data.get("itemDescription", {})
product_description = desc.get("toneOfVoiceSanitised")
material_composition = desc.get("composition")
fit_guide = desc.get("measurements")
image_url = product_data.get("itemMedia", [])
options = product_data.get("options", {}).get("options", [])
size = options[0].get("value", [])
instock = options[0].get("stockStatus", [])

# rating and review count are loaded from an api

 # Site-specific passkey for Next.co.uk Bazaarvoice data
PASSKEY = "caU0xNxR6P7SE6qUePNHXA23s6WTnRqX2TIYz8HEtSzcw"
    
# URL for statistics (total reviews, average rating)
url = "https://api.bazaarvoice.com/data/statistics.json"
    
params = {
        "apiversion": "5.4",
        "passkey": PASSKEY,
        "Filter": f"ProductId:{product_id}",
        "Stats": "Reviews"
    }

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()
stats = data["Results"][0].get("ProductStatistics", {}).get("ReviewStatistics", {})
reviews = stats.get("TotalReviewCount", 0)
rating = stats.get("AverageOverallRating", 0)


###################### F I N D I N G S #######################

#1. rating and review count is not available in the json data it is loaded from a different api
