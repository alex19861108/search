from pyes import ES, HighLighter, Search, MultiMatchQuery
from uliweb import expose, settings, request, json


@expose("/search")
class SearchView(object):

    def __init__(self):
        self.es_client = ES(settings.get_var("BUILD/ES_HOSTS"))
        self.search_fields = settings.get_var("SEARCH/SEARCH_FIELDS")
        self.doc_types = [item["model"] for item in settings.get_var("BUILD/BUILD_TABLES")]
        self.indices = [item["build"]["index"] for item in settings.get_var("BUILD/BUILD_TABLES")]

    @expose("")
    def search(self):
        doc_types = [item.strip() for item in request.values.get("doc_types", self.doc_types).split(",")]
        fields = request.values.get("fields", self.search_fields)
        keyword = request.values.get("keyword", "")
        page = int(request.values.get("page", 1))
        size = int(request.values.get("size", 20))
        start = (page - 1) * size

        h = HighLighter(['<b style="color:red;">'], ['</b>'])
        query = Search(MultiMatchQuery(fields=fields, text=keyword), start=start, size=size, highlight=h)
        for field in fields:
            query.add_highlight(field, fragment_size=150, number_of_fragments=3)

        es_results = self.es_client.search(query, indices=self.index_name, doc_types=doc_types)

        items = []
        for item in es_results:
            for field in fields:
                if field in item._meta.highlight:
                    item[field] = item._meta.highlight[field][0]
            items.append(item)

        result = {
            "items": items,
            "total": es_results.total,
        }

        if "data" in request.GET:
            return json(result)
        else:
            return result
