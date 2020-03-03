"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  models.py
@Description    :  
@CreateTime     :  2020/2/14 17:34
"""

from uliweb.orm import Field, Reference, Model, SelfReference, StringProperty, TextProperty, TimestampProperty


# class ProductInfo(Model):
#     """ 产品信息
#     """
#     homepage = Field(str, verbose_name="主页", unique=True)
#     name = Field(str, verbose_name="名称")
#     type = Field(str, verbose_name="所属分类")
#     desc = Field(str, verbose_name="产品描述", max_length=1024)
#
#
# class HelpDocument(Model):
#     """ 帮助文档
#     """
#     title = Field(str, verbose_name="文档标题")
#     content = Field(str, verbose_name="文档内容")
#
#
# class Assets(Model):
#     """ 资产
#     """
#     pass
