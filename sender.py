# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr


def send_mail_html(host, port, nick, from_addr, tokens, to_addr, title, body):
    msg = MIMEText(body, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(title, 'utf-8')
    nick, from_addr = parseaddr('{} <{}>'.format(nick, from_addr))
    msg['From'] = formataddr((Header(nick, 'utf-8').encode(), from_addr))

    try:
        smtp = smtplib.SMTP_SSL(host, port)
        smtp.login(from_addr, tokens)
        smtp.sendmail(from_addr, to_addr, msg.as_string())
    except Exception as e:
        smtp.quit()
        print(e)
        return False
    else:
        smtp.quit()
        return True

