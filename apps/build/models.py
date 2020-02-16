"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  models.py
@Description    :  
@CreateTime     :  2020/2/14 17:34
"""
import datetime
from uliweb.orm import Field, Model


class BuildRecord(Model):
    index = Field(str, verbose_name="es中的索引类型", max_length=255, unique=True)
    is_mapped = Field(bool, verbose_name="是否建立mapping", default=False)
    build_date = Field(datetime.datetime, verbose_name="上次索引时间")