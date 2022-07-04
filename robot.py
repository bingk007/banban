#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing
import requests

headers = {'Content-Type': 'application/json'}
robot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e1f338ae-b07f-4cbb-be13-5b532dfdb53f"


def robot_send(content):
    try:
        data = {
        "msgtype": "markdown",
        "markdown": {
            "content": "#### 开箱子跑数完成\n"
                       "[点击查看测试报告]({})".format(content)}
        }
        requests.post(robot_url, headers=headers, json=data)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    robot_send('https://test.overseaban.com/public/box-probability/report/2022-06-29-19:12:00.html')