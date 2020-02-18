import requests
import json
import hashlib
import math
from datetime import datetime
from uliweb import settings, functions


def translate_key(dct, key_map):
    result = dict()
    for key, value in dct.items():
        if key in key_map:
            result[key_map[key]] = value
        else:
            result[key] = value
    return result


class Crawler:

    @staticmethod
    def proc_site(cls, site_name, site_config):
        """
        通过api抓取要建库的数据
        api分为两种：使用分页和不使用分页
        api返回的结果可以转换
        """
        page = functions.get_model("page")

        is_last_page = False
        _page = 1
        while is_last_page is False:
            # 根据是否分页，组装成要抓取的url
            if site_config.get("is_use_pagination") is True:
                site_api = site_config.get("api").format(_page)
            else:
                site_api = site_config.get("api")

            # 根据api抓取数据
            response = requests.get(site_api).json()
            data = response.get("data")

            # 如果使用分页，获取下一页的页码
            if site_config.get("is_use_pagination") is True:
                _size, _page, _total = response.get("size"), response.get("page"), response.get("total")
                is_last_page = _page == math.ceil(_total / _size)
                _page += 1
            else:
                is_last_page = True

            # 解析返回的数据
            for item in data:
                if site_config.get("translate"):
                    item = translate_key(item, site_config.get("translate"))

                obj = page.filter(page.c.url == item.get("url")).one()
                if obj:
                    if hashlib.md5(obj.content).hexdigest() != hashlib.md5(json.dumps(item)):
                        obj.update(content=json.dumps(item), site=site_name, update_time=datetime.now()).save()
                else:
                    page(url=item.get("url"), content=json.dumps(item),
                         site=site_name, update_time=datetime.now()).save()

    @staticmethod
    def do(cls):
        for site_name, site_config in settings.get_var("CRAWLER/CRAWL_APIS").items():
            cls.proc_site(site_name, site_config)


def process():
    Crawler.do()
