import datetime

from uliweb.orm import Field, Reference, TEXT, CHAR, Model
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
