from django.utils.deprecation import MiddlewareMixin
from OpenApi.settings import rcon93
from django.utils import timezone
from sdk.jwt import _header_token_check,_method_check,SuccessResponse,ErrorResponse, md5, _check_needs
from api_manage.models import ApiData, ApiGroup, ApiUrl, Collect, SubscribeApi
from match.utiles import get_match_data, get_pk_name_options, _make_odds_detail
import time, requests, random, json
from django.http.response import HttpResponse
from sdk._new_api import NewAutoApi
auto_api = NewAutoApi()


class ZhuanFaMiddleware(MiddlewareMixin):


    def verify_count(self, vip_type, token):
        limit_type = vip_type["limit_type"]
        limit_count = vip_type["limit_count"]
        cost_type = vip_type["cost_type"]
        count = vip_type["count"]
        if cost_type == "day":
            keys = rcon93.keys(f"api_cost:{cost_type}:{token}:*")
            # 每天的访问次数
            # 检查是否超过了每天的访问次数
            if count <= len(keys):
                return ErrorResponse("访问次数已用完")
        elif cost_type == "month":
            keys = rcon93.keys(f"api_cost:{cost_type}:{token}:*")
            # 每天的访问次数
            # 检查是否超过了每天的访问次数
            if count <= len(keys):
                return ErrorResponse("访问次数已用完")
        elif cost_type == "number":
            pass
        else:
            return ErrorResponse("cost_type 错误")

        if limit_type in ["second", "minute", "hour"]:
            # 每天的访问次数
            # 检查是否超过了每天的访问次数
            keys = rcon93.keys(f"api_cost:{limit_type}:{token}:*")
            # 每天的访问次数
            # 检查是否超过了每天的访问次数
            if limit_count <= len(keys):
                return ErrorResponse("访问次数已用完")
        else:
            return ErrorResponse("limit_type 错误")
        return True

    def add_count(self, vip_type, token):
        limit_type = vip_type["limit_type"]
        cost_type = vip_type["cost_type"]
        _time = time.time()
        key = f"api_cost:{cost_type}:{token}:{_time}"
        if cost_type == "day":
            rcon93.set(key, 1, ex=60 * 60 * 24)
        elif cost_type == "month":
            rcon93.set(key, 1, ex=60 * 60 * 24 * 30)
        elif cost_type == "number":
            pass
        else:
            return ErrorResponse("cost_type 错误")
        key = f"api_cost:{limit_type}:{token}:{_time}"
        if limit_type == "second":
            rcon93.set(key, 1, ex=1)
        elif limit_type == "minute":
            rcon93.set(key, 1, ex=60)
        elif limit_type == "hour":
            rcon93.set(key, 1, ex=60 * 60)
        else:
            return ErrorResponse("limit_type 错误")
        return True

    def transpond(self, request):
        url = request.path
        token = request.headers.get('token')
        subscribe_objs = SubscribeApi.objects.filter(token=token, expiration_time__gt=timezone.now())
        if not subscribe_objs:
            return False, "token 不存在, 或者订阅已经过期"
        subscribe_obj = subscribe_objs.first()
        vip_type = subscribe_obj.vip_type
        self.verify_count(vip_type, token)
        api_data_obj = subscribe_obj.api_data
        api_data_id = api_data_obj.id
        api_domain = api_data_obj.api_domain
        api_url_objs = ApiUrl.objects.filter(url=url, api_data_id=api_data_id)
        if not api_url_objs:
            return False, "url 不存在"
        api_url_obj = api_url_objs.first()
        api_headers = api_url_obj.headers
        api_query = api_url_obj.query
        api_body = api_url_obj.body
        api_method = api_url_obj.method
        print(api_method)
        url = random.choice(api_domain) + url
        try:

            query = dict(request.GET)
            api_query = query
            try:
                _da = json.loads(request.body)
                api_headers = _da["headers"]
                api_body = _da["body"]
            except:
                return False, "参数错误"

            resp = requests.request(method=api_method, url=url, params=api_query, headers=api_headers, json=api_body)
            self.add_count(vip_type, token)
            return True, resp
        except Exception as e:
            return False, str(e)


    def process_request(self, request):
        host_name = request.META.get("HTTP_CODE")
        if request.path.startswith("/swagger") or request.path.startswith("/redoc") :
            return None
        if host_name != "main":
            token = request.headers.get('token')
            subscribe_objs = SubscribeApi.objects.filter(token=token, expiration_time__gt=timezone.now())
            if not subscribe_objs:
                return ErrorResponse("token 不存在, 或者订阅已经过期")
            subscribe_obj = subscribe_objs.first()
            vip_type = subscribe_obj.vip_type
            self.verify_count(vip_type, token)
            if host_name in ["hga","ps3838", "kaiyun"]:
                url = request.path
                url_list = url.split('/')
                if url_list[1] == "match_data":
                    page = request.GET.get('page', 1)
                    page_size = request.GET.get('page_size', 10)
                    match_data = get_match_data(host_name, url_list[3], url_list[2], page, page_size)
                    self.add_count(vip_type, token)
                    print(match_data)
                    return SuccessResponse(data=match_data)
                elif url_list[1] == "league_data":
                    data_obj = json.loads(request.body)
                    data_obj["bc_type"] = host_name
                    data_obj["event_type"] = url_list[3]
                    data_obj["sport_type"] = url_list[2]
                    if "username" not in data_obj:
                        return ErrorResponse("username 必传")
                    if "password" not in data_obj:
                        return ErrorResponse("password 必传")
                    if "proxy" not in data_obj:
                        return ErrorResponse("proxy 必传")
                    res_status, req = auto_api.get_league_data(data_obj)
                    self.add_count(vip_type, token)
                    return SuccessResponse(data=req)
                elif url_list[1] == "league_match_data":
                    data_obj = json.loads(request.body)
                    data_obj["bc_type"] = host_name
                    data_obj["event_type"] = url_list[3]
                    data_obj["sport_type"] = url_list[2]
                    if "username" not in data_obj:
                        return ErrorResponse("username 必传")
                    if "password" not in data_obj:
                        return ErrorResponse("password 必传")
                    if "proxy" not in data_obj:
                        return ErrorResponse("proxy 必传")
                    if "league_id" not in data_obj:
                        return ErrorResponse("league_id 必传")
                    res_status, match_list = auto_api.get_event_data(data_obj)
                    for match in match_list:
                        match["ids"] = str(match["league_id"]) + ":" + str(match["home_id"]) + ":" + str(match["away_id"])
                    match_list = get_pk_name_options(match_list, host_name)
                    self.add_count(vip_type, token)
                    return SuccessResponse(data=match_list)
                elif url_list[1] == "match_info":
                    data_obj = json.loads(request.body)
                    data_obj["bc_type"] = host_name
                    data_obj["sport_type"] = url_list[2]
                    if "username" not in data_obj:
                        return ErrorResponse("username 必传")
                    if "password" not in data_obj:
                        return ErrorResponse("password 必传")
                    if "proxy" not in data_obj:
                        return ErrorResponse("proxy 必传")
                    if "event_type" not in data_obj:
                        return ErrorResponse("event_type 必传")
                    if "match_id" not in data_obj:
                        return ErrorResponse("match_id 必传")
                    res_status, match_data = auto_api.get_event_detail(data_obj)
                    match_data = _make_odds_detail(match_data, host_name, data_obj["event_type"])
                    self.add_count(vip_type, token)
                    return SuccessResponse(data=match_data)
                elif url_list[1] in ["member", "order"]:
                    _json = json.loads(request.body)
                    _json["bc_type"] = host_name
                    res_status, req = getattr(auto_api, url_list[2])(_json)
                    self.add_count(vip_type, token)
                    return SuccessResponse(data=req)
                else:
                    return ErrorResponse("url 不存在")

            else:
                status, data = self.transpond(request)
                if status:
                    return HttpResponse(data.text, data.status_code)
                else:
                    return ErrorResponse(data)

        # return SuccessResponse()

    # def process_response(self, request, response):
    #
    #     host = request.get_host()
    #     url = request.path
    #     host_name = host.split('.')[0]
    #     if host_name == "":
    #         pass
    #     elif host_name == "192":
    #         pass
    #     else:
    #         pass
    #
    #
    #     token = request.headers.get('token')
    #     subscribe_objs = SubscribeApi.objects.filter(token=token, expiration_time__gt=timezone.now())
    #     if not subscribe_objs:
    #         return ErrorResponse("token 不存在, 或者订阅已经过期")
    #     subscribe_obj = subscribe_objs.first()
    #     vip_type = subscribe_obj.vip_type
    #     limit_type = vip_type["limit_type"]
    #     cost_type = vip_type["cost_type"]
    #     _time = time.time()
    #     key = f"api_cost:{cost_type}:{token}:{_time}"
    #     if cost_type == "day":
    #         rcon93.set(key, 1, ex=60*60*24)
    #     elif cost_type == "month":
    #         rcon93.set(key, 1, ex=60*60*24*30)
    #     elif cost_type == "number":
    #         pass
    #     else:
    #         return ErrorResponse("cost_type 错误")
    #
    #
    #     key = f"api_cost:{limit_type}:{token}:{_time}"
    #     if limit_type == "second":
    #         rcon93.set(key, 1, ex=1)
    #     elif limit_type == "minute":
    #         rcon93.set(key, 1, ex=60)
    #     elif limit_type == "hour":
    #         rcon93.set(key, 1, ex=60*60)
    #     else:
    #         return ErrorResponse("limit_type 错误")
    #     return response