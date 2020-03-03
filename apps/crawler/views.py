"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  views.py
@Description    :  
@CreateTime     :  2020/3/2 9:13
"""
from uliweb import expose, functions, json, request
from apps.crawler.constant import OBJ_NOT_FOUND, SUCCESS


@expose("/resource")
class Resource:

    @expose("edit/<int:id>", methods=['GET'])
    def edit_get(self, id):
        resource = functions.get_model("resource")
        obj = resource.get(id)
        if not obj:
            return json({
                "status": OBJ_NOT_FOUND,
                "message": "object not found"
            })

        return json({
                "status": SUCCESS,
                "message": "",
                "data": obj
            })
