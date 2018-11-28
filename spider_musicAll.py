# coding=UTF-8
'''
Created on 2018年4月27日

@author: Administrator
@brief : 获取音乐的信息,每一个分类里面，爬取第一页
'''
import requests                       #用来请求网页
from bs4 import BeautifulSoup         #解析网页
from time import sleep         #设置延时时间，防止爬取过于频繁被封IP号
import pymysql       #由于爬取的数据太多，我们要把他存入MySQL数据库中，这个库用于连接数据库
import random        #这个库里用到了产生随机数的randint函数，和上面的time搭配，使爬取间隔时间随机
import re             #处理诡异的书名
import urllib         #下载图片


from src.DBUtil import DB


class spider_musicAll:
    
    #处理文件名，文件名不能含有 :?<>"|\/* 所以用正则表达式处理一下
    def deal_title(self,raw_title):
        r = re.compile('[/\*?"<>|:]')
        return r.sub('~',raw_title)
    
    
    #表演者名字爬取下来格式要处理过，否者会很难看
    def get_performer(self,raw_performer):
        parts = raw_performer.replace(" ","").replace("\n","")                          
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
            print("音乐信息爬虫失败！")
    
    
    
    #爬取书籍信息，并存入数据库    
    def crawl(self):
        
        #打开数据库
        db = DB()
        connection = db.open()
        
        # 获取链接
        channel = []
        musicchannel = unicode("F:\\毕业设计爬取资料\\Book\\musicchannel.txt","utf-8")    #python处理中文路径
        with open(musicchannel,"r") as file:
            channel = file.readlines()
            
            
        #处理每一个链接 （书的类型）
        for url in channel:                                                      
            web_data = self.login(url.strip())                                   #通过url爬取网页信息，获取对象
            
            #Beautiful Soup 是用Python写的一个HTML/XML的解析器，它可以很好的处理不规范标记并生成剖析树(parse tree)
            #soup 就是BeautifulSoup处理格式化后的字符串
            soup = BeautifulSoup(web_data.text.encode('utf-8'),'lxml')      #解析网页信息
            
            #音乐类型
            type = url.strip().replace("https://music.douban.com/tag/","")   #str.strip()就是把这个字符串头和尾的空格，以及位于头尾的\n \t之类给删掉
            
            musics = soup.select(
                    '''#subject_list > table > tr.item > td > a.nbg''')
            
            #处理每一本书的详细信息网址
            for music in musics:
                musicurl = music.attrs['href']             #筛选出a标签中属性为href的内容
                music_data = self.login(musicurl)          #通过url爬取网页信息，获取对象
                try:
                    musicSoup = BeautifulSoup(music_data.text.encode('utf-8'),'lxml')
                    info = musicSoup.select('#info')          #选择id="info"的div
                    infos = list(info[0].strings)            #将第一个id="info"的div，以列表形式存入infos
                except:
                    continue
                
                
                
                try:
                    #标题
                    title = musicSoup.select('#wrapper > h1 > span')[0].contents[0]      #直接.contents，返回的是列表        .contents[x]则是获取列表各元素值
                    title = self.deal_title(title) 
                    #表演者
                    performer = self.get_performer(musicSoup.select("#info > span > span.pl > a")[0].contents[0])  
                    
                    special = infos[infos.index(unicode("专辑类型:","utf-8")) + 1].strip()
                    media = infos[infos.index(unicode("介质:","utf-8")) + 1].strip()
                    time = infos[infos.index(unicode("发行时间:","utf-8")) + 1].strip()
                    publish = infos[infos.index(unicode("出版者:","utf-8")) + 1].strip()
                    
                    coverUrl = musicSoup.select("#mainpic > span > a > img")[0].attrs['src'];   #筛选出img标签中属性为src的内容
                    
                    pattern = re.compile(r'<span property="v:summary">(.*?)</span>',re.S)      #返回pattern实例，根据规则匹配字符串
                    tags = pattern.findall(music_data.text)     #返回匹配好的字符串
                    brief = tags[0]
                    
                except:
                    try:
                        #标题
                        title = musicSoup.select('#wrapper > h1 > span')[0].contents[0]      #直接.contents，返回的是列表        .contents[x]则是获取列表各元素值
                        title = self.deal_title(title) 
                        #表演者
                        performer = self.get_performer(musicSoup.select("#info > span > span.pl > a")[0].contents[0])  
                        
                        special = infos[infos.index(unicode("专辑类型:","utf-8")) + 1].strip()
                        media = infos[infos.index(unicode("介质:","utf-8")) + 1].strip()
                        time = infos[infos.index(unicode("发行时间:","utf-8")) + 1].strip()
                        publish = infos[infos.index(unicode("出版者:","utf-8")) + 1].strip()
                        
                        coverUrl = musicSoup.select("#mainpic > span > a > img")[0].attrs['src'];   #筛选出img标签中属性为src的内容
                        
                        
                        pattern = re.compile(r'<span property="v:summary">(.*?)</span>',re.S)      #返回pattern实例，根据规则匹配字符串
                        tags = pattern.findall(music_data.text)     #返回匹配好的字符串
                        brief = tags[0]    
                    except:
                        continue
                
                
                finally:
                    tag = "../resources/musicimg/"+title+".png"
                    urllib.urlretrieve(coverUrl,tag); 
                    
                    with connection.cursor() as cursor:
                        #获取每首歌的类型id
                        sql = 'SELECT musicTypeId FROM musictype where musicTypeInfo = "%s"' %(type)
                        #print sql
                        try:
                            cursor.execute(sql) 
                            # 获取所有记录列表
                            results = cursor.fetchall()
                            #获取第一行第一列
                            for row in results:
                                musicTypeId = row[0]

                        except:
                            print("获取musicTypeId失败！")  
                            
                            
                        #插入音乐信息
                        sql = '''INSERT INTO musicall (
                            title,  performer, special, media, time, publish, tag, brief, musicTypeId)
                            VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%d")''' % \
                            (title,performer,special,media,time,publish,tag,brief,musicTypeId)
                        try:   
                            cursor.execute(sql)
                        except:
                            print("插入音乐信息失败！") 
                        
                                  
                        connection.commit()
                        sleep(random.randint(0,9)) #防止IP被封                 



        #关闭数据库
        db.close(connection)      