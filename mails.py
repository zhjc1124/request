import requests
import json
from PIL import Image
import pymysql.cursors
from pytesseract import image_to_string
from random import randint
import re
import time
connect_data = open("user.txt")
data = connect_data.read().split('\n')
connections = pymysql.connect(host=data[0], user=data[1], password=data[2], database='studentip', charset=data[3])

# 从ip范围得到ip
ip_addresses = []


with open('ip_addresses.txt', 'r') as f:
    for interval in f.readlines():
        floor, ceiling = interval.split('-')
        floor = floor.split()[0].split('.')
        ceiling = ceiling.split()[0].split('.')
        for i in range(int(floor[2]), int(ceiling[2])+1):
            for j in range(int(floor[3]), int(ceiling[3])+1):
                ip = '.'.join(floor[:2]+[str(i), str(j)])
                ip_addresses.append(ip)
print(len(ip_addresses))

with connections.cursor() as cursor:
    cursor.execute('select ip from valid')
    _ = cursor.fetchall()
    ip_addresses = [j for j in ip_addresses if j not in [i[0] for i in _]]
    print(len(ip_addresses))
    cursor.execute('select ip from noknown')
    _ = cursor.fetchall()
    ip_addresses = [j for j in ip_addresses if j not in [i[0] for i in _]]
    print(len(ip_addresses))
    cursor.execute('select ip from nope')
    _ = cursor.fetchall()
    ip_addresses = [j for j in ip_addresses if j not in [i[0] for i in _]]
    print(len(ip_addresses))
    cursor.execute('select ip from unable')
    _ = cursor.fetchall()
    ip_addresses = [j for j in ip_addresses if j not in [i[0] for i in _]]
    print(len(ip_addresses))

flag = 0
# login
card = '20150108849'
pwd = '109308'
while True:
    flag = 0
    time.sleep(10)
    try:
        session1 = requests.Session()
        # 获取验证码和phpsession
        safecode_url = r'https://ip.jlu.edu.cn/pay/img_safecode.php'
        response = session1.get(safecode_url)
        phpsession = list(response.cookies)[0].value
        with open('code.gif', 'wb') as f:
            f.write(response.content)
        safecode = image_to_string(Image.open('code.gif'), config='-psm 7 digits')
        print(safecode)
        login_url = r'https://ip.jlu.edu.cn/pay/index.php?'
        login_data = 'menu=chklogin&card=' + card + '&pwd=' + pwd + '&imgcode=' + safecode + '&x=' + str(
            randint(1, 43)) + '&y=' + str(randint(1, 23))
        login_data = login_data.encode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://ip.jlu.edu.cn/pay/index.php?menu=logout',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Content-Length': str(len(login_data)),
            'Cookie': 'PHPSESSID=' + phpsession,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = session1.post(login_url, data=login_data, headers=headers, verify=False)
        if '验证码有误' in response.content.decode('gbk'):
            continue


        headers.pop('Content-Length')
        headers.pop('Content-Type')
        headers['Referer'] = login_url
        response = session1.get('https://ip.jlu.edu.cn/pay/index.php', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/index.php'
        response = session1.get('https://ip.jlu.edu.cn/pay/index.php?menu=menu', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/index.php?menu=menu'
        response = session1.get('https://ip.jlu.edu.cn/pay/guanlian.php', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/guanlian.php'
        response = session1.get('https://ip.jlu.edu.cn/pay/guanlian.php?menu=add_ip', headers=headers, verify=False)
        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/guanlian.php?menu=add_ip'
        # 查询2000次后重新打开会话
        while flag < 1000:
            flag = flag + 1
            ip = ip_addresses[0]

            post_url = 'https://ip.jlu.edu.cn/pay/guanlian.php?'
            post_data = 'menu=save_add_ip&ip=' + ip + '&mail=zhangjc2015%40mails.jlu.edu.cn'
            post_data = post_data.encode()
            headers['Content-Length'] = str(len(post_data))
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            response = session1.post(post_url, data=post_data, headers=headers, verify=False)
            pattern = re.compile(r'<script>alert\((.*?)</script>')
            result = response.content.decode('gbk')

            info = pattern.findall(result)[0]
            print(ip, info)
            if '页面超时' in info:
                break
            elif '不存在' in info:
                with connections.cursor() as cursor:
                    cursor.execute('insert into nope values(%s);', ip)
                    connections.commit()
            elif '姓名不符' in info:
                with connections.cursor() as cursor:
                    cursor.execute('insert into unable values(%s);', ip)
                    connections.commit()
            elif '@' in info:
                pattern = re.compile(r'：(.*?)@')
                mail = pattern.findall(info)
                if mail:
                    mail = mail[0]
                    print(mail)
                    with connections.cursor() as cursor:
                        cursor.execute('insert into valid values(%s,%s);', (ip, mail))
                        connections.commit()
                else:
                    with connections.cursor() as cursor:
                        cursor.execute('insert into noknown values(%s);', ip)
                        connections.commit()
            ip_addresses.pop(0)
    except Exception as e:
        ip_addresses.append(ip_addresses.pop(0))
        print(e)
        session1.close()
        time.sleep(20)

