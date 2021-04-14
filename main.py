# -*- coding: utf-8 -*-

import re
import sys
import time
import json
import atexit
import sender
import os.path
from requests_html import HTMLSession


def loadSetting(settingPath):
    global setting, logMsg
    logMsg = []
    with open(settingPath, encoding='utf-8') as f:
        setting = json.loads(f.read())


def loadLastResult():
    global setting, result
    if not os.path.exists(setting['result']):
        result = {}
    else:
        with open(setting['result'], encoding='utf-8') as f:
            result = json.loads(f.read())


def session_get(session, link, max=3, n=0):
    try:
        return session.get(link)
    except Exception as e:
        log(e)
        if n < max:
            log('请求失败，{}秒后重试'.format(n * 2 + 1))
            time.sleep(n * 2 + 1)
            return session_get(session, link, max=max, n=n+1)
        else:
            log('重试{}次仍然失败，结束程序'.format(max))
            sys.exit()


def r_html_render(r, max=3, n=0):
    try:
        return r.html.render()
    except Exception as e:
        log(e)
        if n < max:
            log('渲染失败，{}秒后重试'.format(n * 2 + 1))
            time.sleep(n * 2 + 1)
            return r_html_render(r, max=max, n=n+1)
        else:
            log('重试渲染{}次仍然失败，结束程序'.format(max))
            sys.exit()


def requests():
    global setting, result, nResult
    session = HTMLSession()
    target = setting['target']
    nResult = {}
    for i, v in enumerate(target):
        log('正在请求 {}({})'.format(v['name'], v['link']))
        nResult[v['name']] = []
        r = session_get(session, v['link']) # 自带重新请求的函数
        r_html_render(r) # 自带重新渲染页面的函数
        for li in r.html.find(v['el']['list']):
            title = li.find(v['el']['title'])
            time = li.find(v['el']['time'])

            if len(title) == 0 and len(time) == 0: # 当网页改版，两个都找不到时，使用旧的数据或者[]
                log('无效的title与time对象选择器')
                nResult[v['name']] = result[v['name']] if (v['name'] in result) else []
                break

            nResult[v['name']].append({
                'title': title[0].text if len(title) > 0 else '',
                'time': time[0].text if len(time) > 0 else ''
            })
        log('请求成功')

    session.close()


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
        # style = '<style>'

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
            log('发送成功')
        else:
            log('发送失败')
    else:
        log('未发现更新')


def saveResult():
    global setting, nResult
    with open(setting['result'], 'w', encoding='utf-8') as f:
        json.dump(nResult, f, ensure_ascii=False)


def log(msg):
    global logMsg
    log = '{} {}'.format(time.strftime("%Y/%m/%d %H:%M:%S"), msg)
    print(log)
    logMsg.append(log)


# 退出前执行
@atexit.register
def logToLocal():
    global logMsg
    with open(setting['log'], 'w', encoding='utf-8') as f:
        f.write('\n'.join(logMsg))


def main():
    loadSetting('setting.json')
    loadLastResult()
    requests()
    compare()
    saveResult()


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        log(e)
