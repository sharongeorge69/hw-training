from os import makedirs
from logging import info
from json import dumps, loads


import asyncio
from pydoll.browser import Chrome, Edge
# from pydoll.constants import Key
# from pydoll.protocol.fetch.types import RequestStage
from pydoll.protocol.fetch.events import FetchEvent, RequestPausedEvent
import requests
from pydoll.browser.options import ChromiumOptions
from pydoll.protocol.network.types import ErrorReason

metas = [
    # {"keyword": "Property Management"},
    # {"keyword": "Property Broker"},
    # {"keyword": "Property Brokerage"},
    # {"keyword": "Property Brokers"},
    # {"keyword": "Properties Broker"},
    # {"keyword": "Property Consultant"},
    # {"keyword": "Property Consultants"},
    # {"keyword": "Property Advisory"},
    # {"keyword": "Property Agents"},
    # {"keyword": "Property Agency"},
    # {"keyword": "Real Estate Broker"},
    # {"keyword": "Real Estate Brokerage"},
    # {"keyword": "Real Estate Brokers"},
    # {"keyword": "Business Center"},
    # {"keyword": "Holiday Homes"},
    # {"keyword": "Hotel Apartments"},
    # {"keyword": "Propertes Consultant"},
    # {"keyword": "Properties Consultants"},
    # {"keyword": "Propertyies Advisory"},
    # {"keyword": "Properties Agents"},
    # {"keyword": "Properties Agency"},
    # {"keyword": "Real Estate"},
    # {"keyword": "Properties"},
    # {"keyword": "Broker"},
    # {"keyword": "Brokerage"},
    # {"keyword": "Brokers"},
    # {"keyword": "Realty"},
    # {"keyword": "Property"},
    # {"keyword": "Homes"},
    # {"keyword": "Realtor"},
    # {"keyword": "Realtors"},
    # {"keyword": "Realestate"},
    # {"keyword": "Estates"},
    # {"keyword": "Estate"},
    # {"keyword": "Rental"},
    # {"keyword": "Rentals"},
    # {"keyword": "Leasing"},
    # {"keyword": "Letting"},
    # {"keyword": "Housing"},
    # {"keyword": "Residences"},
    # {"keyword": "Villa"},
    # {"keyword": "Villas"},
    # {"keyword": "Apartment"},
    # {"keyword": "Apartments"},
    # {"keyword": "Tower"},
    # {"keyword": "Building"},
    # {"keyword": "Dwelling"},
    # {"keyword": "Accommodation"},
    # {"keyword": "Real State"},
    # {"keyword": "Real Stat"},
    # {"keyword": "Real Estat"},
    # {"keyword": "Real Estae"},
    # {"keyword": "Real Easte"},
    # {"keyword": "Real Eastate"},
    # {"keyword": "Real Esate"},
    # {"keyword": "Real Esteat"},
    # {"keyword": "Realstate"},
    # {"keyword": "Rel Estate"},
    # {"keyword": "Reality"},
    # {"keyword": "Realsty"},
    # {"keyword": "Proporties"},
    # {"keyword": "Properites"},
    # {"keyword": "Propeties"},
    # {"keyword": "Proprties"},
    # {"keyword": "Propertiies"},
    # {"keyword": "Proparties"},
    # {"keyword": "عقار"},
    # {"keyword": "عقارات"},
    # {"keyword": "العقارية"},
    # {"keyword": "العقاري"},
    # {"keyword": "للعقارات"},
    # {"keyword": "عقاري"},
    # {"keyword": "سمسار"},
    # {"keyword": "سمسرة"},
    # {"keyword": "أملاك"},
    # {"keyword": "الأملاك"},
    # {"keyword": "شقق"},
    # {"keyword": "بيع"},
    # {"keyword": "شراء"},
    # {"keyword": "إيجار"},
    # {"keyword": "الإيجار"},
    {"keyword": "تأجير"},
    {"keyword": "إدارة"},
    # {"keyword": "وساطة عقارية"},
    # {"keyword": "الوساطة العقارية"},
    # {"keyword": "وسيط عقاري"},
    # {"keyword": "وسطاء عقاريين"},
    # {"keyword": "إدارة عقارات"},
    # {"keyword": "تطوير عقاري"},
]

dir_name = 'data'


class InvestDubai:

    def __init__(self):
        # self.page_number = 40
        # self.position = (self.page_number-1)*10
        self.prev_dulno_check = None
        self.pagination_completed = False
        self.metas = metas

        makedirs(dir_name, exist_ok=True)

    def start(self):
        while self.metas:
            meta = self.metas.pop(0)

            self.keyword = meta.get('keyword')
            self.page_number = meta.get('page', 1)
            self.position = (self.page_number - 1) * 100
            self.pagination_completed = False

            asyncio.run(self.license_search())

    async def license_search(self):

        target_url = 'https://app.invest.dubai.ae/search-license'

        # hcaptcha-api-script-id

        while True:

            options = ChromiumOptions()
            options.add_argument('--window-size=1920,1080')
            # options.add_argument('--headless=new')
            # options.page_load_state = PageLoadState.INTERACTIVE
            options.add_argument('--incognito')
            # options.add_argument(f'--proxy-server={self.proxies['http']}')

            # Block content that slows down loading
            # options.block_notifications = True
            # options.block_popups = True

            # Disable images for even faster loading (if you don't need them)
            # options.add_argument('--blink-settings=imagesEnabled=false')

            # Network optimizations
            options.add_argument('--disable-features=NetworkPrediction')
            # options.add_argument('--dns-prefetch-disable')
            self.request_got = False

            async with Chrome(options=options) as browser:

                self.page = await browser.start()
                # self.page = await browser.new_tab()

                info(f"[Paydoll] - {target_url}")

                try:
                    await self.page.go_to(target_url)
                    page_opened = await self.wait_to_load_text(self.page, 'Search License Information', 30)
                except Exception as e:
                    info(f"Error loading page: {e}")
                    page_opened = False

                if page_opened:
                    await asyncio.sleep(5)

                    # self.page._
                    try:
                        search_box = await self.page.find(tag_name='input', class_name="v-field__input", timeout=30)
                        await search_box.insert_text(self.keyword)
                        await asyncio.sleep(2)
                        search_completed = True
                    except:
                        search_completed = False

                    if search_completed:

                        while True:
                            try:

                                await self.page.enable_fetch_events()
                                await self.page.on(FetchEvent.REQUEST_PAUSED, self.redirect_url)

                                self.request_got = False
                                search_button = await self.page.find(tag_name='div', class_name="v-field__append-inner", timeout=15)
                                await search_button.click()
                                await asyncio.sleep(2)

                                retry = 0
                                error = False
                                while True:
                                    if not self.request_got:
                                        print(
                                            f'waiting to get success... {retry}')
                                        retry += 2
                                        await asyncio.sleep(2)

                                        if retry >= 20:
                                            error = True
                                            break
                                    else:
                                        break

                                if error:

                                    break

                                await self.page.disable_fetch_events()

                                if self.pagination_completed:
                                    break

                                status = await self.check_captcha(self.page)
                                if status:
                                    break

                            except:
                                break

                        if self.pagination_completed:
                            self.pagination_completed = False
                            await asyncio.sleep(5)
                            # await self.page.refresh()
                            await self.browser_close(self.page, browser)
                            break

                        else:
                            await asyncio.sleep(5)
                            await self.browser_close(self.page, browser)
                            # break
                    else:
                        await asyncio.sleep(5)
                        await self.browser_close(self.page, browser)

                else:
                    # self.metas.append(
                    #     {"keyword": self.keyword, 'page': self.page_number, 'position': self.position})
                    await self.browser_close(self.page, browser)
                    await asyncio.sleep(5)
                    # break

    async def redirect_url(self, event: RequestPausedEvent):

        request_id = event['params']['requestId']
        request = event['params']['request']

        url = request['url']
        postData = request.get('postData', "{}")
        headers = request.get('headers', {})
        # if 'hcaptcha.com/getcaptcha' in url:
        #     print(event)
        if not self.request_got:
            if 'api/license-search/search' in url:
                # print(event)

                post_data = loads(postData)
                token = post_data.get('token')

                postData = '{"text":"' + self.keyword + '","pageNo":' + \
                    str(self.page_number) + \
                    ',"pageSize":100,"token":"' + token + '"}'

                try:
                    response = requests.post(
                        url, headers=headers, data=postData)  # , proxies=self.proxies)
                    info(response)

                    if response.status_code == 200:
                        json_data = response.json()

                        if json_data.get('data'):
                            info(
                                f"Current page - {self.page_number}")

                            licenses = json_data.get(
                                'data', {}).get('licenses', [])

                            for license in licenses:
                                self.position += 1

                                item = {}
                                item['keyword'] = self.keyword
                                item['page'] = self.page_number
                                item['position'] = self.position
                                item['data'] = license

                                # info(item)

                                f = open(
                                    f"{dir_name}/invest_data_{self.keyword}.txt", "a", encoding="utf-8")
                                f.write(
                                    dumps(item, ensure_ascii=False) + "\n")
                                f.close()

                            total_pages = json_data.get('data', {}).get(
                                'pageInfo', {}).get('pageCount')
                            print(json_data.get(
                                'data', {}).get('pageInfo', {}), '-------------------', self.keyword)

                            if total_pages <= self.page_number:
                                info("Pagination completed.")
                                self.pagination_completed = True
                                self.request_got = True
                                await self.page.fail_request(request_id, ErrorReason.TIMED_OUT)

                            self.page_number += 1
                            self.request_got = True
                            await self.page.fail_request(request_id, ErrorReason.TIMED_OUT)

                        else:
                            print(
                                'Token expired...!!!. Need to restart pydoll')
                            self.request_got = True
                            await self.page.fail_request(request_id, ErrorReason.TIMED_OUT)
                    else:
                        print(
                            'Status code failed...!!!. Need to restart pydoll')
                        self.request_got = True
                        await self.page.fail_request(request_id, ErrorReason.TIMED_OUT)
                except:
                    info('request failed...!!!!!!11')
                    self.request_got = True
                    await self.page.fail_request(request_id, ErrorReason.TIMED_OUT)

        await self.page.continue_request(request_id)

    async def check_captcha(self, page):

        while True:
            await asyncio.sleep(5)

            res = await page.execute_script("""
            const iframes = Array.from(document.querySelectorAll("iframe"));

            for (const el of iframes) {
                const src = el.src || "";

                if (src.includes("hcaptcha") && src.includes("challenge")) {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    if (
                        rect.width > 100 &&
                        rect.height > 100 &&
                        style.display !== 'none' &&
                        style.visibility !== 'hidden'
                    ) {
                        return true;
                    }
                }
            }

            return false;
            """)

            captcha_visible = res.get('result', {}).get(
                'result', {}).get('value', False)

            # frames = await page.get_frame()

            # frames = await page.query_selector_all("iframe")

            # hcaptcha_found = False

            # for f in frames:
            #     src = await f.get("src")
            #     if src and "challenge" in src:

            #         hcaptcha_found = await f["visible"]

            if captcha_visible:
                info("Visible captcha detected (manual solve needed)")
                return True
            else:
                await asyncio.sleep(5)
                return

    async def wait_to_load_text(self, page, text, timeout=10):
        retry = 0
        while True:
            html = await page.page_source

            if text in html:
                print(text, '- load - success')
                await asyncio.sleep(2)
                return True
            else:
                await asyncio.sleep(2)
                retry += 2

                if retry >= timeout:
                    print(text, '- load - failed')
                    return False

    async def browser_close(self, page, browser):
        try:
            await page.close()
        except:
            pass
        try:
            await browser.close()
        except:
            pass


obj = InvestDubai()
obj.start()
