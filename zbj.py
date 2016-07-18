# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import urllib
from BeautifulSoup import BeautifulSoup
import MySQLdb

conn = MySQLdb.connect(host="localhost", user="root", passwd="bobobo", db="zbj")
cur = conn.cursor()

urlprefix = "http://task.zbj.com/t-tuiguang/p"
pagenum = 1
urlsuffix = "s5.html"

while True:
    url = urlprefix + str(pagenum) + urlsuffix
    print url
    page = urllib.urlopen(url).read()
    if page.find("抱歉，没有找到您需要的内容！") > 0:
        break;
    soup = BeautifulSoup(page)
    task_list = soup.findAll("table", attrs={"class":"list-task"})[0]
    trs = task_list.findAll("tr")
    for tr in trs:
        total_price = tr.find("em", attrs={"class":"list-task-reward"}).text
        if total_price.find("可议价") >= 0:
            total_price = -1
        else:
            total_price = float(total_price.split(" ")[1])

        title_tag = tr.find("a", attrs = {"class":"list-task-title"})
        title = title_tag.get("title")
        link = title_tag.get("href")
        id = link.split("/")[3]

        unit_tag = tr.find("p", attrs = {"class":"normal-p zb-per-contri"})
        if unit_tag is None:
            unit_price = -1
            unit_name = ""
        else:
            unit_price = float(unit_tag.text.split("/")[0][1:])
            unit_name = unit_tag.text.split("/")[1]

        num_bids_tag = tr.find("a", attrs={"class":"blue"})
        num_bids = int(num_bids_tag.text)

        cur.execute("SELECT id FROM tuiguang WHERE id = %s", (id,))
        if cur.fetchone() is None:
            cur.execute('''INSERT INTO tuiguang (id, title, total_price, unit_price, unit_name, num_bids, link)
            VALUES (%s, %s,%s,%s,%s,%s,%s)''', (id, title, total_price, unit_price, unit_name, num_bids, link))
            conn.commit()
    pagenum += 1
    time.sleep(10)
