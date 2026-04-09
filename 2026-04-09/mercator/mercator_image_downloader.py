import requests
import os
import time

CATEGORIES = {
    "Delikatesni izdelki in pripravljene jedi": "14535481",
    "Slani prigrizki in aperitivi": "14535736",
}
SAVE_DIR = "product_images"
HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'X-Requested-With': 'XMLHttpRequest'
}

def start_download():
    # Ensure the folder exists
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Downloading images to: {os.path.abspath(SAVE_DIR)}")

    for cat_name, cat_id in CATEGORIES.items():
        print(f"\nProcessing: {cat_name}")
        offset = 0
        
        while True:
            # A. Fetch list of products
            url = f"https://mercatoronline.si/products/browseProducts/getProducts?limit=100&offset={offset}&from={offset*100}&filterData[categories]={cat_id}"
            try:
                response = requests.get(url, headers=HEADERS, timeout=20).json()
            except:
                break
                
            products = response.get('products', [])
            if not products:
                break
            
            # B. Process each product
            for p in products:
                # Get Product ID and Image URL (with fallbacks)
                p_id = p.get('id') or p.get('productId') or p.get('code')
                img_url = p.get('mainImageSrc') or (f"https://mercatoronline.si{p.get('image')}" if p.get('image') else None)
                
                if not img_url:
                    continue
                
                # C. Convert URL to Medium and add Double Slashes //
                img_url = img_url.replace('product_small_image', 'product_medium_image')
                if '://' in img_url:
                    proto, path = img_url.split('://', 1)
                    img_url = f"{proto}://{path.replace('/', '//')}"
                
                # D. Final check for ID (extract from URL if missing)
                if not p_id or p_id == 'None':
                    p_id = img_url.split('//')[-1].split('/')[-1].split('.')[0]
                
                # E. Download and Save
                target_path = os.path.join(SAVE_DIR, f"{p_id}.jpg")
                if not os.path.exists(target_path):
                    try:
                        img_data = requests.get(img_url, headers=HEADERS, timeout=15).content
                        with open(target_path, 'wb') as f:
                            f.write(img_data)
                        print(f"  Saved: {p_id}.jpg")
                    except Exception as e:
                        print(f"  Error saving {p_id}: {e}")
            
            offset += 1
            time.sleep(0.5) # Polite delay

if __name__ == "__main__":
    start_download()
