# coding=UTF-8
'''
Created on 2018年4月21日

@author: Administrator
@brief : 链接数据库
'''
import pymysql       #由于爬取的数据太多，我们要把他存入MySQL数据库中，这个库用于连接数据库

class DB:
    
    #链接数据库
    def open(self):
        try:
            connection = pymysql.connect(host='localhost',user='root',password='root',charset='utf8')
            with connection.cursor() as cursor:
                sql = "USE Graduation_Pro;"
                cursor.execute(sql)
            connection.commit()
            return connection
        except:
            print("链接数据库失败！")
      
    #关闭数据库  
    def close(self,connection):
        try:
            if connection.open:
                connection.close()
        except:
            print("关闭数据库失败！")
            
            
    #建立数据库：booktype
    def set_booktype(self,connection):
        with connection.cursor() as cursor:
                sql = """create table booktype (
                         bookTypeId  int primary key not null auto_increment,
                         bookTypeInfo  varchar(255) not null)"""
                cursor.execute(sql)
                connection.commit()
        