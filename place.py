from linebot.models import *
#from config import Config

# 即時天氣&預報天氣用
city_list = [
    '基隆市','宜蘭縣','花蓮縣',
    '台北市','新北市','桃園市',
    '新竹市','新竹縣','苗栗縣',
    '彰化縣','雲林縣','南投縣',
    '台中市','嘉義市','嘉義縣',
    '高雄市','台南市','屏東縣',
    '澎湖縣','金門縣','臺東縣',
    '連江縣']

# 主要港口清單
def port_nameNo(portName):
    port_list={
        "臺北港":"H001",
        "基隆港":"H002",
        "臺中港":"H003",
        "高雄港":"H004",
        "花蓮港":"H005",
        "蘇澳港":"H006",
        "布袋港":"H007",
        "安平港":"H008",
        "澎湖港(馬公)":"H009",
        "澎湖港(龍門)":"H010",
    }
    try: portNum = port_list[portName]
    except: return "查無此港口"
    return portNum

####################縣市選單(即時、預報)####################
# 全台縣市選單(22個)-即時天氣+預報天氣
def select_city(mat):
    if mat=='即時天氣':
        message_1='請問要查詢'
        message_2='的那個地區'
    elif mat=='天氣預報':
        message_1='我要查詢'
        message_2='的預報天氣'
    flex_message = FlexSendMessage(
        alt_text="請選擇想查詢的縣市：",
        contents={
            "type": "bubble",
            "size": "mega",
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "全台縣市選單",
                    "color": "#4493A3",
                    "margin": "md",
                    "size": "xl",
                    "weight": "bold",
                    "wrap": True,
                    "adjustMode": "shrink-to-fit",
                    "offsetStart": "25px"
                }
                ],
                "paddingAll": "0px"
            },
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[0],
                        "text": message_1+city_list[0]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[3],
                        "text": message_1+city_list[3]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[6],
                        "text": message_1+city_list[6]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[9],
                        "text": message_1+city_list[9]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[12],
                        "text": message_1+city_list[12]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[15],
                        "text": message_1+city_list[15]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[18],
                        "text": message_1+city_list[18]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[21],
                        "text": message_1+city_list[21]+message_2
                        }
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "contents": [
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[1],
                        "text": message_1+city_list[1]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[4],
                        "text": message_1+city_list[4]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[7],
                        "text": message_1+city_list[7]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[10],
                        "text": message_1+city_list[10]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[13],
                        "text": message_1+city_list[13]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[16],
                        "text": message_1+city_list[16]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[19],
                        "text": message_1+city_list[19]+message_2
                        }
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "contents": [
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[2],
                        "text": message_1+city_list[2]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[5],
                        "text": message_1+city_list[5]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[8],
                        "text": message_1+city_list[8]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[11],
                        "text": message_1+city_list[11]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[14],
                        "text": message_1+city_list[14]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[17],
                        "text": message_1+city_list[17]+message_2
                        }
                    },
                    {
                        "type": "button",
                        "adjustMode": "shrink-to-fit",
                        "color": "#7EB5A6",
                        "style": "primary",
                        "margin": "sm",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": city_list[20],
                        "text": message_1+city_list[20]+message_2
                        }
                    }
                    ]
                }
                ],
                "paddingAll": "8px"
            }
        }
    )
    return flex_message

#######################最新氣象-圖片轉盤#######################
# 第一層-圖文選單->最新氣象->4格圖片
def img_Carousel():
    flex_message = FlexSendMessage(
        alt_text="請選擇查詢事項：",
        contents={
            "type": "bubble",
            "header": {
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
                            "url": "https://i.imgur.com/wQcsTzT.jpg",
                            "flex": 1,
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "潮汐預報"
                            },
                            "gravity": "center",
                            "aspectMode": "cover",
                            "size": "full"
                        },
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/jKqO32C.jpg",
                            "aspectMode": "cover",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "港口天氣"
                            },
                            "size": "full"
                        }
                        ],
                        "paddingAll": "0px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/KCCL1B2.jpg",
                            "aspectMode": "cover",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "即時天氣"
                            },
                            "size": "full"
                        },
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/Iwmkr0V.jpg",
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "150:150",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "天氣預報"
                            }
                        }
                        ],
                        "flex": 1,
                        "paddingAll": "0px"
                    }
                    ],
                    "paddingAll": "0px"
                }
                ],
                "paddingAll": "0px"
            }
        }
    )
    return flex_message

########################1+2.quick_reply########################
# 第二層-quick_reply(即時天氣+預測天氣)
def quick_reply_weather(mat):
    content_text = "請選擇您要查詢的天氣："
    text_message = TextSendMessage(
        text = content_text ,
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="查詢其它天氣",
                        text="其它"+mat, 
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="查詢已關注天氣",
                        text="我關注的天氣",
                    )
                ),
                QuickReplyButton(
                    action=LocationAction(
                        label="回傳地址查詢",
                    )
                )
            ]
        )
    )
    return text_message

###########################3.港口天氣###########################
# 第二層-港口天氣->3格圖片(主要港口、休閒漁港、海水浴場)
def img_port():
    flex_message = FlexSendMessage(
        alt_text="請選擇查詢事項：",
        contents={
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/30ESOqB.jpg",
                            "flex": 1,
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "主要港口"
                            },
                            "gravity": "center",
                            "aspectMode": "cover",
                            "aspectRatio": "16:9",
                            "size": "full"
                        }
                        ],
                        "paddingAll": "0px"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/r746Llv.jpg",
                            "aspectMode": "cover",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "海水浴場"
                            },
                            "size": "full"
                        },
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/7MU7NtV.jpg",
                            "aspectMode": "cover",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "休閒漁港"
                            },
                            "size": "full"
                        }
                        ],
                        "flex": 1,
                        "paddingAll": "0px"
                    }
                    ],
                    "paddingAll": "0px"
                }
                ],
                "paddingAll": "0px"
            }
        }
    )
    return flex_message

####待測試,還沒寫完
########################quick_reply-主要港口、休閒漁港、海水浴場########################
# 第三層-quick_reply(主要港口)
def quick_reply_port(mat):
    if mat=='主要港口即時天氣':
        message_1='查詢主要港口'
        message_2='台灣主要港口選單'
        message_3='已關注的主要港口'
    elif mat=='休閒漁港即時天氣':
        message_1='查詢休閒漁港'
        message_2='我想查詢休閒漁港'
        message_3='已關注的休閒漁港'
    elif mat=='海水浴場即時天氣':
        message_1='查詢海水浴場'
        message_2='我想查詢海水浴場'
        message_3='已關注的海水浴場'
    content_text = "請選擇您要查詢的天氣："
    text_message = TextSendMessage(
        text = content_text ,
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label=message_1,
                        text=message_2, 
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label=message_3,
                        text="我關注的天氣",
                    )
                )
            ]
        )
    )
    return text_message

###########################4.潮汐預報###########################
# 第二層-潮汐預報->3格圖片(地方鄉鎮、休閒漁港、海水浴場)
def img_tidal():
    flex_message = FlexSendMessage(
        alt_text="請選擇查詢事項：",
        contents={
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/cc2QZV7.jpg",
                            "aspectRatio": "16:9",
                            "flex": 1,
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "我想知道地方鄉鎮的潮汐預報"
                            },
                            "gravity": "center",
                            "aspectMode": "cover",
                            "size": "full"
                        }
                        ],
                        "paddingAll": "0px"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/r746Llv.jpg",
                            "size": "full",
                            "aspectMode": "cover",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "我想知道海水浴場的潮汐預報"
                            }
                        },
                        {
                            "type": "image",
                            "url": "https://i.imgur.com/7MU7NtV.jpg",
                            "size": "full",
                            "aspectMode": "cover",
                            "gravity": "center",
                            "action": {
                            "type": "message",
                            "label": "action",
                            "text": "我想知道休閒漁港的潮汐預報"
                            }
                        }
                        ],
                        "flex": 1,
                        "offsetTop": "0px"
                    }
                    ],
                    "paddingAll": "0px"
                }
                ],
                "paddingAll": "0px"
            }
        }
    )
    return flex_message