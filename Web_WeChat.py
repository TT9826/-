# -*-coding:utf-8-*-
import pika
import re
import os
import time
import requests
import schedule
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


class WeChatDriver(object):

    def __init__(self):
        # chromedriver = r"C:\个人\软件\Google\Google\Chrome\Application\chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # self.browser = webdriver.Chrome(chromedriver)
        self.browser = webdriver.Chrome()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',

        }

    def login(self):
        self.browser.get('https://wx.qq.com/?&lang=zh_CN')
        WebDriverWait(self.browser, 240).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                            "body > div.login.ng-scope > div.login_box > div.qrcode > img"))
        )
        time.sleep(10)
        self.click_button()

    def click_button(self):
        user_button = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "body > div.main > div > div.panel.give_me > div.tab > div.tab_item.ng-scope > a > i"))
        )
        ActionChains(self.browser).double_click(user_button).perform()
        html = self.browser.page_source
        response = etree.HTML(html)
        lis = response.xpath("//div[@ng-repeat='readItem in articleList']")
        lists = self.click_detail(lis)
        self.parse(lists)

    def click_detail(self, lis):
        lists = []
        for i in range(len(lis)):
            num = str(i + 2)
            string = "#J_NavReadScrollBody > div > div:nth-child(" + num + ") > div > div.cont > h3"
            try:
                cons = WebDriverWait(self.browser, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, string))
                )
                # cons = browser.find_element_by_xpath(AAstrs)
                ActionChains(self.browser).double_click(cons).perform()
                html2 = self.browser.page_source
                response2 = etree.HTML(html2)
                url = response2.xpath("//div[@class='box_bd']/iframe/@ng-src")[0]
                lists.append(url)
                # self.parse(lists)
            # 跳过详情上的栏目
            except TimeoutException:
                print("timeouterror")
        return lists

    def parse(self, lists):
        for url in lists:
            response = requests.get(url=url, headers=self.headers)
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
            print(url)
            print(lis, url, title, autho, pub_time, keyword)
            # self.check_dic('', '', lis, url, title, autho, pub_time,
            #                keyword, '', content, '', '', create_time, '')

    def refresh(self):
        self.browser.refresh()
        # webdriver.ActionChains(self.browser).key_down(Keys.F5).perform()
        time.sleep(2)
        # webdriver.ActionChains(self.browser).key_down(Keys.ENTER).perform()
        self.browser.switch_to.alert.accept()
        self.click_button()


if __name__ == '__main__':
    spider = WeChatDriver()
    spider.login()
    schedule.every(1).minutes.do(spider.refresh)
    while True:
        print("准备再次执行！！！" + time.strftime('%Y-%m-%dT%H:%M:%S',
                                          time.localtime(time.time())))
        schedule.run_pending()
        time.sleep(10)