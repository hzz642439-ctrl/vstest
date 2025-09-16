from django.urls import path
from api_manage import views

api_manage = "api_manage"
urlpatterns = [
      path(api_manage + '/api_create', views.api_create, name='api_create'),
      path(api_manage + '/api_list', views.api_list, name='api_list'),
      path(api_manage + '/api_details', views.api_details, name='api_details'),
      path(api_manage + '/api_update', views.api_update, name='api_update'),
      path(api_manage + '/api_delete', views.api_delete, name='api_delete'),
      path(api_manage + '/api_getcategory',views.api_getcategory,name='api_getcategory'),

      path(api_manage + '/group_create', views.group_create, name='group_create'),
      path(api_manage + '/group_list', views.group_list, name='group_list'),
      path(api_manage + '/group_update', views.group_update, name='group_update'),
      path(api_manage + '/group_delete', views.group_delete, name='group_delete'),

      path(api_manage + '/versions_create', views.versions_create, name='versions_create'),
      path(api_manage + '/versions_list', views.versions_list, name='versions_list'),
      path(api_manage + '/versions_update', views.versions_update, name='versions_update'),
      path(api_manage + '/versions_delete', views.versions_delete, name='versions_delete'),

      path(api_manage + '/url_create', views.url_create, name='url_create'),
      path(api_manage + '/url_list', views.url_list, name='url_list'),
      path(api_manage + '/url_update', views.url_update, name='url_update'),
      path(api_manage + '/url_delete', views.url_delete, name='url_delete'),

      path(api_manage + '/api_all_list', views.api_all_list, name='api_all_list'),
      path(api_manage + '/update_collect', views.update_collect, name='update_collect'),

      path(api_manage + '/create_subscribe', views.create_subscribe, name='create_subscribe'),
      path(api_manage + '/subscribe_list', views.subscribe_list, name='subscribe_list'),
      path(api_manage + '/update_subscribe', views.update_subscribe, name='update_subscribe'),
      path(api_manage + '/cancel_subscribe', views.cancel_subscribe, name='cancel_subscribe'),

]