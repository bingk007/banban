#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing

import requests
import time
import random
import json
from retrying import retry
from connsql import ConnSql
from report import Report
import os

requests.packages.urllib3.disable_warnings()


class Probability:

    predata = {
        'area': ['中国', 'CN', 'zh_CN'],
        'env': 'test.overseaban.com'
    }

    current_path = os.path.dirname(__file__)
    host = 'test.overseaban.com'
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
        'user-model': 'Mi%2010',
        'user-channel': 'gp_os',
        'user-oaid': '1f9c63e5567aaf03',
        'user-tag': 'fb94f09c5636de5c',
        'user-issimulator': 'false',
        'user-idfa': '',
        'user-isroot': 'false',
        'user-language': predata['area'][2],
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; V2020A Build/QP1A.190711.020; wv) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 '
                    'Mobile Safari/537.36 / Xs android V1.7.8.1 / Js V1.0.0.0 / Login V0',
        'accept-encoding': 'gzip',
        'host': host,
        'user-token': '',
        'user-abi': 'arm64-v8a',
        'user-page': '%2FloginByCode'
    }
    req_tail = "package=com.imbb.oversea.android&_ipv=0&_platform=android&_index=23&" \
               "_model=V2020A&_timestamp={}&_abi=arm64-v8a&format=json&_sign=a3c0a440c0ff7644882688ae94c155d1".format(
                int(time.time()))

    box_dic = {
        'gold': 6600,
        'silver': 2100,
        'copper': 600
    }

    blind_dic = {
        'gold': 4000,
        'silver': 1200,
        'copper': 300
    }

    tmp_token = []
    tmp_uid = []

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def http_get_request(self, url):
        domain_name = 'https://' + self.predata['env']
        response = requests.get(domain_name + url + self.req_tail, headers=self.headers, timeout=10, verify=False)
        try:
            if response.status_code == 200:
                return response.json()
            else:
                return
        except Exception as e:
            print("httpGet failed, detail is:%s,%s" % (response.text, e))
            return

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def http_post_request(self, url, params):
        domain_name = 'https://' + self.predata['env']
        response = requests.post(domain_name + url + self.req_tail, params, headers=self.headers, timeout=10,
                                 verify=False)
        try:
            if response.status_code == 200:
                return response.json()
            else:
                return
        except Exception as e:
            print("httpPost failed, detail is:%s,%s" % (response.text, e))
            return

    def mobile_check(self, mobile, area):
        params = {
            'mobile': mobile,
            'area': area
        }
        url = '/go/party/account/mobileCheck?'
        return self.http_post_request(url, params)

    def account_sync(self):
        url = '/account/sync?version=4&act_version=2&money=1&frame=1&'
        return self.http_get_request(url)

    def update_country(self, country, countryCode):
        params = {
            'country': country,
            'countryCode': countryCode
        }
        url = '/account/updateCountry?'
        return self.http_post_request(url, params)

    def update_language(self, countryCode):
        url = '/account/updatelanguage?lan={}&force=1'.format(countryCode)
        return self.http_get_request(url)

    def send_verify_code(self, mobile, type):
        params = {
            'mobile': mobile,
            'area': 86,
            'type': type
        }
        url = '/account/sendVerifyCode?'
        return self.http_post_request(url, params)

    def login_mobile(self, mobile, code, token):
        params = {
            'mobile': mobile,
            'type': 'login',
            'code': code,
            'token': token,
            'dtoken': '',
            'area': '86'
        }
        url = '/account/login?v=1&'
        resp = self.http_post_request(url, params)
        self.headers['user-token'] = resp['data']['token']
        return resp

    def pay_create(self, platform, type, money, params):
        params = {
            'platform': platform,
            'type': type,
            'money': money,
            'params': params
        }
        url = '/pay/create?'
        return self.http_post_request(url, params)

    def box_detail(self, cid):
        url = '/account/boxdetail?cid={}&'.format(cid)
        return self.http_get_request(url)

    def open_box(self, type,num,scene='shop_box',star=0):
        params = {
            'type': type,
            'num': num,
            'star': star,
            'scene':scene
        }
        url = '/account/openbox?'
        return self.http_post_request(url, params)

    def register(self):
        try:
            tel = random.choice(['13']) + ''.join(random.choice('0123456789') for i in range(9))
            check_resp = self.mobile_check(tel, 86)
            if check_resp['data']['exist'] is False:
                send_code = self.send_verify_code(tel, 'PhoneCodeType.register')
                login_resp = self.login_mobile(tel, 1234, send_code['data'])
                print(login_resp)
                self.headers['user-token'] = login_resp['data']['token']
                self.account_sync()
                self.update_country(self.predata['area'][0], self.predata['area'][1])
                self.update_language(self.predata['area'][2])
                return login_resp
        except Exception as e:
            print(e)

    def register_for_room(self, people):
        self.tmp_token.clear()
        for i in range(people):
            try:
                login_resp = self.register()
                token = login_resp['data']['token']
                self.tmp_token.append(token)
                user_uid = str(login_resp['data']['uid'])
                ConnSql.update_money(user_uid)
            except Exception as e:
                print(e)

    @staticmethod
    def get_history_rate(play_type_id, main_cid, box_type):
        try:
            history_reward_rate = ConnSql.select_box_sets(play_type_id, main_cid, box_type)
            if history_reward_rate != 0:
                rate_low = history_reward_rate[0]
                rate_high = history_reward_rate[1]
            else:
                rate_low = 0
                rate_high = 0
            return [rate_low, rate_high]
        except Exception as e:
            print(e)

    @staticmethod
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def get_data_statistics(play_type_id, uid):
        try:
            if play_type_id == 1 or play_type_id == 3:
                money = ConnSql.select_pay(random.choice(uid))
                print(money)
                rate = int(money[0]) / int(money[1])
                gift_stat = ConnSql.select_send_statistics(rate, *uid)
                print(gift_stat)
                comm_stat = ConnSql.select_user_commodity(*uid)
                print(comm_stat)
                if comm_stat == (None, None):
                    money_total = gift_stat[1]
                else:
                    money_total = gift_stat[1] + comm_stat[0]
                print(money_total)
                return [gift_stat[0], int(money_total)]
            elif play_type_id == 2:
                comm_stat = ConnSql.select_user_commodity(*uid)
                return comm_stat
            else:
                print('error play')
        except Exception as e:
            print(e)

    def open_box_room(self, peoples,times,money,rid,giftId,price,num=500,giftNum=500):
        self.register_for_room(peoples)
        for i in range(times):
            try:
                print("房间开箱次数" + str(i))
                user_token = random.choice(self.tmp_token)
                self.headers['user-token'] = user_token
                uids = random.choice(self.tmp_uid)
                params = {"rid":rid,
                          "uids":uids,
                          "positions":"0",
                          "position":-1,
                          "giftId":giftId,
                          "giftNum":giftNum,
                          "price":price,
                          "cid":0,
                          "ctype":"",
                          "duction_money":0,
                          "version":2,
                          "num":num,
                          "gift_type":"normal",
                          "star":0,
                          "refer":"search_results:room",
                          "all_mic":0,
                          "scene":"room_box_send",
                          "useCoin":-1}
                self.pay_create('available', 'package', money, json.dumps(params))
            except Exception as e:
                print(e)
                continue

    def open_box_package(self, times,price,money,box_type,cid,num=500,opennum=500):
        for i in range(times):
            try:
                print('背包开箱次数'+str(i))
                user_token = random.choice(self.tmp_token)
                self.headers['user-token'] = user_token
                for j in range(60):
                    if self.box_detail(cid)['success'] is True:
                        break
                    else:
                        time.sleep(1)
                params = {
                          "price": price,
                          "cid": cid+3,
                          "type": box_type,
                          "duction_money": 0,
                          "version": 2,
                          "num": num,
                          "opennum": opennum,
                          "coupon_id": 0,
                          "star": 0,
                          "scene": "shop_box",
                          "useCoin": -1}
                self.pay_create('available', 'shop-buy', money, json.dumps(params))
            except Exception as e:
                print(e)
                continue

    # 房间开箱子和盲盒
    def open_box_in_room(self, play_type_id, main_cid, box_type, total_money, gift_id, price, peoples,times):
        if play_type_id == 3:
            rid = ConnSql.select_room('union')
        else:
            rid = ConnSql.select_room()
        try:
            if play_type_id == 1:
                ConnSql.update_maincid_send(main_cid, box_type)
            elif play_type_id == 3:
                ConnSql.update_maincid_blind(main_cid, box_type)
            self.tmp_uid.clear()
            for m in range(peoples):
                login_resp = self.register()
                user_uid = login_resp['data']['uid']
                self.tmp_uid.append(user_uid)
                ConnSql.insert_idCard(user_uid,5,3)
            print("当前测试maincid: " + box_type + str(main_cid))
            with open(self.current_path + "/user_data/untitled_uid_be_rewarded", "a")as f_uid_rewarded:
                f_uid_rewarded.write(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '--' + str(play_type_id) + '--' + box_type +
                    str(main_cid) + ':' + str(self.tmp_uid) + '\n')
            self.open_box_room(peoples,times,total_money,rid,gift_id,price)
            stat_date = self.get_data_statistics(play_type_id, tuple(self.tmp_uid))
            print(stat_date)
            open_num = stat_date[0] * 500
            print(open_num)
            if play_type_id == 1:
                box_price = self.box_dic[box_type]
            elif play_type_id == 3:
                box_price = self.blind_dic[box_type]
            else:
                box_price = 0
                print('error play type')
            open_money = open_num * box_price
            print(open_money)
            reward_rate = '{:.5%}'.format(stat_date[1] / open_money)
            print(reward_rate)
            history_reward_rate = ConnSql.select_box_sets(play_type_id, main_cid, box_type)
            Report.add_line(box_type, main_cid, history_reward_rate[0], history_reward_rate[1],
                            peoples, open_num, open_money, stat_date[1], reward_rate)
        except Exception as e:
            print(e)

    # 背包开箱子
    def open_box_in_package(self, main_cid,times,price,money,box_type,cid,peoples, play_type_id=2):
        try:
            print("当前测试maincid: " + box_type + str(main_cid))
            self.tmp_token.clear()
            user_uid = []
            for i in range(peoples):
                try:
                    login_resp = self.register()
                    token = login_resp['data']['token']
                    self.tmp_token.append(token)
                    uid = login_resp['data']['uid']
                    ConnSql.insert_idCard(uid, 5, 3)
                    user_uid.append(uid)
                    ConnSql.delete_commodity(uid)
                    ConnSql.update_money(uid)
                    ConnSql.insert_maincid_myself(uid, main_cid, box_type)
                    ConnSql.insert_commodity(uid, cid)
                except Exception as e:
                    print(e)
                    continue
            with open(self.current_path + '/user_data/untitled_maincid_uid', 'a') as f_uid:
                f_uid.write(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '--' + str(play_type_id) + '--' + box_type +
                    str(main_cid) + ':' + str(user_uid) + '\n')
            self.open_box_package(times,price,money,box_type,cid)
            stat_date = self.get_data_statistics(play_type_id, tuple(user_uid))
            print(stat_date)
            open_num = stat_date[1]
            print(open_num)
            open_money = open_num * (self.box_dic[box_type])
            print(open_money)
            reward_rate = '{:.5%}'.format(stat_date[0] / open_money)
            print(reward_rate)
            history_reward_rate = ConnSql.select_box_sets(play_type_id, main_cid, box_type)
            Report.add_line(box_type, main_cid, history_reward_rate[0],history_reward_rate[1],
                            peoples,open_num, open_money, stat_date[0], reward_rate)
        except Exception as e:
            print(e)
