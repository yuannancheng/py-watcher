# -*- coding: utf-8 -*-

import re
import json
import sender
import os.path
from requests_html import HTMLSession


def loadSetting(settingPath):
    global setting
    with open(settingPath, encoding='utf-8') as f:
        setting = json.loads(f.read())


def loadLastResult():
    global setting, result
    if os.path.exists(setting['result']):
        result = {"专升本-九江学院校园网": [{"title": "关于2020年专升本预录学生、第二学位预录学生、退伍复学学生、休学复学学生以及出...","time": "2020-08-17"}, {"title": "关于2020年我校专升本招生调剂拟录取名单公示的通知","time": "2020-08-07"}, {"title": "九江学院2020年普通专升本招生调剂通知","time": "2020-08-04"}, {"title": "温馨提示","time": "2020-07-31"}, {"title": "九江学院2020年“专升本”考试预录取名单公示","time": "2020-07-21"}, {"title": "关于2020年“专升本”各专业预录取分数线的公告","time": "2020-07-21"}, {"title": "关于九江学院2020年专升本考试成绩公布及复核的通知","time": "2020-07-13"}, {"title": "温馨提示","time": "2020-07-02"}, {"title": "九江学院关于2020年专升本考试现场审核的通知","time": "2020-06-28"}, {"title": "九江学院关于2020年专升本考试准考证打印的通知","time": "2020-06-28"}, {"title": "关于九江学院2020年专升本招生考试网上缴费的通知","time": "2020-06-24"}, {"title": "关于江西省2020年普通高校专升本考试网上报名时间延长的公告","time": "2020-06-23"}, {"title": "关于2020年九江学院专升本报名工作的重要通知","time": "2020-06-21"}],"江西省教育考试院": [{"title": "关于成人高考自2021年起启用新版复习考...","time": "04-02"}, {"title": "江西省教育考试院2021-2023年政府...","time": "03-30"}, {"title": "2021年江西省普通高校专升本考试招生工...","time": "03-25"}, {"title": "关于做好全省2021年普通高校专升本考试...","time": "03-24"}, {"title": "江西省2021年初中学业水平考试学科试卷...","time": "03-19"}, {"title": "江西省教育考试院2021-2023年政府...","time": "03-19"}, {"title": "致全省2021年4月自学考试考生的公开信","time": "03-18"}, {"title": "关于印发《江西省2021年普通高校招生体...","time": "03-18"}, {"title": "2021年研考国家线公布","time": "03-12"}]}
    else:
        with open(setting['result'], encoding='utf-8') as f:
            result = json.loads(f.read())


def requests():
    global setting, result, nResult
    session = HTMLSession()
    target = setting['target']
    nResult = {}
    for i, v in enumerate(target):
        nResult[v['name']] = []
        r = session.get(v['link'])
        for li in r.html.find(v['el']['list']):
            nResult[v['name']].append({
                'title': li.find(v['el']['title'])[0].text,
                'time': li.find(v['el']['time'])[0].text
            })


def compare():
    global setting, result, nResult
    status = {}
    body = ''

    for name in nResult:
        status[name] = []
        if not name in result.keys():
            continue  # 第一次运行，无历史数据
        for data in nResult[name]:
            if not data in result[name]:
                status[name].append(data)

    for i, name in enumerate(status):
        msg = ''
        sum = 0
        for data in status[name]:
            sum += 1
            msg += '<tr><td class="content_td"><strong>{}&nbsp;&nbsp;</strong><span>{}</span></td></tr>'.format(data['time'], data['title'])
        if sum > 0:
            msg = '<tr><td class="title"><strong>{}</strong>&nbsp;&nbsp;<a href="{}" class="a">点击访问</a></td></tr><tr><td class="content_wrap"><table class="content" border="0" cellspacing="" cellpadding=""><tbody>{}</tbody></table></td></tr>'.format(name, setting['target'][i]['link'], msg)
            body += msg
    if not body == '': # 有历史记录可对比才继续
        body = '<!DOCTYPE html><html><head><meta charset="utf-8"/></head><div class="box"><table border="0" cellspacing="" cellpadding="" class="wrap"><tbody><tr><td class="header">以下网站发布了新的公告</td></tr><tr><td class="space"></td></tr>{}<tr><td class="space"></td></tr><tr><td class="theEnd">此邮箱无人值守，请勿回复此邮件 | 来自 <a href="https://github.com/yuannancheng/py-watcher" class="a">PyWatcher</a></td></tr></tbody></table></div></html>'.format(body)

        styleSheet = {
            'box': 'width:666px;max-width:100%;margin:50px auto;',
            'wrap': 'border-top:5px solid #12addb;box-shadow:0 1px 3px #aaa;background-color:#fff;color:#000;line-height:180%;padding:0 15px 12px;font-size:13px;width:100%;box-sizing:border-box;',
            'header': 'border-bottom:1px solid #ddd;background-color:#fff;color:#000;font-size:16px;font-weight:900;padding:26px 0 10px 8px;text-align:left;',
            'space': 'padding:13px 0 0;',
            'a': 'color:#12addb;text-decoration:none;',
            'content_wrap': 'background-color:#fff;color:#000;padding:0 12px 0 12px;margin-top:18px;',
            'content': 'color:#000;position:relative;background-color:#f5f5f5;padding:10px 15px;margin:18px 0;word-wrap:break-word;width:100%;font-size:13px;',
            'content_td': 'padding:3px;',
            'theEnd': 'border-top:#ddd solid 1px;padding:5px;'
        }
        style = '<style>'

        # 替换为内联样式，以适应邮件样式规则
        for i in styleSheet:
            Rex = re.compile(r'class="{}"'.format(i))
            body = Rex.sub('style="{}"'.format(styleSheet[i]), body)
            # 同时保留样式表
            # body = Rex.sub('class="{}" style="{}"'.format(i, styleSheet[i]), body)
            # style += '.' + i + ' {' + styleSheet[i] + '}'

        # 同时保留样式表
        # body = body.replace('</html>', '{}</style></html>'.format(style))

        mail = setting['mail']
        success = sender.send_mail_html(
            mail['host'],
            mail['port'],
            mail['nick'],
            mail['from_addr'],
            mail['tokens'],
            mail['to_addr'],
            '部分网站发布了新的公告',
            body
        )

        if success:
            print('发送成功')
        else:
            print('发送失败')


def saveResult():
    global setting, nResult
    with open(setting['result'], 'w', encoding='utf-8') as f:
        json.dump(nResult, f, ensure_ascii=False)


def main():
    loadSetting('setting.json')
    loadLastResult()
    requests()
    compare()
    saveResult()


if __name__ == '__main__':
    main()
