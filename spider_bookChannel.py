# coding=UTF-8
'''
Created on 2018年4月12日

@author: Administrator
@brief : 获取所有书籍的链接
'''

import urllib2
import re
import pymysql       #由于爬取的数据太多，我们要把他存入MySQL数据库中，这个库用于连接数据库
import random 
from time import sleep          #设置延时时间，防止爬取过于频繁被封IP号

from src.DBUtil import DB

class spider_bookChannel:
    
    
    def bookChannel(self):
        
        #打开数据库
        db = DB()
        connection = db.open()
        
        #建表：booktype
        #db.set_booktype(connection)
        

        
        url = "https://book.douban.com/tag/?icn=index-nav"     #请求网址
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'   #要伪装的浏览器user_agent头
        headers = {'User-Agent': user_agent}                   #创建一个字典，使请求的headers中的User-Agent对应user_agent字符串
        req = urllib2.Request(url,headers = headers)         #创建一个请求，需要将请求中的headers变量换成刚才创建的headers
        response = urllib2.urlopen(req)                        #请求服务器得到回应
        html = response.read()                                 #返回字符串形式
        
        
        pattern = re.compile(r'<a href="/tag/\W*">',re.S)      #返回pattern实例，根据规则匹配字符串
        tags = pattern.findall(html)                           #返回匹配好的字符串
        
        urls = []     #储存所有链接
        for tag in tags:  
            tag = tag.replace("<a href=","").replace(">","").replace('"','')
            helf="https://book.douban.com"                #观察一下豆瓣的网址，基本都是这部分加上标签信息，所以我们要组装网址，用于爬取标签详情页
            url=helf+tag 
            urls.append(url)
            
            
            #将书籍类型存入数据库
            '''
            with connection.cursor() as cursor:
                type = tag.replace("/tag/","")
                print type
                sql = 'INSERT INTO booktype(bookTypeInfo)  VALUES ("%s")' % \
                       (type)
                cursor.execute(sql)
                connection.commit()
            '''
            #sleep(random.randint(0,9)) #防止IP被封
            
        # 将链接存入文件
        bookchannel = unicode("F:\\毕业设计爬取资料\\Book\\bookchannel.txt","utf-8")    #python处理中文路径
        with open(bookchannel,"w") as file:
            i = 0
            for link in urls:
                i = i+1
                if(i>108):
                    file.write(link+'\n')

        
        
        #关闭数据库
        db.close(connection)

