# coding=UTF-8
'''
    https://movie.douban.com/top250
    https://movie.douban.com/top250?start=25&filter=
    https://movie.douban.com/top250?start=50&filter=
    
'''
'''
Created on 2018年4月20日

@author: Administrator
@brief : 获取top250电影的信息
'''

import requests                       #用来请求网页
from bs4 import BeautifulSoup         #解析网页
from time import sleep         #设置延时时间，防止爬取过于频繁被封IP号
import pymysql       #由于爬取的数据太多，我们要把他存入MySQL数据库中，这个库用于连接数据库
import random        #这个库里用到了产生随机数的randint函数，和上面的time搭配，使爬取间隔时间随机
import re             #处理诡异的名
import urllib         #下载图片


from src.DBUtil import DB

class spider_movieAll:
    
    
    
    #处理文件名，文件名不能含有 :?<>"|\/* 所以用正则表达式处理一下
    def deal_title(self,raw_title):
        r = re.compile('[/\*?"<>|:]')
        return r.sub('~',raw_title)
    
    
    #处理演员
    def get_actor(self,line_tags):
        actor = line_tags[0].contents[0]    #将列表内容转成字符串
        for tag in line_tags[1:]:
            helf = "/"
            actor =actor + helf + tag.contents[0]
        return actor
    
    
    #电影呢简介爬取下来格式要处理过，否者会很难看
    def get_brief(self,raw_author):
        brief = raw_author.replace(" ","").replace("\n","")                          
        return brief
    
            
    #通过url爬取网页信息，获取对象
    def login(self,url):
        #代理ip
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
            print("电影信息爬虫失败！")
            
            
            
    #爬取top250电影信息，并存入数据库    
    def crawl(self):
        
        #打开数据库
        db = DB()
        connection = db.open()
        
        for i in range(10): 
            url = 'https://movie.douban.com/top250?start={}&filter='.format(i*25)   #请求网址
            web_data = self.login(url)                                               #通过url爬取网页信息，获取对象
                
            #Beautiful Soup 是用Python写的一个HTML/XML的解析器，它可以很好的处理不规范标记并生成剖析树(parse tree)
            #soup 就是BeautifulSoup处理格式化后的字符串
            soup = BeautifulSoup(web_data.text.encode('utf-8'),'lxml')      #解析网页信息
            
            movies = soup.select(
                   '''#content > div > div > ol > li > div.item > div.info > div > a''')
            
            
            
            #处理每一本书的详细信息网址
            for movie in movies:
                movieurl = movie.attrs['href']                  #筛选出a标签中属性为href的内容
                movie_data = self.login(movieurl)               #通过url爬取网页信息，获取对象
                try:
                    movieSoup = BeautifulSoup(movie_data.text.encode('utf-8'),'lxml')
                    info = movieSoup.select('#info')                #选择id="info"的div
                    infos = list(info[0].strings)                   #将第一个id="info"的div，以列表形式存入infos
                except:
                    continue
                
                try:          
                    title = movieSoup.select('#content > h1 > span')[0].contents[0]      #直接.contents，返回的是列表        .contents[x]则是获取列表各元素值
                    title = self.deal_title(title)                                       #处理文件名                                            
                    time = movieSoup.select('#content > h1 > span')[1].contents[0]
                    director = movieSoup.select('#info > span > span.attrs > a')[0].contents[0]      
                    actor = self.get_actor(movieSoup.select('#info > span.actor > span.attrs > a'))
                     
                     
                    #储存电影类型
                    pattern = re.compile(r'<span property="v:genre">(.*?)</span>',re.S)      #返回pattern实例，根据规则匹配字符串
                    tags = pattern.findall(movie_data.text)     #返回匹配好的字符串
                    type = tags[0]     #储存电影类型，以"/"分割                                
                    for types in tags[1:]: 
                        helf = "/" 
                        type = type+"/"+types                                             
                    
                    
                    #片长
                    pattern1 = re.compile(r' <span property="v:runtime" content=".*?">(.*?)</span>',re.S)      #返回pattern实例，根据规则匹配字符串
                    tags1 = pattern1.findall(movie_data.text)  
                    runtime = tags1[0]
                    
                    
                    country = infos[infos.index(unicode("制片国家/地区:","utf-8")) + 1].strip()
                    language = infos[infos.index(unicode("语言:","utf-8")) + 1].strip()
                    aname = infos[infos.index(unicode("又名:","utf-8")) + 1].strip()
                    
                    
                    #封面链接
                    coverUrl = movieSoup.select("#mainpic > a > img")[0].attrs['src'];   #筛选出img标签中属性为src的内容
                    #简介
                    brief = self.get_brief(movieSoup.select('#link-report > span')[0].contents[0])
                except:
                    try:          
                        title = movieSoup.select('#content > h1 > span')[0].contents[0]      #直接.contents，返回的是列表        .contents[x]则是获取列表各元素值
                        title = self.deal_title(title)                                       #处理文件名                                            
                        time = movieSoup.select('#content > h1 > span')[1].contents[0]
                        director = movieSoup.select('#info > span > span.attrs > a')[0].contents[0]      
                        actor = self.get_actor(movieSoup.select('#info > span.actor > span.attrs > a'))
                                    
                        #储存电影类型
                        pattern = re.compile(r'<span property="v:genre">(.*?)</span>',re.S)      #返回pattern实例，根据规则匹配字符串
                        tags = pattern.findall(movie_data.text)     #返回匹配好的字符串
                        type = tags[0]     #储存电影类型，以"/"分割                                
                        for types in tags[1:]: 
                            helf = "/" 
                            type = type+"/"+types                                             
                                  
                        #片长
                        pattern1 = re.compile(r' <span property="v:runtime" content=".*?">(.*?)</span>',re.S)      #返回pattern实例，根据规则匹配字符串
                        tags1 = pattern1.findall(movie_data.text)  
                        runtime = tags1[0]
                                 
                        country = infos[infos.index(unicode("制片国家/地区:","utf-8")) + 1].strip()
                        language = infos[infos.index(unicode("语言:","utf-8")) + 1].strip()
                        aname = infos[infos.index(unicode("又名:","utf-8")) + 1].strip()
                        
                        #封面链接
                        coverUrl = movieSoup.select("#mainpic > a > img")[0].attrs['src'];   #筛选出img标签中属性为src的内容
                        #简介
                        brief = self.get_brief(movieSoup.select('#link-report > span'))
                    except:
                        continue   
                
                
                finally:
                    try:
                        tag = "../resources/movieimg/"+title+".png"
                        urllib.urlretrieve(coverUrl,tag);
                        
                        
                        with connection.cursor() as cursor:
                        
                            #插入电影信息
                            sql = '''INSERT INTO movieall (
                                title, time, director, actor, type, runtime, country, language, aname, tag, brief)
                                VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")''' % \
                                (title, time, director, actor, type, runtime, country, language, aname, tag, brief)
                            try:   
                                cursor.execute(sql)
                                movieId = long(connection.insert_id())  #最新插入行的主键ID，conn.insert_id()一定要在conn.commit()之前，否则会返回0  
                            except:
                                print("插入电影信息失败！") 
                            
                             
                            # tags储存电影类型
                            for types in tags:
                                
                                #获取电影类型ID
                                sql = 'SELECT movieTypeId FROM movietype where movieTypeInfo = "%s"' %(types)
                                try:
                                    cursor.execute(sql) 
                                    # 获取所有记录列表
                                    results = cursor.fetchall()
                                    #获取第一行第一列
                                    for row in results:
                                        movieTypeId = row[0]
        
                                except:
                                    print("获取movieTypeId失败！")    
                                
                                #将每部电影的类型记录插入movietypenotes（因为每部电影的类别有很多)
                                sql = '''INSERT INTO movietypenotes (movieId, movieTypeId)
                                    VALUES ("%d","%d")''' % \
                                    (movieId, movieTypeId)
                                try:   
                                    cursor.execute(sql)
                                    # 获取所有记录列表,这部电影的id
                                    results = cursor.fetchall()
                                    #获取第一行第一列
                                    for row in results:
                                        movieId = row[0]
                                except:
                                    print("插入电影类型记录失败！") 
                            
                                          
                                connection.commit()
                                sleep(random.randint(0,9)) #防止IP被封
                    except:
                        print "下载图片失败"
        #关闭数据库
        db.close(connection)           