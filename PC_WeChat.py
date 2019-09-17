import re
import time
import json
import win32gui
import win32con
import requests
import win32clipboard
from lxml import etree
from pymouse import PyMouse
from bs4 import BeautifulSoup


class PyMouseWeChat(object):

    def __init__(self):
        self.headers = {
            'Host': 'mp.weixin.qq.com',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'

        }

    # 点击单个公众号
    def click_public_number(self):
        time.sleep(5)
        # 获取句柄
        handle = win32gui.FindWindow('WeChatMainWndForPC', '微信')
        left, top, right, bottom = win32gui.GetWindowRect(handle)
        x = int(left) + 421
        y = int(top) + 126
        # 左右80 上下110
        m = PyMouse()
        for u in range(2):  # 共有几排
            for i in range(21):  # 一排共有几个
                xx = x + i * 80
                yy = y + u * 110
                m.click(xx, yy, 1)  # (1163, 387)
                self.click_history()

    # 点击查看历史
    def click_history(self):
        time.sleep(1)
        handle2 = win32gui.FindWindow('ContactProfileWnd', '微信')
        # handle2 = win32gui.GetForegroundWindow()
        left1, top1, right1, bottom1 = win32gui.GetWindowRect(handle2)
        x = int(left1) + 208
        y = int(bottom1) - 41
        m = PyMouse()
        m.click(x, y, 1)
        time.sleep(3)
        self.click_detail()

    # 点击详情
    def click_detail(self):
        m = PyMouse()
        for i in range(3):
            y = 360 + i * 106
            x = 139
            m.click(x, y, 1)
            time.sleep(5)
            self.get_fidder()
            # 点击后退按钮
            m.click(35, 50, 1)
            time.sleep(2)
        # self.close_browser()
        m.click(1906, 15, 1)
        time.sleep(5)
        # m.click(562, 1060, 1)
        # time.sleep(1)

    # 下拉历史列表,并回拉
    def drop_browser(self):
        m = PyMouse()
        for i in range(15):
            m.click(1356, 725, 1)
        time.sleep(10)
        for i in range(15):
            m.click(1356, 80, 1)
        time.sleep(10)

    # 关闭微信浏览器
    def close_browser(self):
        m = PyMouse()
        m.click(1906, 15, 1)
        time.sleep(5)
        m.click(562, 1060, 1)
        time.sleep(1)

    # 从Fidder中复制url
    def get_fidder(self):
        m = PyMouse()
        m.click(611, 1060, 1)
        time.sleep(1)
        m.click(192, 102, 2)
        time.sleep(1)
        m.move(336, 170)
        time.sleep(1)
        m.click(671, 169, 1)
        time.sleep(1)
        m.click(1807, 12, 1)
        time.sleep(2)
        # m.click(186, 55, 1)
        # time.sleep(1)
        # m.click(234, 77, 1)
        url = self.paste()
        self.parse(url)

    # 粘贴url
    def paste(self):
        win32clipboard.OpenClipboard()
        copy_text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
        win32clipboard.CloseClipboard()
        copy_texts = copy_text.decode("utf-8")
        return copy_texts

    def parse(self, url):
        s = requests.session()
        s.headers.update(self.headers)
        response = s.get(url=url)
        # 内容
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
        # create_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(
        #     time.time())) + ".3059557+08:00"
        print(lis, url, title, autho, pub_time, keyword)
        # key
        appmsg_token = re.findall(r'window.appmsg_token = "(.*?)"', response.text)[0]
        uin = re.findall(r'''window.uin = params..uin.. .. "(.*?)" .. '';''', response.text)[0]
        key = re.findall(r'''window.key = params..key.. .. "(.*?)" .. '';''', response.text)[0]
        biz = re.findall(r'''var biz = "(.*?)".."";''', response.text)[0]
        sn = re.findall(r'''var sn = "(.*?)" .. "".. "";''', response.text)[0]
        mid = re.findall(r'''var mid = "(.*?)" .. "".. "";''', response.text)[0]
        title = re.findall(r'''var msg_title = "(.*?)";''', response.text)[0]
        tim = re.findall(r'''n="(\d+)"''', response.text)[0]
        com_id = re.findall(r'''var comment_id = "(\d+)" ..''', response.text)[0]
        rep_id = re.findall(r'''var req_id = '(.*?)';''', response.text)[0]
        appmsg_type = re.findall(r'''var appmsg_type = "(\d+)";''', response.text)[0]
        idx = re.findall(r'''var idx = "(\d+)" .. "" .. "";''', response.text)[0]
        comment_id = re.findall(r'''var comment_id = "(.*?)" ..''', response.text)[0]
        # 从生成的cookies中提取
        pass_tickt = s.cookies.get("pass_ticket")
        # 浏览数，点赞数url
        post_url = 'https://mp.weixin.qq.com/mp/getappmsgext?f=json&mock=&uin=' + uin + '&key=' + key + '&pass_ticket=' + pass_tickt + '&wxtoken=777&devicetype=Windows%26nbsp%3B10&clientversion=62060833&appmsg_token=' + appmsg_token + '&x5=0&f=json'
        data = {
            # 'r':'0.25275220375435326',
            '__biz': biz,
            'appmsg_type': appmsg_type,
            'mid': mid,
            'sn': sn,
            'idx': idx,
            'scene': '0',
            'title': title,
            'ct': tim,
            'abtest_cookie': '',
            'devicetype': 'Windows%2010',
            'version': '62060833',
            'is_need_ticket': '0',
            'is_need_ad': '0',
            'comment_id': com_id,
            'is_need_reward': '0',
            'both_ad': '0',
            'reward_uin_count': '0',
            'send_time': '',
            'msg_daily_idx': '1',
            'is_original': '0',
            'is_only_read': '1',
            'req_id': rep_id,
            'pass_ticket': pass_tickt,
            'is_temp_url': '0',
            'item_show_type': '0',
            'tmp_version': '1',
            'more_read_type': '0',
            'appmsg_like_type': '2'
        }
        p_content = requests.post(url=post_url, headers=self.headers, data=data)
        p_c = json.loads(p_content.text)
        comment_count = p_c["comment_count"]
        read_num = p_c["appmsgstat"]["read_num"]
        like_num = p_c["appmsgstat"]["like_num"]
        print(comment_count, read_num, like_num)
        # 获取评论
        comment_url = 'https://mp.weixin.qq.com/mp/appmsg_comment?action=getcomment&scene=0&__biz=' + biz + '&appmsgid=' + mid + '&idx=1&comment_id=' + comment_id + '&offset=0&limit=100&uin=' + uin + '&key=' + key + '&pass_ticket=' + pass_tickt + '&wxtoken=777&devicetype=Windows%26nbsp%3B10&clientversion=62060833&appmsg_token=' + appmsg_token + '&x5=0&f=json'
        comment_content = requests.get(url=comment_url)

        c_c = json.loads(comment_content.text)["elected_comment"]
        for i in c_c:
            c_nick_name = i["nick_name"]
            c_content = i["content"]
            c_create_time = i["create_time"]
            c_content_id = i["content_id"]
            c_like_num = i["like_num"]
            print(c_nick_name, c_content, c_create_time, c_content_id, c_like_num)


if __name__ == '__main__':
    spider = PyMouseWeChat()
    spider.click_public_number()
