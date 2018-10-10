# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 16:15:06 2018

@author: wmy
"""

import random
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium import webdriver
from bs4 import BeautifulSoup
import PIL.Image as image
import re
import matplotlib.pyplot as plt

class Crack():
    
    def __init__(self):
        '''初始化参数'''
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome()
        self.username = '18994091839'
        self.password = '106336213wmy'
        self.wait = WebDriverWait(self.browser, 100)
        self.border = 7
        self.have_logged_in = False
        pass
    
    def open_webpage(self):
        '''用chromedriver打开网页'''
        self.browser.get(self.url)
        pass
    
    def login_bilibili(self):
        '''输入登陆的账户和密码'''
        # 找到用户行
        user_element = self.browser.find_element_by_xpath("//li[@class='item username status-box']/input")
        # 找到密码行
        pawd_element = self.browser.find_element_by_xpath("//li[@class='item password status-box']/input")
        user_element.clear()
        for i in range(len(self.username)):     
            user_element.send_keys(self.username[i])
            time.sleep(0.1)
            pass
        print('用户名输入完成')
        pawd_element.clear()
        for i in range(len(self.password)):   
            pawd_element.send_keys(self.password[i])
            time.sleep(0.1)
            pass
        print('密码输入完成')
        pass
    
    def get_identifying_images(self, gapbg_filename='gapbg.jpg', fullbg_filename='fullbg.jpg', show_images=False):
        '''获取验证码图片'''
        gapbg = []
        fullbg = []
        # 储存文件名
        self.gapbg_filename = gapbg_filename
        self.fullbg_filename = fullbg_filename
        while gapbg == [] and fullbg == []:
            bfs = BeautifulSoup(self.browser.page_source, 'lxml')
            gapbg = bfs.find_all('div', class_ = 'gt_cut_bg_slice')
            fullbg = bfs.find_all('div', class_ = 'gt_cut_fullbg_slice')
            if len(gapbg)==0 or len(fullbg)==0:
                self.have_logged_in = True
                return None, None
            pass
        # 找到有缺口背景图的URL
        gapbg_url = re.findall('url\(\"(.*)\"\);', gapbg[0].get('style'))[0].replace('webp', 'jpg')
        # 找到完整背景图的URL
        fullbg_url = re.findall('url\(\"(.*)\"\);', fullbg[0].get('style'))[0].replace('webp', 'jpg')
        gapbg_location_list = []
        fullbg_location_list = []
        for each_gapbg in gapbg:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;',each_gapbg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;',each_gapbg.get('style'))[0][1])
            gapbg_location_list.append(location)
            pass
        for each_fullbg in fullbg:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;',each_fullbg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;',each_fullbg.get('style'))[0][1])
            fullbg_location_list.append(location)
            pass
        # 下载背景图
        urlretrieve(url = gapbg_url, filename = gapbg_filename)
        urlretrieve(url = fullbg_url, filename = fullbg_filename)
        if show_images:
            gapbp_image = plt.imread(gapbg_filename)
            plt.imshow(gapbp_image)
            plt.show()
            fullbp_image = plt.imread(fullbg_filename)
            plt.imshow(fullbp_image)
            plt.show()
            pass
        print('背景图下载完成')
        return gapbg_location_list, fullbg_location_list
    
    def merge_identifying_image(self, filename, location_list, show_images=False):
        '''根据位置对图片进行合并还原'''
        img = image.open(filename)
        img_list_upper=[]
        img_list_down=[]
        for location in location_list:
            if location['y']==-58:
                img_list_upper.append(img.crop((abs(location['x']),58,abs(location['x'])+10,166)))
                pass
            if location['y']==0:
                img_list_down.append(img.crop((abs(location['x']),0,abs(location['x'])+10,58)))
                pass
            pass
        # 新建的图片
        new_img = image.new('RGB', (260,116))
        x_offset = 0
        for img in img_list_upper:
            # 拼接
            new_img.paste(img, (x_offset,0))
            x_offset += img.size[0]
            pass
        x_offset = 0
        for img in img_list_down:
            # 拼接
            new_img.paste(img, (x_offset,58))
            x_offset += img.size[0]
            pass
        new_img.save(filename)
        if show_images:
            img_array = plt.imread(filename)
            plt.imshow(img_array)
            plt.show()
            pass
        print('背景图拼接完成')    
        return new_img
            
    def compare_pixel(self, img1, img2, x, y):
        '''判断两个像素是否相同'''
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        # 比较
        if (abs(pix1[0] - pix2[0]) < threshold and abs(pix1[1] - pix2[1]) < threshold and abs(pix1[2] - pix2[2]) < threshold):
            return True
        else:
            return False
        pass
    
    def get_gap(self, img1, img2):
        '''获取缺口偏移量'''
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.compare_pixel(img1, img2, i, j):
                    left = i
                    return left
        return left
        
    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹（使用加速度与减速度来模拟，当然并不是每个网站都可以使用加速度来解决的，
        如有妖气使用的顶象验证还会判断是否是存在加速度与加速度，毕竟人手动的速度是有波动的）
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 5 / 9
        # 计算间隔
        t = 0.32
        # 初速度
        v = 0
        while current < distance:
            if current < mid:
                # 加速度为正4，实验多次得到的较为准确的速度
                a = 4.5
            else:
                # 加速度为负5
                a = -5.2
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
            pass
        while current > distance:
            move = -random.randint(0, 2)
            current += move
            track.append(round(move))
            pass
        return track
    
    def get_slider(self):
        '''获取滑块'''
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.5)
        return slider
    
    def move_to_gap(self, slider, track):
        '''拖动滑块到缺口处'''
        ActionChains(self.browser).click_and_hold(slider).perform()
        while track:
            x = random.choice(track)
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            track.remove(x)
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()
        
    def crack(self, show_images=False):
        '''log in'''
        self.open_webpage()
        self.login_bilibili()
        while True and self.have_logged_in==False:
            try:
                gapbg_location_list, fullbg_location_list = self.get_identifying_images(show_images=show_images)
                if gapbg_location_list != None and fullbg_location_list != None:
                    gapbg_image = self.merge_identifying_image(bili.gapbg_filename, gapbg_location_list, show_images=show_images)
                    fullbg_image = self.merge_identifying_image(bili.fullbg_filename, fullbg_location_list, show_images=show_images)
                    gap_left = bili.get_gap(gapbg_image, fullbg_image)
                    print('缺口位置', gap_left)
                    track = self.get_track(gap_left-self.border)
                    slider = self.get_slider()
                    self.move_to_gap(slider, track)
                    print('登陆验证中')
                    time.sleep(5)
                    pass
                else:
                    print('登陆成功！')
                    break
                pass
            except:
                print('出错了！')                               
                break
            pass
        pass
    
    pass

bili = Crack()
bili.crack(show_images=True)
