from json import loads as json_loads
from elasticsearch import Elasticsearch
from uliweb import expose, settings, request, json, functions, CORS


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

    @expose("/api/indices")
    @CORS
    def indices(self):
        resources = self.resource.filter(self.resource.c.deleted == 0).order_by(self.resource.c.order)
        data = [{"name": item.name, "cn_name": item.cn_name} for item in resources]
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
        return result["hits"]["total"]["value"], result["hits"]["hits"]

    @expose("/api/search")
    @CORS
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

        total, hits = self._search(wd, index, start=start, size=size)
        data = [item["_source"] for item in hits]
        highlight = [item["highlight"] for item in hits]
        for idx, item in enumerate(data):
            hl = highlight[idx]
            for k, v in hl.items():
                if k in item.keys():
                    if isinstance(v, list):
                        item[k] = "...".join(v)
                    else:
                        item[k] = v
        return json({
            "total": total,
            "data": data,
            "page": page,
            "size": size
        })

    @expose("/api/sug", methods=['GET'])
    @CORS
    def sug(self):
        index = request.values.get("index", "portal").replace(" ", "")
        if index == "portal":
            return self.portal_suggester(index)
        else:
            return self.term_suggester(index)

    def portal_suggester(self, index="portal"):
        wd = request.values.get("wd", "")
        page = int(request.values.get("page", 1))
        size = int(request.values.get("size", 1000))
        start = (page - 1) * size

        sort = [
            {"level1_ref.title": {"nested": {"path": "level1_ref"}}},
            {"level2_ref.title": {"nested": {"path": "level2_ref"}}}
        ]
        total, hits = self._search(wd, index, start=start, size=size, sort=sort)
        data = [item["_source"] for item in hits]

        level1_children = list()
        level2_children = list()
        level3_children = list()
        last_item = None
        for item in data:
            if last_item and last_item["level1_ref"]["title"] == item["level1_ref"]["title"]:
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
                        "desc": last_item["level2_ref"]["desc"],
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
                        "desc": last_item["level2_ref"]["desc"],
                        # "breadcrumb": last_item["level2_ref"]["breadcrumb"],
                        "children": level3_children
                    })
                    level1_children.append({
                        "name": last_item["level1_ref"]["name"],
                        "url": last_item["level1_ref"]["url"],
                        "title": last_item["level1_ref"]["title"],
                        "desc": last_item["level1_ref"]["desc"],
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
                "desc": last_item["level2_ref"]["desc"],
                "children": level3_children
            })
            level1_children.append({
                "name": last_item["level1_ref"]["name"],
                "url": last_item["level1_ref"]["url"],
                "title": last_item["level1_ref"]["title"],
                "desc": last_item["level1_ref"]["desc"],
                "children": level2_children
            })

        return json({
            "total": total,
            "data": level1_children,
            "page": page,
            "size": size
        })

    def completion_suggester(self, index, size=20):
        wd = request.values.get("wd", "")
        fields = self.generate_fields(index)
        body = {
            "suggest": {
                "sug": {
                    "prefix": wd,
                    "completion": {
                        "field": "title.suggest",
                        "size": size,
                        "skip_duplicates": True,
                        "fuzzy": {
                            "fuzziness": 2
                        }
                    }
                }
            }
        }

        result = self.conn.search(index=index, body=body)
        data = list()
        for sug in result["suggest"]["sug"]:
            for opt in sug["options"]:
                data.append(opt["text"])

        return json({
            "total": result["hits"]["total"]["value"],
            "data": data
        })

    def phrase_suggester(self, index, size=5):
        wd = request.values.get("wd", "")
        field = "title"
        body = {
            "suggest": {
                "sug": {
                    "text": wd,
                    "phrase": {
                        "field": field,
                        "size": size,
                        "highlight": {
                            "pre_tag": "<em>",
                            "post_tag": "</em>"
                        }
                    }
                }
            }
        }
        result = self.conn.search(index=index, body=body)
        data = list()
        for sug in result["suggest"]["sug"]:
            for opt in sug["options"]:
                data.append(opt["text"])

        return json({
            "total": result["hits"]["total"]["value"],
            "data": data
        })

    def term_suggester(self, index, size=5):
        wd = request.values.get("wd", "")
        field = "content"
        body = {
            "suggest": {
                "sug": {
                    "text": wd,
                    "term": {
                        "suggest_mode": "popular",
                        "min_word_length": 2,
                        "field": field,
                        "size": size,
                        "string_distance": "ngram"
                    }
                }
            }
        }
        result = self.conn.search(index=index, body=body)
        data = list()
        for sug in result["suggest"]["sug"]:
            for opt in sug["options"]:
                data.append(opt["text"])

        return json({
            "total": result["hits"]["total"]["value"],
            "data": data
        })
