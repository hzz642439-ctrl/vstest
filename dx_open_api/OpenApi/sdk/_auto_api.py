import requests, redis, platform
import json
import os, sys, datetime, threading, difflib, hashlib, time, asyncio, random

sys.path.append("../../")  # 后台调用脚本必须加
sys.path.append("../")  # 后台调用脚本必须加
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OpenApi.settings")

django.setup()
from OpenApi.settings import rcon30, rcon25, rcon45, rcon82, rcon100
from OpenApi import Test


def md5(_code):
    md = hashlib.md5(_code.encode())
    _sign = md.hexdigest()  # 单纯的MD5加密
    return _sign


class AutoApi(object):
    def __init__(self):
        tas = "存放定制数据的基础信息和相关配置信息"
        # self.auto_api={
        #     "username" : "qilin_cms",
        #     "password" : "Qwe123!",
        #     "plant" : "auto_api"
        # }
        self.auto_api = {
            "user_name": "api_fz_tome",
            "pass_word": "123456",
            "plant_code": "data_api_100",
            "mac": "123456",
        }
        self.autoapibaseurl = "http://192.168.1.100:9001"
        self.ucbaseurl = "http://192.168.1.100:8808"
        self.uc_oms_url = "http://192.168.1.100:8808"

        print("当前系统使用的底层域名:", self.autoapibaseurl)

    def _init_response(self):
        # 请求request_session
        self.request_session = requests.Session()
        self.request_session.headers.update({
            "Accept": "Accept: application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Content-Length": "0",
            "Content-Type": "application/json",
        })
        self.request_session.verify = False
        self.request_session.keep_alive = False
        self.request_session.DEFAULT_RETRIES = 0

    def _init_auto_response(self):
        # 请求request_session
        self.request_session = requests.Session()
        self.request_session.headers.update({
            "Accept": "Accept: application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Authorization": "TOKEN " + self._auto_token,
            "PLANTCODE": self.auto_api["plant_code"],
            "MAC": self.auto_api["mac"],
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Content-Length": "0",
            "Content-Type": "application/json",
        })
        self.request_session.verify = False
        self.request_session.keep_alive = False
        self.request_session.DEFAULT_RETRIES = 0

    def _get_domain(self, bc_type, proxy_ip):
        _keys = bc_type + ":ok:ips:*"
        _all_key = rcon25.keys(_keys)
        _this_domain = ""
        if bc_type == "hga":
            _all_domain = json.loads(rcon100.get("domain:hga"))
            _this_domain = random.choice(_all_domain)
        else:
            for _ak in _all_key:
                _this_proxy = json.loads(rcon25.get(_ak))
                if len(_this_proxy) != 0:
                    if proxy_ip in _this_proxy:
                        _all_domain = _this_proxy[proxy_ip]
                        if len(_all_domain) == 0:
                            _this_domain = ""
                        else:
                            _have_ok = 0
                            for _ad in _all_domain:
                                if _have_ok == 0:
                                    _this_json = {
                                        "bc_type": bc_type,
                                        "ua_type": "phone",
                                        "proxy": proxy_ip,
                                        "domain": _ad
                                    }
                                    _url = self.autoapibaseurl + "/api/bocai/test_domain/"
                                    try:
                                        _res = self.request_session.get(_url, params=_this_json, timeout=3)
                                        _res_ok = json.loads(_res.content)
                                        if "success" in _res_ok:
                                            _have_ok = 1
                                            _this_domain = _ad
                                    except Exception as e:
                                        dd = 1
        return _this_domain

    def _get_token(self):
        self._init_response()
        _url = self.ucbaseurl + "/api/uc/login"
        _json = self.auto_api
        _res = self.request_session.post(_url, json=_json)
        # return

        _res_ok = json.loads(_res.content)
        # print("登录",_res_ok)
        if _res_ok["code"] == 200:
            rcon30.set(self.auto_api["user_name"] + ":token", _res_ok["data"]["accessToken"])
            return _res_ok
        else:
            return False

    def _login_uc(self):
        self._init_response()
        _url = self.ucbaseurl + "/api/uc/login"
        _res = self.request_session.post(_url, json=self.auto_api)
        _res_ok = json.loads(_res.content)
        if _res_ok["code"] == 200:
            # print(_res_ok)
            rcon30.set(self.auto_api["user_name"] + ":token", _res_ok["data"]["accessToken"])
            return _res_ok["data"]["accessToken"]
        else:
            return False

    def _check_uc(self, _json):
        self._init_response()
        _url = self.ucbaseurl + "/api/uc/user_check"
        _json = {
            "token": str(_json["token"]),
            "plant": _json["plant"]
        }
        _res = self.request_session.post(_url, json=_json)
        _res_ok = json.loads(_res.content)
        if _res_ok["code"] == 401:
            return self._login_uc()
        elif _res_ok["code"] == 200:
            return _res_ok
        else:
            return False

    def _check_token(self, _token):
        self._init_response()
        _url = self.ucbaseurl + "/api/uc/user_check"
        _json = {
            "token": str(_token),
            "plant_code": self.auto_api["plant_code"],
            "mac": self.auto_api["mac"]
        }
        _res = self.request_session.post(_url, json=_json)
        _res_ok = json.loads(_res.content)
        if _res_ok["code"] == 401:
            self._get_token()
        elif _res_ok["code"] == 200:
            return _token
        else:
            return False

    def _odds_format(self, _od):
        _pk_ratio = '{:g}'.format(_od["pk_ratio"])
        _pk_key = str(_od["hf_type"]) + ":" + str(_od["pk_type"]) + ":" + str(_pk_ratio)
        _od["pk_key"] = _pk_key
        _pk_name = self._make_odd_name(_od)
        _od["pk_name"] = _pk_name
        _this_order = 0
        _new_odds_all = []
        _odds_name_pres = []
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
                    _odds_name_pre = "上盘"
                if _this_order == 1:
                    _odds_name_pre = "下盘"
            _odds_name_pres.append(_odds_name_pre)
            _new_odds["odds_name"] = _odds_name_pre + "@" + str(_do_odds["odd"])
            _new_odds_all.append(_new_odds)
            _this_order = _this_order + 1
            # _do_odds["odds_name"]=_odds_name_pre+"@"+str(_do_odds["odd"])

        _od["odds"] = []
        _od["odds"] = _new_odds_all
        _pk_name = self._make_odd_name(_od)
        _pk_name_options = []
        _idx = 0
        for _onp in _odds_name_pres:
            _this_op = {"label": _pk_name + ":" + _onp, "pk_odds_key": _pk_key + ":" + str(_idx),
                        "value": _pk_key + ":" + str(_idx), "index": _idx, "list": _new_odds_all[_idx]}
            _pk_name_options.append(_this_op)
            _idx = _idx + 1
        _od["pk_name_options"] = _pk_name_options
        if "id" in _od:
            del _od["id"]
        return _od

    def _get_odds_details(self, _config_json):
        # 底层4.3接口
        # _bc_type=_config_json["bc_type"]
        _btime = time.time()
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/data_bocai/event_detail/"
            _json = {
                "bc_type": _config_json["bc_type"],
                "event_type": _config_json["event_type"],
                "ua_type": "phone",
                "sport_type": "soccer",
                "match_id": _config_json["match_id"],
                "league_data": {}
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    odds_data = _res_ok["data"]["odds_data"]
                    for _od in odds_data:
                        _od = self._odds_format(_od)
                    return odds_data
                else:
                    # print(_res_ok["detail"])
                    return False
            except Exception as e:
                print("0000", e, _config_json)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False

    def _get_odds_all_details(self, _config_json):
        # 底层4.3接口
        # _bc_type=_config_json["bc_type"]
        _btime = time.time()
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/event_detail/"
            _json = {
                "bc_type": _config_json["bc_type"],
                "ua_type": "phone",
                "event_type": _config_json["event_type"],
                "sport_type": _config_json["sport_type"],
                "username": _config_json["user_name"],
                "password": _config_json["pass_word"],
                "proxy": _config_json["proxy"],
                "match_id": _config_json["match_id"],
                "league_data": {}
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    odds_data = []
                    ce_odds_data = []
                    pc_odds_data = []
                    pd_odds_data = []
                    go_odds_data = []
                    if "odds_data" in _res_ok["data"]:
                        odds_data = _res_ok["data"]["odds_data"]
                    if "ce_odds_data" in _res_ok["data"]:
                        ce_odds_data = _res_ok["data"]["ce_odds_data"]
                    if "pc_odds_data" in _res_ok["data"]:
                        pc_odds_data = _res_ok["data"]["pc_odds_data"]
                    if "pd_odds_data" in _res_ok["data"]:
                        pd_odds_data = _res_ok["data"]["pd_odds_data"]
                    if "go_odds_data" in _res_ok["data"]:
                        go_odds_data = _res_ok["data"]["go_odds_data"]

                    return {"code": 1, "mgs": "返回正常", "odds_data": odds_data, "ce_odds_data": ce_odds_data,
                            "pc_odds_data": pc_odds_data, "pd_odds_data": pd_odds_data, "go_odds_data": go_odds_data}
                else:
                    return {"code": 0, "msg": _res_ok["detail"]}
            except Exception as e:
                return {"code": 0, "msg": "未知错误:%s" % (e)}
        else:
            return {"code": 0, "msg": "错误:%s" % ("缺少底层接口权限，无法对接底层!")}

    def _get_member_orderlist(self, _user_info):
        _btime = time.time()
        _bc_type = _user_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_order_list/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _user_info["username"],
                "password": _user_info["password"],
                "domain": "",
                "proxy": _user_info["proxy_ip"],
                "status": _user_info["status"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    # print(_res_ok)
                    return _res_ok["data"]
                else:
                    # print(_res_ok)
                    return False
            except Exception as e:
                print("0000", e, _user_info)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False

    async def _get_user_orderlist(self, _user_info):
        _btime = time.time()
        _bc_type = _user_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_order_list/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _user_info["user_name"],
                "password": _user_info["pass_word"],
                "domain": "",
                "proxy": _user_info["ip"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                # print(_res_ok)
                _mlist = []
                if "success" in _res_ok:
                    if _res_ok["code"] == 0:
                        _mlist = _res_ok["data"]
                else:
                    print("异步获取订单失败")
                _etime = time.time()
                print("合计", "user:orders:" + _bc_type + ":" + _user_info["user_name"], len(_mlist), "个实时订单!",
                      "耗时", _etime - _btime)
                rcon30.set("user:orders:" + _bc_type + ":" + _user_info["user_name"], json.dumps(_mlist))
            except Exception as e:
                print("0000", e, _user_info)
        else:
            print("缺少底层接口权限，无法对接底层!")

    def _get_member_balance(self, mb_json):

        _bc_type = mb_json["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_balance/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": mb_json["username"],
                "password": mb_json["password"],
                "domain": "",
                "proxy": mb_json["proxy"]
            }
            # if _bc_type=="kaiyun":
            #     _json["domain"]="https://www.igmh0w.vip:9509"
            try:
                _res = self.request_session.post(_url, json=_json)
                # print(_res.content)
                _res_ok = json.loads(_res.content)
                # print(_res_ok)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    # print(_json)
                    print(_res_ok["detail"], _json["username"], _bc_type)
                    return False
            except Exception as e:
                print("0000", e, mb_json)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return 0

    def _get_agent_balance(self, _agent_info):
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/ag_bocai/user_balance/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _agent_info["username"],
                "password": _agent_info["password"],
                "domain": "",
                "proxy": _agent_info["proxy"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    print(_res_ok["detail"])
                    return False
            except Exception as e:
                print("0000", e, _agent_info)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            # return False
            return 0

    def _test_bc_ips(self, _json_info):
        _bc_type = _json_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/test_domain/"
            _json = {
                "bc_type": _json_info["bc_type"],
                "ua_type": "phone",
                "domain": "",
                "proxy": _json_info["proxy"]
            }
            try:
                _res = self.request_session.get(_url, params=_json, timeout=3)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    # print(_res_ok["detail"])
                    return False
            except Exception as e:
                # print("0000",e,_json_info)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            # return False
            return 0

    def _get_agent_fast_orders(self, _agent_info, _uid, _gid):
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            _member_list = _agent_info["member_list"]
            # if len(_member_list) !=0:
            asyncio.run(self._get_agent_fast_memberlist_orders(_agent_info, _member_list, _bc_type, _uid, _gid))
        else:
            print("缺少底层接口权限，无法对接底层!")

    def _get_agent_orders(self, _agent_info, _uid, _gid):
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            _member_list = _agent_info["member_list"]
            # if len(_member_list) !=0:
            # 获取当前比赛的基础信息

            _early_minfo = json.loads(rcon45.get(_bc_type.replace("ag_", "") + ":early:ids:names"))
            _live_minfo = json.loads(rcon45.get(_bc_type.replace("ag_", "") + ":live:ids:names"))
            _mate_all = json.loads(rcon45.get(_bc_type.replace("ag_", "") + ":mate:check"))
            _all_have_order_keys = {}
            if rcon30.exists("agent:orders:" + _bc_type + ":" + _agent_info["user_name"] + ":key") == 1:
                _all_have_order_keys = json.loads(
                    rcon30.get("agent:orders:" + _bc_type + ":" + _agent_info["user_name"] + ":key"))
            # _all_have_order_keys={}
            asyncio.run(
                self._get_agent_memberlist_orders(_agent_info, _member_list, _bc_type, _early_minfo, _live_minfo,
                                                  _mate_all, _all_have_order_keys))
        else:
            print("缺少底层接口权限，无法对接底层!")

    def _get_agent_members(self, _agent_info, _uid, _gid):
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            _member_list = _agent_info["member_list"]
            asyncio.run(self._get_agent_memberlist(_agent_info, _bc_type))
        else:
            print("缺少底层接口权限，无法对接底层!")

    async def _get_agent_memberlist(self, _agent_info, _bc_type):
        _btime = time.time()
        self._init_auto_response()
        _url = self.autoapibaseurl + "/api/ag_bocai/member_list/"
        _json = {
            "bc_type": _bc_type,
            "ua_type": "phone",
            "username": _agent_info["user_name"],
            "password": _agent_info["pass_word"],
            "domain": "",
            "proxy": _agent_info["ip"]
        }
        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            _mlist = []
            if "code" in _res_ok:
                if _res_ok["code"] == 0:
                    _mlist = _res_ok["data"]
                else:
                    print(_res_ok)
            else:
                print(_res_ok, _agent_info)
            _etime = time.time()
            print("agent:members:" + _bc_type + ":" + _agent_info["user_name"], "合计", len(_mlist), "个下级!", "耗时",
                  _etime - _btime)
            rcon30.set("agent:members:" + _bc_type + ":" + _agent_info["user_name"], json.dumps(_mlist))
        except Exception as e:
            print("1111", _agent_info, _res_ok)

    async def _get_agent_all_orders(self, _agent_info, _bc_type):
        # 这个方法没有用2024-3-19
        _btime = time.time()
        self._init_auto_response()
        _url = self.autoapibaseurl + "/api/ag_bocai/order_list/"
        _json = {
            "bc_type": _bc_type,
            "ua_type": "phone",
            "username": _agent_info["user_name"],
            "password": _agent_info["pass_word"],
            "domain": "",
            "proxy": _agent_info["ip"]
        }

        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            _ok_orders = []
            if _res_ok["code"] == 0:
                for _order_user in _res_ok["data"]:
                    _ok_orders = _res_ok["data"]
            else:
                print("请求代理用户列表订单信息出错!")
            _etime = time.time()
            print("agent:orders_all:" + _bc_type + ":" + _agent_info["user_name"], "合计", len(_ok_orders),
                  "个实时订单!", "耗时", _etime - _btime)
            rcon30.set("agent:orders_all:" + _bc_type + ":" + _agent_info["user_name"], json.dumps(_ok_orders))
        except Exception as e:
            print("2222", _agent_info, e, _res_ok["data"])

    async def _get_agent_fast_memberlist_orders(self, _agent_info, _member_list, _bc_type, _uid, _gid):
        _btime = time.time()
        self._init_auto_response()
        _url = self.autoapibaseurl + "/api/ag_bocai/member_trade_detail/"
        _json = {
            "bc_type": _bc_type,
            "ua_type": "phone",
            "username": _agent_info["user_name"],
            "password": _agent_info["pass_word"],
            "member_list": _member_list,
            "domain": "",
            "proxy": _agent_info["ip"]
        }

        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            _ok_orders = []
            if _res_ok["code"] == 0:
                for _order_user in _res_ok["data"]:
                    for _olist in _order_user["order_list"]:
                        _this_order = {"member": _order_user["member"], "bc_type": _bc_type,
                                       "agent_account": _agent_info["user_name"], "order_info": _olist}
                        _ok_orders.append(_this_order)

            else:
                print("请求代理用户列表订单信息出错!")
            _etime = time.time()
            print("agent:orders:fast:" + _bc_type + ":" + _agent_info["user_name"], "合计", len(_ok_orders),
                  "个实时订单!", "耗时", _etime - _btime)
            rcon30.set("agent:orders:fast:" + _bc_type + ":" + _agent_info["user_name"], json.dumps(_ok_orders))
        except Exception as e:
            print("3333", _agent_info, e)

    async def _get_agent_memberlist_orders(self, _agent_info, _member_list, _bc_type, _early_minfo, _live_minfo,
                                           _mate_all, _all_have_order_keys):
        _btime = time.time()
        self._init_auto_response()
        _url = self.autoapibaseurl + "/api/ag_bocai/member_trade_detail/"
        _json = {
            "bc_type": _bc_type,
            "ua_type": "phone",
            "username": _agent_info["user_name"],
            "password": _agent_info["pass_word"],
            "member_list": _member_list,
            "domain": "",
            "proxy": _agent_info["ip"]
        }
        # try:
        _res = self.request_session.post(_url, json=_json)
        _res_ok = json.loads(_res.content)
        _ok_orders = []
        if "code" in _res_ok:
            if _res_ok["code"] == 0:
                for _order_user in _res_ok["data"]:
                    for _olist in _order_user["order_list"]:
                        _this_order = {"member": _order_user["member"], "bc_type": _bc_type,
                                       "agent_account": _agent_info["user_name"], "order_info": _olist}
                        _this_order_key = md5(str(_this_order))
                        _name_key = _this_order["order_info"]["league_name"] + ":" + _this_order["order_info"][
                            "home_name"] + ":" + _this_order["order_info"]["away_name"]
                        _ids_key = "0"
                        _mate_keys = []
                        event_type = ""
                        if _name_key in _early_minfo:
                            _ids_key = _early_minfo[_name_key]
                            event_type = "early"
                        if _name_key in _live_minfo:
                            _ids_key = _live_minfo[_name_key]
                            event_type = "live"
                        if _ids_key != "0" and _ids_key in _mate_all:
                            _mate_keys = _mate_all[_ids_key]
                        _minfo = {
                            "score": "0:0",
                            "red_card": "0:0",
                            "corner": "0:0",
                            "yellow_card": "0:0",
                        }
                        if rcon82.exists(_bc_type + ":" + str(_ids_key)) == 1:
                            _minfo_obj = json.loads(rcon82.get(_bc_type + ":" + str(_ids_key)))["minfo"]
                            _minfo["score"] = _minfo_obj["score"]
                            _minfo["red_card"] = _minfo_obj["red_card"]
                            _minfo["corner"] = _minfo_obj["corner"]
                            _minfo["yellow_card"] = _minfo_obj["yellow_card"]
                        _this_order["mate_keys"] = _mate_keys
                        _this_order["event_type"] = event_type
                        _this_order["ids_key"] = _ids_key
                        # if _order_user["member"] =="BTAA55F005":
                        #     print(_ids_key,_name_key,_mate_keys,_ids_key in _mate_all)
                        if _this_order_key in _all_have_order_keys:
                            _all_have_order_keys[_this_order_key]["mate_keys"] = _mate_keys
                            _all_have_order_keys[_this_order_key]["ids_key"] = _ids_key
                            # if _order_user["member"] =="BTAA55F005":
                            #     print(_ids_key,_mate_keys,_all_have_order_keys[_this_order_key])
                            _ok_orders.append(_all_have_order_keys[_this_order_key])
                        else:
                            _this_order["minfo"] = _minfo
                            _this_order["get_time"] = time.time()
                            _ok_orders.append(_this_order)
                            _all_have_order_keys[_this_order_key] = _this_order

            else:
                print("请求代理用户列表订单信息出错!")
        else:
            print(_res_ok)
        _etime = time.time()
        print("agent:orders:" + _bc_type + ":" + _agent_info["user_name"], "合计", len(_ok_orders), "个实时订单!",
              "耗时", _etime - _btime)
        rcon30.set("agent:orders:" + _bc_type + ":" + _agent_info["user_name"], json.dumps(_ok_orders))
        rcon30.set("agent:orders:" + _bc_type + ":" + _agent_info["user_name"] + ":key",
                   json.dumps(_all_have_order_keys))
        # except Exception as e:
        #     print("3333",_agent_info,e)

    def _place_order(self, _json):

        _json["ua_type"] = "phone"
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token

            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/odd_order/"

            _this_order_keys = []
            for _e_k, _e_v in _json["nav_data"].items():
                _this_order_key = _e_k + "=" + str(_e_v)
                _this_order_keys.append(_this_order_key)
            _this_order_key = "::".join(_this_order_keys)
            _this_user_orders_key = _json["bc_type"] + ":" + _json["username"] + ":orders"
            _this_user_orders = {}
            if _json["check_repeat"] == True:
                if rcon30.exists(_this_user_orders_key) == 1:
                    _this_user_orders = json.loads(rcon30.get(_this_user_orders_key))
            if _this_order_key not in _this_user_orders:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "code" in _res_ok:
                    if _res_ok["code"] == 0:
                        print(_json["username"], "下单成功!", _json["nav_data"])
                        _this_user_orders[_this_order_key] = _res_ok["data"]
                        rcon30.set(_this_user_orders_key, json.dumps(_this_user_orders))
                        return _res_ok
                else:
                    print(_res_ok)
                    return False
                if "555" in str(_res_ok):
                    print(_json["username"], _res_ok["detail"])
                    return False

            else:
                print("当前用户已经存在这个订单!")
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False

    def _place_odds(self, _json_from):
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()
        _json = {
            "bc_type": _json_from["bc_type"],
            "ua_type": "phone",
            "domain": "",
            "proxy": _json_from["proxy"],
            "username": _json_from["username"],
            "password": _json_from["password"],
            "nav_data": _json_from["nav_data"]
        }
        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/odd_detail/"
            _res = self.request_session.post(_url, json=_json)
            if _res.status_code == 200:
                _res_ok = json.loads(_res.content)
                return _res_ok["data"]
            else:
                _res_ok = json.loads(_res.content)
                print(_res_ok)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False

    def _make_odd_name(self, _pkinfo):
        _new_info = {}
        if _pkinfo["hf_type"] == "full":
            _new_info["hf_type"] = "全场"
        else:
            _new_info["hf_type"] = "半场"

        _new_info["pk_type"] = _pkinfo["pk_type"]

        if _pkinfo["pk_type"] == "M":
            _new_info["pk_type"] = "1X2"
        if _pkinfo["pk_type"] == "R":
            _new_info["pk_type"] = "让球"
        if _pkinfo["pk_type"] == "OU":
            _new_info["pk_type"] = "大小"

        _new_info["pk_ratio"] = _pkinfo["pk_ratio"]
        if _new_info["pk_ratio"] != 0:
            _pk_ratio = '{:g}'.format(_new_info["pk_ratio"])
            _name = str(_new_info["hf_type"]) + ":" + str(_new_info["pk_type"]) + ":" + str(_pk_ratio)
        else:
            _name = str(_new_info["hf_type"]) + ":" + str(_new_info["pk_type"])
        return _name

    def _get_minfo(self, _json):
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _json["ua_type"] = "phone"
            _url = self.autoapibaseurl + "/api/data_bocai/event_data/"
            _res = self.request_session.post(_url, json=_json)
            print(_res.content, 2222)
            if _res.status_code == 200:
                _res_ok = json.loads(_res.content)
                _new_data = []
                for _d in _res_ok["data"]:
                    _d["bc_type"] = _json["bc_type"]
                    for _od in _d["odds_data"]:
                        _pk_ratio = '{:g}'.format(_od["pk_ratio"])
                        _pk_key = str(_od["hf_type"]) + ":" + str(_od["pk_type"]) + ":" + str(_pk_ratio)
                        _od["pk_key"] = _pk_key
                        _pk_name = self._make_odd_name(_od)
                        _od["pk_name"] = _pk_name
                        _this_order = 0
                        _new_odds_all = []
                        _odds_name_pres = []
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
                                    _odds_name_pre = "上盘"
                                if _this_order == 1:
                                    _odds_name_pre = "下盘"
                            _odds_name_pres.append(_odds_name_pre)
                            _new_odds["odds_name"] = _odds_name_pre + "@" + str(_do_odds["odd"])
                            _new_odds_all.append(_new_odds)
                            _this_order = _this_order + 1
                            # _do_odds["odds_name"]=_odds_name_pre+"@"+str(_do_odds["odd"])

                        _od["odds"] = []
                        _od["odds"] = _new_odds_all
                        _pk_name = self._make_odd_name(_od)
                        _pk_name_options = []
                        _idx = 0
                        for _onp in _odds_name_pres:
                            _this_op = {"label": _pk_name + ":" + _onp, "pk_odds_key": _pk_key + ":" + str(_idx),
                                        "value": _pk_key + ":" + str(_idx), "index": _idx, "list": _new_odds_all[_idx]}
                            _pk_name_options.append(_this_op)
                            _idx = _idx + 1
                        _od["pk_name_options"] = _pk_name_options
                        if "id" in _od:
                            del _od["id"]
                    _new_data.append(_d)

                return _new_data
            else:

                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False

    def _agent_login(self, _agent_info):
        # 代理登录和心跳数据
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/ag_bocai/user_login/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _agent_info["username"],
                "password": _agent_info["password"],
                "domain": "",
                "proxy": _agent_info["proxy"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    return False
            except Exception as e:
                print("0000", e, _agent_info)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return 0


    def _user_login(self, _agent_info):
        # 代理登录和心跳数据
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()
        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_login/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _agent_info["username"],
                "password": _agent_info["password"],
                "domain": "",
                "proxy": _agent_info["proxy"]
            }
            try:
                print(_json)
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                print(_res_ok)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    return False
            except Exception as e:
                print("0000", e, _agent_info)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return 0

    def _user_logout(self, _agent_info):
        # 代理登录和心跳数据
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()
        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_logout/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _agent_info["username"],
                "password": _agent_info["password"],
                "domain": "",
                "proxy": _agent_info["proxy"]
            }
            try:
                print(_json)
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                print(_res_ok)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    return False
            except Exception as e:
                print("0000", e, _agent_info)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return 0

    def _user_check(self, _json):
        self._init_response()
        # self.ucbaseurl = "http://127.0.0.1:8808"
        _url = self.uc_oms_url + "/api/uc/user_check"
        # _json = {
        #     "token": str(_json["token"]),
        #     "plant_code": _json["plant_code"],
        #     "mac":_json["mac"]
        # }
        _res = self.request_session.post(_url, json=_json)
        _res_ok = json.loads(_res.content)
        return _res_ok

    def _get_member_beats(self, _agent_info):
        # 用户心跳数据
        _bc_type = _agent_info["bc_type"]
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_profile/"
            _json = {
                "bc_type": _bc_type,
                "ua_type": "phone",
                "username": _agent_info["username"],
                "password": _agent_info["password"],
                "domain": "",
                "proxy": _agent_info["proxy"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok and "text" not in str(_res_ok):
                    return _res_ok["data"]
                else:
                    return -1
            except Exception as e:
                print("0000", e, _agent_info)
                return -2
        else:
            print("缺少底层接口权限，无法对接底层!")
            # return False
            return 0



    def _user_init(self, _json):
        # 代理登录和心跳数据
        _bc_type = _json["bc_type"]
        _json["ua_type"] = "phone"
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            # print(_old_token)
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _json["domain"] = ""
            _url = self.autoapibaseurl + "/api/bocai/user_init/"
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return _res_ok["data"]
                else:
                    return False
            except Exception as e:
                print("0000", e, _json)
                return False
        else:
            print("缺少底层接口权限，无法对接底层!")
            return 0

    def get_beans(self, _json):
        # 代理登录和心跳数据
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
        self._init_auto_response()
        _url = self.uc_oms_url + "/api/uc/api_get_beans"
        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            print(_res_ok)
            if "success" in _res_ok:
                return _res_ok["data"]
            else:
                return False
        except Exception as e:
            print("0000", e, _json)
            return False


    def use_beans (self, _json):
        # 代理登录和心跳数据
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
        self._init_auto_response()
        _url = self.uc_oms_url + "/api/uc/api_use_beans"
        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            if "success" in _res_ok:
                return True
            else:
                return False
        except Exception as e:
            print("0000", e, _json)
            return False

    def api_buy_ips(self, _json):
        # 代理登录和心跳数据
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
        self._init_auto_response()
        _url = self.uc_oms_url + "/api/uc/api_buy_ips"
        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            print(_res_ok)
            if "success" in _res_ok:
                return _res_ok["data"]
            else:
                return False
        except Exception as e:
            print("0000", e, _json)
            return False


    def api_get_ips(self, _json):
        # 代理登录和心跳数据
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
        self._init_auto_response()
        _url = self.uc_oms_url + "/api/uc/api_get_ips"
        try:
            _res = self.request_session.post(_url, json=_json)
            _res_ok = json.loads(_res.content)
            print(_res_ok)
            if "success" in _res_ok:
                return _res_ok["data"]
            else:
                return False
        except Exception as e:
            print("0000", e, _json)
            return False

if __name__ == '__main__':
    api = AutoApi()
    # _json = {
    #     "uid": 3787,
    #     "amount": -5000,
    #     "type": "ZMED",
    #     "plant_code": "auto_bet_99",
    #     "message": {
    #         "type_code":"expend",
    #         "type_lang":{
    #             "zh":"消耗",
    #             "en":"expend"
    #         },
    #         "log": "SP 流水：谢菲尔德 VS 拜仁慕尼黑",
    #         "place_odds": 1.61,
    #         "pk_odds_key": "full:OU:2.5:0",
    #         "place_stake": 5000,
    #         "pk_odds_key_ch": "全场:大:2.5"
    #     }
    # }
    a = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzE4NTI2OTQsImlhdCI6MTc0MDMxNjY5NCwiZGF0YSI6eyJ1c2VybmFtZSI6ImFwaV9mel90b21lIiwiX3N1Yl9wbGFudCI6IiJ9fQ.uvvNPw8GlG0YvQbFu1GxhvB9FTxEBs4HWWmPKHo_-vA"
    # print(api._get_token())
    # print(api._login_uc())
    _json = {
        "uid": 8000277,
        "amount": -0,
        "type": "APIC",
        "plant_code": "plant_code",
        "message": {
            "type_code": "expend",
            "type_lang": {
                "zh": "消耗",
                "en": "expend"
            },
            "log": "订阅API：111"
        }
    }
    print(api.use_beans(_json))
    # _json = {
    #       "region": "hk",
    #       "number": 1
    #     }
    # api.api_get_ips(_json)