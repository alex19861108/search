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
from pyes import ES
from uliweb import settings, functions
log = logging.getLogger(__name__)


class Builder:
    def __init__(self):
        self.es_client = ES(server=settings.get_var("BUILD/ES_HOSTS"))
        # self.headers = {"Content-Type": "application/json"}

    def load_resource(self, obj):
        """
        资源入库
        """
        config = json.loads(obj.config)

        # 数据存储在ES的索引
        index = obj.name
        # 数据存储在ES中的类型
        doc_type = obj.name
        # index对应的mapping
        mapping = obj.mapping

        # 建index，建mapping
        self.es_client.ensure_index(index, {'properties': mapping})

        # 数据入库
        is_last_page = False
        page = 1
        while is_last_page is False:
            # 组装要抓取的url
            crawler_api = config.get("api").format(page)

            # 根据api抓取数据
            log.info("[builder.load_resource]: {}".format(crawler_api))
            # response = requests.get(crawler_api).json()
            mock_response = """{"total":4,"page":1,"size":10,"data":[{"id":"http://128.196.0.127:8000/ap/1","app_type":"app01","app_en_name":"codemng","remark1":"http://128.194.223.6:8000/ap/2","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/3","app_type":"app02","app_en_name":"app_en-name2","remark1":"http://128.194.223.6:8000/ap/4","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/5","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/6","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/7","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/8","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/9","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/10","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/11","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/12","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/13","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/14","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/15","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/16","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/17","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/18","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/19","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/20","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/21","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/22","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/23","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/24","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/25","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/26","remark2":"","desc":"null"},{"id":"http://128.196.0.127:8000/ap/27","app_type":"app03","app_en_name":"app_en_name3","remark1":"http://128.194.223.6:8000/ap/28","remark2":"","desc":"null"}]}"""
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
                if self.es_client.exists(index, doc_type, id) is True:
                    if document.get("deleted", None):
                        self.es_client.delete(index, doc_type, id)
                    else:
                        self.es_client.update(index, doc_type=doc_type, id=id, document=document)
                else:
                    self.es_client.index(document, index, doc_type=doc_type, id=id)

    def do(self):
        resource = functions.get_model("resource")
        for row in resource.filter(resource.c.deleted == 0):
            try:
                self.load_resource(row)
            except Exception as e:
                traceback.print_exc(e)


def process():
    Builder().do()
