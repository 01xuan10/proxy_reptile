import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import csv
import time
import datetime

def agent(protocol, filename):
    row0 = []  # row0用于保存上一行的信息
    ip_add_list = []
    port_list = []
    for i in range(1, 20):
        url = 'https://www.freeip.top/?page=%s&protocol=%s' % (i, protocol)
        # print(url)
        resp = requests.get(url)
        print('\r', "正在爬取第%s页" % i, end = '', flush=True)

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        # names = soup.find_all('table', class_="layui-table")
        # value = names.find('data-url')
        a = soup.tbody.children
        reg = re.compile(("<[^>]*>"))  # 清除html标签,提取文本

        flag = True  # row0未初始化
        for child in a:
            value1 = str(child).split('<td>')
            ip_add = str(value1[1]).split('</td>', 1)[0]
            value2 = str(child).split('<td>')
            port = str(value2[2]).split('</td>', 1)[0]
            end = protocol + '://' + ip_add + ':' + port
            row0.append(end)
            ip_add_list.append(ip_add)
            port_list.append(port)
    start_agent_count = str(len(port_list))
    print()
    print('共爬取%s条%s代理服务器数据' % (start_agent_count, protocol))
    agent = np.array((ip_add_list, port_list, row0)).T

    with open(filename, 'w', newline='') as f:
        # 使用csv写入文件as.csv中
        csvwriter = csv.writer(f)
        # 将融合后的数据写入csv对象
        csvwriter.writerows(agent)
    return start_agent_count

def test(protocol, filename, start_agent_count):
    enable_list = []
    url = '%s://httpbin.org/ip' % protocol
    f = csv.reader(open(filename, 'r'))
    total = 0
    success = 0

    for i in f:
        total += 1
        try:
            proxy = {protocol: i[2]}

            resp = requests.get(url, proxies=proxy, allow_redirects=False, timeout=5)
            # print(resp.text)
            if len(resp.text) < 100:
                enable_list.append(i)
                success += 1
                print('\r', "正在验证第%s个，还剩%s个未验证，可用%s个" % (total, int(start_agent_count) - total, success), end = '', flush=True)
            # time.sleep(2)
        except requests.exceptions.ProxyError as n:
            # print('%s不可用' % i[2])
            pass
        except requests.exceptions.ReadTimeout as m:
            # print('%s超过规定时间无响应' % i[2])
            pass
        except requests.exceptions.ConnectTimeout as l:
            # print('%s连接超时' % i[2])
            pass
        except requests.exceptions.ConnectionError as o:
            pass
    enale_filename = '/var/www/html/%s.csv' % protocol
    with open(enale_filename, 'w', newline='') as a:
        csvwrite = csv.writer(a)
        csvwrite.writerows(enable_list)
        # print("验证%s个，%s个可用" % (total, len(enable_list)))
        print()
        print('共验证%s个%s协议代理服务器，可用%s个' % (total, protocol, success))
    # with open('http.csv', 'r') as f:
    #     reader = csv.reader(f)
    #     print(type(reader))
    # for row in reader:
    #     print(row)


if __name__ == '__main__':
    start_time = time.time()
    time_show = datetime.datetime.fromtimestamp(int(str(start_time).split('.', 1)[0]))
    print('运行时间%s' % time_show)
    a = agent('http', 'temp_http.csv')
    b = agent('https', 'temp_https.csv')
    test('http', 'temp_http.csv', a)
    test('https', 'temp_https.csv', b)
    end_time = time.time()
    run_time = int(str(end_time - start_time).split('.', 1)[0])
    h = run_time // 3600
    m = (run_time - h * 3600) // 60
    s = run_time - (h * 3600 + m * 60)
    print("程序运行时间 %s时:%s分:%s秒" % (h, m, s))
