# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from config import Config
import sqlite3
import os

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊ fishingmap and report & 商城 ＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
current_dir = os.path.dirname(__file__)  #透過os取得目前的路徑
db_path = 'sqlite:///{}/{}.db'.format(current_dir, Config.DATABASE_NAME)
engine = create_engine(db_path, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

#初始化database
def init_db():
    # 如果database_exists(db_path)路徑下已經有就回傳false,
    # 否則就會Base.metadata.create_all(bind=engine)新增資料庫回傳True-初始化資料庫
    if database_exists(db_path):
        return False
    else:
        Base.metadata.create_all(bind=engine)
        return True

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊ weather ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
##############資料庫連接(目前無使用)##############
def db_weather():
    conn=sqlite3.connect(Config.DATABASE_NAME+'.db') #建立連線物件
    return conn
##############先確認資料庫是否有資料##############
def select_db(userID,mat,pointName,pointNum):
    conn=sqlite3.connect(Config.DATABASE_NAME+'.db') #建立連線物件
    if mat=='即時天氣' or mat=='天氣預報' or mat=='休閒漁港即時天氣':
        collect=conn.execute('select * from weather WHERE uid="{}" AND mat_d="{}" AND pointName_d="{}"'.format(userID,mat,pointName)).fetchone()
    elif mat=='主要港口即時天氣' or mat=='海水浴場即時天氣':
        collect=conn.execute('select * from weather WHERE uid="{}" AND mat_d="{}" AND pointName_d="{}" AND pointNum_d="{}"'.format(userID,mat,pointName,pointNum)).fetchone()
    return collect
    conn.close()  #關閉與資料庫的連結
##############關注-即時天氣&天氣預報##############
# content=db.add_my_weather(uid,mat_d[uid],pointName_d[uid],pointNum_d[uid])
def add_my_weather(userID,mat,pointName,pointNum):
    conn=sqlite3.connect(Config.DATABASE_NAME+'.db') #建立連線物件
    conn.isolation_level=None  #設為自動提交模式
    collect=select_db(userID,mat,pointName,pointNum)
    if collect!= None:
        return f"{pointName}的{mat}，您已有關注了。"
    else:
        if mat=='即時天氣' or mat=='天氣預報' or mat=='休閒漁港即時天氣':
            conn.execute("INSERT INTO weather (uid,mat_d,pointName_d) VALUES('{}','{}','{}');".format(userID,mat,pointName))
        elif mat=='主要港口即時天氣' or mat=='海水浴場即時天氣':
            conn.execute("INSERT INTO weather (uid,mat_d,pointName_d,pointNum_d) VALUES('{}','{}','{}','{}');".format(userID,mat,pointName,pointNum))
    conn.close()  #關閉與資料庫的連結
    return f"{pointName}的{mat}，已新增至您的常用天氣中。"
##############刪除-即時天氣&天氣預報##############
# content=db.del_my_weather(uid,mat_d[uid],pointName_d[uid],pointNum_d[uid])
def del_my_weather(userID,mat,pointName,pointNum):
    conn=sqlite3.connect(Config.DATABASE_NAME+'.db') #建立連線物件
    conn.isolation_level=None  #設為自動提交模式
    collect=select_db(userID,mat,pointName,pointNum)
    if collect!= None:
        if mat=='即時天氣' or mat=='天氣預報' or mat=='休閒漁港即時天氣':
            conn.execute('DELETE FROM weather WHERE uid="{}" AND mat_d="{}" AND pointName_d="{}" '.format(userID,mat,pointName))
        elif mat=='主要港口即時天氣' or mat=='海水浴場即時天氣':
            conn.execute('DELETE FROM weather WHERE uid="{}" AND mat_d="{}" AND pointName_d="{}" AND pointNum_d="{}" '.format(userID,mat,pointName,pointNum))
        return f"您已經不愛{pointName}的{mat}了。"
    else:
        return f"您本就沒愛過{pointName}的{mat}喔！！"
    conn.close()  #關閉與資料庫的連結
##############查詢已關注清單All-供後續查詢用##############
# 供後續查詢用
# dataList=db.get_love_weather(uid,mat)
def get_love_weather(userID,mat):
    conn=sqlite3.connect(Config.DATABASE_NAME+'.db')
    data=conn.execute('select * from weather WHERE uid="{}" AND mat_d="{}" '.format(userID,mat)).fetchone()
    if data == None: return f'查無您有關注的{mat}。'
    else:
        return conn.execute('select * from weather WHERE uid="{}" AND mat_d="{}" '.format(userID,mat)).fetchall()
    conn.close()
##############我的最愛-所有已關注清單(All_List-OK)##############
# 查詢該user_id所有已關注清單(All_List)
# content=get_allList_weather(uid)
def show_allList_weather(userID):
    conn=sqlite3.connect(Config.DATABASE_NAME+'.db') #建立連線物件
    dataList=conn.execute('select * from weather WHERE uid="{}" ORDER BY mat_d '.format(userID)).fetchall()
    if dataList == []: return f"目前無您關注的天氣，請新增您想關注的天氣喔！！"
    return dataList
    conn.close()