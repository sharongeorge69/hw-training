import csv
import re
from html import unescape
from pymongo import MongoClient
import settings

csv_headers = [
    "unique_id", "url", "productname", "brand", "selling_price",
    "regular_price", "discount", "description", "specification",
    "fit_type", "image", "rating", "review", "size", "colour"
]

class Exporter:
    def __init__(self, writer):
        self.writer = writer
        self.client = MongoClient(settings.MONGO_URI)
        self.collection = self.client[settings.MONGO_DB][settings.MONGO_COLLECTION_PRODUCTS]

    def start(self):
        self.writer.writerow(csv_headers)
        for item in self.collection.find().limit(200):
            row = []
            for h in csv_headers:
                val = item.get(h, "")
                if val:
                    val = str(val)
                    if h == "description":
                        val = re.sub(r"<.*?>", " ", unescape(val))
                    val = re.sub(r"\s+", " ", val).strip()
                
                if h in ["selling_price", "regular_price"] and val:
                    try: val = format(float(val), ".2f")
                    except: pass
                
                if h in ["rating", "review"]:
                    try:
                        f_val = float(val)
                        if f_val == 0:
                            val = ""
                        elif h == "rating":
                            val = str(round(f_val, 1))
                    except (ValueError, TypeError):
                        pass

                row.append(val)
            self.writer.writerow(row)

if __name__ == "__main__":
    import os
    path = os.path.join(os.path.dirname(__file__), settings.FILE_NAME_FULLDUMP)
    print(f"Exporting to: {path}")
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            Exporter(csv.writer(f, quoting=csv.QUOTE_MINIMAL)).start()
        print("Export successful.")
    except Exception as e:
        print(f"Export failed: {e}")
