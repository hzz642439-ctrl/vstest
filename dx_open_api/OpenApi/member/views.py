import json, datetime, time, pytz
from sdk.jwt import _header_token_check,_method_check,SuccessResponse,ErrorResponse, md5, _check_needs
from sdk._auto_api import AutoApi
from member.models import MemberUser
from member import serializers
from django.utils import timezone
from OpenApi.settings import rcon99,rcon30, TIME_ZONE
from audit_log.views import creat_log
auto_api = AutoApi()



# def member_accredit(gid, uid, plant_code, member_id):
#     plant_group_objs = PlantGroup.objects.filter(gid=gid, plant_code=plant_code)
#
#     if plant_group_objs:
#         plant_group_obj = plant_group_objs.first()
#     else:
#         authority = ["memeber", "ip", "order"]
#         plant_group_obj = PlantGroup.objects.create(
#             gid=gid,
#             uid=uid,
#             plant_code=plant_code,
#             pg_name="共享组织",
#             sub_gid=gid,
#             sub_name=plant_code,
#             authority=authority,
#         )
#     objs = MemberAccredit.objects.filter(gid=gid, plant_group_id=plant_group_obj.id, member_id=member_id)
#     if not objs:
#         obj = MemberAccredit.objects.create(
#             gid=gid,
#             uid=uid,
#             plant_group_id=plant_group_obj.id,
#             member_id=member_id,
#         )
#     return True
#
#
#
# def member_deaccredit(gid, member_id):
#     objs = MemberAccredit.objects.filter(gid=gid, member_id=member_id).delete()
#     return True


@_header_token_check("POST")
def member_create(request):
    _needs = ["bc_type", "percent", "is_init",
             "user_name", "pass_word", "remark", "proxy_ip",
             "status", "amount"]
    #, "place_league", "no_place_pk_key"
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _wuis = request.wuis
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    bc_type = _da["bc_type"]
    try:
        _check_memuser = MemberUser.objects.filter(user_name=_da["user_name"], status__gte=0).count()
        if _check_memuser:
            return ErrorResponse(message="会员账号已存在!", error_code=40016)

        try:
            if _da["is_init"] == 1:
                if "init_username" not in _da or "init_password" not in _da:
                    return ErrorResponse(message="缺少参数:init_username,init_password", error_code=40003, extra_data={"format": ("init_username,init_password")})
                init_data = {
                    "bc_type": bc_type,
                    "username": _da["user_name"],
                    "password": _da["pass_word"],
                    "domain": "",
                    "proxy": _da["proxy_ip"],
                    "init_username": _da["init_username"],
                    "init_password":  _da["init_password"],
                }
                _init_res = auto_api._user_init(init_data)
                if not _init_res:
                    return ErrorResponse(message="用户初始化失败！请联系管理员！", error_code=40022)
                _da["user_name"] = _da["init_username"]
                _da["pass_word"] = _da["init_password"]
                del _da["init_username"]
                del _da["init_password"]
            member_data ={
                "bc_type" : bc_type,
                "username" : _da["user_name"],
                "password" :  _da["pass_word"],
                "domain" :  "",
                "proxy" :  _da["proxy_ip"]
            }
            _login_res = auto_api._user_login(member_data)
        except Exception as e:
            return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
        if not _login_res:
            return ErrorResponse(message="用户登录失败！密码错误或者代理ip不可用", error_code=40023)

        del _da["is_init"]
        _da["gid"] = gid
        _da["uid"] = uid
        _add = MemberUser(**_da, gid=gid, uid=uid)
        _add.save()
        log = "创建新的账号：%s" % _add.user_name
        log_data = {
            "gid": gid,
            "uid": uid,
            "level": 1,
            "message": log,
            "type": "member",
            "plant_code": plant_code,
        }
        creat_log(log_data)
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()



@_header_token_check("GET")
def member_list(request):
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    bc_type = request.GET.get("bc_type", None)
    key_word = request.GET.get("key_word", None)
    login_status = request.GET.get("login_status", None)
    gid = request.gid
    uid = request.uid
    data={}
    _not_ok = []
    if not _page or not _page_size:
        return ErrorResponse(message="page,page_size必传！", error_code=40003, extra_data={"format": ("page,page_size")})
    _page = int(_page)
    _page_size = int(_page_size)
    try:
        filter_obj = {
            "status__gte": 0,
            "gid": gid,
            "uid": uid
        }
        if bc_type:
            filter_obj["bc_type"] = bc_type
        if key_word:
            filter_obj["user_name__icontains"] = key_word
        if login_status:
            filter_obj["login_status"] = login_status
        _wuis = request.wuis
        if _wuis:
            filter_obj["uid__in"] = _wuis
        objs_all = MemberUser.objects.filter(**filter_obj)
        objs = objs_all[(_page - 1) * _page_size: (_page * _page_size)]
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data["list"] = objs
    data["total"] = objs_all.count()
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)

@_header_token_check("POST")
def member_status(request):
    gid = request.gid
    uid = request.uid
    _needs = ["id", "status"]    # , "place_league", "no_place_pk_key"
    _wuis = request.wuis
    plant_code = request.plant_code
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    filter_obj = {
        "gid": gid
    }
    if _wuis:
        filter_obj["uid__in"] = _wuis
    user_objs = MemberUser.objects.filter(**filter_obj, id=_da["id"])
    if _da["status"] == 1:
        status_str = "开启"
    elif _da["status"] == 2:
        status_str = "暂停"
    elif _da["status"] == 3:
        status_str = "关闭"
    else:
        status_str = "准备"
    if user_objs:
        user_obj = user_objs[0]
        user_name = user_obj.user_name
        bc_type = user_obj.bc_type
        if rcon30.hexists("member:lost:login", bc_type + ":" +user_name):
            rcon30.hdel("member:lost:login", bc_type + ":" +user_name)

        if user_obj.status == 1:
            user_status_str = "开启"
        elif user_obj.status == 2:
            user_status_str = "暂停"
        elif user_obj.status == 3:
            user_status_str = "关闭"
        else:
            user_status_str = "准备"
        log = "账号：%s,状态由%s修改为%s" % (user_obj.user_name, user_status_str, status_str)
        log_data = {
            "gid": gid,
            "uid": uid,
            "level": 1,
            "message": log,
            "type": "member",
            "plant_code": plant_code,
        }
        creat_log(log_data)
        user_objs.update(status=_da["status"], login_status=0)
    return SuccessResponse()


@_header_token_check("POST")
def member_update(request):
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _needs = ["id", "login_rule_id", "group_id", "percent",
             "pass_word", "remark", "proxy_ip",
             "status", "amount"]    # , "place_league", "no_place_pk_key"
    _wuis = request.wuis
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)


    filter_obj = {
        "gid": gid
    }
    if _wuis:
        filter_obj["uid__in"] = _wuis
    _member_objs = MemberUser.objects.filter(**filter_obj, id=_da["id"])
    if _member_objs:
        _member_obj = _member_objs[0]
        if _da["proxy_ip_id"] != _member_obj.proxy_ip.id:
            _check_ip_member = MemberUser.objects.filter(proxy_ip=_da["proxy_ip_id"], bc_type=_member_obj.bc_type, status__gte=0)
            if _check_ip_member:
                return ErrorResponse(message="IP已经被使用，操作失败!", error_code=40021)
        update_data = {
            "pass_word": _da["pass_word"],
            "remark": _da["remark"],
            "status": _da["status"],
            "amount": _da["amount"],
            "percent": _da["percent"],
            "proxy_ip": _da["proxy_ip"],
            "updated_at": timezone.localtime(timezone.now())
        }

        log = "账号：%s"
        if update_data["pass_word"] != _member_obj.pass_word:
            log += ",密码由%s修改为%s" % (_member_obj.pass_word, update_data["pass_word"])
        if update_data["amount"] != _member_obj.amount:
            log += ",有效金额由%s修改为%s" % (_member_obj.amount, update_data["amount"])
        if update_data["percent"] != _member_obj.percent:
            log += ",层数由%s修改为%s" % (_member_obj.percent, update_data["percent"])
        if _member_obj.proxy_ip:
            if update_data["proxy_ip"] != _member_obj.proxy_ip:
                log += ",代理IP由%s修改为%s" % (_member_obj.proxy_ip, update_data["proxy_ip"])
        else:
            log += ",代理IP由None修改为%s" % update_data["proxy_ip"].ip

        log_data = {
            "gid": gid,
            "uid": uid,
            "level": 1,
            "message": log,
            "type": "member",
            "plant_code": plant_code,
        }
        creat_log(log_data)
        _member_objs.update(**update_data)
        return SuccessResponse(message="修改成功!")
    return ErrorResponse(message="未获取到！", error_code=40001)

@_header_token_check("DELETE")
def member_delete(request):
    _id=request.GET.get("id")
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _not_ok = ["id"]
    if not _id:
        return ErrorResponse(message="id必传！", error_code=40003, extra_data={"format": ("id")})

    try:
        member_obj = MemberUser.objects.filter(gid=gid, id=_id).first()
        del_mblr = MemberUser.objects.filter(gid=gid, id=_id).delete()
        if not del_mblr:
            return ErrorResponse(message="未获取到！", error_code=40001)
        member_obj.status = -1
        member_obj.save()
        log = "删除账号：%s," % member_obj.user_name
        log_data = {
            "gid": gid,
            "uid": uid,
            "level": 1,
            "message": log,
            "type": "member",
            "plant_code": plant_code,
        }
        creat_log(log_data)
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()



# Create your views here.
@_header_token_check(["POST"])
def member_login(request):
    gid = request.gid
    uid = request.uid
    _wuis = request.wuis
    _needs = ["user_name", "pass_word", "bc_type", "proxy_ip"]
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)


    filter_obj = {
        "gid": gid,
        "uid": uid
    }
    _json = {
        "bc_type": _da["bc_type"],
        "username": _da["user_name"],
        "password": _da["pass_word"],
        "domain": "",
        "proxy": ""
    }
    if "ip" in _da:
        _json["proxy"] = _da["proxy_ip"]
    _login_res=auto_api._user_login(_json)
    # _login_res = True
    if _login_res:
        MemberUser.objects.update_or_create(
            gid=gid,
            uid=uid,
            bc_type=_da["bc_type"],
            user_name=_da["user_name"],
            defaults={
                'pass_word': _da["pass_word"],
                'proxy_ip': _json["proxy"],
                'status': 1
            }
        )
        return SuccessResponse(data=_login_res)
    return ErrorResponse(message="操作失败！", error_code=40024)

