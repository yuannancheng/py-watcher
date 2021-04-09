# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_mail_html(host, port, nick, from_addr, tokens, to_addr, title, body):
    msg = MIMEText(body, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(title, 'utf-8')
    h = Header(nick, 'utf-8')
    h.append(from_addr, 'ascii')
    msg['From'] = h

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

