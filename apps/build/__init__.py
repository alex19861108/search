import sys
import logging
import time
import traceback
from datetime import datetime

from uliweb import functions
from uliweb.orm import Begin, Commit, Rollback, Reset

log = logging.getLogger(__name__)


class Job:
    def __init__(self, title, responsible, job_type=""):
        self.batch_admin = functions.get_model("batch_admin")
        self.batch_admin_details = functions.get_model("batch_admin_details")
        self.title = title
        self.responsible = responsible
        self.job_type = job_type

    def finish(self):
        pass

    def error(self, error_message):
        pass

    def run(self):
        pass


class BatchJob(Job):
    def __init__(self, title, responsible, job_type, *args, **kwargs):
        super(BatchJob, self).__init__(title, responsible, job_type, *args, **kwargs)
        self.batch = self.batch_admin(title=self.title, responsible=responsible, job_type=job_type)

    def process(self, *args, **kwargs):
        pass

    def success(self):
        self.batch.finish_time = datetime.now()
        self.batch.status = True
        self.batch.save()

    def error(self, error_message):
        self.batch.finish_time = datetime.now()
        self.batch.error_message = error_message
        self.batch.status = False
        self.batch.save()

    def run(self, *args, **kwargs):
        try:
            Begin()
            self.process(*args, **kwargs)
            Commit()
            self.success()
        except Exception as e:
            Rollback()
            traceback.print_exc()
            self.error(traceback.format_exc())


