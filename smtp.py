import datetime
import json
import logging
import os
import re
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import requests

ip_cache = '/ip_cache.log'
log_file = 'get_ip.log'

logger = logging.getLogger('ip-logger')
file_log = logging.FileHandler(log_file, encoding='utf-8')
fmt = "%(asctime)s || %(levelname)s || %(message)s"
datefmt = "%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
file_log.setFormatter(formatter)

logger.setLevel(logging.DEBUG)
logger.addHandler(file_log)


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail(outer_ip):
    from_addr = 'maicss_mk@163.com'
    password = 'xxxxxx'
    to_addr = 'maicss@foxmail.com'
    smtp_server = 'smtp.163.com'
    
    html = '<!doctype html><html><body><p>日期：<span style="padding: 10px; background-color: #ccc; border-radius: 4px; margin-top: 10px;">'
    html += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html += '</span></p>'
    html += '<p>树莓派IP: <input style="padding: 8px; background-color: #ccc; border-radius: 4px; border-width: 0;" value='
    html += outer_ip
    html += '></p></html></body>'
    
    msg = MIMEText(html, 'html', 'utf-8')
    msg['From'] = _format_addr('163mail <%s>' % from_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_addr)
    msg['Subject'] = Header('树莓派IP', 'utf-8').encode()
    
    server = smtplib.SMTP(smtp_server, 25)
    try:
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        logger.info('send mail success.')
    except smtplib.SMTPException as e:
        logger.error(e)
    server.quit()


def get_ip_by_tplink():
    home_url = 'http://192.168.1.1/'
    
    auth_param = {"method": "do", "login": {"password": "W10Xw6w2KTefbwK"}}
    
    r = requests.post(home_url, data=json.dumps(auth_param)).json()
    data_param = {"network": {"name": "wan_status"},
                  "cloud_config": {"name": ["new_firmware", "device_status", "bind"]},
                  "wireless": {"name": "wlan_wds_2g"}, "method": "get"}
    if r['error_code'] == 0:
        stok = r['stok']
        data_url = home_url + '/stok=' + stok + '/ds'
        r_inner = requests.post(data_url, json.dumps(data_param)).json()
        
        if r_inner['error_code'] == 0:
            return r_inner['network']['wan_status']['ipaddr']


def is_connect():
    for i in range(10):
        try:
            if requests.get('http://www.baidu.com').status_code == 200:
                return True
            else:
                continue
        except requests.ConnectionError as e:
            logger.error(e)
        time.sleep(1)
    return False


# def get_ip_socket():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("100.1.1.1", 80))
#     ipaddr = s.getsockname()[0]
#     s.close()
#     return ipaddr


def get_ip_re():
    url_list = ['http://www.ip.cn/', 'http://www.123cha.com/', 'http://ip111.cn/', 'http://ip.51240.com/',
                'http://www.j4.com.tw/james/remoip/']
    for i in url_list:
        try:
            r = requests.get(i, timeout=10)
            if r.status_code == 200:
                ip = re.search(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)', r.text).group()
                if ip is not None:
                    return ip
                else:
                    continue
        except requests.ConnectionError as e1:
            logger.error(e1)
            continue
    return None


if __name__ == "__main__":
    
    path = current_dir = os.getcwd()
    cached_ip = ''
    
    if is_connect():
        try:
            ip = get_ip_re()
            logger.info('get ip: %s success.' % ip)
            if os.path.isfile(path + ip_cache):
                with open(path + ip_cache, 'r+') as f:
                    cached_ip = f.read()
                    if cached_ip != ip:
                        send_mail(ip)
                        f.seek(0)
                        f.write(ip)
                        f.truncate()
            else:
                with open(path + ip_cache, 'w') as f:
                    f.write(ip)
                send_mail(ip)
        
        except Exception as e:
            logger.error(e)
