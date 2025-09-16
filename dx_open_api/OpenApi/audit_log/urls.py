from django.urls import path
from audit_log import views as views
log="log"
urlpatterns = [
    # path(log+'/create', views.log_create, name='log_create'),
    path(log+'/list', views.log_list, name='log_list'),
    path(log+'/delete', views.log_delete, name='log_delete'),
    path(log+'/read', views.read_log, name='read_log'),
    path(log+'/unread_count', views.unread_count, name='unread_count'),
    ]