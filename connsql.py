#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing

import pymysql
import time
import re
import random


class ConnSql:

    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           passwd='123456',
                           charset='utf8',
                           autocommit=True)

    conn.select_db('xianshi')
    conn.ping(reconnect=True)
    cur = conn.cursor()

    @staticmethod
    def update_maincid_send(maincid, box_type):
        sql = "update xs_global_box set last_refresh_cid={},last_refresh_sub_cid={} where type='{}'" \
              "".format(maincid, maincid, box_type)
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('update fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def update_maincid_blind(maincid, box_type):
        sql = "update xs_global_mystery_box set last_refresh_cid={},last_refresh_sub_cid={} where type='{}'" \
              "".format(maincid, maincid, box_type)
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('update fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def insert_maincid_myself(uid, maincid, box_type):
        sql_fir = "delete from xs_user_box where uid='{}' and type='{}'".format(uid, box_type)
        sql_sec = "insert into xs_user_box (uid, type, num, total_money, last_refresh_cid, last_refresh_dateline, " \
                  "dateline, last_refresh_sub_cid) values ({}, '{}', 0, 0, {}, {}, {}, {})".format(
                   uid, box_type, maincid, int(time.time()), int(time.time()), maincid)
        try:
            ConnSql.cur.execute(sql_fir)
            ConnSql.cur.execute(sql_sec)
        except Exception as error:
            ConnSql.conn.rollback()
            print('insert maincid fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def insert_commodity(uid, cid):
        sql = "insert into xs_user_commodity (uid, cid, state, num, period_end, used, in_use, dateline) " \
                  "values ({}, {}, 0, 1000000, 0, 0, 0, {})".format(
                   uid, cid, int(time.time()))
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('insert commodity fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def insert_idCard(uid, app_id, state):
        sql = "insert into xs_user_idcard(uid,app_id,state) values({},{},{})".format(
            uid, app_id, state)
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('insert idcard fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def insert_box_rate(type, mainCid, low, high, boxtype):
        sql = "insert into xs_boxs_set_records (type,mainCid,low,high,boxtype,dateline) values({},{},{},{},'{}',{})" \
              "".format(type, mainCid, low, high, boxtype,int(time.time()))
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('insert box_rate fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def update_money(uid):
        sql = "update xs_user_money set money=999999999 where uid={}".format(uid)
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('update fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def delete_commodity(uid):
        sql = "delete from xs_user_commodity where uid={}".format(uid)
        try:
            ConnSql.cur.execute(sql)
        except Exception as error:
            ConnSql.conn.rollback()
            print('delete fail', error)
        finally:
            ConnSql.conn.commit()

    @staticmethod
    def select_pay(uid):
        sql = "select reason from xs_pay_change_new where uid={}".format(uid)
        try:
            ConnSql.cur.execute(sql)
            res = ConnSql.cur.fetchone()
            if res is None:
                return 0
            else:
                re_str = 'd:(.*?);'
                money = re.compile(re_str).findall(res[0])
                return money
        except Exception as error:
            print(error)

    @staticmethod
    def select_send_statistics(rate, *uid):
        sql = 'select count(*) ,sum(money)/{} from xs_pay_change_new where uid in {}'.format(rate, uid)
        try:
            ConnSql.cur.execute(sql)
            res = ConnSql.cur.fetchone()
            return res
        except Exception as error:
            print(error)

    @staticmethod
    def select_user_commodity(*uid):
        sql = 'select sum(a.num*b.price) as money,sum(a.num) as num from ' \
              'xs_user_commodity a,xs_commodity b where a.cid=b.cid and a.cid>=5 and b.type!="header" ' \
              'and a.uid in {}'.format(uid)
        try:
            ConnSql.cur.execute(sql)
            res = ConnSql.cur.fetchone()
            return res
        except Exception as error:
            print(error)

    @staticmethod
    def select_box_sets(play_type_id, main_cid, box_type):
        sql = 'select low, high from xs_boxs_set_records where type={} and mainCid={} and boxtype="{}" ' \
              'order by id desc limit 1'.format(play_type_id, main_cid, box_type)
        try:
            ConnSql.cur.execute(sql)
            res = ConnSql.cur.fetchone()
            if res is None:
                return [0, 0]
            else:
                return [str(res[0])+'%', str(res[1])+'%']
        except Exception as error:
            print(error)

    @staticmethod
    def select_room(room_type='business'):
        sql = 'select rid from xs_chatroom where property = "{}" order by rid desc limit 100'.format(room_type)
        try:
            ConnSql.cur.execute(sql)
            res = ConnSql.cur.fetchone()
            if res is None:
                return 0
            else:
                return random.choice(res)
        except Exception as error:
            print(error)




