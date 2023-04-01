from re import S, X
from cachelib import SimpleCache
from linebot.models import *
from sqlalchemy.orm import lazyload
from sqlalchemy.sql.expression import true
from database import db_session
from menuproduct import Menuproducts
from urllib.parse import quote #使用者自動輸入專用，可避免空白輸入
from config import Config
#建立類別設定給cart
cache = SimpleCache()

class Cart(object):
    def __init__(self,user_id):
        self.cache = cache
        self.user_id = user_id
    def bucket(self):
        
        #透過user_id查詢使用者的購物車如果沒有東西就會回傳空值
        return cache.get(key=self.user_id) or {}
    def add(self,forma_t,num=1):
        bucket = self.bucket()
        bucket =cache.get(key=self.user_id)#透過user_id取得使用者的購物車
        #如果購物車是空的就會加入一個字典 product:int(num)
        if bucket == None :
            cache.add(key=self.user_id,value={forma_t:int(num)})
        else:
            #如購物車其他商品就會更新一個字典 product:int(num)
            bucket.update({forma_t:int(num)})
            #接著再更新到使用者的購物車
            cache.set(key=self.user_id,value=bucket)
    def reset(self):#清空購物車
        cache.set(key=self.user_id,value={})

    def display(self):#計算購物車內容及價格
        total = 0#總金額
        total_number = 0#總共項目
        product_box_component = []#放置產品明細
        for product_name, num in self.bucket().items():#透過for迴圈抓取購物車內容
            if num > 0 :
            #透過 Menuproducts.forma_t 去搜尋
                forma_t = db_session.query(Menuproducts).filter(Menuproducts.forma_t.ilike(product_name)).first()
                amount = forma_t.price * int(num)#然後再乘以購買的數量
                product = forma_t.product
                total += amount
                total_number += 1
                product_box_component.append(
                    {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": 'NT$ {amount}'.format(amount=amount),
                        "weight": "bold",
                        "size": "sm",
                        "color": "#CACACA"
                    },
                    {
                        "type": "text",
                        "text": product,
                        "color": "#86340A",
                        "size": "lg",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": '規格：{forma_t}'.format(forma_t=product_name),
                        "color": "#4D4D4D",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": "數量：{number}".format(number=num),
                        "size": "md",
                        "color": "#4D4D4D"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": "數量選擇",
                                "size": "10px",
                                "align": "end",
                                "action": {
                                "type": "postback",
                                "label": "number",
                                "data": '更改數量{product_name}'.format(product_name=product_name)
                                }
                            }
                            ],
                            "flex": 5
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "image",
                                "url": "https://i.imgur.com/nrLi1g0.png",
                                "size": "15px",
                                "flex": 5,
                                "action": {
                                "type": "postback",
                                "label": "number",
                                "data": '更改數量{product_name}'.format(product_name=product_name)
                                }
                            },
                            {
                                "type": "image",
                                "url": "https://i.imgur.com/GfZEGJw.png",
                                "size": "15px",
                                "flex": 5,
                                "action": {
                                "type": "postback",
                                "label": "number",
                                "data": '更改數量{product_name}'.format(product_name=product_name)
                                }
                            }
                            ],
                            "flex": 1,
                            "action": {
                            "type": "postback",
                            "label": "number",
                            "data": "number"
                            }
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "image",
                                "url": "https://i.imgur.com/eSBgsbP.png",
                                "size": "20px",
                                "action": {
                                "type": "postback",
                                "label": "delete",
                                "data": '刪除{product_name}'.format(product_name=product_name)
                                }
                            }
                            ],
                            "alignItems": "flex-end",
                            "flex": 2,
                            "action": {
                            "type": "postback",
                            "label": "delete",
                            "data": "delete"
                            }
                        }
                        ],
                        "paddingBottom": "10px"
                    }
                    ]
                })
        if total > 0:
            message = FlexSendMessage(
                alt_text='購物車',
                contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "購物車  🛒",
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
                            "text": "總共項目：{total_number}".format(total_number=total_number),
                            "size": "sm",
                            "align": "end",
                            "color": "#000000"
                        },
                        {
                            "type":"box",
                            "layout": "vertical",
                            "margin":'xxl',
                            "spacing":'sm',
                            "contents":product_box_component   
                        },
                        {
                            "type": "separator",
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": '總共：NT${total}'.format(total=total),
                            "align": "end",
                            "color": "#4D4D4D",
                            "size": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {   "type": "button",
                                "action": {
                                "type": "postback",
                                "label": "結帳",
                                "data": "結帳"
                                },
                                "color": "#C36839",
                                "style": "primary",
                                "flex": 4,
                                "margin": "none"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "postback",
                                "label": "繼續選購",
                                "data": "繼續選購"
                                },
                                "color": "#7EB5A6",
                                "style": "primary",
                                "flex": 4
                                
                            }
                            ],
                            "offsetTop": "2px",
                            "spacing": "md"
                        }
                        ]}})
        else:
            message = TextSendMessage(text='您的購物車是空的。')
        return message
    def change_number(self,name='藍色 BLUE'):
        # for product_name, num in self.bucket().items():#透過for迴圈抓取購物車內容
            #透過 Menuproducts.forma_t 去搜尋
        forma_t = db_session.query(Menuproducts).filter(Menuproducts.forma_t.ilike(name)).first()
        message = FlexSendMessage(
                    alt_text='數量更改',
                    contents={
                        "type": "bubble",
                        "size": "kilo",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": "{format_}".format(format_=forma_t.forma_t),
                                "weight": "bold",
                                "size": "20px",
                                "margin": "md",
                                "offsetBottom": "10px"
                            },
                            {
                                "type": "text",
                                "text": "請選擇數量:",
                                "size": "xs",
                                "color": "#aaaaaa",
                                
                                "offsetBottom": "10px"
                            },
                            {
                                "type": "separator",
                                "margin": "xs"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "xs",
                                "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "postback",
                                    "label": "1",
                                    "data": '數量1{forma_t}'.format(forma_t=forma_t.forma_t)
                                    },
                                    "margin": "xs",
                                    "height": "sm"
                                },
                                {
                                "type": "button",
                                    "action": {
                                    "type": "postback",
                                    "label": "2",
                                    "data": '數量2{forma_t}'.format(forma_t=forma_t.forma_t)
                                    },
                                    "margin": "xs",
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "postback",
                                    "label": "3",
                                    "data": '數量3{forma_t}'.format(forma_t=forma_t.forma_t)
                                    },
                                    "margin": "xs",
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "uri",
                                    "label": "其他數量",
                                    "uri": 'line://oaMessage/{base_id}/?{message}'.format(base_id=Config.BASE_ID,message=quote('{forma_t},輸入數量：'.format(forma_t=forma_t.forma_t)))
                                    },
                                    "margin": "xs",
                                    "height": "sm",
                                    "style": "primary",
                                    "color": "#C36839"
                                }
                                ],
                                "spacing": "xs"
                            }
                            ]
                        }
                })
        return message
cart = Cart(user_id='10')#戴入user_id才知道購物車是誰的
cart.bucket()#查詢購物車的內容可以用bucket()
cart.add('S98M',2)#利用add加入兩杯咖啡
cart.reset()#清除購物車