from uliweb.orm import Model, TimestampProperty, TextProperty, StringProperty, BooleanProperty

    
class Resource(Model):
    """ 资源方 """
    name = StringProperty(primary_key=True, index=True, required=True, max_length=20, verbose_name="英文名, 唯一标识")
    cn_name = StringProperty(max_length=20, verbose_name="中文名")
    config = TextProperty(verbose_name="资源配置")
    mapping = TextProperty(verbose_name="ES中的mapping配置")
    create_time = TimestampProperty(verbose_name="接入时间")
    contact = StringProperty(max_length=20, verbose_name="联系人")
    desc = TextProperty(verbose_name="资源描述")
    deleted = BooleanProperty(default=0, verbose_name="逻辑删除标记")
