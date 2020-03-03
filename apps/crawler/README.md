###抓取模块配置说明
```
wikipage:                                               # 资源名
  api: "http://{host}/api/wikipage?page={}&size=10"     # 访问资源api接口
```

###数据预处理模块配置说明
```
wikipage:
  translate:                                            # 数据字段转换
    app_url: "url"                                      # 将key为app_url的数据转换为url
```

###请求资源方的数据
``` python
[{
    "primary_key": "http://127.0.0.1:8000",
    "app_name": "name",
    "app_type": "app_type",
    "title": "tilte1",
    "content": "content",
    "deleted": 0
}, {
	"primary_key": "http://127.0.0.1:8001",
    "app_name": "name2",
    "app_type": "app_type2",
    "title": "tilte2",
    "content": "content2",
    "deleted": 0
}]
```

#### example
``` python
{
    "pre_action": {
        "api": "http://128.196.96.210:8000/mp_e/header/getApp",
        "translate": {
            "app_url": "primary_key",
            "app_type": "app_type",
            "app_en_name": "app_en_name",
            "remark1": "remark1",
            "remark2": "remark2",
            "desc": "desc"
        }
    },
    "api": "http://localhost:8000/api/portal"
}
```