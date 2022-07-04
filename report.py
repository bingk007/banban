#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing
from HTMLTable import HTMLTable
import time
import fileinput
import os
import robot


class Report:
    current_path = os.path.dirname(__file__)
    html_name = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())) + ".html"
    html = current_path + "/report/" + html_name
    link_dir = 'https://test.overseaban.com/public/box-probability/report/'
    table = None

    def __init__(self, play):
        Report.table = HTMLTable(caption=play + '跑数报告')

    @staticmethod
    def table_format():
        # 表格样式，即<table>标签样式
        Report.table.set_style({
            'border-collapse': 'collapse',
            'word-break': 'keep-all',
            'white-space': 'nowrap',
            'font-size': '14px',
        })
        # 统一设置所有单元格样式，<td>或<th>
        Report.table.set_cell_style({
            'border-color': '#000',
            'border-width': '1px',
            'border-style': 'solid',
            'padding': '5px',
        })

    @staticmethod
    def create_html():
        with open(Report.html, 'w') as html_report:
            html_report.write('<meta charset="utf-8">')
            Report.table.append_header_rows((
                 ('类型', 'MainCid', '上拉阀值', '下拉阀值', '开箱人数', '开箱数', '开箱总费用', '奖品总金额', '返奖率'),))
            # 标题样式
            Report.table.caption.set_style({
                'font-size': '18px',
            })
            # 表头样式
            Report.table.set_header_row_style({
                'color': '#fff',
                'background-color': '#48a6fb',
                'font-size': '15px',
            })
            # 覆盖表头单元格字体样式
            Report.table.set_header_cell_style({
                'padding': '15px',
            })
            Report.table_format()
            html_report.write(Report.table.to_html())

    @staticmethod
    def add_line(box_type, main_cid, history_rate_low, history_rate_high, num_box, peoples, use_money, get_money, reward_rate):
        with open(Report.html, 'w') as html_report:
            html_report.write('<meta charset="utf-8">')
            Report.table.append_data_rows((
                (box_type, main_cid, history_rate_low, history_rate_high, num_box, peoples, use_money, get_money, reward_rate),
            ))
            Report.table_format()
            html_report.write(Report.table.to_html())

    @staticmethod
    def insert_link(play_type):
        link = '<a href="{}{}">{}{}</a>'.format(
            Report.link_dir,Report.html_name,play_type,Report.html_name)
        for line in fileinput.FileInput(Report.current_path + "/templates/report.html", inplace=1):
            if "<body>" in line:
                line = line.replace(line, line + link + '\n')
            print(line, end='')
        robot.robot_send(Report.link_dir+Report.html_name)
