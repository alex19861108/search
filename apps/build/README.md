### ES的字段类型
######index: 
* no 不检索
* not_analyzed 全匹配检索
* analyzed 分词检索
######store:
* yes 独立存储
* no （默认）不存储，从_source中解析
######indexAnalyzer:
当启用分词检索功能后，需要设置索引分词器和搜索分词器indexAnalyzer/searchAnalyzer。算法中使用名字为ik的分词器。
######分词器配置
```yaml
=== elasticsearch.yml ===
index:
  analysis:
    analyzer:
      ik:
```
#####文档类型mapping结构
```
{
	"title": {
		"boost": 1.0,
		"index": "analyzed",
		"store": "yes",
		"type": "string",
		"indexAnalyzer": "ik",
		"searchAnalyzer": "ik",
		"term_vector": "with_positions_offsets"
	},
	"url": {
		"store": "yes",
		"index": "not_analyzed",
		"type": "string"
	},
	"author": {
		"store": "yes",
		"index": "not_analyzed",
		"type": "string"
	},
	"content": {
		"boost": 1.0,
		"index": "analyzed",
		"store": "yes",
		"type": "string",
		"indexAnalyzer": "ik",
		"searchAnalyzer": "ik",
		"term_vector": "with_positions_offsets"
	},
	"created_date": {
		"store": "yes",
		"index": "not_analyzed",
		"type": "date"
	},
	"modified_date": {
		"store": "yes",
		"index": "not_analyzed",
		"type": "date"
	},
	"type": {
		"store": "yes",
		"index": "not_analyzed",
		"type": "string"
	}
}
```