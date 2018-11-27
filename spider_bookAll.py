# coding=UTF-8
'''
Created on 2018年4月14日

@author: Administrator
@brief : 获取书籍的信息,每一个分类里面，爬取第一页
'''

import requests                       #用来请求网页
from bs4 import BeautifulSoup         #解析网页
from time import sleep         #设置延时时间，防止爬取过于频繁被封IP号
import pymysql       #由于爬取的数据太多，我们要把他存入MySQL数据库中，这个库用于连接数据库
import random        #这个库里用到了产生随机数的randint函数，和上面的time搭配，使爬取间隔时间随机
import re             #处理诡异的书名
import urllib         #下载图片


from src.DBUtil import DB




class spider_bookAll:


    #处理文件名，文件名不能含有 :?<>"|\/* 所以用正则表达式处理一下
    def deal_title(self,raw_title):
        r = re.compile('[/\*?"<>|:]')
        return r.sub('~',raw_title)
    
    
    #处理图书简介
    def get_brief(self,line_tags):
        brief = line_tags[0].contents    #将列表内容转成字符串
        for tag in line_tags[1:]:
            brief += tag.contents
        brief = '\n'.join(brief)         #处理完一行图书简介后，换行
        return brief
    
    
    #作者名字爬取下来格式要处理过，否者会很难看
    def get_author(self,raw_author):
        parts = raw_author.replace(" ","").replace("\n","")                          
        return parts
       
                                                
    
    
    #通过url爬取网页信息，获取对象
    def login(self,url):
        proxies = {
            'http': 'http://124.72.109.183:8118',
            'http': 'http://49.85.1.79:31666',
            'http': 'http://60.177.225.245:18118',
            'http': 'http://223.241.118.91:8010'

        }
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'   #要伪装的浏览器user_agent头
            headers = {'User-Agent': user_agent}                   #创建一个字典，使请求的headers中的User-Agent对应user_agent字符串
            s = requests.get(url, headers=headers,timeout=3, proxies=proxies)
            return s   
        except:
            print("书籍信息爬虫失败！")
        
        
    #爬取书籍信息，并存入数据库    
    def crawl(self):
        
        #打开数据库
        db = DB()
        connection = db.open()
        
        # 获取链接
        channel = []
        bookchannel = unicode("F:\\毕业设计爬取资料\\Book\\bookchannel.txt","utf-8")    #python处理中文路径
        with open(bookchannel,"r") as file:
            channel = file.readlines()
        
        
        #处理每一个链接 （书的类型）
        for url in channel:                                                      
            web_data = self.login(url.strip())                                   #通过url爬取网页信息，获取对象
            
            #Beautiful Soup 是用Python写的一个HTML/XML的解析器，它可以很好的处理不规范标记并生成剖析树(parse tree)
            #soup 就是BeautifulSoup处理格式化后的字符串
            soup = BeautifulSoup(web_data.text.encode('utf-8'),'lxml')      #解析网页信息
            
            type = url.strip().replace("https://book.douban.com/tag/","")   #str.strip()就是把这个字符串头和尾的空格，以及位于头尾的\n \t之类给删掉
            
            books = soup.select(
                    '''#subject_list > ul > li > div.info > h2 > a''')
            
            #处理每一本书的详细信息网址
            for book in books:
                bookurl = book.attrs['href']             #筛选出a标签中属性为href的内容
                book_data = self.login(bookurl)          #通过url爬取网页信息，获取对象
                try:
                    bookSoup = BeautifulSoup(book_data.text.encode('utf-8'),'lxml')
                    info = bookSoup.select('#info')          #选择id="info"的div
                    infos = list(info[0].strings)            #将第一个id="info"的div，以列表形式存入infos
                except:
                    continue
                title = ''
                publish = ''
                author = ''
                ISBN = ''
                time = ''
                price= ''
                brief = ''
                
                try:         
                    title = bookSoup.select('#wrapper > h1 > span')[0].contents[0]      #直接.contents，返回的是列表        .contents[x]则是获取列表各元素值
                    title = self.deal_title(title)                                      #处理文件名
                    publish = infos[infos.index(unicode("出版社:","utf-8")) + 1]          #index() 方法检测字符串中是否包含子字符串 str,有返回下标，没有抛异常
                    
                    
                    author = self.get_author(bookSoup.select("#info > a")[0].contents[0])
                    ISBN = infos[infos.index('ISBN:') + 1].strip()                              
                    time = infos[infos.index(unicode("出版年:","utf-8")) + 1].strip()
                    price = infos[infos.index(unicode("定价:","utf-8")) + 1].strip()
                    
                
                    coverUrl = bookSoup.select("#mainpic > a > img")[0].attrs['src'];   #筛选出img标签中属性为src的内容
                    brief = self.get_brief(bookSoup.select('#link-report > div > div > p'))  #处理图书简介
                
                except:
                    try:
                        title = bookSoup.select('#wrapper > h1 > span')[0].contents[0]      #直接.contents，返回的是列表        .contents[x]则是获取列表各元素值
                        title = self.deal_title(title)                                      #处理文件名
                        publish = infos[infos.index(unicode("出版社:","utf-8")) + 1]          #index() 方法检测字符串中是否包含子字符串 str,有返回下标，没有抛异常
                 
                        author = self.get_author(bookSoup.select("#info > a")[0].contents[0])
                        ISBN = infos[infos.index('ISBN:') + 1].strip()                               
                        time = infos[infos.index(unicode("出版年:","utf-8")) + 1].strip() 
                        price = infos[infos.index(unicode("定价:","utf-8")) + 1].strip() 
                        
               
                        coverUrl = bookSoup.select("#mainpic > a > img")[0].attrs['src'];   #筛选出img标签中属性为src的内容
                        brief = self.get_brief(bookSoup.select('#link-report > div > div > p'))  #处理图书简介
                    except:
                        continue
                
                
                
                
                
                finally:
                    tag = "../resources/bookimg/"+title+".png"
                    urllib.urlretrieve(coverUrl,tag);
                               
                    with connection.cursor() as cursor:
                        #获取每本书的类型id
                        sql = 'SELECT bookTypeId FROM booktype where bookTypeInfo = "%s"' %(type)
                        try:
                            cursor.execute(sql) 
                            # 获取所有记录列表
                            results = cursor.fetchall()
                            #获取第一行第一列
                            for row in results:
                                bookTypeId = row[0]

                        except:
                            print("获取bookTypeId失败！")       
                        
                        
                        #插入书籍信息
                        sql = '''INSERT INTO bookall (
                            title,  author, price, time, publish, tag, brief, ISBN, bookTypeId)
                            VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%d")''' % \
                            (title,author,price,time,publish,tag,brief,ISBN,bookTypeId)
                        try:   
                            cursor.execute(sql)
                        except:
                            print("插入书籍信息失败！") 
                        
                                  
                        connection.commit()
                        sleep(random.randint(0,9)) #防止IP被封
        
                    
        #关闭数据库
        db.close(connection)