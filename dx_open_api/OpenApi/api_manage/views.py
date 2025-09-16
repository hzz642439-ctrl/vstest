import json, datetime, time, pytz
import random
import re
import string
from tokenize import String
from api_manage.sdk.random_name import is_english,stable_random_name
from sdk.jwt import _header_token_check,_method_check,SuccessResponse,ErrorResponse, md5, _check_needs
from sdk._auto_api import AutoApi
from api_manage import serializers
from django.utils import timezone
from OpenApi.settings import rcon99,rcon30, TIME_ZONE
from api_manage.models import ApiData, ApiGroup, ApiUrl, Collect, SubscribeApi, UrlVersions
from django.db.models import Q
from audit_log.views import creat_log
from api_manage.sdk.minio_upload import minio_upload
from sdk._new_api import NewAutoApi
autoApi=NewAutoApi()
auto_api = AutoApi()
import redis
from OpenApi.settings import rcon100
@_header_token_check("POST")
def api_create(request):
    _needs = ["name", "type", "logo", "price_obj", "official_website", "use_method", "visible",
             "api_domain", "remark", "details", "common_problem"]
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
    # try:
    if ApiData.objects.filter(name=_da["name"]):
        return ErrorResponse(message="项目已存在!")
    if '.' in _da["name"]:
        return ErrorResponse(message="项目名称不能包含'.'")
    _da["gid"] = gid
    _da["uid"] = uid
    _da["author"] = request.user_name
    _add = ApiData(**_da)
    _add.save()
    log = "创建新的项目：%s" % _add.name
    log_data = {
        "gid": gid,
        "uid": uid,
        "level": 1,
        "message": log,
        "type": "API",
        "plant_code": plant_code,
    }
    creat_log(log_data)
    # except Exception as e:
    #     return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()



@_header_token_check("GET")
def api_list(request):
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    type = request.GET.get("type", None)
    search_word = request.GET.get("search_word", None)
    sort_type = request.GET.get("sort_type", None)
    if sort_type is None:
        sort_type = "-updated_at"
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
        if type:
            filter_obj["type"] = type
        search_filter = Q()
        if search_word:
            search_filter = Q(name__icontains=search_word) | Q(remark__icontains=search_word) | Q(details__icontains=search_word)
        objs_all = ApiData.objects.filter(search_filter, **filter_obj).order_by(sort_type)
        objs = objs_all[(_page - 1) * _page_size: (_page * _page_size)]
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data["list"] = objs
    data["total"] = objs_all.count()
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)


@_header_token_check("GET")
def api_details(request):
    gid = request.gid
    uid = request.uid
    id = request.GET.get("id", None)
    _not_ok = []
    try:
        filter_obj = {
            "status__gte": 0,
            "id": id
        }
        objs_all = ApiData.objects.filter(**filter_obj)
        obj = objs_all.first()
        api_uid=obj.uid
        api_gid=obj.gid

        creator=0
        if api_uid==uid and api_gid==gid:
            creator=1
        if not objs_all:
            return ErrorResponse(message="未获取到！", error_code=40001)
        _info = serializers.ApiDataSerializers(objs_all, many=True,context={'request':request}).data
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data = _info[0]
    # name=data.get("name")
    # if not bool(re.fullmatch(r'[A-Za-z0-9]+', name)):
    #     data["name"]=''.join(random.choices(string.ascii_letters+string.digits,k=10))
    # print(data["name"])
    if not is_english(data.get("name", "")):
        data["name"] = stable_random_name(data["name"])
    print(data["name"])
    subscribe_objs = SubscribeApi.objects.values().filter(gid=gid, uid=uid, api_data_id=data["id"],expiration_time__gt=timezone.now())
    data["subscribe_obj"] = subscribe_objs.first()
    print(data["subscribe_obj"])
    data["creator"]=creator
    return SuccessResponse(data=data)

@_header_token_check("POST")
def api_update(request):
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    file=request.FILES.get("file", None)
    data_str = request.POST.get("data")

    # print("name:", request.body)
    if file :
        url=minio_upload(file,"open-api")
    _needs = ["id", "name", "type","price_obj", "official_website", "use_method", "visible",
             "api_domain", "remark", "details", "common_problem"]    # , "place_league", "no_place_pk_key"
    _wuis = request.wuis
    try:
        _da=json.loads(data_str)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    id = _da["id"]
    del _da["id"]
    if file:
        _da["logo"]=url
    try:
        _obj = ApiData.objects.filter(id=id, gid=gid, uid=uid)
        _obj.update(**_da)
        log = "修改API：%s," % _obj.first().name
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
        return ErrorResponse(message="修改失败!")
    return SuccessResponse(data=_da)

@_header_token_check("DELETE")
def api_delete(request):
    _id=request.GET.get("id")
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _not_ok = ["id"]
    if not _id:
        return ErrorResponse(message="id必传！", error_code=40003, extra_data={"format": ("id")})

    try:
        objs = ApiData.objects.filter(gid=gid, uid=uid, id=_id)
        obj = objs.first()
        del_count, _ = objs.delete()
        # del_mblr = objs.update(status=-1)
        # if not del_mblr:
        #     return ErrorResponse(message="未获取到！", error_code=40001)
        # obj = objs.first()
        log = "删除API：%s," % obj.name
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



@_header_token_check("POST")
def group_create(request):
    _needs = ["name", "api_id", "versions_id"]
    #, "place_league", "no_place_pk_key"
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    # try:
    if ApiGroup.objects.filter(name=_da["name"], gid=gid, uid=uid):
        return ErrorResponse(message="分组已存在!", error_code=40001)
    data = {
        "gid": gid,
        "uid": uid,
        "name": _da["name"],
        "api_data_id": _da["api_id"],
        "versions_id": _da["versions_id"],
    }
    _add = ApiGroup.objects.create(**data)
    log = "创建新的分组：%s" % _add.name
    log_data = {
        "gid": gid,
        "uid": uid,
        "level": 1,
        "message": log,
        "type": "API",
        "plant_code": plant_code,
    }
    creat_log(log_data)
    # except Exception as e:
    #     return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()



@_header_token_check("GET")
def group_list(request):
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    api_id = request.GET.get("api_id", None)
    versions_id = request.GET.get("versions_id", None)
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
            "api_data_id": api_id,
            "versions_id": versions_id
        }
        objs_all = ApiGroup.objects.filter(**filter_obj).order_by("-created_at")
        objs = objs_all[(_page - 1) * _page_size: (_page * _page_size)]
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data["list"] = objs
    data["total"] = objs_all.count()
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)


@_header_token_check("PUT")
def group_update(request):
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _needs = ["id", "name"]    # , "place_league", "no_place_pk_key"
    _wuis = request.wuis
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    id = _da["id"]
    del _da["id"]
    try:
        _obj = ApiGroup.objects.filter(id=id, gid=gid, uid=uid)
        _obj.update(**_da)
        log = "修改分组：%s," % _obj.first().name
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
        return ErrorResponse(message="修改失败!")
    return SuccessResponse(data=_da)

@_header_token_check("DELETE")
def group_delete(request):
    _id=request.GET.get("id")
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _not_ok = ["id"]
    if not _id:
        return ErrorResponse(message="id必传！", error_code=40003, extra_data={"format": ("id")})

    try:
        _id_list = _id.split(",")
        objs = ApiGroup.objects.filter(gid=gid, uid=uid, id__in=_id_list)
        if not objs:
            return ErrorResponse(message="未获取到！", error_code=40001)
        obj = objs.first()
        objs.delete()
        log = "删除分组：%s," % obj.name
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




@_header_token_check("POST")
def versions_create(request):
    _needs = ["name", "api_id", "versions"]
    #, "place_league", "no_place_pk_key"
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    # try:
    if UrlVersions.objects.filter(name=_da["name"], gid=gid, api_data_id=_da["api_id"], uid=uid):
        return ErrorResponse(message="版本名称已存在!", error_code=40001)
    if UrlVersions.objects.filter(versions=_da["versions"], gid=gid, api_data_id=_da["api_id"], uid=uid):
        return ErrorResponse(message="版本号已存在!", error_code=40001)
    data = {
        "gid": gid,
        "uid": uid,
        "name": _da["name"],
        "versions": _da["versions"],
        "api_data_id": _da["api_id"],
    }
    _add = UrlVersions.objects.create(**data)
    log = "创建新的分组：%s" % _add.name
    log_data = {
        "gid": gid,
        "uid": uid,
        "level": 1,
        "message": log,
        "type": "API",
        "plant_code": plant_code,
    }
    creat_log(log_data)
    # except Exception as e:
    #     return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()



@_header_token_check("GET")
def versions_list(request):
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    api_id = request.GET.get("api_id", None)
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
            "api_data_id": api_id
        }
        objs_all = UrlVersions.objects.filter(**filter_obj).order_by("-created_at")
        objs = objs_all[(_page - 1) * _page_size: (_page * _page_size)]
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data["list"] = objs
    data["total"] = objs_all.count()
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)


@_header_token_check("PUT")
def versions_update(request):
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _needs = ["id", "name"]    # , "place_league", "no_place_pk_key"
    _wuis = request.wuis
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    id = _da["id"]
    del _da["id"]
    try:
        _obj = UrlVersions.objects.filter(id=id, gid=gid, uid=uid)
        _obj.update(**_da)
        log = "修改版本：%s," % _obj.first().name
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
        return ErrorResponse(message="修改失败!")
    return SuccessResponse(data=_da)

@_header_token_check("DELETE")
def versions_delete(request):
    _id=request.GET.get("id")
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _not_ok = ["id"]
    if not _id:
        return ErrorResponse(message="id必传！", error_code=40003, extra_data={"format": ("id")})

    try:
        objs = UrlVersions.objects.filter(gid=gid, uid=uid, id=_id)
        if not objs:
            return ErrorResponse(message="未获取到！", error_code=40001)
        obj = objs.first()
        objs.delete()
        log = "删除分组：%s," % obj.name
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


@_header_token_check("POST")
def url_create(request):
    _needs = ["name", "api_id", "url", "remark", "headers", "query", "body", "versions_id", "response"]
    #, "place_league", "no_place_pk_key"
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    try:
        if ApiUrl.objects.filter(name=_da["name"], api_data_id=_da["api_id"], gid=gid, uid=uid):
            return ErrorResponse(message="url已存在!", error_code=40001)
        _da["api_data_id"] = _da["api_id"]
        del _da["api_id"]
        _add = ApiUrl(**_da, gid=gid, uid=uid)
        _add.save()
        log = "创建新的url：%s" % _add.name
        log_data = {
            "gid": gid,
            "uid": uid,
            "level": 1,
            "message": log,
            "type": "API",
            "plant_code": plant_code,
        }
        creat_log(log_data)
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    return SuccessResponse()



@_header_token_check("GET")
def url_list(request):
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    api_id = request.GET.get("api_id", None)
    group_id = request.GET.get("group_id", None)
    versions_id = request.GET.get("versions_id", None)
    gid = request.gid
    uid = request.uid
    data={}
    _not_ok = []
    if not _page or not _page_size:
        return ErrorResponse(message="page,page_size必传！", error_code=40003, extra_data={"format": ("page,page_size")})
    if not api_id:
        return ErrorResponse(message="api_id必传！", error_code=40003, extra_data={"format": ("api_id")})
    if not versions_id:
        return ErrorResponse(message="versions_id必传！", error_code=40003, extra_data={"format": ("versions_id")})
    _page = int(_page)
    _page_size = int(_page_size)
    try:
        filter_obj = {
            "api_data_id": api_id,
            "versions_id": versions_id,
            "gid": gid,
            "uid": uid
        }
        if group_id:
            filter_obj["group_id"] = group_id
        objs_all = ApiUrl.objects.filter(**filter_obj).order_by("-created_at")
        objs = objs_all[(_page - 1) * _page_size: (_page * _page_size)]
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    data["list"] = objs
    data["total"] = objs_all.count()
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)


@_header_token_check("PUT")
def url_update(request):
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _needs = ["id", "name", "url", "remark", "headers", "query", "body", "versions", "response"]
    _wuis = request.wuis
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    id = _da["id"]
    del _da["id"]
    try:
        _obj = ApiUrl.objects.filter(id=id, gid=gid, uid=uid)
        _obj.update(**_da)
        log = "修改分组：%s," % _obj.first().name
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
        return ErrorResponse(message="修改失败!")
    return SuccessResponse(data=_da)

@_header_token_check("DELETE")
def url_delete(request):
    _id=request.GET.get("id")
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _not_ok = ["id"]
    if not _id:
        return ErrorResponse(message="id必传！", error_code=40003, extra_data={"format": ("id")})

    try:
        _id_list = _id.split(",")
        objs = ApiUrl.objects.filter(gid=gid, uid=uid, id__in=_id_list)
        if not objs:
            return ErrorResponse(message="未获取到！", error_code=40001)
        obj = objs.first()
        log = "删除分组：%s," % obj.name
        objs.delete()
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
def api_all_list(request):

    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    type = request.GET.get("type", None)
    search_word = request.GET.get("search_word", None)
    sort_type = request.GET.get("sort_type", None)
    collect = request.GET.get("collect", None)
    if sort_type is None:
        sort_type = "-updated_at"
    data={}
    _not_ok = []
    if not _page or not _page_size:
        return ErrorResponse(message="page,page_size必传！", error_code=40003, extra_data={"format": ("page,page_size")})
    _page = int(_page)
    _page_size = int(_page_size)
    try:
        filter_obj = {
            "status__gte": 0,
            "visible": 1
        }

        if collect in [1, '1']:
            api_data_id_list = list(Collect.objects.filter(gid=request.gid, uid=request.uid).values_list("api_data_id", flat=True))
            print(api_data_id_list)
            # filter_obj["api_data_id"] = api_data_id_list
            filter_obj["id__in"] = api_data_id_list
        if type:
            filter_obj["type"] = type
        search_filter = Q()

        if search_word:
            search_filter = Q(name__icontains=search_word) | Q(remark__icontains=search_word) | Q(details__icontains=search_word)
        objs_all = ApiData.objects.filter(search_filter, **filter_obj).order_by(sort_type)
        objs = objs_all[(_page - 1) * _page_size: (_page * _page_size)]
        # print(objs_all)
        _info = serializers.ApiDataAllSerializers(objs, many=True,context={'request': request}).data
        # print(_info)
    except Exception as e:
        return ErrorResponse(message="失败!%s" % str(e), error_code=40011, extra_data={"format": (str(e))})
    test = rcon100.get("api:categories:env")
    # print(test)
    if isinstance(test, bytes):
        test = test.decode("utf-8")
    try:
        test = json.loads(test)
    except Exception as e:
        print("json decode error:", e)
        test = []

    # print(test)
    data["categories"] = test[0:8]
    data["list"] = _info
    data["total"] = objs_all.count()
    data["page"] = _page
    data["page_size"] = _page_size

    return SuccessResponse(data=data)


@_header_token_check("PUT")
def update_collect(request):

    gid = request.gid
    uid = request.uid
    #看gid解析
    # print(f"gid: {gid}")
    # print(f"uid: {uid}")
    _needs = ["id", "type"]
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    if _da["type"] == "cancel":
        Collect.objects.filter(api_data_id=_da["id"], gid=gid, uid=uid).delete()
    elif _da["type"] in "collect":
        if Collect.objects.filter(api_data_id=_da["id"], gid=gid, uid=uid).exists():
            return ErrorResponse("该API已被收藏！")
        Collect.objects.create(api_data_id=_da["id"], gid=gid, uid=uid)
    return SuccessResponse()


@_header_token_check("POST")
def create_subscribe(request):
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _needs = ["id", "vip_type"]
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    api_objs = ApiData.objects.filter(id=_da["id"], status__gte=0)
    if not api_objs:
        return ErrorResponse("该API已下架！")
    api_obj = api_objs[0]
    price_objs = api_obj.price_obj
    vip_type_obj = {}
    for price_obj in price_objs:
        if price_obj["type"] == _da["vip_type"]:
            vip_type_obj = price_obj
    if vip_type_obj["cost_type"] == "day":
        now = timezone.now() + timezone.timedelta(days=1)
    elif vip_type_obj["cost_type"] == "month":
        now = timezone.now() + timezone.timedelta(days=30)
    elif vip_type_obj["cost_type"] == "number":
        now = "2099-12-31 00:00:00"
    else:
        return ErrorResponse("时间类型错误！")
    APIC = vip_type_obj["APIC"]
    beans = autoApi.get_beans({"uid": uid})
    print(beans)
    if "APIC" not in beans:
        beans["APIC"]=0
    if APIC > beans["APIC"]:
        return ErrorResponse("账户余额不足！")
    if APIC >= 0:
        _json = {
            "uid": uid,
            "amount": -APIC,
            "type": "APIC",
            "plant_code": plant_code,
            "message": {
                "type_code": "expend",
                "type_lang": {
                    "zh": "消耗",
                    "en": "expend"
                },
                "log": "订阅API：%s" % api_obj.name
            }
        }
        _res_ok = autoApi.use_beans(_json)
        if not _res_ok:
            return ErrorResponse("订阅失败！")
    token = md5(str(vip_type_obj) + str(time.time()))
    SubscribeApi.objects.create(api_data_id=_da["id"], gid=gid, uid=uid, vip_type=vip_type_obj, expiration_time=now, token=token)
    return SuccessResponse(data=_da)



@_header_token_check("GET")
def subscribe_list(request):
    gid = request.gid
    uid = request.uid
    _page = request.GET.get("page", None)
    _page_size = request.GET.get("page_size", None)
    if not _page or not _page_size:
        return ErrorResponse(message="page,page_size必传！", error_code=40003, extra_data={"format": ("page,page_size")})
    subscribe_objs = SubscribeApi.objects.filter(gid=gid, uid=uid).order_by("-created_at")
    _page = int(_page)
    _page_size = int(_page_size)
    objs = subscribe_objs[(_page - 1) * _page_size: (_page * _page_size)]
    _info = serializers.SubscribeSerializers(objs, many=True).data
    data={}
    data["list"] = _info
    data["total"] = subscribe_objs.count()
    data["page"] = _page
    data["page_size"] = _page_size
    return SuccessResponse(data=data)


@_header_token_check("PUT")
def update_subscribe(request):
    gid = request.gid
    uid = request.uid
    _needs = ["id", "vip_type"]
    plant_code = request.plant_code
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误!", error_code=40002)
    _cn=_check_needs(_da, _needs)

    api_objs = ApiData.objects.filter(id=_da["id"], status__gte=0)
    if not api_objs:
        return ErrorResponse("该API已下架！")
    subscribe_objs = SubscribeApi.objects.filter(api_data_id=_da["id"], gid=gid, uid=uid)
    if not subscribe_objs:
        return ErrorResponse("未获取到该订阅信息！", error_code=40001)
    api_obj = api_objs[0]
    price_objs = api_obj.price_obj
    vip_type_obj = {}
    for price_obj in price_objs:
        if price_obj["type"] == _da["vip_type"]:
            vip_type_obj = price_obj
    if vip_type_obj["cost_type"] == "day":
        now = timezone.now() + timezone.timedelta(days=1)
    elif vip_type_obj["cost_type"] == "month":
        now = timezone.now() + timezone.timedelta(days=30)
    elif vip_type_obj["cost_type"] == "number":
        now = "2099-12-31 00:00:00"
    else:
        return ErrorResponse("时间类型错误！")
    APIC = vip_type_obj["APIC"]
    beans = autoApi.get_beans({"uid": uid})
    if "APIC" not in beans:
        return ErrorResponse("账户无余额！")
    if APIC > beans["APIC"]:
        return ErrorResponse("账户余额不足！")
    if APIC >= 0:
        _json = {
            "uid": uid,
            "amount": -APIC,
            "type": "APIC",
            "plant_code": plant_code,
            "message": {
                "type_code": "expend",
                "type_lang": {
                    "zh": "消耗",
                    "en": "expend"
                },
                "log": "订阅API：%s" % api_obj.name
            }
        }
        _res_ok = autoApi.use_beans(_json)
        if not _res_ok:
            return ErrorResponse("订阅失败！")
    subscribe_objs.update(vip_type=vip_type_obj, expiration_time=now)
    return SuccessResponse(data=_da)


@_header_token_check("DELETE")
def cancel_subscribe(request):
    _id=request.GET.get("id")
    gid = request.gid
    uid = request.uid
    plant_code = request.plant_code
    _not_ok = ["id"]
    if not _id:
        return ErrorResponse(message="id必传！", error_code=40003, extra_data={"format": ("id")})

    try:
        objs = SubscribeApi.objects.filter(gid=gid, uid=uid, id=_id)
        if not objs:
            return ErrorResponse(message="未获取到！", error_code=40001)
        obj = objs.first()
        log = "取消订阅：%s," % obj.id
        objs.delete()
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
def api_getcategory(request):
    _page = int(request.GET.get("page", 1))
    _page_size = int(request.GET.get("page_size", 8))
    test=rcon100.get("api:categories:env")

    if isinstance(test, bytes):
        test = test.decode("utf-8")
    try:
        test=json.loads(test)
    except Exception as e:
        print("json decode error:", e)
        test = []

    # print(test)
    start=(_page-1)*_page_size
    end=_page*_page_size
    data={}
    data["page"] = _page
    data["page_size"] = _page_size
    categorylist = test[start:end]
    data["total"]=len(test)
    data["list"] =categorylist
    str in categorylist
    # test = json.loads(data)
    # print(data)
    return SuccessResponse(data)

