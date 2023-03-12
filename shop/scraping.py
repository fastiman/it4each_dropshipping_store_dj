import json
import random
from _decimal import Decimal

import requests
from bs4 import BeautifulSoup
from requests import RequestException, HTTPError

from main.settings import URL_SCRAPING_DOMAIN, URL_SCRAPING
from shop.models import Product

"""
{
    'name': 'Труба профильная 40х20 2 мм 3м', 
    'image_url': 'https://my-website.com/30C39890-D527-427E-B573-504969456BF5.jpg', 
    'price': Decimal('493.00'), 
    'unit': 'за шт', 
    'code': '38140012'
 }
 """

USER_AGENTS = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
               'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577',
               'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16.2',
               'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
               'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13']

# ====================== scraping errors =================


class ScrapingError(Exception):
    pass


class ScrapingTimeoutError(ScrapingError):
    pass


class ScrapingHTTPError(ScrapingError):
    pass


class ScrapingOtherError(ScrapingError):
    pass
# =============================================================


def get_proxy():
    proxy_list = requests.get('https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous')
    proxy = requests.get(
        'https://gimmeproxy.com/api/getProxy?get=true&user-agent=true&supportsHttps=true&anonymityLevel=1&protocol=http&ipPort=true',
        timeout=10.0)
    if proxy:
        print(f"[proxy] {proxy.text}")
        return {'http': 'http://' + proxy.text}
    else:
        proxy.raise_for_status()


def get_proxy_list():
    proxy_list = requests.get('https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous')
    # proxy = requests.get(
    #     'https://gimmeproxy.com/api/getProxy?get=true&user-agent=true&supportsHttps=true&anonymityLevel=1&protocol=http&ipPort=true',
    #     timeout=10.0)
    if proxy_list:
        # print(f"[proxy] {proxy.text}")
        # return {'http': 'http://' + proxy.text}

        pretty_proxy = proxy_list.text.split()
        # for i in pretty_proxy:
        #     print(i)
        #     print(50 * '=')
        return pretty_proxy
    else:
        proxy_list.raise_for_status()


def get_html():
    proxy_list = get_proxy_list()
    proxy_http = {'http': 'http://'+random.choice(proxy_list)}
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        response = requests.get(URL_SCRAPING, proxies=proxy_http, headers=headers, timeout=20.0)
        # response = requests.get("https://a.com", proxies=proxy_http, headers=headers, timeout=20.0)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise ScrapingTimeoutError("request timed out")
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        exit(0)
    except Exception as err:
        raise ScrapingOtherError(err)
        print(f'Other error occurred: {err}')
        exit(0)
    else:
        print("[PROXY] Success!", proxy_http)
        return response


def scraping():
    response = get_html()
    data_list = []
    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    blocks = soup.select('.product-list-item')
    for block in blocks:
        data = {}
        code = block.select_one('a')['data-id']
        data['code'] = code
        name = block.select_one('img')['title']
        data['name'] = name

        # image_url = URL_SCRAPING_DOMAIN + block.select_one('img')['src']
        image_url = block.select_one('img')['data-original']
        data['image_url'] = image_url

        price_raw = block.select_one('.m-campaignPrice').text  # 1,529.15 TL
        price = Decimal(price_raw.replace(' TL', '').replace(',', ''))  # 1529.15
        data['price'] = price
        data['unit'] = 'за шт'
        # print(f'HTML text consists of {len(block.text)} symbols')
        # print(50 * '=')
        # break
        print(data)
        data_list.append(data)

    for item in data_list:
        if not Product.objects.filter(code=item['code']).exists():
            Product.objects.create(
                name=item['name'],
                code=item['code'],
                price=item['price'],
                unit=item['unit'],
                image_url=item['image_url'],
            )

    return data_list


if __name__ == '__main__':
    scraping()
    # print(type(get_proxy_list()))
    # get_proxy_list()
    # print(get_proxy_list().text)
