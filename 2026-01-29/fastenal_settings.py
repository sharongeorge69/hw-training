
BASE_URL = "https://www.fastenal.com/catalog/api/product-search"

ENDPOINT_URL = "https://www.fastenal.com/catalog/api/product-search"

COOKIES = {
    'XSRF-TOKEN': '9db81951-2a38-4ffc-84da-a8045711513f',
    'mt.v': '2.651376006.1769580855815',
    'usr_typ': 'external',
    '_fbp': 'fb.1.1769580856195.599233254605607879',
    '_ga': 'GA1.1.868271075.1769580856',
    'sa-user-id': 's%253A0-61d38389-237d-5f86-60dd-e4527209f824.vnnFWhE%252B1u3CTQMpjZGYKVqa4g8M9xDIjmrkBHhOYHc',
    'sa-user-id-v2': 's%253AYdODiSN9X4Zg3eRScgn4JGfXNIY.tIsg4uJqB%252FFZe3Xi6N4OS%252BCakXI%252FqopClQx4X1i%252Fyeg',
    'sa-user-id-v3': 's%253AAQAKIBUVN7LKcXZwEJzTD_oYwjyVIuzCcwVs91dDikWmGBsWEAEYAyDgvoHLBjABOgSq5aCgQgQsfGll.vLrRo9u5CadaKN2krHTZ26oJciXCUYSZizcwRl1qrPg',
    'srch_ver': 'v5',
    '_clck': '1k7r0j0%5E2%5Eg33%5E0%5E2219',
    'COOKIE_AGREEMENT': '"1"',
    'CJSESSIONID': 'ODkzNDE4MzQtMzk2MS00ODJiLWE4ZTAtZmQ2YzlkYjA4NDk4',
    '_uetsid': '93291f40fc1011f0bc74e9126a80170a',
    '_uetvid': '93292a90fc1011f096b2ab1908c9d622',
    '_clsk': '1rgnyvf%5E1769589036933%5E1%5E1%5Ewww.clarity.ms%2Feus-c%2Fcollect',
    '_ga_X40YWNGS17': 'GS2.1.s1769589034$o2$g1$t1769589082$j12$l0$h0',
}

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.fastenal.com/product/Adhesives,%20Sealants,%20and%20Tape?fsi=1&categoryId=613859',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-xsrf-token': '9db81951-2a38-4ffc-84da-a8045711513f',
}


#mongodb configuration

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "fastenal"
CATEGORY_COLLECTION_NAME = "fastenal_category"
PRODUCT_COLLECTION_NAME = "fastenal_product_urls"

ROOT_CATEGORY_ID = "613850"
ROOT_CATEGORY_NAME = "Adhesives, Sealants, and Tape"
