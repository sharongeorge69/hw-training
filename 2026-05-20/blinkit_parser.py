import time
import random
import pymongo
import logging
from datetime import datetime
from curl_cffi import requests
from pymongo import MongoClient

from settings import (
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION_RESPONSE,
    MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_URL_FAILED,
    headers,
    SAMPLE_URLS,
)
from items import ProductDataItem


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BlinkitParser:
    """Fetches and parses product data from the Blinkit PDP API."""

    def __init__(self):
        self.headers = headers
        self.browser = "chrome"

        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.url_collection = self.db[MONGO_COLLECTION_RESPONSE]
        self.product_collection = self.db[MONGO_COLLECTION_DATA]
        self.failed_url_collection = self.db[MONGO_COLLECTION_URL_FAILED]

        self.product_collection.create_index("unique_id", unique=True)
        logger.info("Connected to MongoDB")

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def fetch_product(self, pdp_url, latitude, longitude):
        """POST to the Blinkit layout API and return the response, or None on failure."""
        product_id = pdp_url.split("/")[-1]
        api_url = f"https://blinkit.com/v1/layout/product/{product_id}"
        max_retries = 3

        request_headers = self.headers.copy()
        request_headers["lat"] = str(latitude)
        request_headers["lon"] = str(longitude)
        request_headers["cookie"] = (
            f"city=; gr_1_lat={latitude}; gr_1_lon={longitude}; gr_1_landmark=undefined"
        )

        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    api_url,
                    headers=request_headers,
                    impersonate=self.browser,
                    timeout=20,
                )
                if resp.status_code == 200:
                    return resp
                if resp.status_code == 404:
                    logger.error(f"Product not found (404): {api_url}")
                    return None
                logger.error(
                    f"HTTP {resp.status_code} for {api_url} (attempt {attempt + 1})"
                )
            except Exception as exc:
                logger.warning(
                    f"Request error for {api_url} on attempt {attempt + 1}: {exc}"
                )

            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1) + random.uniform(0, 1))
            else:
                logger.error(f"Max retries reached for: {api_url}")

        return None

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def start(self):
        """Iterate over SAMPLE_URLS, fetch each product, and persist to MongoDB."""
        total = len(SAMPLE_URLS)
        logger.info(f"Total items to parse: {total}")

        for idx, doc in enumerate(SAMPLE_URLS, 1):
            pdp_url = doc.get("pdp_url", "")
            latitude = doc.get("lat", 0)
            longitude = doc.get("lon", 0)

            if not pdp_url:
                logger.warning(f"Item {idx}/{total}: missing pdp_url. Skipping.")
                continue

            unique_id = pdp_url.split("/")[-1]
            if not unique_id:
                logger.warning(f"Item {idx}/{total}: invalid pdp_url '{pdp_url}'. Skipping.")
                continue

            if self.product_collection.find_one({"unique_id": unique_id}):
                logger.debug(f"Already parsed, skipping: {unique_id}")
                continue

            logger.info(f"Processing {idx}/{total}: {unique_id}")
            response = self.fetch_product(pdp_url, latitude, longitude)

            if not response:
                logger.error(f"Fetch failed for {unique_id}. Recording to failed collection.")
                self.failed_url_collection.update_one(
                    {"pdp_url": pdp_url}, {"$set": doc}, upsert=True
                )
                continue

            self.parse(response, doc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _text(node):
        """Extract the `text` string from a Blinkit text-node dict."""
        if isinstance(node, dict):
            return node.get("text", "")
        return ""

    # ------------------------------------------------------------------
    # Extraction methods
    # ------------------------------------------------------------------

    def _extract_images(self, snippets):
        """Return a deduplicated list of full-resolution product image URLs.

        Prefers gallery assets from the first carousel snippet; falls back to
        the thumbnail URL when assets are absent.
        """
        images = []
        seen = set()
        carousel = snippets[0] if snippets else {}

        for item in carousel.get("data", {}).get("itemList", []):
            assets = (
                item.get("data", {})
                .get("click_action", {})
                .get("show_gallery", {})
                .get("assets", [])
            )
            for asset in assets:
                url = asset.get("image_url", "")
                if url and url not in seen:
                    seen.add(url)
                    images.append(url)

            # Fallback: thumbnail embedded directly on the item
            if not assets:
                url = (
                    item.get("data", {})
                    .get("media_content", {})
                    .get("image", {})
                    .get("url", "")
                )
                if url and url not in seen:
                    seen.add(url)
                    images.append(url)

        return images

    def _extract_breadcrumbs(self, snippets, product_name=""):
        """Return (breadcrumbs list, deepest category name) from the breadcrumb widget."""
        breadcrumbs = ["home"]
        category_name = ""

        for snippet in snippets:
            if snippet.get("widget_type") != "horizontal_text_list_snippet":
                continue

            attrs = snippet.get("tracking", {}).get("common_attributes", {})
            for key in ["l0_category", "l1_category", "l2_category"]:
                value = attrs.get(key, "").strip()
                if value and value not in breadcrumbs:
                    breadcrumbs.append(value)

            category_name = breadcrumbs[-1] if len(breadcrumbs) > 1 else ""
            if product_name:
                breadcrumbs.append(product_name)
            break

        return breadcrumbs, category_name

    def _extract_grammage(self, snippets, updater_data):
        """Return the product weight/size string (grammage).

        Checks three locations in order:
        1. `variant` text node on main snippets.
        2. `variant_info.primary.text.text` on main snippets.
        3. `highlights.items[].text.text` on main snippets.
        4. Expanded updater snippets where title == "unit".
        """
        for snippet in snippets:
            d = snippet.get("data", {})

            variant = self._text(d.get("variant"))
            if variant:
                return variant

            variant_info = (
                d.get("variant_info", {})
                .get("primary", {})
                .get("text", {})
                .get("text", "")
                .strip()
            )
            if variant_info:
                return variant_info

            for item in d.get("highlights", {}).get("items", []):
                text = item.get("text", {}).get("text", "").strip()
                if text:
                    return text

        # Fall back to expanded product-detail snippets
        for _, updater_value in updater_data.items():
            for snippet in updater_value.get("payload", {}).get("snippets_to_add", []):
                d = snippet.get("data", {})
                if self._text(d.get("title")).strip().lower() == "unit":
                    return self._text(d.get("subtitle")).strip()

        return ""

    def _extract_pricing_and_availability(self, snippets):
        """Return a dict with product_id, inventory, rating, merchant_id, etc.

        Two widget formats are handled:
        - Standard product card (contains `product_id` or `normal_price`).
        - Rating/availability widget (`text_right_icons_rating_snippet_type`),
          which also provides the definitive inventory count and sold-out flag.
        """
        result = {}

        for snippet in snippets:
            d = snippet.get("data", {})
            widget_type = snippet.get("widget_type", "")

            # Standard product card
            if "product_id" in d or "normal_price" in d:
                result.setdefault("product_id", d.get("product_id", ""))
                result.setdefault("group_id", d.get("group_id", ""))
                result.setdefault("variant", self._text(d.get("variant")))
                result.setdefault("inventory", d.get("inventory"))
                result.setdefault(
                    "merchant_id", d.get("meta", {}).get("merchant_id", "")
                )
                result.setdefault("product_state", d.get("product_state", ""))
                result.setdefault(
                    "promotion_description",
                    d.get("offer_tag", {}).get("title", {}).get("text", ""),
                )

            # Rating/availability widget — overrides inventory and state
            if widget_type == "text_right_icons_rating_snippet_type":
                tracking = snippet.get("tracking", {}).get("common_attributes", {})
                inventory = tracking.get("inventory", 0)
                state = tracking.get("state", "").lower()

                result["inventory"] = inventory
                result["product_state"] = state
                result["merchant_id"] = tracking.get("merchant_id", "")
                result["rating"] = tracking.get("rating", "")
                result["is_sold_out"] = (
                    state in ("out_of_stock", "sold_out", "unavailable")
                    or inventory == 0
                )

            # Variant can also live on nested snippet data
            if "variant" in d:
                result["variant"] = self._text(d.get("variant"))

            nested_d = snippet.get("snippet", {}).get("data", {})
            if isinstance(nested_d, dict) and "variant" in nested_d:
                result["variant"] = self._text(nested_d.get("variant"))

        return result

    def _extract_related_products(self, snippets):
        """Return a dict of {section_title: [product_card, ...]} for related carousels."""
        sections = {}
        current_section = None

        for snippet in snippets:
            widget_type = snippet.get("widget_type", "")
            d = snippet.get("data", {})

            if widget_type == "image_text_vr_type_header":
                current_section = self._text(d.get("title"))
                if current_section:
                    sections[current_section] = []

            elif widget_type == "horizontal_list" and current_section:
                for card in d.get("horizontal_item_list", []):
                    cd = card.get("data", {})
                    if not cd.get("name"):
                        continue
                    deeplink = (
                        cd.get("click_action", {})
                        .get("blinkit_deeplink", {})
                        .get("url", "")
                    )
                    sections[current_section].append({
                        "product_id": cd.get("identity", {}).get("id", ""),
                        "name": self._text(cd.get("name")),
                        "variant": self._text(cd.get("variant")),
                        "price": self._text(cd.get("price") or cd.get("normal_price")),
                        "image_url": cd.get("image", {}).get("url", ""),
                        "deeplink": deeplink,
                    })

        return sections

    def _extract_product_details(self, snippets, updater_data):
        """Return a flat {label: value} dict from the product-details section.

        Sources (in order):
        1. Snippets with `identity.id` starting with `product_details_`.
        2. Overlay expandable data embedded in snippet data.
        3. All updater payloads (snippets_to_add / snippets / data.snippets).
        """
        details = {}

        def _add(title, subtitle):
            """Insert title→subtitle only when title is non-empty and not already set."""
            title = str(title).strip()
            if not title:
                return
            if title not in details or not details[title]:
                details[title] = str(subtitle).strip() if subtitle else ""

        # Source 1 & 2: main snippets
        for snippet in snippets:
            d = snippet.get("data", {})

            identity_id = d.get("identity", {}).get("id", "")
            if identity_id.startswith("product_details_"):
                _add(self._text(d.get("title")), self._text(d.get("subtitle")))

            for item in (
                d.get("overlay_data", {})
                .get("expandable_data", {})
                .get("expanded_state", {})
                .get("vertical_item_list", [])
            ):
                _add(self._text(item.get("title")), self._text(item.get("subtitle")))

        # Source 3: all updater payloads
        for _, updater_value in updater_data.items():
            payload = updater_value.get("payload", {})
            snippet_lists = [
                payload.get("snippets_to_add", []),
                payload.get("snippets", []),
                payload.get("data", {}).get("snippets", []),
            ]
            for snippet_list in snippet_lists:
                if not isinstance(snippet_list, list):
                    continue
                for snippet in snippet_list:
                    d = snippet.get("data", {})
                    _add(self._text(d.get("title")), self._text(d.get("subtitle")))

        return details

    # ------------------------------------------------------------------
    # Parse & persist
    # ------------------------------------------------------------------

    def parse(self, response, meta):
        """Parse a raw API response and upsert the product document into MongoDB."""
        data = response.json()

        # Unwrap the response payload (API returns it in different shapes)
        if "data" in data and "response" in data.get("data", {}):
            payload = data["data"]["response"]
        elif "response" in data:
            payload = data["response"]
        else:
            payload = data

        if not payload:
            return

        # Merge any server-side meta into our request meta dict
        resp_meta = (
            data.get("meta", {})
            if "meta" in data
            else data.get("data", {}).get("meta", {})
        )
        meta.update(resp_meta)

        snippets = payload.get("snippets", [])
        updater_data = payload.get("snippet_list_updater_data", {})

        # Core fields from the SEO tracking block
        seo = (
            data.get("response", {})
            .get("tracking", {})
            .get("le_meta", {})
            .get("custom_data", {})
            .get("seo", {})
        )
        product_name = seo.get("product_name", "")
        brand = seo.get("brand", "")
        selling_price = seo.get("price", "")
        regular_price = seo.get("mrp", "")

        # "How to Use" instruction from SEO attributes list
        usage_instruction = next(
            (
                attr.get("value", "")
                for attr in (seo.get("attributes") or [])
                if attr.get("name") == "How to Use"
            ),
            "",
        )

        # Run all extractors
        image_urls = self._extract_images(snippets)
        breadcrumbs, category_name = self._extract_breadcrumbs(snippets, product_name)
        pricing = self._extract_pricing_and_availability(snippets)
        product_details = self._extract_product_details(snippets, updater_data)
        related_products = self._extract_related_products(snippets)
        grammage = self._extract_grammage(snippets, updater_data)

        description = product_details.get("Description", "")
        promotion_description = pricing.get("promotion_description", "")
        discount_percentage = (
            promotion_description.replace("% OFF", "") if promotion_description else ""
        )

        # Seller lookup from product details (case-insensitive)
        seller = next(
            (v for k, v in product_details.items() if k.strip().lower() == "seller"),
            "",
        )

        unique_id = pricing.get("product_id", "") or meta.get("pdp_url", "").split("/")[-1]

        item = {}
        item["unique_id"] = unique_id
        item["group_id"] = pricing.get("group_id", "")
        item["product_url"] = meta.get("pdp_url", "")
        item["product_name"] = product_name
        item["brand"] = brand
        item["breadcrumbs"] = breadcrumbs
        item["category_name"] = category_name
        item["selling_price"] = str(selling_price) if selling_price is not None else ""
        item["regular_price"] = regular_price
        item["discount_percentage"] = discount_percentage
        item["promotion_description"] = promotion_description
        item["grammage"] = grammage
        item["product_description"] = description
        item["instructions"] = usage_instruction
        item["storage_instructions"] = ""
        item["seller_details"] = seller
        item["image_urls"] = image_urls
        item["main_image_url"] = image_urls[0] if image_urls else ""
        item["product_availability"] = pricing.get("product_state", "")
        item["is_sold_out"] = pricing.get("is_sold_out", False)
        item["stock_quantity"] = pricing.get("inventory", 0)
        item["highlights"] = product_details
        item["store_id"] = str(pricing.get("merchant_id", "") or "")
        item["product_rating"] = str(pricing.get("rating", ""))
        item["category_rank"] = meta.get("rank")
        item["extraction_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item["page_depth"] = meta.get("page")
        item["listing_type"] = meta.get("label")
        item["additional_product_details"] = product_details
        item["response"] = data
        item["meta_data"] = meta

        try:
            ProductDataItem(**item).validate()
            self.product_collection.insert_one(item)
            logger.info(f"Saved: {unique_id}")
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"Skipped duplicate: {unique_id}")
        except Exception as exc:
            logger.error(f"Save error for {unique_id}: {exc}")

    def close(self):
        """Close the MongoDB connection."""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception:
            pass


if __name__ == "__main__":
    parser = BlinkitParser()
    try:
        parser.start()
    finally:
        parser.close()