# *_*coding:utf-8 *_*
"""
修改yourtoken,number
number表示从第number页开始爬取，为5的倍数，从0开始。如0、5、10……
token可以使用Chrome自带的工具进行获取
fakeid是公众号独一无二的一个id，等同于后面的__biz
"""
import re
import time
import requests
from lxml import etree
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Spider(object):
    def __init__(self):
        self.username = '774827740@qq.com'
        self.pass_wd = 'seCy3ai4HGpgtpX'
        self.search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz'
        self.list_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
        cookie, token = self.get_cookies()
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        }
        self.token = token
        self.headers2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate',
            # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 'Cache-Control': 'max-age=0',
            # 'Connection': 'keep-alive',
            # 'Upgrade-Insecure-Requests': '1',

        }

    def search(self):
        query_list = ["远方青木", "网易新闻", "hisdhs"]
        for query in query_list:
            data = {
                "token": self.token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": "1",
                "query": query,
                "begin": '0',
                "count": "5"
            }
            content_json = requests.get(self.search_url, headers=self.headers, params=data).json()
            print(content_json)
            lis = []
            try:
                for nik in content_json["list"]:
                    lis.append(nik["nickname"])
            except KeyError:
                print("cookie失效")
            if query in lis:
                for index, m in enumerate(lis):
                    if m == query:
                        fake_id = content_json["list"][int(index)]["fakeid"]
                        print(m)
                        self.get_list(fake_id)
            else:
                print("该公众号名称或者公众号账号有误" + query)

    def get_list(self, fake_id):
        data = {
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "action": "list_ex",
            "begin": '0',
            "count": "5",
            "query": "",
            "fakeid": fake_id,
            "type": "9",
        }
        content_json = requests.get(self.list_url, headers=self.headers, params=data).json()
        time.sleep(5)
        for item in content_json["app_msg_list"]:
            print(item["title"], item["link"])
            # self.parse(item["link"])

    def parse(self, url):
        response = requests.get(url=url, headers=self.headers2)
        time.sleep(3)
        html4 = etree.HTML(response.content)
        lis = html4.xpath("//span[@id='profileBt']/a/text()")[0]
        title_lis = html4.xpath("//h2[@id='activity-name']/text()")
        if title_lis:
            title = title_lis[0]
        else:
            title = ""
        pub_timess = re.findall(r'n="(\d+)"', response.text)
        if pub_timess:
            pub_time = time.strftime('%Y-%m-%dT%H:%M:%S',
                                     time.localtime(time.time()))
        else:
            pub_times = time.localtime(int(pub_timess[0]))
            pub_time = time.strftime('%Y-%m-%dT%H:%M:%S', pub_times)
        soup = BeautifulSoup(response.content, "lxml")
        author = re.findall(r'user_name = "(.*?)";', response.text)
        if author:
            autho = author[0]
        else:
            autho = ''
        keywords = re.findall(r'var msg_desc = "(.*?)";', response.text)
        if keywords:
            keyword = keywords[0]
        else:
            keyword = ''
        contents = soup.find_all(attrs={
            "class": "rich_media_content "})
        if contents:
            content = contents[0]
        else:
            content = ''
        create_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(
            time.time())) + ".3059557+08:00"
        print(lis, url, title, autho, pub_time, keyword)

    def get_cookies(self):
        # chromedriver = r"C:\个人\软件\Google\Google\Chrome\Application\chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # browser = webdriver.Chrome(chromedriver)
        browser = webdriver.Chrome()
        browser.get('https://mp.weixin.qq.com/')
        input_name = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#header > div.banner > div > div > form > div.login_input_panel > div:nth-child(1) > div > span > input"))
        )
        input_name.send_keys(self.username)
        input_pass = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#header > div.banner > div > div > form > div.login_input_panel > div:nth-child(2) > div > span > input"))
        )
        input_pass.send_keys(self.pass_wd)
        button = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#header > div.banner > div > div > form > div.login_btn_panel > a"))
        )
        button.click()

        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#app > div.weui-desktop-layout__main__bd > div > div.js_scan.weui-desktop-qrcheck > div.weui-desktop-qrcheck__qrcode-area > div > img"))
        )
        browser.get_screenshot_as_file(os.getcwd() + '\\img.png')
        WebDriverWait(browser, 300000).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              "#app > div.weui-desktop-layout__main__bd > div > div.js_scan.weui-desktop-qrcheck > div.weui-desktop-qrcheck__qrcode-area > div > img"))
        )
        a = ''
        for i in browser.get_cookies():
            cookie_string = i["name"] + "=" + i["value"]
            a += cookie_string + ';'
        cookies = a.rstrip(';')
        token = browser.current_url.split('token=')[1]
        print(cookies, token)
        return cookies, token


if __name__ == '__main__':
    a = Spider()
    a.search()
