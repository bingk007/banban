#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing

from probability import Probability
from report import Report
import sys
import subprocess
import json
from connsql import ConnSql

box_send = {
    'gold': [3300000, 48, 6600],
    'silver': [1050000, 47, 2100],
    'copper': [300000, 46, 600]
}

box_myself = {
    'gold': [6600,3300000,4],
    'silver': [2100,1050000,3],
    'copper': [600,300000,2]
}


box_blind = {
    'gold': [2000000, 775, 4000],
    'silver': [600000, 774, 1200],
    'copper': [150000, 773, 300]
}

play_type = {
    '1': '开箱子送人',
    '2': '自己开箱子',
    '3': '开盲盒送人'
}

area_lang = {'CN': ['中国', 'CN', 'zh_CN'],
             'TH': ['泰国','TH', 'th'],
             'VI': ['越南', 'VI', 'vi'],
             'MY': ['马来西亚', 'MY', 'ms'],
             'ID': ['印度尼西亚', 'ID','id'],
             'SA': ['沙特阿拉伯', 'SA','ar']}


def process_form(play_type_id, dict_box_params):
    args = []
    times = int(dict_box_params['times'])
    area = dict_box_params['area']
    env = dict_box_params['env']
    Probability.predata['area'] = area_lang[area]
    Probability.predata['env'] = env
    for param in dict_box_params:
        try:
            if dict_box_params[param] != '':
                if param[:4] == 'rate':
                    type_maincid = param[5:].split('_')
                    history_rate = dict_box_params[param].split(',')
                    ConnSql.insert_box_rate(play_type_id,type_maincid[1],history_rate[0],history_rate[1],type_maincid[0])
                elif 'on' in dict_box_params[param]:
                    type_maincid = param.split('_')
                    temp_list = [type_maincid[0], type_maincid[1], int(times / 10000), int(times / 500)]
                    args.append(temp_list)
        except Exception as e:
            print(e)
            continue
    return args


def get_process_id(name):
    child = subprocess.Popen(['pgrep', '-f', name], stdout=subprocess.PIPE, shell=False)
    response = child.communicate()[0]
    pid = [int(pid) for pid in response.split()]
    return pid


def main_box_send(play_type_id, box_type, main_cid, peoples, times):
    if play_type_id == 1:
        Probability().open_box_in_room(
            play_type_id, main_cid, box_type, box_send[box_type][0], box_send[box_type][1],box_send[box_type][2],peoples,times
        )
    elif play_type_id == 3:
        Probability().open_box_in_room(
            play_type_id, main_cid, box_type, box_blind[box_type][0], box_blind[box_type][1],box_blind[box_type][2],peoples,times
        )


def main_box_myself(box_type, main_cid, peoples, times):
    Probability().open_box_in_package(
        main_cid, times, box_myself[box_type][0], box_myself[box_type][1], box_type, box_myself[box_type][2], peoples
    )


def main_test(play_type_id, box_params):
    box_params = box_params.replace("\\","")
    box_params = json.loads(box_params)
    run_params = process_form(play_type_id, box_params)
    if not run_params:
        sys.exit()
    Report(play_type[str(play_type_id)])
    Report.create_html()
    if play_type_id == 1 or play_type_id == 3:
        for params in run_params:
            main_box_send(play_type_id, *params)
    if play_type_id == 2:
        for params in run_params:
            main_box_myself(*params)
    Report.insert_link(play_type[str(play_type_id)])


if __name__ == '__main__':
    main_test(int(sys.argv[1]), sys.argv[2])
