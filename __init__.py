# coding=UTF-8
#HelloWorld是文件名称，Hello是类
#from HelloWorld import Hello
'''
Created on 2018年4月13日

@author: Administrator
@brief : 获取影视书音信息的main函数
'''


from spider_bookChannel import spider_bookChannel
from spider_bookAll import spider_bookAll
from spider_movieAll import spider_movieAll
from spider_musicChannel import spider_musicChannel
from spider_musicAll import spider_musicAll

if __name__ == '__main__':
    print "爬虫开始"
    '''
    #爬取书籍链接
    bookChannelSpider = spider_bookChannel()
    bookChannelSpider.bookChannel()
    
    #爬取书籍信息
    bookAllSpider = spider_bookAll()
    bookAllSpider.crawl()
    
    
    #爬取电影信息
    movieAllSpider = spider_movieAll()
    movieAllSpider.crawl()
    
    
    #爬取音乐链接
    musicChannelSpider = spider_musicChannel()
    musicChannelSpider.musicChannel()
    '''
    
    #爬取音乐信息
    musicAllSpider = spider_musicAll()
    musicAllSpider.crawl()