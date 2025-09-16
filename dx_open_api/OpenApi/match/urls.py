from django.urls import path
from match import views as cviews

match_urls = [
]

order_urls = [

]  # 包含产品管理和订单管理
match = "match"
urlpatterns = [
                  path(match + '/match_select', cviews.match_select, name='match_select'),
                  path(match + '/other_platform_odd_list', cviews.other_platform_odd_list, name='other_platform_odd_list'),
                  path(match + '/member_limit', cviews.member_limit, name='member_limit'),
                  path(match + '/get_now_odds_all_details', cviews.get_now_odds_all_details, name='get_now_odds_all_details'),
                  # path(league + '/delete_scheme', cviews.delete_scheme, name='delete_scheme')
              ] + match_urls + order_urls