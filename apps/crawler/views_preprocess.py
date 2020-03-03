import requests
from json import loads as json_loads
from uliweb import expose, settings, functions, request, json


def translate_dct(dct, trans_map):
    """ 不在变换字典中的值会被舍弃 """
    result = dict()
    for key, value in dct.items():
        if key in trans_map.keys():
            result[trans_map[key]] = value
        # else:
        #     result[key] = value
    return result


def translate(lst, trans_map):
    if trans_map is None:
        return lst

    result = list()
    for dct in lst:
        result.append(translate_dct(dct, trans_map))
    return result


@expose("/api/portal")
def api_portal():
    page = int(request.values.get("page", 1))
    size = int(request.values.get("size", 10))

    resource = functions.get_model("resource")
    portal = resource.get("portal")
    if not portal:
        return json({
            "status": "error",
            "message": "there's no resource named portal",
            "data": ""
        })

    pre_action = json_loads(portal.config).get("pre_action")
    site_api = pre_action.get("api")

    response = requests.get(site_api).json()

    # from apps.crawler.mock import mock_portal
    # response = mock_portal
    data = translate(response.get("data"), pre_action.get("translate", None))

    result = {
        "total": len(data),
        "page": page,
        "size": size,
        "data": data
    }
    return json(result)

