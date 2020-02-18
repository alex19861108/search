"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  models.py
@Description    :  
@CreateTime     :  2020/2/14 17:34
"""
import datetime

from uliweb.orm import Field, Reference, TEXT, CHAR, Model, SelfReference
from uliweb.utils.common import get_var


class BatchAdmin(Model):
    __dispatch_enabled__ = False

    title = Field(str, max_length=50, verbose_name="批处理名称", required=True)
    file_name = Field(str, max_length=255, verbose_name="文件名")
    responsible = Reference("user", verbose_name="责任人", required=True)
    begin_time = Field(datetime.datetime, verbose_name="批处理开始时间", auto_now_add=True)
    finish_time = Field(datetime.datetime, verbose_name="批处理结束时间")
    job_type = Field(CHAR, max_length=1, verbose_name="批处理类型", choices=get_var("BATCH_CONFIG/JOB_TYPE"))
    error_message = Field(TEXT, verbose_name="出错信息")
    status = Field(bool, verbose_name="状态")

    class Table:
        fields = [
            {"name": "title", "width": 100},
            {"name": "file_name", "width": 100},
            {"name": "responsible", "width": 50},
            {"name": "job_type", "width": 50},
            {"name": "begin_time", "width": 100},
            {"name": "finish_time", "width": 100},
            {"name": "duration", "verbose_name": "耗时", "width": 100},
            {"name": "error_message", "width": 100},
            {"name": "success_flag", "width": 50}
        ]


class BatchAdminDetails(Model):
    __dispatch_enabled__ = False

    batch_admin = Reference("batch_admin", verbose_name="批处理程序", collection_name="batch_details")
    info_time = Field(datetime.datetime, verbose_name="日志记录时间", auto_now_add=True, required=True)
    log = Field(TEXT, verbose_name="日志记录信息")

    class Table:
        fields = [
            {"name": "log_type", "width": 40},
            {"name": "log", "width": 400},
            {"name": "info_time", "width": 100},
        ]


class BuildRecord(Model):
    index = Field(str, verbose_name="es中的索引类型", max_length=255, unique=True)
    is_mapped = Field(bool, verbose_name="是否建立mapping", default=False)
    build_date = Field(datetime.datetime, verbose_name="上次索引时间")


class ProductInfo(Model):
    """ 产品信息
    """
    homepage = Field(str, verbose_name="主页", unique=True)
    name = Field(str, verbose_name="名称")
    type = Field(str, verbose_name="所属分类")
    desc = Field(str, verbose_name="产品描述", max_length=1024)


class HelpDocument(Model):
    """ 帮助文档
    """
    title = Field(str, verbose_name="文档标题")
    content = Field(str, verbose_name="文档内容")


class Assets(Model):
    """ 资产
    """
    pass


class ForumTopic(Model):
    forum = Reference("forum", verbose_name="所属主题", collection_name="forum_topics", required=True)
    topic_type = Reference("forumtopictype", verbose_name="主题类型", collection_name="topic_topictype")
    posted_by = Reference("user", verbose_name="发帖人", auto_add=True, collection_name="user_topics")


class ForumPost(Model):
    """ 论坛回复
    """
    topic = Reference("forumtopic", verbose_name="所属主题", collection_name="topic_posts")
    parent = SelfReference(verbose_name="所属回复", collection_name="children_post")
    num_replies = Field(verbose_name="回复总数", default=0)
    floor = Field(int, verbose_name="楼层", required=True)
    slug = Field(str, max_length=32, verbose_name="唯一识别串")
    # posted_by = Reference("user", verbose_name="回复人", auto_add=True, collection_name="user_posts")
    # modified_by = Reference("user", verbose_name="修改人", collection_name="user_modified_posts")
    # deleted_by = Reference("user", verbose_name="删除人", collection_name="user_deleted_posts")
    # last_post_user = Reference("user", verbose_name="最后回复人", collection_name="last_reply_user_post")
    created_on = Field(datetime.datetime, verbose_name="创建时间", auto_now_add=True)
    update_on = Field(datetime.datetime, verbose_name="修改时间")
    deleted_on = Field(datetime.datetime, verbose_name="删除时间")
    last_reply_on = Field(datetime.datetime, verbose_name="最新回复时间")
    deleted = Field(bool, verbose_name="删除标志", default=False)
    reply_email = Field(bool, verbose_name="有回复时是否邮件通知")

    @property
    def es_doc(self):
        doc = {
            "id": self.id,
            "title": self.topic.subject,
            # "url": "/forum/{}/{}".format(self.topic.forum.id, self.topic.id),
            "author": self.posted_by.nickname,
            "content": self.content,
            "created_date": self.created_on,
            "modified_date": self.update_on,
            "type": "forumpost"
        }
        return doc
