from django.urls import path
from member import views

match_urls = [
]

order_urls = [

]  # 包含产品管理和订单管理
member = "member"
group = "group"
source = "source"
money = "money"
loginrule = "loginrule"
proxyip = "proxyip"
config = "config"
accredit = "accredit"
urlpatterns = [
      path(member + '/member_create', views.member_create, name='member_create'),
      path(member + '/member_list', views.member_list, name='member_list'),
      path(member + '/member_update', views.member_update, name='member_update'),
      path(member + '/member_delete', views.member_delete, name='member_delete'),
      path(member + '/member_login', views.member_login, name='member_login'),
      path(member + '/member_status', views.member_status, name='member_status'),
] + match_urls + order_urls