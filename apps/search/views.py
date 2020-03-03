from json import loads as json_loads
from elasticsearch import Elasticsearch
from pyes import ES, HighLighter, Search, MultiMatchQuery
from uliweb import expose, settings, request, json, functions, CORS


@expose("/api/search")
class SearchView(object):

    def __init__(self):
        self.conn = Elasticsearch(hosts=settings.get_var("BUILD/ES_HOSTS"))
        self.resource = functions.get_model("resource")
        self.index = ",".join([item.name for item in self.resource.filter(self.resource.c.deleted == 0)])

    def generate_fields(self, index):
        fields = list()
        rows = self.resource.filter(self.resource.c.name.in_(index.split(",")))
        for row in rows:
            mapping = json_loads(row.mapping)
            for column, attr in mapping.items():
                # index属性的值为true或者不存在index属性时，将当前列名称添加到fields中
                if isinstance(attr, dict) and attr.get("index") is False:
                    continue
                fields.append(column)
        return fields

    @expose("indices")
    def indices(self):
        data = [{"name": item.name, "cn_name": item.cn_name} for item in self.resource.filter(self.resource.c.deleted == 0)]
        return json(data)

    def _search(self, wd, index, start=0, size=10, **kwargs):
        fields = self.generate_fields(index)
        body = {
            "query": {
                "multi_match": {
                    "query": wd,
                    "fields": fields,
                }
            },
            "highlight": {
                "pre_tags": ['<b style="color:red;">'],
                "post_tags": ['</b>'],
                "fields": {key: {} for key in fields}
            },
            "from": start,
            "size": size
        }
        body.update(kwargs)

        result = self.conn.search(index=index, body=body)
        data = [item["_source"] for item in result["hits"]["hits"]]
        # highlight = [item["highlight"] for item in result["hits"]["hits"]]
        # for idx, item in enumerate(data):
        #     hl = highlight[idx]
        #     for k, v in hl.items():
        #         if k in item.keys():
        #             item[k] = v
        return result["hits"]["total"]["value"], data

    @expose("")
    def search(self):
        """
        参数：
        index: 需要检索的索引
        field根据mapping计算出来
        """
        index = request.values.get("index").replace(" ", "") if request.values.get("index") else self.index
        wd = request.values.get("wd", "")
        page = int(request.values.get("page", 1))
        size = int(request.values.get("size", 10))
        start = (page - 1) * size

        total, data = self._search(wd, index, start=start, size=size)

        return json({
            "total": total,
            "data": data,
            "page": page,
            "size": size
        })

    @expose("portal", methods=['GET'])
    @CORS
    def search_portal(self):
        index = request.values.get("index").replace(" ", "") if request.values.get("index") else self.index
        wd = request.values.get("wd", "")
        page = int(request.values.get("page", 1))
        size = int(request.values.get("size", 100))
        start = (page - 1) * size

        sort = [
            "level1_ref",
            {"level2_ref.title": {"nested": {"path": "level2_ref"}}}
        ]
        total, data = self._search(wd, index, start=start, size=size, sort=sort)

        level1_children = list()
        level2_children = list()
        level3_children = list()
        last_item = None
        for item in data:
            if last_item and last_item["level1_ref"] == item["level1_ref"]:
                if last_item["level2_ref"] == item["level2_ref"]:
                    level3_children.append({
                        "name": item["name"],
                        "url": item["url"],
                        "title": item["title"],
                        "desc": item["desc"],
                        "breadcrumb": item["breadcrumb"]
                    })
                else:
                    level2_children.append({
                        "name": last_item["level2_ref"]["name"],
                        "url": last_item["level2_ref"]["url"],
                        "title": last_item["level2_ref"]["title"],
                        # "desc": last_item["level2_ref"]["desc"],
                        # "breadcrumb": last_item["breadcrumb"],
                        "children": level3_children
                    })
                    level3_children = list()
                    level3_children.append({
                        "name": item["name"],
                        "url": item["url"],
                        "title": item["title"],
                        "desc": item["desc"],
                        "breadcrumb": item["breadcrumb"]
                    })
            else:
                if last_item:
                    level2_children.append({
                        "name": last_item["level2_ref"]["name"],
                        "url": last_item["level2_ref"]["url"],
                        "title": last_item["level2_ref"]["title"],
                        # "desc": last_item["level2_ref"]["desc"],
                        # "breadcrumb": last_item["level2_ref"]["breadcrumb"],
                        "children": level3_children
                    })
                    level1_children.append({
                        "name": last_item["level1_ref"],
                        "url": "",
                        "title": last_item["level1_ref"],
                        "desc": "",
                        "children": level2_children
                    })
                level2_children = list()
                level3_children = list()
                level3_children.append({
                    "name": item["name"],
                    "url": item["url"],
                    "title": item["title"],
                    "desc": item["desc"],
                    "breadcrumb": item["breadcrumb"]
                })

            last_item = item

        # 处理最后一条记录
        if level3_children:
            level2_children.append({
                "name": last_item["level2_ref"]["name"],
                "url": last_item["level2_ref"]["url"],
                "title": last_item["level2_ref"]["title"],
                # "desc": last_item["level2_ref"]["desc"],
                "children": level3_children
            })
            level1_children.append({
                "name": last_item["level1_ref"],
                "url": "",
                "title": last_item["level1_ref"],
                # "desc": last_item["desc"],
                "children": level2_children
            })

        return json({
            "total": total,
            "data": level1_children,
            "page": page,
            "size": size
        })

