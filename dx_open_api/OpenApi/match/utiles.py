import json
import asyncio
from OpenApi.settings import rcon45, rcon25, rcon85, rcon81, rcon55, rcon100, rcon99, rcon82
from sdk._new_api import NewAutoApi
autoApi = NewAutoApi()

def get_match_data(bc_type, event_type, sport_type, page, page_size):
    _this_list = {}
    if rcon25.exists(bc_type + "_" + event_type + "_" + sport_type) == 1:
        _this_league_ids = rcon25.hgetall(bc_type + "_" + event_type + "_" + sport_type)
        if "event_type".encode() in _this_league_ids:
            del _this_league_ids["event_type".encode()]
        if "update_time".encode() in _this_league_ids:
            del _this_league_ids["update_time".encode()]
        if "sport_type".encode() in _this_league_ids:
            del _this_league_ids["sport_type".encode()]

        _match_list = []
        _league_ids_options_obj = {}
        for _league_id, _value in _this_league_ids.items():
            _match_list += json.loads(_value.decode('utf-8'))
        _totle = len(_match_list)
        _match_list = sorted(_match_list, key=lambda x: (x['match_time_stamp'], x['home_id']))
        page = int(page)
        page_size = int(page_size)
        _this_list["page"] = page
        _this_list["page_size"] = page_size
        _match_list = _match_list[(page - 1) * page_size:page * page_size]
        for _match in _match_list:
            _match["ids"] = str(_match["league_id"]) + ":" + str(_match["home_id"]) + ":" + str(_match["away_id"])
        _this_list["match_list"] = get_pk_name_options(_match_list, bc_type)
        _this_list["totle"] = _totle
    return _this_list


def _make_order_leagues(request, _da):

    key = "auto_api:need:bookies"
    group_tasks = json.loads(rcon100.get(key))
    _platform_list = group_tasks["need_bookies_ch"]
    _platform_options = []
    for _platform in _platform_list:
        _platform_options.append(
            {
                "label": _platform["name"],
                "value": _platform["bc_type"]
            }
        )
    _gid = request.gid
    _this_op = []
    if "page" not in _da or "page_size" not in _da:
        _da["page"] = 1
        _da["page_size"] = 10

    _this_list = {
        "match_list": [],
        "page": _da["page"],
        "page_size": _da["page_size"],
        "total": 0
    }
    if "platform_from" in _da:
        _ch_platform_from=_da["platform_from"]
    else:
        _ch_platform_from="hga"

    _this_platform_from = {"platform_from": {
        "name": "选择平台",
        "type": "select",
        "options": _platform_options,
        "require": 1,
        "choiced": _ch_platform_from,
        "default": "hga"
    }}
    _this_op.append(_this_platform_from)


    if "select_type_from" in _da:
        _select_type_form = _da["select_type_from"]
    else:
        _select_type_form = "date_type"

    _this_select_type_from={"select_type_from":{
        "name":"筛选类型",
        "type": "select",
        "options":[
            {
                "label": "日期",
                "value": "date_type"
            },
            {
                "label": "时间",
                "value": "event_type"
            }
            ],
            "require": 1,
            "choiced": _select_type_form,
            "default":"date_type"
    }}
    _this_op.append(_this_select_type_from)

    if _select_type_form == "event_type":
        if "sport_type_from" in _da:
            _ch_sport_type_from=_da["sport_type_from"]
        else:
            _ch_sport_type_from="soccer"
        _this_sport_type_from = {"sport_type_from": {
            "name": "选择玩法",
            "type": "select",
            "options": [
                {
                    "label": "足球",
                    "value": "soccer"
                },
                {
                    "label": "篮球",
                    "value": "basketball"
                }
            ],
            "require": 1,
            "choiced": _ch_sport_type_from,
            "default": "soccer"
        }}
        _this_op.append(_this_sport_type_from)

        if "event_type_from" in _da:
            _ch_event_type_from=_da["event_type_from"]
        else:
            _ch_event_type_from="early"
        _this_event_type_from = {"event_type_from": {
            "name": "选择时间",
            "type": "select",
            "options": [
                {
                    "label": "早盘",
                    "value": "early"
                },
                {
                    "label": "今日盘",
                    "value": "today"
                },
                {
                    "label": "实时盘",
                    "value": "live"
                }
            ],
            "require": 1,
            "choiced": _ch_event_type_from,
            "default": "early"
        }}
        _this_op.append(_this_event_type_from)
        if _ch_event_type_from:
            if rcon25.exists(_ch_platform_from + "_" + _ch_event_type_from + "_" + _ch_sport_type_from) == 1:
                _this_league_ids = rcon25.hgetall(_ch_platform_from + "_" + _ch_event_type_from + "_" + _ch_sport_type_from)
                if "event_type".encode() in _this_league_ids:
                    del _this_league_ids["event_type".encode()]
                if "update_time".encode() in _this_league_ids:
                    del _this_league_ids["update_time".encode()]
                if "sport_type".encode() in _this_league_ids:
                    del _this_league_ids["sport_type".encode()]
                _this_league_ids = list(_this_league_ids.items())

                _league_ids_options = []
                _league_ids_options_obj = {}
                for _league_id, _value in _this_league_ids:
                    _minfo = json.loads(_value.decode("utf-8"))
                    _league_id = _league_id.decode("utf-8")

                    _label = _minfo[0]["league_name"]
                    if _label in _league_ids_options_obj:
                        if _league_id not in _league_ids_options_obj[_label]:
                            _league_ids_options_obj[_label]["ids"].append(_league_id)
                            _league_ids_options_obj[_label]["num"] = _league_ids_options_obj[_label]["num"] + len(
                                _minfo)
                    else:
                        _league_ids_options_obj[_label] = {"ids": [_league_id], "num": len(_minfo)}
                for _lb, _lb_v in _league_ids_options_obj.items():
                    _league_ids_options.append(
                        {
                            "label": _lb + "(" + str(_lb_v["num"]) + ")",
                            "value": json.dumps(_lb_v["ids"])
                        }
                    )

                if "league_from" in _da:
                    _ch_league_from = _da["league_from"]
                else:
                    _ch_league_from = "all"
                _league_ids_options = sorted(_league_ids_options, key=lambda x: x['label'])
                _league_ids_options.insert(0, {"label": "全部","value": "all"})
                _this_league_value_from = {"league_from": {
                    "name": "联赛信息",
                    "type": "select",
                    "options": _league_ids_options,
                    "require": 1,
                    "choiced": _ch_league_from,
                    "default": _league_ids_options[0]["value"]
                }}
                _this_op.append(_this_league_value_from)
                _match_list = []
                if _ch_league_from:
                    if _ch_league_from != "all":
                        for league_id in json.loads(_ch_league_from):
                            if rcon25.hexists(_ch_platform_from + "_" + _ch_event_type_from + "_" + _ch_sport_type_from, league_id) == 1:
                                _match = json.loads(rcon25.hget(_ch_platform_from + "_" + _ch_event_type_from + "_" + _ch_sport_type_from, league_id).decode("utf-8"))
                                _match_list += _match
                    else:
                        if rcon25.exists(_ch_platform_from + "_" + _ch_event_type_from + "_" + _ch_sport_type_from) == 1:
                            _match = rcon25.hgetall(_ch_platform_from + "_" + _ch_event_type_from + "_" + _ch_sport_type_from)
                            for league_id, league_value in _match.items():
                                if league_id.decode("utf-8") in ["update_time", "event_type", "sport_type"]:
                                    continue
                                _l = json.loads(league_value.decode("utf-8"))
                                _match_list += _l
                _totle = len(_match_list)
                # for i in _match_list:
                #     if not i["match_id"]:
                #         print(_match_list)
                # _match_list = sorted(_match_list, key=lambda x: x['match_time_stamp'])
                _match_list = sorted(_match_list, key=lambda x: (x['match_time_stamp'], x['home_id']))
                if "page" in _da and "page_size" in _da:
                    _page = int(_da["page"])
                    _page_size = int(_da["page_size"])
                    _this_list["page"]=_page
                    _this_list["page_size"]=_page_size
                    if _ch_league_from == "all":
                        _match_list = _match_list[(_page-1)*_page_size:_page*_page_size]
                for _match in _match_list:
                    _match["ids"] = str(_match["league_id"]) + ":" + str(_match["home_id"]) + ":" + str(_match["away_id"])
                _this_list["match_list"]= get_pk_name_options(_match_list, _ch_platform_from)
                _this_list["totle"]=_totle

    else:
        _this_dates = []
        if rcon85.exists(_ch_platform_from + ":date:minfo") == 1:
            _this_date_ids = list(json.loads(rcon85.get(_ch_platform_from + ":date:minfo")).items())
            for _date, ids in _this_date_ids:
                _year_month_day = _date.split(" ")[0]
                if _year_month_day not in _this_dates:
                    _this_dates.append(_year_month_day)
        _date_ids_options = []
        for _date in _this_dates:
            _date_ids_options.append(
                {
                    "label": _date,
                    "value": _date
                }
            )
        if "date_ids_from" in _da:
            _ch_date_ids_from = _da["date_ids_from"]
        else:
            _ch_date_ids_from = "all"
        _date_ids_options = sorted(_date_ids_options, key=lambda x: x['label'])
        _date_ids_options.insert(0, {"label": "全部", "value": "all"})
        _this_date_ids_from = {"date_ids_from": {
            "name": "选择日期",
            "type": "select",
            "options": _date_ids_options,
            "require": 1,
            "choiced": _ch_date_ids_from,
            "default": _date_ids_options[0]["value"]
        }}
        _this_op.append(_this_date_ids_from)

        if _ch_date_ids_from:

            _league_date_ids =  []
            if _ch_date_ids_from != "all":
                if rcon85.exists(_ch_platform_from + ":date:minfo") == 1:
                    _this_date_ids = list(json.loads(rcon85.get(_ch_platform_from + ":date:minfo")).items())
                    for _date, ids in _this_date_ids:
                        if _ch_date_ids_from in _date:
                            _league_date_ids.append({"date": _date, "ids": ids})
            else:
                if rcon85.exists(_ch_platform_from + ":date:minfo") == 1:
                    _this_date_ids = list(json.loads(rcon85.get(_ch_platform_from + ":date:minfo")).items())
                    for _date, ids in _this_date_ids:
                        _league_date_ids.append({"date": _date, "ids": ids})
            _league_date_ids = sorted(_league_date_ids, key=lambda x: x['date'])
            _league_ids = []
            for _d in _league_date_ids:
                _league_ids += _d["ids"]
            _totle = len(_league_ids)
            if "page" in _da and "page_size" in _da:
                _page = int(_da["page"])
                _page_size = int(_da["page_size"])
                if _ch_date_ids_from == "all":
                    _league_ids = _league_ids[(_page-1)*_page_size:_page*_page_size]
                _this_list["page"]=_page
                _this_list["page_size"]=_page_size
            _date_value_options = []

            for _id in _league_ids:
                if rcon81.exists(_ch_platform_from + ":" + _id) == 1:
                    _this_league_froms = rcon81.hgetall(_ch_platform_from + ":" + _id)
                    for _event_type, _value in _this_league_froms.items():
                        value = json.loads(_value.decode("utf-8"))["minfo"]
                    value["ids"] = str(value["league_id"]) + ":" + str(value["home_id"]) + ":" + str(value["away_id"])
                    _date_value_options.append(
                        value
                    )
            _this_list["match_list"]=get_pk_name_options(_date_value_options, _ch_platform_from)
            _this_list["totle"]=_totle

    _this_op = {
        "_this_op": _this_op,
        "_match_list": _this_list
    }

    return _this_op

def get_pk_name_options(_match_list, bc_type):
    _new_match_list = []
    for _match in _match_list:
        _match["bc_type"] = bc_type
        _match["strong"] = "away"

        odds_data_objs = get_odds_data_objs(_match)
        _match["main_odds_data"] = get_main_odds_data(odds_data_objs)
        _new_match_list.append(_match)
    return _new_match_list


def get_odds_data_objs(_match):
    odds_data_objs = {}
    for _od in _match["odds_data"]:
        if _od["hf_type"] not in odds_data_objs:
            odds_data_objs[_od["hf_type"]] = {}
        if _od["pk_type"] not in odds_data_objs[_od["hf_type"]]:
            odds_data_objs[_od["hf_type"]][_od["pk_type"]] = []
        if _od["pk_type"] == "R":
            if _od["pk_ratio"] < 0:
                _match["strong"] = "home"
        _pk_key = str(_od["hf_type"]) + ":" + str(_od["pk_type"]) + ":" + '{:g}'.format(_od["pk_ratio"])
        _od["pk_key"] = _pk_key
        _pk_name = _make_odd_name_by_kinfo(_od)
        _od["pk_name"] = _pk_name
        _this_order = 0
        _new_odds_all = []
        _odds_name_pres = []
        _i = 0
        _pk_type = _od["pk_type"]
        _pk_ratio = _od["pk_ratio"]
        _pk_name_options = []
        for _do_odds in _od["odds"]:
            _new_odds = {"odd": _do_odds["odd"],
                         "nav_data": _do_odds["nav_data"]
                         }
            _odds_name_pre = ""
            if _od["pk_type"] == "M":
                if _this_order == 0:
                    _odds_name_pre = "主胜"
                if _this_order == 1:
                    _odds_name_pre = "客胜"
                if _this_order == 2:
                    _odds_name_pre = "平局"
            if _od["pk_type"] == "OU":
                if _this_order == 0:
                    _odds_name_pre = "大"
                if _this_order == 1:
                    _odds_name_pre = "小"
            if _od["pk_type"] == "R":
                if _this_order == 0:
                    _odds_name_pre = "主队"
                if _this_order == 1:
                    _odds_name_pre = "客队"
            _odds_name_pres.append(_odds_name_pre)
            _now_pk_ratio = _pk_ratio
            if _pk_type == "R":
                if _i == 0:
                    _pk_key = str(_od["hf_type"]) + ":" + str(_od["pk_type"]) + ":" + '{:g}'.format(_od["pk_ratio"])
                    pk_odds_name = str(_pk_ratio)
                else:
                    _pk_key = str(_od["hf_type"]) + ":" + str(_od["pk_type"]) + ":" + '{:g}'.format(-_od["pk_ratio"])
                    pk_odds_name = str(-_pk_ratio)
                    _now_pk_ratio = -_pk_ratio
            elif _pk_type in ["OU", "OUC", "OUH"]:
                if _i == 0:
                    pk_odds_name = "大" + str(_pk_ratio)
                else:
                    pk_odds_name = "小" + str(_pk_ratio)
            else:
                if _i == 0:
                    pk_odds_name = "主胜"
                elif _i == 1:
                    pk_odds_name = "客胜"
                else:
                    pk_odds_name = "平局"
            _new_odds["odds_name"] = pk_odds_name
            _new_odds["pk_ratio"] = _now_pk_ratio

            _new_odds["pk_odds_key"] = _pk_key + ":" + str(_this_order)
            _new_odds_all.append(_new_odds)
            _this_pk_name_op = {
                "label": _make_odd_name(_pk_key + ":" + str(_this_order)) + "@" + str(_do_odds["odd"]),
                "pk_odds_key": _pk_key + ":" + str(_this_order),
                "value": _pk_key + ":" + str(_this_order),
                "index": _i,
                "list": _new_odds
            }
            _pk_name_options.append(_this_pk_name_op)
            _this_order = _this_order + 1
            _i += 1
            # _do_odds["odds_name"]=_odds_name_pre+"@"+str(_do_odds["odd"])

        _od["odds"] = []
        _od["odds"] = _new_odds_all
        _od["pk_name_options"] = _pk_name_options
        if "id" in _od:
            del _od["id"]
        odds_data_objs[_od["hf_type"]][_od["pk_type"]].append(_od)
    return odds_data_objs



def get_main_odds_data(odds_data_objs, type="main"):
    main_odds_data = []
    bookies_main_pk_struc_all = json.loads(rcon100.get("bookies:main:pk_struc").decode("utf-8"))
    bookies_main_pk_all = json.loads(rcon100.get("bookies:main:pk").decode("utf-8"))
    for _pk_key, bookies_main_pk_s in bookies_main_pk_struc_all.items():
        bookies_main_pk_struc = bookies_main_pk_s.copy()
        _hf_type, _pk_type = _pk_key.split(":")
        bookies_main_pk_struc["status"] = 0
        if _hf_type in odds_data_objs:
            if _pk_type in odds_data_objs[_hf_type]:
                odds_data_list = odds_data_objs[_hf_type][_pk_type]
                bookies_main_pk = bookies_main_pk_all[_hf_type][_pk_type]
                _index = bookies_main_pk["index"]
                odds_data = odds_data_list[_index]
                bookies_main_pk_struc["pk_ratio"] = odds_data["pk_ratio"]
                _i = 0
                if odds_data["odds"]:
                    new_odds = []
                    bookies_main_pk_struc_status_list = []
                    for _odds in bookies_main_pk_struc["odds"]:
                        _pk_ratio = odds_data["pk_ratio"]
                        if _pk_type == "R":
                            if _i == 0:
                                pk_odds_name = str(_pk_ratio)
                            else:
                                pk_odds_name = str(-_pk_ratio)
                                _pk_ratio = -_pk_ratio
                        elif _pk_type == "OU":
                            if _i == 0:
                                pk_odds_name = "大" + str(_pk_ratio)
                            else:
                                pk_odds_name = "小" + str(_pk_ratio)
                        else:
                            pk_odds_name = _odds["pk_odds_name"]
                        if odds_data["odds"][_i]["odd"]:
                            if type == "ce":
                                pk_odds_key = "C:" + _pk_key + ":" + '{:g}'.format(_pk_ratio) + ":" + str(_i)
                            elif type == "pc":
                                pk_odds_key = "F:" + _pk_key + ":" + '{:g}'.format(_pk_ratio) + ":" + str(_i)
                            else:
                                pk_odds_key = _pk_key + ":" + '{:g}'.format(_pk_ratio) + ":" + str(_i)
                            new_odds.append({
                                "nav_data": odds_data["odds"][_i]["nav_data"],
                                "odd": odds_data["odds"][_i]["odd"],
                                "pk_odds_name": pk_odds_name,
                                "pk_ratio": _pk_ratio,
                                "pk_odds_key": pk_odds_key
                            })
                            bookies_main_pk_struc_status_list.append(1)
                        else:
                            new_odds.append(_odds)
                            bookies_main_pk_struc_status_list.append(0)
                        _i += 1
                    bookies_main_pk_struc["odds"] = new_odds
                    if 0 in bookies_main_pk_struc_status_list:
                        bookies_main_pk_struc["status"] = 0
                    else:
                        bookies_main_pk_struc["status"] = 1
        main_odds_data.append(bookies_main_pk_struc)
    return main_odds_data


def _make_odd_name_by_kinfo(_pkinfo):
    _new_info={}
    _new_info["market_type"] = ""
    if "market_type" in _pkinfo:
        if _pkinfo["market_type"] == "corner":
            _new_info["market_type"] = "角球:"
        elif _pkinfo["market_type"] == "pcard":
            _new_info["market_type"] = "罚牌:"
        elif _pkinfo["market_type"] == "pd":
            _new_info["market_type"] = "波胆:"
        elif _pkinfo["market_type"] == "goal":
            _new_info["market_type"] = "总进球:"

    if _pkinfo["hf_type"]=="full":
        _new_info["hf_type"]="全场"
    else:
        _new_info["hf_type"]="半场"

    _new_info["pk_type"]=_pkinfo["pk_type"]

    if _pkinfo["pk_type"]=="M":
        _new_info["pk_type"]="1X2"
    if _pkinfo["pk_type"]=="R":
        _new_info["pk_type"]="让球"
    if _pkinfo["pk_type"]=="OU":
        _new_info["pk_type"]="大小"

    _new_info["pk_ratio"]='{:g}'.format(_pkinfo["pk_ratio"])
    if _new_info["pk_ratio"] !=0:
        _name=str(_new_info["hf_type"])+":"+ _new_info["market_type"] + str(_new_info["pk_type"])+":"+str(_new_info["pk_ratio"])
    else:
        _name=str(_new_info["hf_type"])+":"+ _new_info["market_type"] + str(_new_info["pk_type"])
    return _name




def _make_odd_name(_pk_odds_key):
    _pkinfo = {}
    _new_info={}
    _pk_odds_key_list = _pk_odds_key.split(":")
    if "C" == _pk_odds_key_list[0]:
        _pk_odds_key = _pk_odds_key.replace("C:", "")
        _new_info["market_type"] = "角球:"
    elif "F" == _pk_odds_key_list[0]:
        _pk_odds_key = _pk_odds_key.replace("F:", "")
        _new_info["market_type"] = "罚牌:"
    elif "B" == _pk_odds_key_list[0]:
        _pk_odds_key = _pk_odds_key.replace("B:", "")
        _new_info["market_type"] = "波胆:"
    elif "G" == _pk_odds_key_list[0]:
        _pk_odds_key = _pk_odds_key.replace("G:", "")
        _new_info["market_type"] = "总进球:"
    else:
        _new_info["market_type"] = ""


    _new_info["pk_ratio"] = _pk_odds_key.split(":")[2]
    if _pk_odds_key.split(":")[0] == "full":
        _new_info["hf_type"] = "全场:"
    else:
        _new_info["hf_type"] = "半场:"

    # _new_info["pk_type"] =  _pk_odds_key.split(":")[1]

    if  _pk_odds_key.split(":")[1] == "M":
        _new_info["pk_type"] = "1X2"
    if  _pk_odds_key.split(":")[1] == "R":
        _new_info["pk_type"] = "让球"
    if  _pk_odds_key.split(":")[1] == "OU":
        _new_info["pk_type"] = "大小"
    _this_order=int(_pk_odds_key.split(":")[-1])
    _odds_pk_type=_pk_odds_key.split(":")[1]
    _odds_name_pre = ""
    if _odds_pk_type == "M": # 需要全半场：(角球)
        if _this_order == 0:
            _odds_name_pre = "主胜"
        if _this_order == 1:
            _odds_name_pre = "客胜"
        if _this_order == 2:
            _odds_name_pre = "平局"
    if _odds_pk_type == "OU":  # 需要全半场：(角球)
        if _this_order == 0:
            _odds_name_pre = "大" + _new_info["pk_ratio"]
        if _this_order == 1:
            _odds_name_pre = "小" + _new_info["pk_ratio"]
    if _odds_pk_type == "R":  # 需要全半场:(角球):主客队
        if _this_order == 0:
            _odds_name_pre = "主队:" + _new_info["pk_ratio"]
        if _this_order == 1:
            _odds_name_pre = "客队:" + _new_info["pk_ratio"]

    _name = _new_info["hf_type"] + _new_info["market_type"] + _odds_name_pre
    return _name



def _make_odds_detail(res, bc_type, event_type):
    main_odds_objs = {}
    if rcon25.exists(bc_type + ":" + event_type + ":main:odds") == 1:
        main_odds_objs = json.loads(rcon25.get(bc_type + ":" + event_type + ":main:odds").decode("utf-8"))
        pass
    ids = res["league_id"] + ":" + res["home_id"] + ":" + res["away_id"]
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
    return res