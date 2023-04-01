from os import WIFEXITED
from re import M
from sqlalchemy import Column,String,Integer, ForeignKey
from linebot.models import *
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.operators import asc_op
from database import Base,db_session
from urllib.parse import quote #使用者自動輸入專用，可避免空白輸入
from sqlalchemy.orm import relationship
from cachelib import SimpleCache
from config import Config
#訂單建立-->寫入購買人收件資料的表格
class P_Informations(Base):
    __tablename__ = 'p_informations'
    
    id = Column(String,primary_key=True)
    name = Column(String)
    phone = Column(String)
    address = Column(String)
    addr_number = Column(String)
    
    def information_show(nam ='王OO',pho='09xxxxxxxx',num='10455',addr='台北市大安區金山O路O段OO號'):
        message = FlexSendMessage(
                alt_text='收件資料',
                contents=
                    {
                    "type": "bubble",
                    "size": "mega",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "收件資料 📮",
                            "weight": "bold",
                            "margin": "md",
                            "size": "xxl",
                            "color": "#4493A3"
                        },
                        {
                            "type": "separator",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": "⚠ 收件資訊請確實填寫 ⚠",
                            "size": "sm",
                            "align": "center",
                            "offsetTop": "3px",
                            "color": "#FF0000"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/BZ9xTrn.png"
                                },
                                {
                                    "type": "text",
                                    "text": nam,
                                    "color": "#4D4D4D",
                                    "size": "md"
                                }
                                ],
                                "spacing": "md"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/BEyR2pH.png"
                                },
                                {
                                    "type": "text",
                                    "text": pho,
                                    "color": "#4D4D4D",
                                    "size": "md"
                                }
                                ],
                                "spacing": "md"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/3M1oh2K.png"
                                },
                                {
                                    "type": "text",
                                    "text":num,
                                    "color": "#4D4D4D",
                                    "size": "md"
                                }
                                ],
                                "spacing": "md"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/q9fiyD5.png"
                                },
                                {
                                    "type": "text",
                                    "text": addr,
                                    "color": "#000000",
                                    "size": "sm"
                                }
                                ],
                                "spacing": "md"
                            }
                            ],
                            "height": "100px",
                            "offsetTop": "10px"
                        },
                        {
                            "type": "separator",
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "button",
                                "action": {
                                "type": "postback",
                                "label": "進入付款",
                                "data": 'LinePay'
                                },
                                "color": "#C36839",
                                "flex": 4,
                                "style": "primary",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "uri",
                                "label": "點選填寫",
                                "uri": 'line://oaMessage/{base_id}/?{message}'.format(base_id=Config.BASE_ID,message=quote('☛姓名：\n•電話：\n•郵遞區號：\n•地址：'))
                                },
                                "color": "#7EB5A6",
                                "style": "primary",
                                "flex": 4,
                                "height": "md"
                            }
                            ],
                            "offsetTop": "5px",
                            "spacing": "md"
                        }
                        ]
                    }
                    }
                )
        
        return message

cache = SimpleCache()
class Input_Information(object):
    def __init__(self,user_id):
        self.cache = cache
        self.user_id = user_id
    def find(self):
        return cache.get(key=self.user_id) or {}
    def add(self,name,phone,address,addr_number):
        info_list = self.find()
        info_list =cache.get(key=self.user_id)#透過user_id取得使用者的購物車
        #如果購物車是空的就會加入一個字典 product:int(num)
        if info_list == None :
            cache.add(key=self.user_id,value={name:phone,address:addr_number})
        else:
            #如購物車其他商品就會更新一個字典 product:int(num)
            info_list.update({name:phone,address:addr_number})
            #接著再更新到使用者的購物車
            cache.set(key=self.user_id,value=info_list)
    def reset(self):#清空購物車
        cache.set(key=self.user_id,value={})

Input_information= Input_Information(user_id='10')#戴入user_id才知道購物車是誰的
Input_information.find()#查詢購物車的內容可以用bucket()
Input_information.reset()
Input_information.add('王OO','0912345678','台北市','600')#利用add加入兩杯咖啡  