import requests
from PIL import Image
from pytesseract import image_to_string
from random import randint
import re
import time

# 从ip范围得到ip


def ip_generator():
    with open('ip_addresses.txt', 'r') as f:
        for interval in f.readlines():
            floor, ceiling = interval.split('-')
            floor = floor.split()[0].split('.')
            ceiling = ceiling.split()[0].split('.')
            for i in range(int(floor[2]), int(ceiling[2])+1):
                for j in range(int(floor[3]), int(ceiling[3])+1):
                    ip = '.'.join(floor[:2]+[str(i), str(j)])
                    yield ip
inters = ip_generator()
flag = 0
# login
card = '+++++++++++'
pwd = '》》》》》》》》'
while True:
    flag = 0
    time.sleep(10)
    try:
        session = requests.Session()
        # 获取验证码和phpsession
        safecode_url = r'https://ip.jlu.edu.cn/pay/img_safecode.php'
        response = session.get(safecode_url)
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
        response = session.post(login_url, data=login_data, headers=headers, verify=False)
        if '验证码有误' in response.content.decode('gbk'):
            continue
        headers.pop('Content-Length')
        headers.pop('Content-Type')
        headers['Referer'] = login_url
        response = session.get('https://ip.jlu.edu.cn/pay/index.php', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/index.php'
        response = session.get('https://ip.jlu.edu.cn/pay/index.php?menu=menu', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/index.php?menu=menu'
        response = session.get('https://ip.jlu.edu.cn/pay/guanlian.php', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/guanlian.php'
        response = session.get('https://ip.jlu.edu.cn/pay/guanlian.php?menu=add_ip', headers=headers, verify=False)

        headers['Referer'] = 'https://ip.jlu.edu.cn/pay/guanlian.php?menu=add_ip'
        # 查询2000次后重新打开会话
        while flag < 2000:
            flag = flag + 1
            ip = next(inters)
            print(ip)
            post_url = 'https://ip.jlu.edu.cn/pay/guanlian.php?'
            post_data = 'menu=save_add_ip&ip=' + ip + '&mail=chenzhuo2016%40mails.jlu.edu.cn'
            post_data = post_data.encode()
            headers['Content-Length'] = str(len(post_data))
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            response = session.post(post_url, data=post_data, headers=headers, verify=False)
            pattern = re.compile(r'：(.*?)@mails')
            result = response.content.decode('gbk')

            mail = pattern.findall(result)

            if mail:
                f = open('c.txt', 'a+')
                f.write(mail[0] + '\t' + ip + '\n')
                f.close()
                print('%s----------------------------------------------------' % mail[0])
    except Exception:
        print('*'*20)


