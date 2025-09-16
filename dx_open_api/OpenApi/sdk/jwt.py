import rest_framework_simplejwt

from OpenApi.response import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
from OpenApi.settings import rcon98
from sdk._auto_api import AutoApi
import hashlib, json
autoApi=AutoApi()
def _header_token_check(_method):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 格式化权限
            if request.method not in _method:
                JsonResponse.status_code=400
                return JsonResponse({"success": False,"code": 400,"data":"","msg": "请求方法不对:%s"%(_method)})
            # try:
            auth = request.META.get('HTTP_AUTHORIZATION', None)
            if auth:
                auth = auth.split()
            else:
                JsonResponse.status_code=200
                return JsonResponse({"success": False,"code": 401,"data":"","msg": "未获取到权限信息:AUTHORIZATION"})
            _plant_code= request.META.get('HTTP_PLANTCODE')
            _mac= request.META.get('HTTP_MAC')
            _version = request.META.get('HTTP_VERSION')
                # print(request.META)
            if auth ==None or _plant_code==None or _mac==None:
                JsonResponse.status_code=200
                return JsonResponse({"success": False,"code": 401,"data":"","msg": "未获取到权限信息:AUTHORIZATION,PLANTCODE,MAC"})
            if auth[0].lower() == 'token':
                _token=auth[1]
                if _token =="visitor":
                    print("------------hello---------------")
                    request.wuis=[]
                    request.name="visitor"
                    request.uid=0
                    request.gid=0
                    request.wid=0
                    request.aid=0
                    request.plant_code="visitor"
                    request.roles=[]
                    request.subscribe=[]
                else:
                    _json={"token":_token,"plant_code":_plant_code,"mac":_mac, "version": _version}
                    _check_token=autoApi._user_check(_json)
                    if _check_token["code"]==200:
                        _gid=_check_token["data"]["gid"]
                        _uid=_check_token["data"]["uid"]
                        _wuis=[]
                        if "work_list" in _check_token["data"]:
                            if "all_sub_uids" in _check_token["data"]["work_list"]:
                                _wuis+=_check_token["data"]["work_list"]["all_sub_uids"]
                            if "this_uids" in _check_token["data"]["work_list"]:
                                _wuis+=_check_token["data"]["work_list"]["this_uids"]
                        if not _wuis:
                            _wuis=_check_token["data"]["wuis"]
                        _wid=_check_token["data"]["wid"]
                        request.gid = _gid
                        request.uid = _uid
                        request.wuis = list(set(_wuis))
                        request.wid = _wid
                        request.user_name = _check_token["data"]["user_name"]
                        request.plant_code = ""
                        if "plant_code" in _check_token["data"]:
                            request.plant_code = _check_token["data"]["plant_code"]
                        request.roles = _check_token["data"]["roles"]
                    else:
                        JsonResponse.status_code=200
                        AuthenticationFailed(_check_token["msg"])
                        return JsonResponse(_check_token)
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

def _method_check(_method):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 格式化权限
            if request.method not in _method:
                return JsonResponse({"success": False,"code": 400,"data":"","msg": "请求方法不对:%s"%(_method)})
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
              
def md5(s) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# def SuccessResponse(data=None, message='操作成功', code=200,  extra_data={}, **kwargs):
#     tmp_data = {'success': True, 'code': code, 'msg': message, 'data': data}
#     tmp_data.update(extra_data)
#     JsonResponse.status_code=code
#     response=JsonResponse(tmp_data)
#     response['Access-Control-Allow-Origin'] = '*'
#     return response
#
#
# def ErrorResponse(data=None, message='操作失败', code=400, extra_data={}, **kwargs):
#     tmp_data = {'success': False, 'code': code, 'msg': message, 'data': data}
#     tmp_data.update(extra_data)
#     tmp_data["code"]=400
#     JsonResponse.status_code=200
#     response=JsonResponse(tmp_data)
#     response['Access-Control-Allow-Origin'] = '*'
#     return response

def get_message_lang(message_lang, error_code, message, extra_data):
    language = "zh"
    if rcon98.hexists("message:all:" + error_code, language):
        message = rcon98.hget("message:all:" + error_code, language).decode("utf-8")
    message_zh = message
    message_en = message
    if rcon98.hexists("message:all:" + error_code, "zh"):
        message_zh = rcon98.hget("message:all:" + error_code, "zh").decode("utf-8")
    if rcon98.hexists("message:all:" + error_code, "en"):
        message_en = rcon98.hget("message:all:" + error_code, "en").decode("utf-8")
    if extra_data:
        if "format" in extra_data:
            # print(message_zh, extra_data["format"])
            message_zh = message_zh % extra_data["format"]
            message_en = message_en % extra_data["format"]
    message_lang["code"] = error_code
    message_lang["text_zh"] = message_zh
    message_lang["text_en"] = message_en
    return message_lang

def SuccessResponse(data=None, message='操作成功', code=200, error_code=40000,message_lang={"code":"msg_code","text_zh":"中文信息","text_en":"English msg"} , extra_data={}, **kwargs):
    # error_code = str(error_code)
    # message_lang = get_message_lang(message_lang, error_code, message, extra_data)
    # message = message_lang["text_zh"]
    tmp_data = {'success': True, 'code': code, 'msg': message,"msg_lang":message_lang, 'data': data}
    tmp_data.update(extra_data)
    JsonResponse.status_code=code
    response=JsonResponse(tmp_data)
    response['Access-Control-Allow-Origin'] = '*'
    return response


def ErrorResponse(data=None, message='操作失败', code=400, error_code=40024, message_lang={"code":"msg_code","text_zh":"中文信息","text_en":"English msg"} , extra_data={}, **kwargs):
    # error_code = str(error_code)
    # message_lang = get_message_lang(message_lang, error_code, message, extra_data)
    # message = message_lang["text_zh"]
    tmp_data = {'success': False, 'code': code, 'msg': message,"msg_lang":message_lang, 'data': data}
    tmp_data.update(extra_data)
    response=JsonResponse(tmp_data)
    response['Access-Control-Allow-Origin'] = '*'
    return response


def _check_needs(_da, _needs):
    data={}
    data['code']=200
    _need_not_ok=[]
    for _need in _needs:
        if _need not in _da:
            _need_not_ok.append(_need)
        else:
            if _da[_need] is None:
                if not _da[_need]:
                    _need_not_ok.append(_need)

    if len(_need_not_ok) !=0:
        data={}
        data['code']=400
        data['error_code']=40003
        data['success']=False
        data['extra_data'] = {
            "format": (",".join(_need_not_ok))
        }
        data["message"]="缺少参数:%s" % ",".join(_need_not_ok)
        data['data']={}
    return data
