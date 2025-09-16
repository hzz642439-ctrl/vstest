from django.db import models
# from bulk_update_or_create import BulkUpdateOrCreateQuerySet

# Create your models here.

class AuditLog(models.Model):
    # 数据库表名
    # __tablename__ = 'ql_league_rlue'
    gid = models.IntegerField(null=False,default=0,help_text="gid")
    uid = models.IntegerField(null=False,default=0,help_text="uid")
    message = models.TextField(help_text="日志内容")
    level = models.IntegerField(null=False, default=0, help_text="日志级别")
    type = models.CharField(max_length=255, default="", help_text="日志类别")
    check_status = models.IntegerField(null=False, default=0, help_text="消息查看状态{0:未查看; 1:已查看}")
    plant_code = models.CharField(max_length=255, default="", help_text="plant_code")
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True,help_text='创建时间')
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True,help_text='更新时间')
    class Meta:
        db_table=("audit_log")
