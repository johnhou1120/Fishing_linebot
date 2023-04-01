from os import WIFEXITED
from re import M
from sqlalchemy import Column,String,Integer
from linebot.models import *
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.operators import asc_op
from database import Base,db_session
from urllib.parse import quote #使用者自動輸入專用，可避免空白輸入
#產品選單的表格
class Products(Base):
    __tablename__ = 'products'
    
    id = Column(Integer,primary_key=True)
    type = Column(String)
    product1 = Column(String)
    price1 = Column(String)
    product_image_url1 = Column(String)
    product2 = Column(String)
    price2 = Column(String)
    product_image_url2 = Column(String)
    product3 = Column(String)
    price3 = Column(String)
    product_image_url3 = Column(String)

    @staticmethod
    def list_all():
        products = db_session.query(Products).all()#抓取資料庫中所有產品的資料
       
        bubbles = []
        i = 0 
        for product in products:
          
            bubble={
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "url": 'https://i.imgur.com/UC88Ryk.jpg'
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": "{}🎣".format(product.type),
                                "weight": "bold",
                                "size": "xl",
                                "color": "#E88400"
                            }
                            ],
                            "height": "18%"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "image",
                                        "url": product.product_image_url1,
                                        "aspectRatio": "1:1",
                                        "size": "5xl",
                                        "flex": 3,
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product1
                                        }
                                    }
                                    ],
                                    "flex": 3,
                                    "borderColor": "#000000",
                                    "borderWidth": "light",
                                    "offsetTop": "10px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": product.product1,
                                        "weight": "bold",
                                        "size": "lg",
                                        "color": "#86340A",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product1
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": product.price1,
                                        "size": "md",
                                        "color": "#CACACA",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product1
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "⤣ 點擊圖片查看更多....",
                                        "size": "sm",
                                        "color": "#000000",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product1
                                        }
                                    }
                                    ],
                                    "flex": 7,
                                    "alignItems": "center",
                                    "justifyContent": "center"
                                }
                                ],
                                "height": "32%",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "paddingBottom": "20px"
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
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "image",
                                        "url": product.product_image_url2,
                                        "aspectRatio": "1:1",
                                        "size": "5xl",
                                        "flex": 3,
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product2
                                        }
                                    }
                                    ],
                                    "flex": 3,
                                    "borderColor": "#000000",
                                    "borderWidth": "light",
                                    "offsetTop": "10px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": product.product2,
                                        "weight": "bold",
                                        "size": "lg",
                                        "color": "#86340A",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product2
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": product.price2,
                                        "size": "md",
                                        "color": "#CACACA",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product2
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "⤣ 點擊圖片查看更多",
                                        "size": "sm",
                                        "color": "#000000",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product2
                                        }
                                    }
                                    ],
                                    "flex": 7,
                                    "alignItems": "center",
                                    "justifyContent": "center"
                                }
                                ],
                                "height": "32%",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "paddingBottom": "20px"
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
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "image",
                                        "url": product.product_image_url3,
                                        "aspectRatio": "1:1",
                                        "size": "5xl",
                                        "flex": 3,
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product3
                                        }
                                    }
                                    ],
                                    "flex": 3,
                                    "borderColor": "#000000",
                                    "borderWidth": "light",
                                    "offsetTop": "10px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": product.product3,
                                        "weight": "bold",
                                        "size": "lg",
                                        "color": "#86340A",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product3
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": product.price3,
                                        "size": "md",
                                        "color": "#CACACA",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product3
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "⤣ 點擊圖片查看更多",
                                        "size": "sm",
                                        "color": "#000000",
                                        "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data":product.product3
                                        }
                                    }
                                    ],
                                    "flex": 7,
                                    "alignItems": "center",
                                    "justifyContent": "center"
                                }
                                ],
                                "height": "32%",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "paddingBottom": "20px"
                            }
                            ],
                            "height": "95%",
                            "margin": "sm",
                            "spacing": "sm",
                            "paddingBottom": "20px",
                            "offsetBottom": "19px"
                        }
                        ],
                        "height": "330px",
                        "offsetBottom": "5px",
                        "paddingBottom": "20px"
                    }   
                }

            bubbles.append(bubble)
            i = i + 1
        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='產品選單', contents=carousel_container)

        return message
    def menu_all(x='HR SLOW JIGGING III R'):
        products = db_session.query(Products).all()#抓取資料庫中所有產品的資料
        for product in products:
            if x==product.product1:
                message = FlexSendMessage(
                    alt_text='產品選單', 
                    contents={
                        "type": "bubble",
                        "size": "mega",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": product.product1,
                                "weight": "bold",
                                "size": "lg",
                                "align": "center",
                                "color": "#86340A"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "image",
                                    "url": product.product_image_url1,
                                    "size": "full",
                                    "aspectRatio": "1:1",
                                    "aspectMode": "cover",
                                    "action": {
                                    "type": "uri",
                                    "uri": "http://linecorp.com/"
                                    }
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": product.price1,
                                    "size": "md",
                                    "flex": 7,
                                    "weight": "bold",
                                    "color": "#4D4D4D"
                                }
                                ],
                                "alignItems": "center"
                            }
                            ]
                        }
                        }
                    )

 
            elif x==product.product2:
                message = FlexSendMessage(
                    alt_text='產品選單', 
                    contents={
                        "type": "bubble",
                        "size": "mega",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": product.product2,
                                "weight": "bold",
                                "size": "lg",
                                "align": "center",
                                "color": "#86340A"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "image",
                                    "url": product.product_image_url2,
                                    "size": "full",
                                    "aspectRatio": "1:1",
                                    "aspectMode": "cover",
                                    "action": {
                                    "type": "uri",
                                    "uri": "http://linecorp.com/"
                                    }
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": product.price2,
                                    "size": "md",
                                    "flex": 7,
                                    "weight": "bold",
                                    "color": "#4D4D4D"
                                }
                                ],
                                "alignItems": "center"
                            }
                            ]
                        }
                        }
                    )
                
            elif x==product.product3:
                message = FlexSendMessage(
                    alt_text='產品選單', 
                    contents={
                        "type": "bubble",
                        "size": "mega",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": product.product3,
                                "weight": "bold",
                                "size": "lg",
                                "align": "center",
                                "color": "#86340A"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "image",
                                    "url": product.product_image_url3,
                                    "size": "full",
                                    "aspectRatio": "1:1",
                                    "aspectMode": "cover",
                                    "action": {
                                    "type": "uri",
                                    "uri": "http://linecorp.com/"
                                    }
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "md",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": product.price3,
                                    "size": "md",
                                    "flex": 7,
                                    "weight": "bold",
                                    "color": "#4D4D4D"
                                }
                                ],
                                "alignItems": "center"
                            }
                            ]
                        }
                        }
                    )

        return  message
    def product_all():
        products = db_session.query(Products).all()#抓取資料庫中所有產品的資料
        product_list=[]
        for product in products:
                   product_list.append(product.product1)
                   product_list.append(product.product2)
                   product_list.append(product.product3)
        return product_list