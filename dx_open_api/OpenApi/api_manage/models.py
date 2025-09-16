from django.db import models
# from bulk_update_or_create import BulkUpdateOrCreateQuerySet

# Create your models here.


# 第三方用户表
class ApiData(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    # 用户名 : 字符串类型
    name = models.CharField(max_length=255, default=None,help_text="接口名称")
    author = models.CharField(max_length=255, default=None,help_text="作者")
    type = models.CharField(max_length=255, default=None,help_text="类型")
    logo = models.CharField(max_length=255, default=None,help_text="logo")
    price_obj = models.JSONField(null=False,default=dict,help_text="价格")
    official_website = models.CharField(max_length=255, default=None,help_text="官网(外部连接)")
    use_method = models.CharField(max_length=255, default=None,help_text="使用条款，方案")
    visible = models.IntegerField(null=False,default=0,help_text="是否对外公布")
    api_domain = models.JSONField(null=False,default=dict,help_text="域名")
    # 备注/描述 : 字符串类型
    remark = models.TextField(help_text="备注")
    details = models.TextField(help_text="详情")
    common_problem = models.TextField(help_text="常见问题")
    status = models.IntegerField(null=False, default=0, help_text='状态 {0:准备; 1:开启; 2:暂停; 3:关闭}')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table="api_data"



class UrlVersions(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    # 用户名 : 字符串类型
    name = models.CharField(max_length=255, default=None,help_text="接口名称")
    versions = models.CharField(max_length=255, default=None,help_text="url")
    api_data = models.ForeignKey(ApiData, blank=True, null=True, verbose_name=u'会员', related_name='url_versions', on_delete=models.CASCADE, help_text="来源")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table="url_versions"



class ApiGroup(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    # 用户名 : 字符串类型
    name = models.CharField(max_length=255, default=None,help_text="接口名称")
    api_data = models.ForeignKey(ApiData, blank=True, null=True, verbose_name=u'会员', related_name='api_group', on_delete=models.CASCADE, help_text="来源")
    versions = models.ForeignKey(UrlVersions, blank=True, null=True, verbose_name=u'会员', related_name='api_group', on_delete=models.SET_NULL, help_text="来源")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table="api_group"



class ApiUrl(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    # 用户名 : 字符串类型
    name = models.CharField(max_length=255, default=None,help_text="接口名称")
    api_data = models.ForeignKey(ApiData, blank=True, null=True, verbose_name=u'会员', related_name='api_url', on_delete=models.CASCADE, help_text="来源")
    group = models.ForeignKey(ApiGroup, blank=True, null=True, verbose_name=u'会员', related_name='api_url', on_delete=models.SET_NULL, help_text="来源")
    url = models.CharField(max_length=255, default=None,help_text="url")
    method = models.CharField(max_length=255, default=None,help_text="请求方式")
    remark = models.TextField(help_text="备注")
    headers = models.JSONField(null=False,default=dict,help_text="请求头")
    query = models.JSONField(null=False,default=dict,help_text="参数")
    body = models.JSONField(null=False,default=dict,help_text="body")
    response = models.JSONField(null=False,default=dict,help_text="返回")
    versions = models.ForeignKey(UrlVersions, blank=True, null=True, verbose_name=u'会员', related_name='api_url', on_delete=models.SET_NULL, help_text="来源")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table="api_url"


class Collect(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    api_data = models.ForeignKey(ApiData, blank=True, null=True, verbose_name=u'会员', related_name='api_collect', on_delete=models.CASCADE, help_text="来源")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table="collect"


class SubscribeApi(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    api_data = models.ForeignKey(ApiData, blank=True, null=True, verbose_name=u'会员', related_name='subscribe_api', on_delete=models.CASCADE, help_text="来源")
    vip_type = models.JSONField(null=False,default=dict,help_text="body")
    token = models.CharField(max_length=255, default=None,help_text="url")
    expiration_time = models.DateTimeField(blank=True, null=True,help_text='创建时间')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table="subscribe_api"


    # class ApiCategory(models.Model):
    #     uid = models.IntegerField(null=False,default=0,help_text="uid")
    #     gid = models.IntegerField(null=False,default=0,help_text="gid")
    #     categoryname= models.CharField(max_length=255, default=None,help_text="分类名称")


