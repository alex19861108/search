"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  mock.py
@Description    :  
@CreateTime     :  2020/2/20 19:42
"""
import os
from uliweb import expose, json

cur_dir = os.path.abspath(os.path.dirname(__file__))
apps_dir = os.path.dirname(cur_dir)


def read_file(fname):
    lines = ""
    with open(fname, 'r', encoding="utf-8") as fd:
        for line in fd:
            lines += line
    return lines


mock_portal = read_file(os.path.join(apps_dir, "crawler", "data", "portal.txt"))
mock_forumpost = read_file(os.path.join(apps_dir, "crawler", "data", "forumpost.txt"))
mock_wiki = read_file(os.path.join(apps_dir, "crawler", "data", "wikipage.txt"))


@expose("/mp_e/header/getApp")
def mock_get_app():

    return json(mock_portal)
