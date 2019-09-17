# -*-coding:utf-8-*-
import time
import re
import requests
import schedule
import pika
import xlrd
import json
from lxml import etree
from bs4 import BeautifulSoup
from urllib import parse


class WeChatSpider(object):

    def __init__(self):
        # 微信公众号excel表
        self.execl_path = r'C:\个人\软件\微信公众号.xlsx'
        self.headers = {
            #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',

        }

    def read(self):
        excel_file = xlrd.open_workbook(self.execl_path)
        sheet = excel_file.sheet_by_index(0)
        colss = sheet.col_values(0)
        cols = colss[1:]
        return cols

    def get_ip(self):
        # 代理IP接口
        tar_url = 'https://api.2808proxy.com/proxy/unify/get?token=N6SORZ6Y3GGMPUN9C1L3YCK0WMEB26WO&amount=1&proxy_type=http&format=json&splitter=rn&expire=300'
        text = requests.get(url=tar_url).text
        ip_s = json.loads(text)
        dic = {}
        ip_a = ip_s["data"][0]["ip"] + ':' + str(ip_s["data"][0]["http_port"])
        dic["https"] = ip_a
        return dic

    def check_ip(self, status, prox):
        if status == ['您的访问出错了']:
            proxi = self.get_ip()
        else:
            proxi = prox
        return proxi

    def parse(self):
        # 搜索流程
        proxi = self.get_ip()  # 获取代理IP
        lists = self.read()
        for lis in lists:
            dic = parse.quote(lis)
            url_s = 'https://weixin.sogou.com/weixin?type=1&s_from=input&query=' + dic + '&ie=utf8&_sug_=n&_sug_type_='
            s = requests.session()
            s.headers.update(self.headers)
            s.headers.update({'Referer': url_s})
            # 根据公众号名称搜索
            response = s.get(url=url_s, proxies = proxi).content.decode('utf-8')
            html = etree.HTML(response)
            # 判断是否被封
            status = html.xpath("//div[@class='other']/span[@class='s1']/text()")
            # proxi = self.check_ip(status, proxi)
            print(status)  # ['您的访问出错了']
            try:
                acc_url = "https://weixin.sogou.com" + html.xpath("//a[@uigs='account_name_0']/@href")[0].replace("amp;", "") + "&k=12&h=I"
            except IndexError:
                print(lis + "该公众号不存在")
                continue
            s.headers.update({"Referer": url_s})
            # 获取公众号url
            response2 = s.get(url=acc_url, proxies = proxi).content
            html2 = etree.HTML(response2)
            acount_url = html2.xpath("//script/text()")[0].split('url.replace("@", "")')[0].replace("var url = '';","").replace("url += '","").replace("';","").replace("window.location.replace(url)","").replace(' ','').replace('\r','').replace('\n','')
            s.headers.update({"Referer": acc_url})
            s.headers.update({"Cache-Control":None})
            # 请求公众号url获取key值
            resss = s.get(url=acount_url, proxies = proxi)
            response3 = resss.text
            # html3 = etree.HTML(resss.content)
            # # 判断是否被封
            # status2 = html3.xpath(
            #     "//div[@class='other']/span[@class='s1']/text()")
            # if status2 == ['您的访问出错了']:
            #     proxi = self.get_ip(ip_lists)
            #     print(proxi)
            #     resss = s.get(acount_url, proxies=proxi)
            #     response3 = resss.text
            sc = re.findall(r'"content_url":"(.*?)",',response3)
            author = re.findall(r'"author":"(.*?)",', response3)
            keywords = re.findall(r'"digest":"(.*?)",', response3)
            s.headers.update({"Referer": acount_url})
            for i in range(len(sc)):
                detail_url = 'https://mp.weixin.qq.com' + sc[i].replace('amp;', '')
                # 进入详情
                response4 = s.get(url=detail_url, proxies = proxi)
                html4 = etree.HTML(response4.content)
                title_lis = html4.xpath("//h2[@id='activity-name']/text()")
                if title_lis:
                    title = ""
                else:
                    title = title_lis[0]
                try:
                    pub_timess = re.findall(r'n="(\d+)"', response4.text)[0]
                    pub_times = time.localtime(int(pub_timess))
                    pub_time = time.strftime('%Y-%m-%dT%H:%M:%S', pub_times)
                    soup = BeautifulSoup(response4.content, "lxml")
                    content = soup.find_all(attrs={
                        "class": "rich_media_content "})[0]
                except IndexError as e:
                    pub_time = ''
                    content = ''
                    print(response4.content.decode("utf-8"))
                autho = author[i]
                keyword = keywords[i]
                create_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(
                    time.time())) + ".3059557+08:00"
                print(lis, detail_url, title, autho, pub_time, keyword, content)
            print(lis)
            time.sleep(10)


if __name__ == '__main__':
    spider = WeChatSpider()
    spider.parse()
    schedule.every(60).minutes.do(spider.parse)
    while True:
        print("准备再次执行！！！"+time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time())))
        schedule.run_pending()
        time.sleep(10)
