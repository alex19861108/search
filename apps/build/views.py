from uliweb import expose, json


@expose("/api/build")
def build():
    from apps.build.build_resource import Builder
    Builder.build()
    return json({"code": 0, "message": "success", "data": []})
