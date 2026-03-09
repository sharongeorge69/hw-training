import csv
import logging
import re
from pymongo import MongoClient
from settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION_DATA, FILE_NAME_FULLDUMP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EXPORT_LIMIT = 200

# Target availability values — export will be evenly distributed across these
AVAILABILITY_VALUES = [
    "In Stock",
    "No Longer Available",
    "On Order",
    "Special Order",
]

CSV_HEADERS = [
    "input_part_number",
    "url",
    "title",
    "manufacturer",
    "price",
    "description",
    "oem_part_number",
    "retailer_part_number",
    "competitor_part_numbers",
    "compatible_products",
    "equivalent_part_numbers",
    "product_specifications",
    "additional_description",
    "availability",
    "image_urls",
    "linked_files",
]

# Fields that need whitespace/newline cleaning (in addition to universal strip)
TEXT_CLEAN_FIELDS = {"description", "compatible_products", "equivalent_part_numbers"}


def clean_text(value: str, field: str) -> str:
    """Strip leading/trailing spaces from every field.
    For TEXT_CLEAN_FIELDS also collapse internal newlines and extra whitespace."""
    value = value.strip()

    if field in TEXT_CLEAN_FIELDS:
        # Replace non-breaking spaces and zero-width spaces
        value = value.replace('\xa0', ' ').replace('\u200b', '')
        # Collapse \r\n \n \r into a single space
        value = re.sub(r'[\r\n]+', ' ', value)
        # Collapse multiple consecutive spaces
        value = re.sub(r'\s{2,}', ' ', value)
        value = value.strip()

    return value


def compute_quotas(bucket_counts: dict, total_limit: int) -> dict:
    """
    Distribute total_limit rows evenly across non-empty buckets.
    Any shortfall (bucket has fewer docs than quota) is redistributed
    to the richest remaining buckets.
    """
    non_empty = {av: c for av, c in bucket_counts.items() if c > 0}
    if not non_empty:
        return {}

    n = len(non_empty)
    base = total_limit // n
    remainder = total_limit % n

    # Sort buckets by size descending to give remainder to the largest
    sorted_avs = sorted(non_empty, key=lambda av: non_empty[av], reverse=True)
    quotas = {av: base for av in non_empty}
    for i in range(remainder):
        quotas[sorted_avs[i]] += 1

    # Clamp and redistribute shortfalls
    shortfall = 0
    for av in list(non_empty):
        if quotas[av] > bucket_counts[av]:
            shortfall += quotas[av] - bucket_counts[av]
            quotas[av] = bucket_counts[av]

    if shortfall:
        for av in sorted_avs:
            extra = bucket_counts[av] - quotas[av]
            take = min(shortfall, extra)
            quotas[av] += take
            shortfall -= take
            if shortfall <= 0:
                break

    return quotas


def export_data():
    client = None
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DATA]

        # Step 1 — fast count per bucket via aggregation (single pass in Mongo)
        logger.info("Counting availability buckets via aggregation...")
        pipeline = [
            {"$match": {"availability": {"$in": AVAILABILITY_VALUES}}},
            {"$group": {"_id": "$availability", "count": {"$sum": 1}}},
        ]
        agg_result = list(collection.aggregate(pipeline))
        bucket_counts = {av: 0 for av in AVAILABILITY_VALUES}
        for r in agg_result:
            if r["_id"] in bucket_counts:
                bucket_counts[r["_id"]] = r["count"]

        logger.info("Availability distribution in collection:")
        for av in AVAILABILITY_VALUES:
            logger.info(f"  '{av}': {bucket_counts[av]} documents")

        # Step 2 — compute how many rows to take from each bucket
        quotas = compute_quotas(bucket_counts, EXPORT_LIMIT)
        logger.info("Export quota per bucket:")
        for av in AVAILABILITY_VALUES:
            logger.info(f"  '{av}': {quotas.get(av, 0)} rows")

        # Step 3 — fetch docs per bucket (targeted queries, each with a limit)
        all_docs = []
        for av in AVAILABILITY_VALUES:
            q = quotas.get(av, 0)
            if q == 0:
                continue
            docs = list(collection.find({"availability": av}).limit(q))
            all_docs.extend(docs)
            logger.info(f"  Fetched {len(docs)} rows for '{av}'")

        logger.info(f"Total rows collected: {len(all_docs)}")

        # Step 4 — write CSV
        with open(FILE_NAME_FULLDUMP, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=CSV_HEADERS,
                extrasaction='ignore',
                delimiter=',',
                quoting=csv.QUOTE_ALL,
            )
            writer.writeheader()

            count = 0
            for doc in all_docs:
                row = {}
                for header in CSV_HEADERS:
                    val = doc.get(header, "")
                    if val is None:
                        val = ""

                    val_str = clean_text(str(val), header)

                    # Normalize sentinel values
                    if val_str.lower() in ("na", "none"):
                        val_str = ""

                    row[header] = val_str

                writer.writerow(row)
                count += 1

                if count % 50 == 0:
                    logger.info(f"Exported {count}/{len(all_docs)} rows...")

        logger.info(f"Done. Exported {count} rows to '{FILE_NAME_FULLDUMP}'")

    except Exception as e:
        logger.error(f"Export failed: {e}")
    finally:
        if client:
            client.close()


if __name__ == '__main__':
    export_data()
