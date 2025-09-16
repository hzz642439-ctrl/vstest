import json, datetime, time
from sdk.jwt import _header_token_check,_method_check,SuccessResponse,ErrorResponse, md5, _check_needs
from sdk._auto_api import AutoApi
from audit_log.models import AuditLog

auto_api = AutoApi()



def creat_log(_da):
    _da["check_status"] = 0
    _add = AuditLog(**_da)
    _add.save()
    return _add


@_header_token_check("GET")
def log_list(request):
    gid = request.gid
    uid = request.uid
    _wuis = request.wuis
    data={}
    _not_ok = []
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    _level = request.GET.get("level", None)
    _type = request.GET.get("type", None)
    if not _page:
        _not_ok.append("page")
    if not _page_size:
        _not_ok.append("page_size")
    if len(_not_ok) !=0:
        return ErrorResponse(message="缺少参数:%s"%(",".join(_not_ok)), error_code=40003, extra_data={"format": (",".join(_not_ok))})
    _page = int(_page)
    _page_size = int(_page_size)
    try:
        filter_obj = {
            "gid": gid,
            "uid": uid
        }
        if _level:
            filter_obj["level"] = _level
        if _type:
            filter_obj["type"] = _type
        objs = list(AuditLog.objects.values().filter(**filter_obj).order_by("-id"))
        total = len(objs)
        objs = objs[(_page-1)*_page_size:_page*_page_size]
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data["list"] = objs
    data["total"] = total
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)


@_header_token_check("GET")
def read_log(request):
    gid = request.gid
    uid = request.uid
    id = request.GET.get("id", None)
    data={}
    _not_ok = ["id"]
    if not id:
        return ErrorResponse(message="缺少参数:%s"%(",".join(_not_ok)), error_code=40003, extra_data={"format": (",".join(_not_ok))})

    try:
        message_objs = AuditLog.objects.filter(gid=gid, id=id)
        if not message_objs:
            return ErrorResponse(message="不能读取其他用户信息!", error_code=40025)
        message_objs.update(check_status=1)
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()


@_header_token_check("DELETE")
def log_delete(request):
    _message_ids=request.GET.get("ids")
    gid = request.gid
    uid = request.uid
    _not_ok = []
    if not _message_ids:
        _not_ok.append("id")
    if len(_not_ok) !=0:
        return ErrorResponse(message="缺少参数:%s"%(",".join(_not_ok)), error_code=40003, extra_data={"format": (",".join(_not_ok))})
    _message_ids_list = _message_ids.split(",")
    try:
        _message_obj = AuditLog.objects.filter(gid=gid, id__in=_message_ids_list).delete()
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()


@_header_token_check("GET")
def unread_count(request):
    gid = request.gid
    uid = request.uid
    _wuis = request.wuis
    filter_obj = {
        "gid": gid,
        "uid": uid,
        "check_status": 0
    }
    message_objs = list(AuditLog.objects.values_list("id",flat=True).filter(**filter_obj))
    unread_count = len(message_objs)
    data = {
        "unread_count": unread_count
    }
    return SuccessResponse(data=data)