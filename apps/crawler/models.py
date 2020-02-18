import datetime
from uliweb import settings
from uliweb.orm import Model, Field, Reference, Text


def generate_page_type_choices():
    choices = []
    for site_name, site_config in settings.get_var("CRAWLER/CRAWL_APIS").items():
        choices.append((site_name, site_config.get("name")))


class Page(Model):
    url = Field(str, primary_key=True, index=True, required=True, max_length=2048, verbose_name="页面url,页面存储时作为主键")
    content = Field(Text, verbose_name="页面内容")
    site = Field(str, verbose_name="页面站点", choices=generate_page_type_choices())
    update_time = Field(datetime.datetime, verbose_name="更新时间")
