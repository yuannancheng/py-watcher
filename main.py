# -*- coding: utf-8 -*-

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
    if not os.path.exists(setting['result']):
        result = {}
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
            continue # 第一次运行，无历史数据
        for data in nResult[name]:
            if not data in result[name]:
                status[name].append(data)

    for i, name in enumerate(status):
        msg = ''
        sum = 0
        for data in status[name]:
            sum += 1
            msg += '<p><span>{}&nbsp;&nbsp;</span><span>{}</span></p>'.format(data['time'], data['title'])
        if sum > 0:
            msg = '<p><strong>{}</strong>&nbsp;&nbsp;<a href="{}">点击访问</a></p><div class="Meet_you_mail_content">{}</div>'.format(
                name, setting['target'][i]['link'], msg)
            body += msg
    if not body == '':  # 有历史记录可对比才继续
        body = '''<div class="Meet_you_mail_wrap">
                  <div class="Meet_you_mail_title_wrap">
                    <p class="Meet_you_mail_title">以下网站发布了新的公告</p>
                  </div>
                  <div style="margin:40px auto;width:90%">
                ''' + body + '''
                    <br>
                    <p style="border-top: #eee solid 1px;padding: 5px;">
                      此邮箱无人值守，请勿回复此邮件 | 来自 <a href="https://github.com/yuannancheng/py-watcher" style="text-decoration:none;color:#12addb!important">PyWatcher</a>
                    </p>
                  </div>
                  <style> body { background-color: #fff !important; } * { color: #000 !important; background-color: transparent !important; } a:active, a:hover, a:link, a:visited { text-decoration: none } .Meet_you_mail_wrap div:nth-child(2) a { color: #12addb !important; } .Meet_you_mail_wrap { border-radius: 10px 10px 10px 10px; font-size: 13px; width: 666px; font-family: 'Century Gothic', 'Trebuchet MS', 'Hiragino Sans GB', 微软雅黑, 'Microsoft Yahei', Tahoma, Helvetica, Arial, SimSun, sans-serif; margin: 50px auto; border: 1px solid #eee !important; max-width: 100%; background: #fff repeating-linear-gradient(-45deg, #fff, #fff 1.125rem, transparent 1.125rem, transparent 2.25rem) !important; box-shadow: 0 1px 5px rgba(0, 0, 0, .15) } .Meet_you_mail_title_wrap { width: 100%; background: #49bdad !important; border-radius: 10px 10px 0 0; background-image: -moz-linear-gradient(0deg, #43c6b8, #ffd1f4) !important; background-image: -webkit-linear-gradient(0deg, #43c6b8, #ffd1f4) !important; height: auto } .Meet_you_mail_title { font-size: 15px; word-break: break-all; padding: 23px 32px; margin: 0; background-color: hsla(0, 0%, 100%, .4); border-radius: 10px 10px 0 0; color: #fff !important; } .Meet_you_mail_content { position: relative; margin: 20px 0; padding: 5px 15px; border-radius: 0 5px 5px 0; font-size: 14px; color: #555 !important; border-left: 5px #eee solid !important; margin-left: 2em } .Meet_you_mail_wrap div:nth-child(2) * { color: #555 !important; } .Meet_you_mail_content>* { margin-block-start: unset; margin-block-end: unset; margin: 5px auto; } </style>
                </div>'''

        mail = setting['mail']
        success = sender.send_mail_html(
            mail['host'],
            mail['port'],
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