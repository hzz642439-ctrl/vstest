from django.db import models
# from bulk_update_or_create import BulkUpdateOrCreateQuerySet

# Create your models here.


# 第三方用户表
class MemberUser(models.Model):
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    # 用户名 : 字符串类型
    user_name = models.CharField(max_length=255, default=None,help_text="用户名")
    # 密码 : 字符串类型
    pass_word = models.CharField(max_length=255, default=None,help_text="密码")
    # 备注 : 字符串类型
    remark = models.TextField(help_text="备注")
    # 分组 ##
    # 代理ip ##
    proxy_ip = models.CharField(max_length=255, default=None,help_text="代理ip")
    # 会员用户状态
    status = models.IntegerField(null=False, default=0, help_text='会员用户状态 {0:准备; 1:开启; 2:暂停; 3:关闭}')
    work_status = models.IntegerField(default=1, help_text='工作状态 {0:不工作; 1:工作;}')
    bc_type = models.CharField(max_length=255,help_text="平台类型")
    sport_type = models.CharField(max_length=255,default="all",help_text="玩法类型")
    # 成数 下级账号购买100块，按照80块钱支付，叫做8成
    percent = models.FloatField(default=10, help_text="成数")

    amount = models.FloatField(default=0, help_text="账面金额")
    # 交收预警金额
    is_warn = models.IntegerField(null=False, default=0, help_text="是否预警")
    # 登录状态
    login_status = models.IntegerField(null=False, default=0, help_text='会员用户登录状态 {0:未登录; 1:登陆中; 2:已登录}')
    # login_status = IntegerField(help_text="登录状态")

    # 定义字段创建时间 ： 时间类型 当数据创建或者更新时自动更新时间 注释
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')


    class Meta:
        db_table="member_user"

