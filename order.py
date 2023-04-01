from time import time
from p_information import P_Informations
from item import Items
from sqlalchemy import Column, DateTime, String, Integer, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from linebot.models import *
from database import Base,db_session

#訂單建立時-->訂單的表格
class Orders(Base):
    __tablename__ = 'orders' #table name

    id = Column(String, primary_key=True)
    created_time = Column(DateTime, default=func.now())#訂單建立時間
    amount = Column(Integer)#記錄訂單總金額
    is_pay = Column(Boolean, default=False)#記錄訂單是否已經付款，預設False代表未付款
    items = relationship('Items', backref='order')#加上這行建立訂單關聯性
    transaction_id = Column(String)#串接line pay 的時候會用到
    user_id = Column("user_id", ForeignKey("users.id"))#ForeignKey外來鍵的意思，訂單是由哪一個user建立的
    delivery_status = Column(String)

    def display_receipt(self):
        item_box_component = []
        order_id = []
        for item in self.items:#透過self.items取得訂單明細項目
            prodcut_forma_t = item.product
            product_name = prodcut_forma_t.split('&')[0]
            product_format = prodcut_forma_t.split('&')[1]
            amount = item.number * item.price
            item_box_component.append(
                {
                "type": "box",
                "layout": "vertical",
                "margin": "md",
                "spacing": "xs",
                "contents": [
                {
                    "type": "text",
                    "text": 'NT${price} x {num}'.format(price=item.price,num=item.number),
                    "weight": "bold",
                    "size": "sm",
                    "color": "#CACACA"
                },
                {
                    "type": "text",
                    "text": '{product}'.format(product=product_name),
                    "color": "#4D4D4D",
                    "size": "md",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": '{forma_t}'.format(forma_t=product_format),
                    "color": "#929AAB",
                    "size": "13px"
                }
                ]
            }
            )
            order_id.append(item.order_id)
        order_id = order_id[0]#只抓一比order_id 因為都是一樣的。
        # p_informations = db_session.query(P_Informations).filter(P_Informations.id == order_id).first()    
        p_informations = db_session.query(P_Informations).all()
        for p_information in p_informations:
            if p_information.id== order_id:
                name = p_information.name
                phone = p_information.phone
                address = p_information.address
                addr_number = p_information.addr_number
            else:
                name = 'nobody'
                phone = '0912345678'
                address = 'xxx'
                addr_number = '600'


        #產生資料後就append到item_box_component等等會用到
        #透過BubbleContainer產生收據格式
        message = [
            FlexSendMessage(
                alt_text='收據',
                contents={
                "type": "bubble",
                "size": "kilo",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "收據",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "愛釣客",
                        "weight": "bold",
                        "size": "xxl",
                        "margin": "none",
                        "color": "#4493A3"
                    },
                    {
                        "type": "text",
                        "text": "線上購物商城",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "sm"
                    },
                       {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "購買明細",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#86340A"
                        }
                        ],
                        "paddingTop": "5px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": item_box_component,
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": '總共NT${total}'.format(total=self.amount),
                            "size": "15px",
                            "align": "end",
                            "weight": "bold",
                            "color": "#4D4D4D"
                        }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "收件資訊",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#86340A"
                        }
                        ],
                        "paddingTop": "5px"
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
                                "text": name,
                                "size": "md",
                                "offsetBottom": "2px",
                                "offsetStart": "3px",
                                "color": "#4D4D4D",
                                "weight": "bold"
                            }
                            ]
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
                                "text": phone,
                                "size": "md",
                                "offsetBottom": "2px",
                                "offsetStart": "3px",
                                "color": "#4D4D4D",
                                "weight": "bold"
                            }
                            ]
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
                                "text": addr_number,
                                "size": "md",
                                "offsetBottom": "2px",
                                "offsetStart": "3px",
                                "color": "#4D4D4D",
                                "weight": "bold"
                            }
                            ]
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
                                "text": address,
                                "size": "md",
                                "offsetBottom": "2px",
                                "offsetStart": "3px",
                                "color": "#4D4D4D",
                                "weight": "bold"
                            }
                            ]
                        }
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    }
                    ]
                }
                }),
            TextSendMessage(text='本商城預設出貨時間為10天，如訂購商品皆有庫存，寄出時間為1-3天(不含連假)，若無庫存則需等待3-10天，造成不便敬請見諒。')]

        return message #return回給app.py裡的 confirm()這裡message = order.display_receipt()再push給user