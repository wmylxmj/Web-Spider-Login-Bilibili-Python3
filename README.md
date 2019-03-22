# Web-Spider-login-bilibili-python3
## 网络爬虫模拟登陆bilibili-滑动验证码的破解-更新至version14.py-2018-10-9
## version14： 可自动发送弹幕
### 思路：
###  1.先从网站上找到验证码，并完成拼接
#### 原始图像：
![](images/bg1.png)
![](images/bg2.png)
#### 拼接好后的滑动验证码：
![](images/fullbg.jpg)
![](images/gapbg.jpg)
### 2.比较两图片，找到缺口的左侧边界，误差阈值为60是比较合适的
### 3.按先加速再减速的方式拖动验证码，加速度，中间位置需调整好
### 4.运行程序，登陆成功！
## 注意：
- 1.请先安装chrome和chromedriver以及bs4,selenium库
- 2.一定要按先加速再减速的方式拖动验证码，否则会显示拼图被怪兽吃掉
#### 捕获的信息:
![](images/keys.jpg)
