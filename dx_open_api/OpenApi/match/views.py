import json, datetime, time, demjson3, asyncio
from sdk.jwt import _header_token_check,_method_check,SuccessResponse,ErrorResponse, md5, _check_needs
from sdk.public_method import get_reverse_pk_odds_key, get_now_pk_odd_key
from match.utiles import _make_order_leagues, _make_odd_name, get_odds_data_objs, get_main_odds_data, get_match_data
from OpenApi.settings import rcon25, rcon100, rcon45, rcon30, rcon82, rcon99
from member.models import MemberUser
from sdk._auto_api import AutoApi

autoApi = AutoApi()

# @_header_token_check(["GET"])
# def match_data(request, bc_type, sport_type, event_type):
#     page = request.GET.get("page", None)
#     page_size = request.GET.get("page_size", None)
#     all_match_data = get_match_data(bc_type, sport_type, event_type, page, page_size)
#     return SuccessResponse(data=all_match_data)

@_header_token_check(["POST"])
def match_select(request):
    try:
        _da = json.loads(request.body)
    except:
        return ErrorResponse(message="参数错误！", error_code=40002)
    _mot = _make_order_leagues(request, _da)
    _list = []
    for _mo in _mot["_this_op"]:
        for _mo_k, _mo_v in _mo.items():
            _mo_v["type"] = _mo_k
            if _mo_v not in _list:
                _list.append(_mo_v)

    if _mot:
        return SuccessResponse(data={"options": _list, "match_data": _mot["_match_list"]})
    else:
        return ErrorResponse(message="获取失败!", error_code=40001)



@_header_token_check("POST")
def other_platform_odd_list(request):
    _needs=["bc_type","sport_type","event_type","league_id","home_id","away_id","pk_odds_key"]
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误！", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    if _da["event_type"] == "today":
        _da["event_type"] = "early"
    sport_type = _da["sport_type"]
    bc_type = _da["bc_type"].replace("ag_", "")
    if "hga" in bc_type:
        bc_type = "hga"
    ids = str(_da["league_id"]) + ":" + str(_da["home_id"]) + ":" + str(_da["away_id"])
    roles = request.roles
    pk_ratio = _da["pk_odds_key"].split(":")[-2]
    if "all_bookies" in roles:
        if sport_type != "soccer":
            _key = sport_type + ":" + bc_type + ":mate:check:" + _da["event_type"]
        else:
            _key = bc_type + ":mate:check:" + _da["event_type"]
        if rcon45.exists(_key) == 1:
            _match = json.loads(rcon45.get(_key).decode("utf-8"))
            if ids in _match:
                if "leisu" in _match[ids]:
                    leisu_ids = _match[ids]["leisu"]
                    if rcon45.hexists("leisu:" + _da["event_type"] + ":odds_combins:key", leisu_ids) == 1:
                        leisu_match = json.loads(rcon45.hget("leisu:" + _da["event_type"] + ":odds_combins:key", leisu_ids).decode("utf-8"))
                        # if leisu_ids in leisu_match:
                        if _da["pk_odds_key"] in leisu_match:
                            _match_odd_data = leisu_match[_da["pk_odds_key"]]
                            pk_odds_key_ch = _make_odd_name(_da["pk_odds_key"])
                            reverse_match_odd_data = []
                            reverse_pk_odds_key = get_reverse_pk_odds_key(_da["pk_odds_key"])
                            if reverse_pk_odds_key:
                                reverse_match_odd_data = leisu_match[reverse_pk_odds_key]
                            all_bc_type_list = []
                            for odd_data in _match_odd_data:
                                all_bc_type_list.append(odd_data["bc_type"])
                                league_id, home_id, away_id = odd_data["ids"].split(":")
                                odd_data["league_id"] = league_id
                                odd_data["home_id"] = home_id
                                odd_data["away_id"] = away_id
                                odd_data["pk_odds_key_ch"] = pk_odds_key_ch
                                odd_data["pk_odds_key"] = _da["pk_odds_key"]
                                odd_data["pk_ratio"] = pk_ratio
                                # odd_data["select_team"] = get_select_team(_da["pk_odds_key"])
                                odd_data["reverse_pk_odds_key_ch"] = ""
                                odd_data["reverse_pk_odds_key"] = ""
                                odd_data["reverse_nav_data"] = ""
                                if reverse_match_odd_data:
                                    for reverse_odd_data in reverse_match_odd_data:
                                        if odd_data["bc_type"] == reverse_odd_data["bc_type"]:
                                            odd_data["reverse_pk_odds_key_ch"] = _make_odd_name(reverse_pk_odds_key)
                                            odd_data["reverse_pk_odds_key"] = reverse_pk_odds_key
                                            odd_data["reverse_nav_data"] = reverse_odd_data["nav_data"]

                            if bc_type not in all_bc_type_list and bc_type != 'leisu':
                                odd_d = {
                                    "bc_type": bc_type,
                                    "odd": _da["odd"],
                                    "nav_data": _da["nav_data"],
                                    "ids": ids,
                                    "league_id": _da["league_id"],
                                    "home_id": _da["home_id"],
                                    "away_id": _da["away_id"],
                                    "pk_odds_key_ch": _make_odd_name(_da["pk_odds_key"]),
                                    "pk_odds_key": _da["pk_odds_key"],
                                    "pk_ratio": pk_ratio
                                    # "select_team": get_select_team(_da["pk_odds_key"])
                                }
                                if "reverse_pk_odds_key" in _da:
                                    odd_d["reverse_pk_odds_key"] = _da["reverse_pk_odds_key"]
                                if "reverse_pk_odds_key_ch" in _da:
                                    odd_d["reverse_pk_odds_key_ch"] = _da["reverse_pk_odds_key_ch"]
                                if "reverse_nav_data" in _da:
                                    odd_d["reverse_nav_data"] = _da["reverse_nav_data"]
                                _match_odd_data.append(odd_d)
                            return SuccessResponse(data=_match_odd_data, message="获取成功")

        if rcon45.exists(sport_type + ":" + bc_type + ":" + _da["event_type"] + ":ids:odds") == 1:
            _all_league = json.loads(rcon45.get(sport_type + ":" + bc_type + ":" + _da["event_type"] + ":ids:odds").decode("utf-8"))
            if ids in _all_league:
                if _da["pk_odds_key"] in _all_league[ids]:
                    odds_data = _all_league[ids][_da["pk_odds_key"]]
                    reverse_pk_odds_key_ch = ""
                    reverse_nav_data = ""
                    reverse_pk_odds_key = get_reverse_pk_odds_key(_da["pk_odds_key"])
                    if reverse_pk_odds_key in _all_league[ids]:
                        reverse_odds_data = _all_league[ids][reverse_pk_odds_key]
                        reverse_pk_odds_key_ch = _make_odd_name(reverse_pk_odds_key)
                        reverse_pk_odds_key = reverse_pk_odds_key
                        reverse_nav_data = reverse_odds_data["nav_data"]
                    data = [{
                        "bc_type": bc_type,
                        "odd": odds_data["odd"],
                        "nav_data": odds_data["nav_data"],
                        "ids": ids,
                        "league_id": _da["league_id"],
                        "home_id": _da["home_id"],
                        "away_id": _da["away_id"],
                        "pk_odds_key_ch": _make_odd_name(_da["pk_odds_key"]),
                        "pk_odds_key": _da["pk_odds_key"],
                        "pk_ratio": pk_ratio,
                        # "select_team": get_select_team(_da["pk_odds_key"]),
                        "reverse_pk_odds_key_ch": reverse_pk_odds_key_ch,
                        "reverse_pk_odds_key": reverse_pk_odds_key,
                        "reverse_nav_data": reverse_nav_data
                    }]
                    return SuccessResponse(data=data, message="获取成功")
    _not_ok = []
    if "nav_data" not in _da:
        _not_ok.append("nav_data")
    if "odd" not in _da:
        _not_ok.append("odd")
    if len(_not_ok) !=0:
        return ErrorResponse(message="缺少参数:%s"%(",".join(_not_ok)), error_code=40003, extra_data={"format": (",".join(_not_ok))})

    odd_d = {
        "bc_type": bc_type,
        "odd": _da["odd"],
        "nav_data": _da["nav_data"],
        "ids": ids,
        "league_id": _da["league_id"],
        "home_id": _da["home_id"],
        "away_id": _da["away_id"],
        "pk_odds_key_ch": _make_odd_name(_da["pk_odds_key"]),
        "pk_odds_key": _da["pk_odds_key"],
        "pk_ratio": pk_ratio,
        # "select_team": get_select_team(_da["pk_odds_key"])
    }
    if "reverse_pk_odds_key" in _da:
        odd_d["reverse_pk_odds_key"] = _da["reverse_pk_odds_key"]
    if "reverse_pk_odds_key_ch" in _da:
        odd_d["reverse_pk_odds_key_ch"] = _da["reverse_pk_odds_key_ch"]
    if "reverse_nav_data" in _da:
        odd_d["reverse_nav_data"] = _da["reverse_nav_data"]
    return SuccessResponse(data=[odd_d])



@_header_token_check("POST")
def member_limit(request):
    _needs=["nav_data", "user_type", "pk_odds_key"]
    gid = request.gid
    uid = request.uid
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误！", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)
    _jsons = []
    if _da["user_type"] == "member":
        if "member_id" not in _da:
            return ErrorResponse(message="缺少参数:%s"%("member_id"), error_code=40003, extra_data={"format": ("member_id")})
        try:
            if _da["member_id"] == "all":
                if "bc_type" not in _da:
                    return ErrorResponse(message="缺少参数:%s"%("bc_type"), error_code=40003, extra_data={"format": ("bc_type")})
                user_config_id = _da["user_config_id"]
                bc_type = _da["bc_type"]
                _member_obj = MemberUser.objects.get(gid=gid, uid=uid, status__gte=0)
                bc_type = _member_obj.bc_type
                _json = {
                       "bc_type": bc_type,
                       "domain": "",
                       "proxy": _member_obj.proxy_ip,
                       "username": _member_obj.user_name,
                       "password": _member_obj.pass_word,
                       "nav_data": _da["nav_data"]
                    }
                _jsons.append(_json)

            else:
                _member_obj = MemberUser.objects.prefetch_related('proxy_ip').get(gid=gid, uid=uid, id=_da["member_id"], status__gte=0)
                bc_type = _member_obj.bc_type
                _json = {
                       "bc_type": bc_type,
                       "domain": "",
                       "proxy": _member_obj.proxy_ip.ip,
                       "username": _member_obj.user_name,
                       "password": _member_obj.pass_word,
                       "nav_data": _da["nav_data"]
                    }
                _jsons.append(_json)
        except Exception as e:
            return ErrorResponse(message="失败!未找到对应账号", error_code=40004)
    else:
        _need_user = ["bc_type", "user_name", "pass_word"]
        _cn=_check_needs(_da, _need_user)
        if _cn["code"]==400:
            return ErrorResponse(**_cn)
        bc_type = _da["bc_type"]
        _json = {
               "bc_type": _da["bc_type"],
               "domain": "",
               "proxy": "",
               "username": _da["user_name"],
               "password": _da["pass_word"],
               "nav_data": _da["nav_data"]
            }
        _jsons.append(_json)
    _ret = ""
    try:
        if not _jsons:
            return SuccessResponse()
        for _json in _jsons:
            _ret = autoApi._place_odds(_json)
            print(_ret)
            if _ret:
                if _ret["max_stake"] == 0:
                    continue
                now_pk_odds_key = get_now_pk_odd_key(_ret)
                if now_pk_odds_key != _da["pk_odds_key"]:
                    return ErrorResponse(message="盘口匹配失败!%s平台，%s，%s" % (bc_type, _da["pk_odds_key"], now_pk_odds_key), error_code=40005, extra_data={"format": (bc_type, _da["pk_odds_key"], now_pk_odds_key)})

                _no_plus_1 = json.loads(rcon100.get("odds:plus"))["api"]
                new_odd = float(_ret["odd"])
                if bc_type not in _no_plus_1:
                    if _ret["pk_type"] != "M":
                        new_odd += 1
                data = {
                    "odd": round(new_odd, 3),
                    "min_stake": _ret["min_stake"],
                    "max_stake": _ret["max_stake"],
                }
                return SuccessResponse(data=data)
    except Exception as e:
        return ErrorResponse(message="失败!账号异常,请检查帐号!", error_code=40058)
    return ErrorResponse(message="失败!账号异常,请检查帐号!", error_code=40058)



@_header_token_check("POST")
def get_now_odds_all_details(request):
    gid = request.gid
    uid = request.uid
    _wuis = request.wuis
    _needs=["bc_type","sport_type","event_type","match_id", "ids"]
    try:
        _da=json.loads(request.body)
    except Exception as e:
        return ErrorResponse(message="参数错误！", error_code=40002)
    _cn=_check_needs(_da, _needs)
    if _cn["code"]==400:
        return ErrorResponse(**_cn)

    _jsons = []
    try:
        bc_type = _da["bc_type"]
        filter_obj = {
            "gid": gid,
            "uid": uid,
            "bc_type": bc_type,
            "status": 1
        }
        member_user_objs = MemberUser.objects.filter(**filter_obj)
        if member_user_objs:
            for _value in member_user_objs:
                try:
                    _da["proxy"] = _value.proxy_ip
                except Exception as e:
                    continue
                _da["user_name"] = _value.user_name
                _da["pass_word"] = _value.pass_word
                _jsons.append(_da)
    except Exception as e:
        print(e)
        return ErrorResponse(message="暂未分配账号权限，请联系上级管理员!", error_code=40007)
    error_msg = ""
    # print(_jsons)
    for _json in _jsons:
        res = autoApi._get_odds_all_details(_json)
        if res:
            if res["code"] == 1:
                main_odds_objs = {}
                if rcon25.exists(_da["bc_type"] + ":" + _da["event_type"] + ":main:odds") == 1:
                    main_odds_objs = json.loads(rcon25.get(_da["bc_type"] + ":" + _da["event_type"] + ":main:odds").decode("utf-8"))
                    pass
                ids = _da["ids"]
                new_odds_data_obj = {}
                ce_odds_data = {}
                pc_odds_data = {}
                if "odds_data" in res:
                    odds_data_objs = get_odds_data_objs(res)
                    if ids in main_odds_objs:
                        for _hf_type, _vaule in odds_data_objs.items():
                            for _pk_type, _odds_datas in _vaule.items():
                                for _odds_data in _odds_datas:
                                    if _odds_data["pk_key"] in main_odds_objs[ids]:
                                        continue
                                    if _odds_data["hf_type"] not in new_odds_data_obj:
                                        new_odds_data_obj[_odds_data["hf_type"]] = {}
                                    if _odds_data["pk_type"] not in new_odds_data_obj[_odds_data["hf_type"]]:
                                        new_odds_data_obj[_odds_data["hf_type"]][_odds_data["pk_type"]] = []
                                    new_odds_data_obj[_odds_data["hf_type"]][_odds_data["pk_type"]].append(_odds_data)
                    else:
                        new_odds_data_obj = odds_data_objs
                if "ce_odds_data" in res:

                    for _ce_od in res["ce_odds_data"]:
                        _ce_od = autoApi._odds_format(_ce_od)
                        if _ce_od["hf_type"] not in ce_odds_data:
                            ce_odds_data[_ce_od["hf_type"]] = {}
                        if _ce_od["pk_type"] not in ce_odds_data[_ce_od["hf_type"]]:
                            ce_odds_data[_ce_od["hf_type"]][_ce_od["pk_type"]] = []
                        for _pk_name_option in _ce_od["pk_name_options"]:
                            _label = _pk_name_option["label"]
                            _odd = _pk_name_option["list"]["odd"]
                            _pk_name_option["label"] = _label + "@" + str(_odd)
                        ce_odds_data[_ce_od["hf_type"]][_ce_od["pk_type"]].append(_ce_od)
                if "pc_odds_data" in res:

                    for _pc_od in res["pc_odds_data"]:
                        _pc_od = autoApi._odds_format(_pc_od)
                        if _pc_od["hf_type"] not in pc_odds_data:
                            pc_odds_data[_pc_od["hf_type"]] = {}
                        if _pc_od["pk_type"] not in pc_odds_data[_pc_od["hf_type"]]:
                            pc_odds_data[_pc_od["hf_type"]][_pc_od["pk_type"]] = []
                        for _pk_name_option in _pc_od["pk_name_options"]:
                            _label = _pk_name_option["label"]
                            _odd = _pk_name_option["list"]["odd"]
                            _pk_name_option["label"] = _label + "@" + str(_odd)
                        pc_odds_data[_pc_od["hf_type"]][_pc_od["pk_type"]].append(_pc_od)
                res["data"] = {}
                res["data"]["odds_data"] = new_odds_data_obj
                res["data"]["ce_odds_data"] = get_main_odds_data(ce_odds_data, type="ce")
                res["data"]["pc_odds_data"] = get_main_odds_data(pc_odds_data, type="pc")
                return SuccessResponse(data=res["data"])
        else:
            error_msg = res["msg"]
        print(res)
    return ErrorResponse(message=error_msg, error_code=40008)


