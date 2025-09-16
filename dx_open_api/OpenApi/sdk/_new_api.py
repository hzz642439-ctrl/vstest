import requests, redis, platform
import json
import os, sys, datetime, threading, difflib, hashlib, time, asyncio, random

sys.path.append("../../")  # 后台调用脚本必须加
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nodeserver.settings")
from sdk._auto_api import AutoApi
from OpenApi.settings import rcon30, rcon25, rcon82, rcon100


def md5(_code):
    md = hashlib.md5(_code.encode())
    _sign = md.hexdigest()  # 单纯的MD5加密
    return _sign


class NewAutoApi(AutoApi):

    def get_order_photo(self, _json):
        _json["ua_type"] = "phone"
        bc_type = _json['bc_type']
        proxy = _json['proxy']
        _json["domain"] = ""
        _token_key = self.auto_api["user_name"] + ":token"
        if rcon30.exists(_token_key) == 1:
            _old_token = str(rcon30.get(_token_key), "utf-8")
            _this_token = self._check_token(_old_token)
        else:
            _this_token = self._get_token()

        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/user_order_detail/"
            _res = self.request_session.post(_url, json=_json)
            return _res
        return False


    def user_init(self, _json):
        # 修改初始密码
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
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _json)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"


    def user_set_password(self, _json):
        # 修改密码
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
            _url = self.autoapibaseurl + "/api/bocai/user_set_password/"
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _json)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"


    def user_login(self, _user_info):
        # 登陆
        _bc_type = _user_info["bc_type"]
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
                "username": _user_info["username"],
                "password": _user_info["password"],
                "domain": "",
                "proxy": _user_info["proxy"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _user_info)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"

    def user_logout(self, _user_info):
        # 登出
        _bc_type = _user_info["bc_type"]
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
                "username": _user_info["username"],
                "password": _user_info["password"],
                "domain": "",
                "proxy": _user_info["proxy"]
            }
            try:
                print(_json)
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                print(_res_ok)
                if "success" in _res_ok:
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _user_info)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"

    def get_member_beats(self, _user_info):
        # 用户心跳数据
        _bc_type = _user_info["bc_type"]
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
                "username": _user_info["username"],
                "password": _user_info["password"],
                "domain": "",
                "proxy": _user_info["proxy"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok and "text" not in str(_res_ok):
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _user_info)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            # return False
            return False, "缺少底层接口权限，无法对接底层!"

    def get_member_balance(self, _user_info):
        # 用户余额数据
        _bc_type = _user_info["bc_type"]
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
                "username": _user_info["username"],
                "password": _user_info["password"],
                "domain": "",
                "proxy": _user_info["proxy"]
            }
            # if _bc_type=="kaiyun":
            #     _json["domain"]="https://www.igmh0w.vip:9509"
            try:
                _res = self.request_session.post(_url, json=_json)
                # print(_res.content)
                _res_ok = json.loads(_res.content)
                # print(_res_ok)
                if "success" in _res_ok:
                    return True, _res_ok["data"]
                else:
                    # print(_json)
                    print(_res_ok["detail"], _json["username"], _bc_type)
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _user_info)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"


    def get_member_orderlist(self, _user_info):
        # 会员订单列表
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
                    return True, _res_ok["data"]
                else:
                    # print(_res_ok)
                    return False, str(_res_ok)
            except Exception as e:
                print("0000", e, _user_info)
                return False, e
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"


    def place_odds(self, _json_from):
        # 获取实时赔率
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
        # print(json.dumps(_json))
        if _this_token:
            self._auto_token = _this_token
            self._init_auto_response()
            _url = self.autoapibaseurl + "/api/bocai/odd_detail/"
            _res = self.request_session.post(_url, json=_json)
            # print(_res.content.decode("utf-8"))
            _res_ok = json.loads(_res.content)
            if _res.status_code == 200:
                return True, _res_ok["data"]
            else:
                return False, str(_res_ok)
        else:
            print("缺少底层接口权限，无法对接底层!")
            return False, "缺少底层接口权限，无法对接底层!"





    def place_order(self, _json):
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
            _json["domain"] = ""
            _this_user_orders = {}
            if _json["check_repeat"] == True:
                if rcon30.exists(_this_user_orders_key) == 1:
                    _this_user_orders = json.loads(rcon30.get(_this_user_orders_key))
            if _this_order_key not in _this_user_orders:
                # print(json.dumps(_json))
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "code" in _res_ok:
                    if _res_ok["code"] == 0:
                        print(_json["username"], "下单成功!", _json["nav_data"])
                        _this_user_orders[_this_order_key] = _res_ok["data"]
                        rcon30.set(_this_user_orders_key, json.dumps(_this_user_orders))
                        return True, _res_ok
                else:
                        return False, str(_res_ok)
                if "555" in str(_res_ok):
                    return False, str(_res_ok)
            else:
                return False, "当前用户已经存在这个订单"
        else:
            return False, "缺少底层接口权限，无法对接底层!"



    def get_league_data(self, _config_json):
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
            _url = self.autoapibaseurl + "/api/bocai/league_data/"
            _json = {
                "bc_type": _config_json["bc_type"],
                "ua_type": "phone",
                "event_type": _config_json["event_type"],
                "sport_type": _config_json["sport_type"],
                "username": _config_json["user_name"],
                "password": _config_json["pass_word"],
                "proxy": _config_json["proxy"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                return False, str(e)
        else:
            return False, "缺少底层接口权限，无法对接底层!"


    def get_event_data(self, _config_json):
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
            _url = self.autoapibaseurl + "/api/bocai/event_data/"
            _json = {
                "bc_type": _config_json["bc_type"],
                "ua_type": "phone",
                "event_type": _config_json["event_type"],
                "sport_type": _config_json["sport_type"],
                "username": _config_json["user_name"],
                "password": _config_json["pass_word"],
                "proxy": _config_json["proxy"],
                "league_id": _config_json["league_id"]
            }
            try:
                _res = self.request_session.post(_url, json=_json)
                _res_ok = json.loads(_res.content)
                if "success" in _res_ok:
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                return False, str(e)
        else:
            return False, "缺少底层接口权限，无法对接底层!"


    def get_event_detail(self, _config_json):
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
                    return True, _res_ok["data"]
                else:
                    return False, str(_res_ok)
            except Exception as e:
                return False, str(e)
        else:
            return False, "缺少底层接口权限，无法对接底层!"