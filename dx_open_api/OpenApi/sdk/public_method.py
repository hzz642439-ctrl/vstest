
import sys
sys.path.append("../../../")  # 后台调用脚本必须加
sys.path.append("../../")  # 后台调用脚本必须加
sys.path.append("../")  # 后台调用脚本必须加
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OpenApi.settings")
import json
from OpenApi.settings import rcon100, rcon82, rcon30
import math

# 计算pk_odss_key
def get_now_pk_odd_key(_da):
    hf_type = _da["hf_type"]
    pk_type = _da["pk_type"]
    pk_ratio = '{:g}'.format(_da["pk_ratio"])
    select_team = _da["select_team"]
    if pk_type == 'M':
        if select_team == "home":
            _index = 0
        elif select_team == "away":
            _index = 1
        elif select_team == "draw":
            _index = 2
        else:
            _index = -1
    else:
        if select_team == "home":
            _index = 0
        elif select_team == "away":
            _index = 1
            if pk_type == "R":
                pk_ratio = '{:g}'.format(-_da["pk_ratio"])
        else:
            _index = -1
    _this_pk_odds_key = ":".join([hf_type, pk_type, str(pk_ratio), str(_index)])
    if _da["market_type"] == "main":
        pk_odds_key = _this_pk_odds_key
    elif _da["market_type"] == "corner":
        pk_odds_key = "C:" + _this_pk_odds_key
    elif _da["market_type"] == "pcard":
        pk_odds_key = "F:" + _this_pk_odds_key
    elif _da["market_type"] == "pd":
        pk_odds_key = "B" + ":" + _this_pk_odds_key
    elif _da["market_type"] == "goal":
        pk_odds_key = "G" + ":" + _this_pk_odds_key
    else:
        pk_odds_key = _this_pk_odds_key
    return pk_odds_key

def get_pk_odd_key_ch(pk_odds_key):
    _pkinfo = {}
    new_info={}
    if "C:" in pk_odds_key:
        pk_odds_key = pk_odds_key.replace("C:", "")
        new_info["market_type"] = "角球:"
    elif "F:" in pk_odds_key:
        pk_odds_key = pk_odds_key.replace("F:", "")
        new_info["market_type"] = "罚牌:"
    else:
        new_info["market_type"] = ""


    new_info["pk_ratio"] = pk_odds_key.split(":")[2]
    if pk_odds_key.split(":")[0] == "full":
        new_info["hf_type"] = "全场:"
    elif pk_odds_key.split(":")[0] == "half":
        new_info["hf_type"] = "半场:"
    elif pk_odds_key.split(":")[0] == "section1":
        new_info["hf_type"] = "第一节:"
    else:
        new_info["hf_type"] = "第二节:"

    # new_info["pk_type"] =  pk_odds_key.split(":")[1]

    if pk_odds_key.split(":")[1] == "M":
        new_info["pk_type"] = "1X2"
    if pk_odds_key.split(":")[1] == "R":
        new_info["pk_type"] = "让球"
    if pk_odds_key.split(":")[1] == "OU":
        new_info["pk_type"] = "大小"
    _this_order=int(pk_odds_key.split(":")[-1])
    _odds_pk_type=pk_odds_key.split(":")[1]
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
            _odds_name_pre = "大" + new_info["pk_ratio"]
        if _this_order == 1:
            _odds_name_pre = "小" + new_info["pk_ratio"]
    if _odds_pk_type == "R":  # 需要全半场:(角球):主客队
        if _this_order == 0:
            _odds_name_pre = "主队:" + new_info["pk_ratio"]
        if _this_order == 1:
            _odds_name_pre = "客队:" + new_info["pk_ratio"]

    _name = new_info["hf_type"] + new_info["market_type"] + _odds_name_pre
    return _name


# 根据pk_odds_key获取相反盘口
def get_reverse_pk_odds_key(pk_odds_key):
    reverse_pk_odds_key = ""
    if "M" not in pk_odds_key:
        reverse_pk_odds_key_list = pk_odds_key.split(":")
        if reverse_pk_odds_key_list[-1] == "0":
            reverse_pk_odds_key_list[-1] = "1"
        else:
            reverse_pk_odds_key_list[-1] = "0"
        if "R" in pk_odds_key:
            if reverse_pk_odds_key_list[-2] != "0":
                reverse_pk_odds_key_list[-2] = '{:g}'.format(-float(reverse_pk_odds_key_list[-2]))
        reverse_pk_odds_key = ":".join(reverse_pk_odds_key_list)
    return reverse_pk_odds_key


def get_user_config(gid, user_config_id):
    user_config_id_obj = {}
    # for user_config_id in user_config_ids:
    user_config_id = str(user_config_id)
    if rcon100.hexists("user_config:" + str(gid), user_config_id):
        user_config_obj = json.loads(
            rcon100.hget("user_config:" + str(gid), user_config_id).decode("utf-8"))
        for _bc_type, _values in user_config_obj.items():
            _bc_type = _bc_type.replace("ag_", "")
            if "hga" in _bc_type:
                _bc_type = "hga"
            if _bc_type not in user_config_id_obj:
                user_config_id_obj[_bc_type] = []
            for _value in _values:
                if _value["groupName"] == "member_sort":
                    for _u in _value["groupValue"]:
                        user_config_id_obj[_bc_type].append(_u["user_value"])
    return user_config_id_obj


# 优势盘口判断
class SuperiorPk:
    def pk_OU_condition(self, pk_index, from_pk_ratio, now_pk_ratio):
        now_pk_ratio = float(now_pk_ratio)
        from_pk_ratio = float(from_pk_ratio)
        if pk_index == "0":  # 大
            if now_pk_ratio < from_pk_ratio:  # 实际盘值小于2.5得 True
                return True
        else:                      # 小
            if now_pk_ratio > from_pk_ratio: # 实际盘值大于2.5得 True
                return True
        return False

    def pk_R_condition(self, from_score, now_score, from_pk_ratio, now_pk_ratio, pk_index):
        from_home_score = int(from_score.split(":")[0])
        from_away_score = int(from_score.split(":")[1])
        now_home_score = int(now_score.split(":")[0])
        now_away_score = int(now_score.split(":")[1])
        from_JS_ball = from_home_score - from_away_score
        now_JS_ball = now_home_score - now_away_score
        pk_ratio = math.ceil(abs(now_pk_ratio))
        if from_JS_ball == now_JS_ball:
            if now_pk_ratio > from_pk_ratio: return True
        else:
            if pk_index == "0":  # 主队
                if from_pk_ratio < 0:  # 让
                    if now_JS_ball - from_JS_ball > 0:  # 主队进球
                        if (now_home_score - from_home_score) >= abs(from_pk_ratio): return False
                        if now_pk_ratio >= 0: return True
                        if abs(now_pk_ratio) < abs(from_pk_ratio) - (now_home_score - from_home_score): return True
                        return False
                    else:   # 客队进球
                        if now_pk_ratio >= from_pk_ratio: return True
                        if 0 < pk_ratio - abs(from_pk_ratio) < 1: return True
                else:  # 受让
                    if now_JS_ball - from_JS_ball > 0:  # 主队进球
                        if now_pk_ratio > from_pk_ratio: return True
                    else:   # 客队进球
                        if now_pk_ratio >= from_pk_ratio: return True
                        if (now_away_score - from_away_score) >= from_pk_ratio:
                            if now_pk_ratio >= 0: return True
                        if now_pk_ratio > from_pk_ratio - (now_away_score - from_away_score): return True
            else:  # 客队
                if from_pk_ratio < 0:  # 让
                    if now_JS_ball - from_JS_ball > 0:  # 主队进球
                        if now_pk_ratio >= from_pk_ratio: return True
                    else:   # 客队进球
                        if (now_away_score - from_away_score) >= abs(from_pk_ratio): return False
                        if now_pk_ratio >= 0: return True
                        if abs(now_pk_ratio) < abs(from_pk_ratio) - (now_away_score - from_away_score): return True
                        return False
                else:  # 受让
                    if now_JS_ball - from_JS_ball > 0:  # 主队进球
                        if now_pk_ratio >= from_pk_ratio: return True
                        if (now_home_score - from_home_score) > from_pk_ratio:
                            if now_pk_ratio >= 0: return True
                        if now_pk_ratio > from_pk_ratio - (now_home_score - from_home_score): return True
                    else:   # 客队进球
                        if now_pk_ratio >= from_pk_ratio: return True
        return False

    def get_superior_pk_data(self, from_score, now_score, from_pk_odds_key, pk_odds_key):
        now_pk_odds_key_list = pk_odds_key.split(":")
        now_pk_ratio = float(now_pk_odds_key_list[-2])
        now_pk_odds_key_list[-2] = "*"
        from_pk_odds_key_list = from_pk_odds_key.split(":")
        from_pk_type = from_pk_odds_key_list[-3]
        from_pk_ratio = float(from_pk_odds_key_list[-2])
        from_pk_index = from_pk_odds_key_list[-1]
        from_pk_odds_key_list[-2] = "*"
        if now_pk_odds_key_list != from_pk_odds_key_list:
            return False
        if from_pk_type == 'OU':
            return self.pk_OU_condition(from_pk_index, from_pk_ratio, now_pk_ratio)
        elif from_pk_type == 'R':
            return self.pk_R_condition(from_score, now_score, from_pk_ratio, now_pk_ratio, from_pk_index)
        else:
            return False


def get_score(bc_type, ids):
    score = {
        "score": "0:0",
        "half_score": "0:0",
        "red_card": "0:0",
        "yellow_card": "0:0",
        "corner": "0:0"
    }
    if rcon82.exists(bc_type + ":" + ids):
        _minfo = json.loads(rcon82.get(bc_type + ":" + ids))
        if "score" in _minfo["minfo"]:
            score["score"] = _minfo["minfo"]["score"]
        if "half_score" in _minfo["minfo"]:
            score["half_score"] = _minfo["minfo"]["half_score"]
        if "yellow_card" in _minfo["minfo"]:
            score["yellow_card"] = _minfo["minfo"]["yellow_card"]
        if "red_card" in _minfo["minfo"]:
            score["red_card"] = _minfo["minfo"]["red_card"]
        if "corner" in _minfo["minfo"]:
            score["corner"] = _minfo["minfo"]["corner"]
    return score

def user_is_pass(no_place_pk_key_all, league_id, place_league, no_place_pk_type, pk_odds_key):
    no_place_pk_key_list = []
    for key, no_place_pk_key in no_place_pk_key_all.items():
        no_place_pk_key_list += no_place_pk_key
    if pk_odds_key in no_place_pk_key_list:
        return False, "不玩该盘口！"
    if league_id:
        if place_league:
            if league_id not in place_league:
                return False, "该会员账号无法下注该联赛比赛！"
    pk_type_list = pk_odds_key.split(":")[:-2]
    pk_type = ":".join(pk_type_list)
    if pk_type in no_place_pk_type:
        return False, "不玩该盘口类型！"
    # if place_order_stakes:
    #     if order_stake < place_order_stakes[0] or order_stake > place_order_stakes[1]:
    #         return False, "订单金额超过设定值！"
    return True, "成功！"


def get_membername_obj(bc_type, agent):
    _this_member_key = "agent:members:" + bc_type + ":" + agent
    membername_obj = {}
    if rcon30.exists(_this_member_key):
        _mlist=json.loads(rcon30.get(_this_member_key))
        for _ml in _mlist:
            membername_obj[_ml["username"]] = _ml["login_username"]
    return membername_obj

def get_bc_type_ch(bc_type):

    _key = "auto_api:need:bookies"
    if rcon100.exists(_key) == 1:
        need_bookies = json.loads(rcon100.get(_key))
        out_platforms = need_bookies["need_bookies_ch"]
        cp_platforms = need_bookies["cp_need_bookies_ch"]
        for _out_platform in out_platforms:
            if _out_platform["bc_type"] == bc_type:
                return _out_platform["name"]
        for _cp_platform in cp_platforms:
            if _cp_platform["bc_type"] == bc_type:
                return _cp_platform["name"]
    return bc_type


if __name__ == '__main__':
    # from_score = "0:0"
    # now_score = "2:0"
    # from_pk_odds_key = "full:OU:4.75:1"
    # pk_odds_key = "full:OU:4.75:1"
    # superior_pk = SuperiorPk()
    # test = superior_pk.get_superior_pk_data(from_score, now_score, from_pk_odds_key, pk_odds_key)
    # if test:
    #     print(test, "现在盘口为优势盘口")
    # else:
    #     print(test, "现在盘口不为优势盘口")

    print(get_score("hga", "100032:101925:103729"))