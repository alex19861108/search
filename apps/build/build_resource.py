"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  build_resource.py
@Description    :  
@CreateTime     :  2020/2/21 15:58
"""
import requests
import json
import math
import logging
import traceback
from elasticsearch import Elasticsearch
from uliweb import settings, functions
log = logging.getLogger(__name__)


class Builder:
    conn = Elasticsearch(hosts=settings.get_var("BUILD/ES_HOSTS"))

    @staticmethod
    def load_resource(obj):
        """
        资源入库
        """
        config = json.loads(obj.config)

        # 数据存储在ES的索引
        index = obj.name
        # index对应的mapping
        mapping = json.loads(obj.mapping)

        # 建index，建mapping
        if not Builder.conn.indices.exists(index):
            Builder.conn.indices.create(index, {"mappings": {"properties": mapping}})

        # 数据入库
        is_last_page = False
        page = 1
        while is_last_page is False:
            # 组装要抓取的url
            crawler_api = config.get("api").format(page)

            # 根据api抓取数据
            log.info("[builder.load_resource]: {}".format(crawler_api))
            # response = requests.get(crawler_api).json()

            from apps.crawler.mock import mock_portal, mock_forumpost
            if index == "portal":
                mock_response = mock_portal
            elif index == "forumpost":
                mock_response = mock_forumpost
            else:
                mock_response = json.dumps(mock_forumpost)
            response = json.loads(mock_response)
            data = response.get("data")

            # 获取下一页的页码
            size, page, total = response.get("size"), response.get("page"), response.get("total")
            is_last_page = page == math.ceil(total / size)
            page += 1

            # 解析api返回的数据
            for document in data:
                # 文档内容
                # document = json.dumps(item)
                # 主键
                id = document.get("id")
                # 删除标记
                if Builder.conn.exists(index, id) is True:
                    if document.get("deleted", None):
                        Builder.conn.delete(index, id)
                    else:
                        Builder.conn.update(index, id=id, body={"doc": document})
                else:
                    Builder.conn.index(index, document, id=id)

    @staticmethod
    def build():
        resource = functions.get_model("resource")
        for row in resource.filter(resource.c.deleted == 0):
            try:
                Builder.load_resource(row)
            except Exception as e:
                traceback.print_exc(e)


def process():
    Builder.build()
