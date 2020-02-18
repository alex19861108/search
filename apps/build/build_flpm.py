"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  main.py
@Description    :  将数据库中的数据导入到es,并创建es索引
@CreateTime     :  2020/2/14 16:18
"""
import logging
from datetime import datetime
from pyes import ES
from uliweb import settings, functions
from apps.build import BatchJob

log = logging.getLogger(__name__)


def oper_index(es_client, index, doc_type=None, mapping=None):
    if not isinstance(mapping, dict):
        return

    if index is None:
        return
    exists = es_client.indices.exists_index(index)
    if exists:
        if doc_type is None:
            return
        es_client.indices.put_mapping(doc_type, {"properties": mapping}, [index])
    if not exists:
        es_client.indices.create_index(index)
        es_client.indices.refresh(index, timesleep=1)


def do_build(es_client, build_tables):
    build_record = functions.get_model("build_record")

    for tbl in build_tables:
        doc_type = tbl["build"]["doc_type"]
        index = tbl["build"]["index"]
        mapping = tbl["build"]["mapping"]

        # 通过模型名获取模型
        model_name = tbl["model"]
        model = functions.get_model(model_name)

        # 数据库修改，创建标志
        column_created_date = tbl.get("translate").get("column_created_date", None)
        column_modified_date = tbl.get("translate").get("column_modified_date", None)

        # 有效和删除标志
        column_enabled = tbl.get("translate").get("column_enabled", None)
        column_deleted = tbl.get("translate").get("column_deleted", None)

        # 获得model.c.column_created_date, model.c.column_modifed_date
        if column_created_date and hasattr(model.c, tbl["column_created_date"]):
            attr_created_date = getattr(model.c, tbl["column_created_date"])
        else:
            log.info("%s没有定义column_created_date属性" % model_name)
            continue

        if column_modified_date and hasattr(model.c, tbl["column_modified_date"]):
            attr_modified_date = getattr(model.c, tbl["column_modified_date"])
        else:
            log.info("%s没有定义modified_date属性" % model_name)
            continue

        if column_deleted and hasattr(model.c, tbl["column_deleted"]):
            attr_deleted = getattr(model.c, tbl["column_deleted"])
        else:
            log.info("%s没有定义deleted属性" % model_name)
            continue

        if column_enabled and hasattr(model.c, tbl["column_enabled"]):
            attr_enabled = getattr(model.c, tbl["column_enabled"])
        else:
            attr_enabled = True

        created_condition = (attr_deleted == 0) & (attr_enabled == 1)
        modified_condition = (attr_deleted == 0) & (attr_enabled == 1)
        deleted_condition = (attr_enabled == 0) if attr_enabled is not None else (attr_deleted == 1)

        rec = build_record.get(build_record.c.index_name == index)
        # 建立mapping,更新数据索引时间 build_date 为上次数据库记录的索引时间
        if not rec:
            # es_client.ensure_index(index, [(doc_type, {"properties": mapping})])
            oper_index(es_client, index, doc_type, mapping)
            rec = build_record(index=index, is_mapped=True, build_date=datetime.now())
            rec.save()

            # build index
            for post in model.filter(created_condition):
                es_client.index(post.es_doc, index, doc_type=doc_type, id=post.es_doc["id"])
                log.info("insert (create-time) index %s--%d" % (doc_type, post.es_doc["id"]))
        else:
            last_build_date = rec.build_date
            if not rec.is_mapped:
                oper_index(es_client, index, doc_type, mapping)
                # es_client.ensure_index(index, [(doc_type, {"properties": mapping})])
                rec.is_mapped = True
            rec.build_date = datetime.now()
            rec.save()

            created_condition = (attr_created_date > last_build_date) & created_condition
            modified_condition = (attr_modified_date > last_build_date) & modified_condition
            deleted_condition = (attr_modified_date > last_build_date) & deleted_condition

            # build index
            for post in model.filter(created_condition):
                es_client.index(post.es_doc, index, doc_type=doc_type, id=post.es_doc["id"])
                log.info("insert (create-time) index %s--%d" % (doc_type, post.es_doc["id"]))

            # update index
            for post in model.filter(modified_condition):
                if es_client.exists(index, doc_type, post.es_doc["id"]):
                    es_client.update(index, doc_type=doc_type, id=post.es_doc["id"], document=post.es_doc)
                    log.info("update index %s--%d" % (doc_type, post.es_doc["id"]))
                else:
                    es_client.index(post.es_doc, index, doc_type=doc_type, id=post.es_doc["id"])
                    log.info("insert (modified-time) index %s--%d" % (doc_type, post.es_doc["id"]))

            # delete index
            for post in model.filter(deleted_condition):
                if es_client.exists(index, doc_type, post.es_doc["id"]):
                    es_client.delete(index, doc_type, post.es_doc["id"])
                    log.info("delete index %s--%d" % (doc_type, post.es_doc["id"]))


class BatchRunner(BatchJob):

    def process(self, *args, **kwargs):
        """
        write your code here, and write log into file use log
        """
        es_client = ES(server=settings.get_var("BUILD/ES_HOSTS"))
        build_tables = settings.get_var("BUILD/BUILD_TABLES")
        do_build(es_client, build_tables)
