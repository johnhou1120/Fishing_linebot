# https://fishinglinebot.herokuapp.com/callback
# 載入LineBot所需要的套件
from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from urllib.parse import parse_qsl ,quote #quote-使用者自動輸入專用，可避免空白輸入
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import json
import uuid
import os
import time

from config import Config
from user import Users
from fishmap import Fishingmaps
from report import Reports
from reportbuff import Buffer
from database import db_session,init_db
from item import Items
from product import Products
from menuproduct import Menuproducts
from cart import Cart
from p_information import P_Informations,Input_Information
from order import Orders
from linepay import LinePay
import place, database, Message

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(Config.CHANNEL_ACCESS_TOKEN)
# Channel Secret
handler = WebhookHandler(Config.CHANNEL_SECRET)
print('🔊可以開始使用囉🔊')

#暫存用dict
mat_d={}
pointName_d={}  #海水浴場即時天氣無用到，其它皆有
pointNum_d={}   #主要港口即時天氣、海水浴場即時天氣
mat_tidal={}    #潮汐用,主要用於csv裡sort的判斷

def is_ascii(s):
    return all(ord(c) < 128 for c in s)
    
# 加上這個function可以幫我們每一次執行完後都回關閉資料庫連線
@app.teardown_appcontext 
def shutdown_session(exception=None):
    db_session.remove()

#建立或取得user
def get_or_create_user(user_id):
    # 從id=user_id先搜尋有沒有這個user,如果有的話直接return
    user = db_session.query(Users).filter_by(id=user_id).first()
    # 沒有的話就透過line_bot_api來取得用戶資訊
    if not user:
        profile = line_bot_api.get_profile(user_id)
        # 然後在建立user並且存入資料庫當中
        user = Users(id=user_id, nick_name = profile.display_name, image_url = profile.picture_url)
        db_session.add(user)
        db_session.commit()
    return user

# Line_Pay用
@app.route("/confirm")
def confirm():
    transaction_id = request.args.get('transactionId')
    order = db_session.query(Orders).filter(Orders.transaction_id == transaction_id).first()
    if order:
        line_pay = LinePay()
        line_pay.confirm(transaction_id=transaction_id, amount=order.amount)
        order.is_pay = True#確認收款無誤時就會改成已付款
        db_session.commit()
        #傳收據給用戶 問題在這裡！！
        
        message = order.display_receipt()
        line_bot_api.push_message(order.user_id,messages=message)

        return '<h1>您的付款已成功，感謝您的購買</h1>'

# 接收 LINE 的資訊-監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)
    return 'OK'

###########################以下為處理程式##########################
# selenium 取即時天氣、港口即時天氣、休閒漁港即時天氣、海水浴場即時天氣用
def use_selenium(api_link):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # options=Options()   #本機用
    options=webdriver.ChromeOptions()  #上傳Heroku用
    options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")  #上傳Heroku用
    #關閉瀏覽器跳出訊息
    prefs = {
        'profile.default_content_setting_values' :
        {
            'notifications' : 2
            }
        }
    options.add_experimental_option('prefs',prefs)
    options.add_argument("--headless")            #不開啟實體瀏覽器背景執行
    options.add_argument("--incognito")           #開啟無痕模式
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    #win用
    #driver=webdriver.Chrome(options=options)
    #上傳Heroku用
    driver=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)
    
    driver.get(api_link)
    soup=BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊ weather ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
##############################即時類##############################
# 即時天氣-無地圖,有tip；接收地點名稱(ex:高雄市三民區),從csv裡比對取得id後查詢
# mat_d=即時天氣
def get_now_weather(pointName,uid):
    pointName_d[uid]=pointName
    pointNum_d[uid]='Null'
    if pointName[:2]=='臺中' or pointName[:2]=='臺南' or pointName[:2]=='臺北':
        pointName=pointName[0].replace('臺','台')+pointName[1:]
    df=pd.read_csv('./file/district.csv',encoding='big5')
    dfs=df[(df['縣市名稱']==pointName[:3])&(df['區鄉鎮名稱']==pointName[3:])]
    if len(dfs)>0:
        pointNum=str(dfs.iloc[0,1])
        if (pointName[:3]=='連江縣' or pointName[:3]=='金門縣'):
            pointNum='0'+pointNum
        api_link='https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=%s' % (pointNum) #ID改成需要的行政區域
    soup=use_selenium(api_link)
    if soup != '':
        res=json.load(open('./json/card_tem.json','r',encoding='utf-8'))   #讀取輪播模版
        show_now=json.load(open('./json/show_now.json','r',encoding='utf-8'))    #讀取呈現即時天氣模版
        #截取各項要呈現的數值
        show_now['body']['contents'][0]['text']=pointName+' 即時天氣'    # title
        show_now['body']['contents'][1]['contents'][1]['text']=soup.select('span.GT_Time')[0].text          #資料時間
        show_now['body']['contents'][2]['text']=soup.select('a.marquee')[0].text.strip('看更多')             #小提醒 tip
        show_now['body']['contents'][4]['contents'][0]['contents'][1]['text']=soup.select('td span.GT_T span')[0].text+' °C'   #現在溫度
        show_now['body']['contents'][4]['contents'][1]['contents'][1]['text']=soup.select('td span.GT_AT span')[0].text+' °C'  #體感溫度
        show_now['body']['contents'][4]['contents'][2]['contents'][1]['text']=soup.select('td span.GT_RH')[0].text            #相對溼度
        show_now['body']['contents'][4]['contents'][3]['contents'][1]['text']=soup.select('td span.GT_Rain')[0].text          #時雨量
        show_now['body']['contents'][4]['contents'][4]['contents'][1]['text']=soup.select('td span.GT_Sunrise')[0].text       #日出時間
        show_now['body']['contents'][4]['contents'][5]['contents'][1]['text']=soup.select('td span.GT_Sunset')[0].text        #日落時間
        #查詢潮汐預報-data->tai=pointName&mat_tidal&uid
        show_now['body']['contents'][4]['contents'][6]['action']['data']='tai='+pointName+'&'+'潮汐鄉鎮'
        show_now['body']['contents'][4]['contents'][6]['action']['displayText']=pointName+'潮汐預報查詢中'
        #建立LINE訊息要出現的內容
        res['contents'].append(show_now)
    else: 
        res=''
    return res
    time.sleep(3)

# 主要港口即時天氣-有地圖,無tip；接收已經取得的港口編號,並代入網址id後查詢
# mat_d=主要港口即時天氣
def get_port_now_weather(portNum,portName,uid):
    pointName_d[uid]=portName
    pointNum_d[uid]=portNum
    if len(portNum)>0:
        api_link='https://www.cwb.gov.tw/V8/C/L/Port/Port.html?QS=&PID=%s' % (portNum) #需改成需要的港口ID
    soup=use_selenium(api_link)
    if soup != '':
        res=json.load(open('./json/card_tem.json','r',encoding='utf-8'))   #讀取輪播模版
        show_now=json.load(open('./json/show_now_noTip_main.json','r',encoding='utf-8'))    #讀取呈現主要港口天氣模版
        #截取各項要呈現的數值
        show_now['body']['contents'][0]['text']=portName+' 即時天氣'   # title
        show_now['body']['contents'][1]['contents'][1]['text']=soup.select('span#GT_Time')[0].text          #資料時間
        show_now['body']['contents'][3]['contents'][0]['contents'][1]['text']=soup.select('span#GT_C_T')[0].text+' °C'   #現在溫度
        show_now['body']['contents'][3]['contents'][1]['contents'][1]['text']=soup.select('span#GT_C_AT')[0].text+' °C'  #體感溫度
        show_now['body']['contents'][3]['contents'][2]['contents'][1]['text']=soup.select('span#GT_RH')[0].text+' %'         #相對溼度
        show_now['body']['contents'][3]['contents'][3]['contents'][1]['text']=soup.select('span#GT_Rain')[0].text+' mm'       #時雨量
        show_now['body']['contents'][3]['contents'][4]['contents'][1]['text']=soup.select('span#GT_Sunrise')[0].text    #日出時間
        show_now['body']['contents'][3]['contents'][5]['contents'][1]['text']=soup.select('span#GT_Sunset')[0].text     #日落時間
        # 查看地圖-data=loc=title&address&latitude&longitude＝>loc=高雄港&地址&latitude緯度&longitude經度
        show_now['body']['contents'][3]['contents'][6]['contents'][0]['action']['data']='loc='+soup.select('div.margin-top-50 h4')[0].text+'&'+soup.select('ul.small-font li')[0].text[3:]+'&'+soup.select('ul.small-font li')[2].text[3:][:-1]+'&'+soup.select('ul.small-font li')[1].text[3:][:-1]
        show_now['footer']['contents'][0]['action']['data']='我要關注主要港口即時天氣'
        show_now['footer']['contents'][1]['action']['data']='我要刪除主要港口即時天氣'
        res['contents'].append(show_now)
    else: 
        res=''
    return res
    time.sleep(3)

# 休閒漁港即時天氣-有地圖,無tip；接收地點名稱(ex:七美),從csv裡比對取得PID後查詢
# mat_d=休閒漁港即時天氣
def get_fishing_port_now_weather(pointName,uid):
    pointName_d[uid]=pointName
    pointNum_d[uid]='Null'
    df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5')
    dfs=df[(df['sort']=='休閒漁港')&(df['web_name']==pointName)]
    if len(dfs)>0:
        pointNum=str(dfs.iloc[0,4])
        api_link='https://www.cwb.gov.tw/V8/C/L/Harbors/Harbors.html?QS=&PID=%s' % (pointNum) #ID改成需要的漁港代碼PID
    soup=use_selenium(api_link)
    if soup != '':
        res=json.load(open('./json/card_tem.json','r',encoding='utf-8'))
        show_now=json.load(open('./json/show_now_noTip_loc.json','r',encoding='utf-8'))
        #截取各項要呈現的數值
        show_now['body']['contents'][0]['text']=pointName+'漁港 即時天氣'   # title
        show_now['body']['contents'][1]['contents'][1]['text']=soup.select('span#GT_Time')[0].text          #資料時間
        show_now['body']['contents'][3]['contents'][0]['contents'][1]['text']=soup.select('span#GT_C_T')[0].text+' °C'   #現在溫度
        show_now['body']['contents'][3]['contents'][1]['contents'][1]['text']=soup.select('span#GT_C_AT')[0].text+' °C'  #體感溫度
        show_now['body']['contents'][3]['contents'][2]['contents'][1]['text']=soup.select('span#GT_RH')[0].text+' %'         #相對溼度
        show_now['body']['contents'][3]['contents'][3]['contents'][1]['text']=soup.select('span#GT_Rain')[0].text+' mm'       #時雨量
        show_now['body']['contents'][3]['contents'][4]['contents'][1]['text']=soup.select('span#GT_Sunrise')[0].text    #日出時間
        show_now['body']['contents'][3]['contents'][5]['contents'][1]['text']=soup.select('span#GT_Sunset')[0].text     #日落時間
        #查詢潮汐預報-data->tai=pointName(ex:七美)&mat_tidal&uid
        show_now['body']['contents'][3]['contents'][6]['contents'][0]['action']['data']='tai=漁港'+pointName+'&'+'休閒漁港'
        show_now['body']['contents'][3]['contents'][6]['contents'][0]['action']['displayText']=pointName+'漁港潮汐預報查詢中'
        # 查看地圖-data=loc=title&address&latitude&longitude＝>loc=七美漁港&七美漁港&latitude緯度&longitude經度
        show_now['body']['contents'][3]['contents'][6]['contents'][1]['action']['data']='loc='+pointName+'漁港&'+str(dfs.iloc[0,1])+pointName+'漁港&'+str(dfs.iloc[0,6])+'&'+str(dfs.iloc[0,5])
        show_now['footer']['contents'][0]['action']['data']='我要關注休閒漁港即時天氣'
        show_now['footer']['contents'][1]['action']['data']='我要刪除休閒漁港即時天氣'
        res['contents'].append(show_now)
    else: 
        res=''
    return res
    time.sleep(3)

# 海水浴場即時天氣-有地圖,無tip；接收地點名稱(ex:旗津海岸公園海水浴場),從Postback取得PID後查詢
# mat_d=海水浴場即時天氣
def get_beach_port_now_weather(pointNum,uid):
    pointNum_d[uid]=pointNum
    if len(pointNum)>0:
        api_link='https://www.cwb.gov.tw/V8/C/L/Beach/Beach.html?QS=&PID=%s' % (pointNum) #ID改成需要的漁港代碼PID
    soup=use_selenium(api_link)
    if soup != '':
        res=json.load(open('./json/card_tem.json','r',encoding='utf-8'))
        show_now=json.load(open('./json/show_now_noTip_loc.json','r',encoding='utf-8'))
        df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5')
        #截取各項要呈現的數值
        pointName=soup.select('li#PageTitle')[0].text  # ex:西子灣
        dfs=df[(df['sort']=='海水浴場')&(df['web_name']==pointName)]
        show_now['body']['contents'][0]['text']=pointName+'海水浴場 即時天氣'   # title
        show_now['body']['contents'][1]['contents'][1]['text']=soup.select('span#GT_Time')[0].text          #資料時間
        show_now['body']['contents'][3]['contents'][0]['contents'][1]['text']=soup.select('span#GT_C_T')[0].text+' °C'   #現在溫度
        show_now['body']['contents'][3]['contents'][1]['contents'][1]['text']=soup.select('span#GT_C_AT')[0].text+' °C'  #體感溫度
        show_now['body']['contents'][3]['contents'][2]['contents'][1]['text']=soup.select('span#GT_RH')[0].text+' %'         #相對溼度
        show_now['body']['contents'][3]['contents'][3]['contents'][1]['text']=soup.select('span#GT_Rain')[0].text+' mm'       #時雨量
        show_now['body']['contents'][3]['contents'][4]['contents'][1]['text']=soup.select('span#GT_Sunrise')[0].text    #日出時間
        show_now['body']['contents'][3]['contents'][5]['contents'][1]['text']=soup.select('span#GT_Sunset')[0].text     #日落時間
        #查詢潮汐預報-data->tai=pointName(ex:西子灣)&mat_tidal&uid
        show_now['body']['contents'][3]['contents'][6]['contents'][0]['action']['data']='tai=海水浴場'+pointName+'&'+'海水浴場'
        show_now['body']['contents'][3]['contents'][6]['contents'][0]['action']['displayText']=pointName+'海水浴場潮汐預報查詢中'
        # 查看地圖-data=loc=title&address&latitude&longitude＝>loc=高雄港&地址&latitude緯度&longitude經度
        show_now['body']['contents'][3]['contents'][6]['contents'][1]['action']['data']='loc='+pointName+'&'+str(dfs.iloc[0,1])+pointName+'&'+str(dfs.iloc[0,6])+'&'+str(dfs.iloc[0,5])
        show_now['footer']['contents'][0]['action']['data']='我要關注海水浴場即時天氣'
        show_now['footer']['contents'][1]['action']['data']='我要刪除海水浴場即時天氣'
        res['contents'].append(show_now)
    else: 
        res=''
    pointName_d[uid]=pointName
    return res
    time.sleep(3)
####################################預報類####################################
# 預報天氣-36小時預報
# mat_d=天氣預報
def get_36h_weather(city_name,uid):
    pointName_d[uid]=city_name
    pointNum_d[uid]='Null'
    user_key=Config.Air_key
    api_link='https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=%s&format=JSON&locationName=%s' % (user_key,str(city_name))
    html=requests.get(api_link)
    Data=(json.loads(html.text,encoding='utf-8'))['records']['location'][0]['weatherElement']
    res=json.load(open('./json/card_tem.json','r',encoding='utf-8'))   #讀取輪播模版
    for j in range(3):
        show_w36h=json.load(open('./json/show_w36h.json','r',encoding='utf-8'))
        show_w36h['body']['contents'][1]['text']=city_name+'未來 36 小時天氣'    # title
        show_w36h['body']['contents'][2]['contents'][0]['text']='{} ~ {}'.format(Data[0]['time'][j]['startTime'][5:-3],Data[0]['time'][j]['endTime'][5:-3])   # time 時間
        show_w36h['body']['contents'][4]['contents'][0]['contents'][1]['text']=Data[0]['time'][j]['parameter']['parameterName']       # weather 天氣狀況
        show_w36h['body']['contents'][4]['contents'][1]['contents'][1]['text']='{}°C ~ {}°C'.format(Data[2]['time'][j]['parameter']['parameterName'],Data[4]['time'][j]['parameter']['parameterName'])   # temp 溫度狀況
        show_w36h['body']['contents'][4]['contents'][2]['contents'][1]['text']=Data[1]['time'][j]['parameter']['parameterName']+'%'  # rain 降雨機率
        show_w36h['body']['contents'][4]['contents'][3]['contents'][1]['text']=Data[3]['time'][j]['parameter']['parameterName']  # comfort 舒適度
        res['contents'].append(show_w36h)
    return res
    time.sleep(3)

# 潮汐1個月預報-取前3天,有地圖(鄉鎮、休閒漁港、海水浴場)
# mat_d=潮汐鄉鎮or休閒漁港潮汐or海水浴場潮汐
def get_tidal(pointName,mat_tidal,uid):
    pointName_d[uid]=pointName  #澎湖縣七美鄉/漁港白沙/海水浴場大安
    print('mat_tidal=',mat_tidal)
    user_key=Config.Air_key
    api_link='https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-A0021-001?Authorization=%s&format=JSON&locationName=%s&sort=validTime' % (user_key,str(pointName))
    html=requests.get(api_link)
    Data=(json.loads(html.text,encoding='utf-8'))['records']['location'][0]['validTime'][:3] #取前3天的預報
    res=json.load(open('./json/card_tem.json','r',encoding='utf-8'))   #讀取輪播模版-第一天
    df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5')
    dfs=df[(df['sort']==mat_tidal)&(df['locationName']==pointName)]
    if mat_tidal=='海水浴場':
        pointName=pointName[4:]+'海水浴場'
    elif mat_tidal=='休閒漁港':
        pointName=pointName[2:]+'漁港'
    for i in range(len(Data)):
        oneday=[]
        oneday_list=''
        show_tidal=json.load(open('./json/show_tidal_new.json','r',encoding='utf-8'))
        show_tidal['body']['contents'][0]['text']=pointName #地方名
        show_tidal['body']['contents'][2]['text']='{}/{}'.format(Data[i]['startTime'][5:7],Data[i]['startTime'][8:10])   # 預報開始時間~預報結束時間,3天,Data[i-0:2]
        show_tidal['body']['contents'][3]['contents'][1]['text']=Data[i]['weatherElement'][0]['elementValue']
        show_tidal['body']['contents'][4]['contents'][1]['text']=Data[i]['weatherElement'][1]['elementValue']
        # 查詢即時天氣-data->now=pointName&mat_tidal&uid
        show_tidal['body']['contents'][6]['contents'][0]['contents'][2]['contents'][0]['action']['data']='now='+pointName+'&'+mat_tidal
        # 查詢即時天氣-displayText=pointName即時天氣查詢中
        show_tidal['body']['contents'][6]['contents'][0]['contents'][2]['contents'][0]['action']['displayText']=pointName+'即時天氣查詢中'
        # 查看地圖-data->loc=title&address&latitude&longitude＝>loc=高雄市小港區&地址&latitude緯度&longitude經度
        show_tidal['body']['contents'][6]['contents'][0]['contents'][2]['contents'][1]['action']['data']='loc='+pointName+'&'+str(dfs.iloc[0,1])+pointName+'&'+str(dfs.iloc[0,6])+'&'+str(dfs.iloc[0,5])
        #1日潮汐資料-1天4筆=['time'][J-0~3]
        for j in range(len(Data[i]['weatherElement'][2]['time'])):
            #時間=Data[i-0:2]['weatherElement'][2]['time'][j-0:3]['dataTime']
            tidal_time=Data[i]['weatherElement'][2]['time'][j]['dataTime'][11:-3]+'\t'
            #潮汐=Data[i-0:2]['weatherElement'][2]['time'][j-0:3]['parameter'][0]['parameterValue']
            tidal=Data[i]['weatherElement'][2]['time'][j]['parameter'][0]['parameterValue']+'\t'
            #潮高(當地),單位:cm=Data[i-0:2]['weatherElement'][2]['time'][j-0:3]['parameter'][2]['parameterValue']
            tidal_loc=Data[i]['weatherElement'][2]['time'][j]['parameter'][2]['parameterValue']+'cm\n'
            oneday.append(tidal_time+tidal+tidal_loc)
            oneday.sort()  #依時間排序
        for k in range(len(oneday)):
            oneday_list+=oneday[k]
        show_tidal['body']['contents'][6]['contents'][0]['contents'][1]['contents'][0]['text']=oneday_list
        res['contents'].append(show_tidal)
    return res
    time.sleep(3)

###############################回傳Postback訊息用###############################
# 接收回傳Postback(!!Postback的屬性沒有message，所以無法取得message)
@handler.add(PostbackEvent)
def sendPosition(event):
    print('Activate PostbackEvent')
    #抓使用者的資料
    profile=line_bot_api.get_profile(event.source.user_id)
    uid=profile.user_id #使用者ID
    user_name = profile.display_name   #使用者名稱
    p_data=event.postback.data
    print('p_data='+p_data)
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊weather＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
# 傳送位置地圖/接收海水浴場即時天氣用的PID碼/接收海水浴場潮汐預報用的locationName
    # 查看地圖用
    if p_data[:3]=='loc':
        # loc=title&add&latitude&longitude＝高雄港&地址&latitude緯度&longitude經度
        locat_data=p_data[4:].split('&')
        try:
            message = LocationSendMessage(
                title=locat_data[0],
                address=locat_data[1],
                latitude=locat_data[2],  #緯度
                longitude=locat_data[3]  #經度
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
    
    #查詢海水浴場即時天氣用
    if p_data[:3]=='PID':
        mat_d[uid]='海水浴場即時天氣'
        pointNum=str(p_data[4:])
        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢海水浴場的即時天氣，請稍候..."))
        content=get_beach_port_now_weather(pointNum,uid)  #呼叫def程式-查詢海水浴場即時天氣
        if content !='':
            line_bot_api.reply_message(event.reply_token,FlexSendMessage('海水浴場的即時天氣',content))
        else: 
            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此海水浴場名稱，請重新輸入。'))
    
    #查詢海水浴場潮汐用
    if p_data[:5]=='beach':
        # beach=海水浴場大安
        mat_d[uid]='海水浴場潮汐'
        mat_t=mat_tidal.get(uid)
        pointName=str(p_data[6:]) #海水浴場大安
        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢海水浴場的潮汐預報，請稍候..."))
        content=get_tidal(pointName,mat_t,uid)  #呼叫def程式-查詢潮汐預報
        if content !='':
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'{pointName}的潮汐預報',content))
        else: 
            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此海水浴場名稱，請重新輸入。'))
    
    #我要關注即時天氣/我要關注天氣預報/我要關注主要港口即時天氣
    if p_data[:4]=='我要關注':
        print('mat_d[uid]=',mat_d[uid])
        print('p_data[4:]=',p_data[4:])
        print('pointName_d[uid]=',pointName_d[uid])
        print('pointNum_d[uid]=',pointNum_d[uid])
        if mat_d[uid]==p_data[4:]:
            print('開始關注'+pointName_d[uid]+'的'+p_data[4:])
            try:
                content=database.add_my_weather(uid,mat_d[uid],pointName_d[uid],pointNum_d[uid])
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content))
            except:
                line_bot_api.reply_message(event.reply_token,TextSendMessage('無法確認您目前想做什麼，請重新選擇。'))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage('無法確認您目前想做什麼，請重新選擇。'))
    
    #我要刪除即時天氣/我要刪除天氣預報/我要刪除主要港口即時天氣
    if p_data[:4]=='我要刪除':
        print('mat_d[uid]=',mat_d[uid])
        print('p_data[4:]=',p_data[4:])
        print('pointName_d[uid]=',pointName_d[uid])
        print('pointNum_d[uid]=',pointNum_d[uid])
        if mat_d[uid]==p_data[4:]:
            print('正在刪除您所關注的'+p_data[4:]+'-'+pointName_d[uid])
            try:
                content=database.del_my_weather(uid,mat_d[uid],pointName_d[uid],pointNum_d[uid])
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content))
            except:
                line_bot_api.reply_message(event.reply_token,TextSendMessage('無法確認您目前想做什麼，請重新選擇。'))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage('無法確認您目前想做什麼，請重新選擇。'))
    
    #從潮汐預報結果回查即時天氣用
    if p_data[:3]=='now':
        #now=pointName(澎湖縣七美鄉/大安海水浴場/七美漁港)&mat_tidal(潮汐鄉鎮/休閒漁港/休閒漁港)&uid
        now_data=p_data[4:].split('&')    #澎湖縣七美鄉/大安海水浴場/七美漁港
        mat=now_data[1]         #潮汐鄉鎮/休閒漁港/休閒漁港
        if mat=='休閒漁港' or mat=='海水浴場':
            if mat=='休閒漁港':
                mat_d[uid]='休閒漁港即時天氣'
                pointName=now_data[0].strip('漁港')
                line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}漁港的即時天氣，請稍候..."))
                content=get_fishing_port_now_weather(pointName,uid)  #呼叫def程式-休閒漁港即時天氣查詢
                if content !='':
                    line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
                else: 
                    line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此漁港名稱，請重新輸入。'))
            elif mat=='海水浴場':
                mat_d[uid]='海水浴場即時天氣'
                pointName=now_data[0].strip('海水浴場')
                df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5')
                dfs=df[(df['sort']=='海水浴場')&(df['web_name']==pointName)]
                if len(dfs)>0:
                    pointNum=str(dfs.iloc[0,4])
                line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢海水浴場的即時天氣，請稍候..."))
                content=get_beach_port_now_weather(pointNum,uid)  #呼叫def程式-查詢海水浴場即時天氣
                if content !='':
                    line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'海水浴場的即時天氣',content))
                else: 
                    line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此海水浴場名稱，請重新輸入。'))
        elif mat=='潮汐鄉鎮':
            mat_d[uid]='即時天氣'
            pointName=now_data[0]
            line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的即時天氣，請稍候..."))
            content=get_now_weather(pointName,uid)  #呼叫def程式-查詢即時天氣
            if content !='':
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此縣市區鄉鎮名稱，請重新輸入。'))
    
    #從即時天氣結果查詢潮汐預報用
    if p_data[:3]=='tai':
        #tai=pointName&mat_tidal(潮汐鄉鎮/休閒漁港/海水浴場)
        tai_data=p_data[4:].split('&')
        mat_ti=tai_data[1]
        df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5')
        if mat_ti=='潮汐鄉鎮':
            mat_d[uid]=='潮汐鄉鎮'
            pointName=tai_data[0]           ##澎湖縣七美鄉
            if pointName[:2]=='台中' or pointName[:2]=='台南' or pointName[:2]=='台北':
                pointName=pointName[0].replace('台','臺')+pointName[1:]
            dfs=df[(df['sort']=='潮汐鄉鎮')&(df['locationName']==pointName)]
            if len(dfs)>0:
                line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的潮汐預報，請稍候..."))
                content=get_tidal(pointName,mat_ti,uid)  #呼叫def程式-查詢潮汐預報
                if content !='':
                    line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'{pointName}的潮汐預報',content))
                else: 
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(f'查無此{pointName}的潮汐預報，請重新輸入。'))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage(f'查無此{pointName}的潮汐預報，請重新輸入。'))
        elif mat_ti=='休閒漁港':
            mat_d[uid]=='休閒漁港潮汐'
            pointName=tai_data[0]         #漁港七美
            line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢"+pointName[2:]+"漁港的潮汐預報，請稍候..."))
            content=get_tidal(pointName,mat_ti,uid)  #呼叫def程式-查詢潮汐預報
            pointName=pointName[2:] #漁港七美->七美
            if content !='':
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'{pointName}漁港的潮汐預報',content))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage(f'查無此{pointName}漁港的潮汐預報，請重新輸入。'))
        elif mat_ti=='海水浴場':
            mat_d[uid]=='海水浴場潮汐'
            pointName=tai_data[0]             #海水浴場西子灣
            line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢"+pointName[4:]+"海水浴場的潮汐預報，請稍候..."))
            content=get_tidal(pointName,mat_ti,uid)  #呼叫def程式-查詢潮汐預報
            if content !='':
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'{pointName[4:]}海水浴場的潮汐預報',content))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此海水浴場名稱，請重新輸入。'))

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊fishingmap and report＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    if p_data[:6]=='action':
        message = []
        report_buff = Buffer(user_id=event.source.user_id)
        data = dict(parse_qsl(event.postback.data))#先將postback中的資料轉成字典
        action = data.get('action')#再get action裡面的值
        if action == 'showmapoption':
            type= data.get('type')
            if type == '墾丁國家公園':
                message.append(ImageSendMessage(
                                original_content_url='https://i.imgur.com/Lhia2Cb.jpg',
                                preview_image_url='https://i.imgur.com/Lhia2Cb.jpg'
                            )
                )
            message.append(Fishingmaps.ShowLocationOfSelectedType(type))
        elif action == 'ReportStep1':
            location = data.get('location')
            report_buff.add(key = '所在地', val= location)
            message.append(Reports.report_step2_type())
        elif action == 'ReportStep2':
            type = data.get('type')
            report_buff.add(key = '垂釣類型', val= type)
            message.append(Reports.report_step3_fish())
        elif action == '我不想分享我的定位':
            message.append(Reports.report_step5_sharephoto())
        elif action == '我不想上傳圖片':
            message.append(report_buff.display())
        elif action == 'reportdone':
            report_data = report_buff.report() 
            Location = report_data.get('所在地')
            Type = report_data.get('垂釣類型')
            Address = report_data.get('地址')
            Latitude = report_data.get('緯度')
            Longitude= report_data.get('經度')
            Fish_type = report_data.get('魚種')
            Photo = report_data.get('photo')

            report_sql = Reports(user_id= uid, Location = Location, Type = Type, 
                    Address = Address, Latitude = Latitude, Longitude= Longitude,
                    Fish_type = Fish_type, Photo = Photo)

            db_session.add(report_sql)
            db_session.commit()      
            report_buff.reset()
            
            message.append(
                StickerSendMessage(
                    package_id='8522',
                    sticker_id='16581267'
                )
            )
        if message:
            line_bot_api.reply_message(event.reply_token,message)
        return 'OK'

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊商城＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    if mat_d[uid]=='漁夫裝備':
        cart = Cart(user_id=event.source.user_id)
        input_information = Input_Information(user_id=event.source.user_id)
    
        if event.postback.data in Products.product_all() :#產品選單點後啟動的規格頁面
            message=[
                Products.menu_all(x=event.postback.data),
                Menuproducts.format_list(x=event.postback.data)]
        elif event.postback.data in ['返回產品選單','繼續選購']:#由規格頁面回到產品選單&由購物車頁面回到產品選單
            message = Products.list_all()
        elif event.postback.data in Menuproducts.all_format():#規格頁面後進入商品確認
            message=Menuproducts.forat_check(x=event.postback.data)
        elif event.postback.data[:2]=='加入':#由確認頁面進入購物車
            forma_t= event.postback.data[2:]
            print(forma_t)
            num=1 #預設數量1
            cart.add(forma_t=forma_t,num=num) 
            if cart.bucket():
                message = cart.display() 
            else:
                message = TextSendMessage(text='您的購物車是空的') 
        elif event.postback.data[:2]=='數量':#更改產品數量時啟動的頁面
            num = int(event.postback.data[2])
            forma_t=event.postback.data[3:]
            cart.add(forma_t=forma_t,num=num) 
            if cart.bucket():
                message = cart.display() 
            else:
                message = TextSendMessage(text='您的購物車是空的') 
        elif event.postback.data[:4]=='更改數量': #更改產品數量時啟動的頁面中數量選擇
            forma_t= event.postback.data[4:]
            message=cart.change_number(name=forma_t)
        elif event.postback.data[:2]=='刪除':#購物車頁面的叉叉按鈕
            num=0
            forma_t=event.postback.data[2:] 
            cart.add(forma_t=forma_t,num=num) 
            if cart.bucket():
                message = cart.display() 
            else:
                message = TextSendMessage(text='您的購物車是空的') 
        elif event.postback.data=='結帳':#進入收件資料前的reply
            template=ConfirmTemplate(
                text='不繼續購買了嗎？那麽開始進行資料填寫嘍！',
                actions=[
                    PostbackAction(
                        label='返回購物車',
                        data='返回購物車',
                        text='返回購物車'),
                    PostbackAction(
                        label='進入資料填寫',
                        data='進入資料填寫',
                        text='進入資料填寫')])
            message=TemplateSendMessage(alt_text='cart_check',template=template)
        elif event.postback.data=='返回購物車':#選擇返回購物車
            if cart.bucket():
                message = cart.display() 
            else:
                message = TextSendMessage(text='您的購物車是空的') 
        elif event.postback.data=='進入資料填寫':#進入收件資訊頁面
            message = P_Informations.information_show()
        elif event.postback.data=='LinePay':
            if input_information.find():
                user_id = event.source.user_id
                order_id = uuid.uuid4().hex#如果有訂單的話就會使用uuid的套件來建立，因為它可以建立獨一無二的值
                a=[]
                b=[]
                for i,j in input_information.find().items():
                    a.append(i)
                    b.append(j)
                name = a[0]
                phone = b[0] 
                address = a[1]
                addr_number = b[1]
                total = 0 #總金額
                items = [] #暫存訂單項目
                
                p_information = P_Informations(
                                    id = order_id,
                                    name = name,
                                    phone=phone,
                                    address=address,
                                    addr_number=addr_number)
                for product_name, num in cart.bucket().items():#透過迴圈把項目轉成訂單項目物件
                    #透過產品名稱搜尋產品是不是存在
                    if num > 0:
                        forma_t = db_session.query(Menuproducts).filter(Menuproducts.forma_t.ilike(product_name)).first()
                        #接著產生訂單項目的物件
                        product  = forma_t.product + '&' + forma_t.forma_t #把產品和規格串在一起
                        item = Items(
                                    product=product,
                                    price=forma_t.price,
                                    order_id=order_id,
                                    number=num)
                        items.append(item)   
                        total += forma_t.price * int(num)#訂單價格 * 訂購數量 
                    
                input_information.reset()
                cart.reset() 
                ##這裡if寫兩種付款方式，如果轉帳付款(核對完手動更動是否付款的項目)
                #建立LinePay的物件
                line_pay = LinePay()
                #再使用line_pay.pay的方法，最後就會回覆像postman的格式
                info = line_pay.pay(product_name='愛釣客',
                                    amount=total,
                                    order_id=order_id,
                                    product_image_url=Config.STORE_IMAGE_URL)
                #取得付款連結和transactionId後
                pay_web_url = info['paymentUrl']['web']
                transaction_id = info['transactionId']

                #接著就會產生訂單
                order = Orders(
                            id = order_id,
                            transaction_id=transaction_id,
                            is_pay=False,
                            amount=total,
                            user_id=user_id,
                            delivery_status='尚未出貨'
                            )
                # #接著把訂單和訂單項目加入資料庫中
                db_session.add(order)
                db_session.add(p_information)
                for item in items:
                    db_session.add(item)
                
                db_session.commit()
                #最後告知用戶並提醒付款
                message = TemplateSendMessage(
                    alt_text='感謝您的購買，請點擊進行結帳。',
                    template=ButtonsTemplate(
                        text='感謝您的購買，請點擊進行結帳。',
                        actions=[
                            URIAction(label='NT${}'.format(order.amount),
                                    uri=pay_web_url)
                        ]))
            else:
                message = [
                    TextSendMessage(text='請確認填寫收件資訊'),
                    P_Informations.information_show()]                    
        if message:
            line_bot_api.reply_message(event.reply_token,message)

###########################訊息傳遞區塊LocationMessage###########################
# 接收使用者傳回的位址資訊
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    #抓使用者的資料
    profile=line_bot_api.get_profile(event.source.user_id)
    uid=profile.user_id #使用者ID
    user_name = profile.display_name   #使用者名稱
    print('recived Location Message')
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊weather用＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    if (event.message.type=='location'):
        mat=mat_d.get(uid)
        if mat=='即時天氣' or mat=='天氣預報':
            location_add=event.message.address
            if location_add[5:7]=='台東':
                pointName=location_add[5:].replace('台','臺')
                if pointName[3:5]=='台東':
                    pointName=pointName[3:].replace('台','臺')
            else: 
                pointName=location_add[5:].replace('臺','台')
            print('new_add='+pointName)
            #找出縣市名後的地方鄉鎮關鍵字
            if ('市' in pointName[3:]): index_no=pointName.index('市')
            elif ('區' in pointName[3:]): index_no=pointName.index('區')
            elif ('鄉' in pointName[3:]): index_no=pointName.index('鄉')
            else: index_no=pointName.index('鎮')
            pointName=pointName[:index_no+1] #取至包含該字之前的縣市名＋地方鄉鎮名
            pointName_d[uid]=pointName
            print('現在查詢的是=',mat)
            if mat=='即時天氣':
                line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的即時天氣，請稍候..."))
                content=get_now_weather(pointName,uid)  #呼叫def程式-查詢即時天氣
            if mat=='天氣預報':
                pointName=pointName[:3]
                line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的預報天氣，請稍候..."))
                content=get_36h_weather(pointName,uid)  #呼叫def程式-查詢預測天氣
            if content !='':
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+mat,content))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此縣市區鄉鎮名稱，請重新輸入。'))
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊回報用＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
        elif mat=='漁獲回報':
            report_buff = Buffer(user_id= event.source.user_id)
            addr = event.message.address #地址
            lat = str(event.message.latitude)  #緯度
            lon = str(event.message.longitude) #經度

            report_buff.add(key='地址', val=addr)
            report_buff.add(key='緯度', val=lat)
            report_buff.add(key='經度', val=lon)

            message = Reports.report_step5_sharephoto()

            if message:
                line_bot_api.reply_message(event.reply_token,message)
        return 0

#########################圖片ImageMessage#########################
@handler.add(MessageEvent, message=ImageMessage)
def handle_Image_message(event):
    print('recived Image Message')
    report_buff = Buffer(user_id= event.source.user_id)
    message_Image = event.message
    message_content = line_bot_api.get_message_content(message_Image.id)

    print('Image Message content have been loaded...')
    data = b''
    for chunk in message_content.iter_content():
        data += chunk

    print('檔案取得完成...')
    report_buff.add(key='photo', val=data)
    report_buff.add(key='照片上傳', val='Yes')
    message = report_buff.display()
    
    if message:
        line_bot_api.reply_message(event.reply_token,message)

#########################訊息傳遞區塊TextMessage#########################
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #抓使用者的資料
    profile=line_bot_api.get_profile(event.source.user_id)
    uid=profile.user_id #使用者ID
    user_name = profile.display_name   #使用者名稱
    usespeak=str(event.message.text)   #使用者講的話
    emsg=event.message.text            #使用者選擇後回傳訊息
    get_or_create_user(event.source.user_id) #使用者被加入資料庫
    message = None
    message_text = None
    if is_ascii(str(event.message.text)):
        message_text = str(event.message.text).lower()
    else:
        message_text = event.message.text
    print('message recive : '+message_text)

    def check_stor():
        try:
            if mat_d[uid]!='':
                del mat_d[uid] #刪除暫存
                print('mat_d 已清空')
            if pointName_d[uid]!='':
                del pointName_d[uid]  #海水浴場即時天氣無用到，其它皆有
                print('pointName_d 已清空')
            if pointNum_d[uid]!='':
                del pointNum_d[uid]   #主要港口即時天氣、海水浴場即時天氣
                print('pointNum_d 已清空')
            if mat_tidal[uid]!='':
                del mat_tidal[uid]    #潮汐專用
                print('mat_tidal 已清空')
        except:
            print('無資料可刪除')
        return 0

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊fishingmap and report＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    # region 訊息判斷區
    if re.match('釣魚地圖', message_text):
        check_stor()
        message = Fishingmaps.ShowFishingLocationType()
    elif 'Get Map' in message_text:
        strLocationName = message_text.split(':')[1] 
        message = Fishingmaps.GetMapMessage(strLocationName)
    elif message_text in ['漁獲回報']:
        check_stor()
        message = Reports.report_step1_location()
    elif '回報流程三' in message_text:
        mat_d[uid]='漁獲回報'
        report_buffer = Buffer(user_id= event.source.user_id)
        fishname = message_text.rsplit(':')[1]
        if fishname == '':
            message = [ TextSendMessage(text= 'Sorry, 您未選擇或輸入魚類名稱, 請重新選擇或輸入.') ]
            message.append(Reports.report_step3_fish())
        else:
            report_buffer.add(key='魚種', val=fishname)
            message = Reports.report_step4_sharelocation()
    # if message:
    #     line_bot_api.reply_message(event.reply_token,message)

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊weather＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    # 圖文選單
    # 第一層-最新氣象->4格圖片Flex Message
    if re.match('最新氣象|查詢天氣|天氣查詢|weather|Weather',emsg):
        content=place.img_Carousel()  #呼叫4格圖片Flex Message
        line_bot_api.reply_message(event.reply_token,content)
        check_stor()
        return 0
    #######################1.即時天氣-OK#######################
    # 1.第二層-即時天氣->呼叫quick_reply
    if re.match('即時天氣|即時氣象',emsg): 
        mat_d[uid]='即時天氣'
        content=place.quick_reply_weather(mat_d[uid])  #呼叫quick_reply
        line_bot_api.reply_message(event.reply_token,content)     #ex:回傳->其它即時天氣
        return 0
    # 1.第三層-其它即時天氣->呼叫縣市選單
    if event.message.text.endswith('即時天氣'): #if結尾=即時天氣
        mat_d[uid]='即時天氣'
        content=place.select_city(mat_d[uid])             #呼叫全台縣市選單-22個
        line_bot_api.reply_message(event.reply_token,content) #ex:高雄市->請問要查詢高雄市的那個地區
        return 0
    # 1.第四層-請問要查詢高雄市的那個地區->呼叫區鄉鎮選單
    if event.message.text.endswith('地區'):  #if結尾=地區
        mat_d[uid]='即時天氣'
        city_name=event.message.text[5:8]   #高雄市
        df=pd.read_csv('./file/district.csv',encoding='big5') #讀取縣市檔.csv
        #為了計算該縣市有幾個地區，用來選擇呼叫那個區域選單
        point_list=df[(df['縣市名稱']==city_name)]
        point_list=list(point_list['區鄉鎮名稱'])
        p_no=len(point_list) #取出地區數量
        json_name='./json/select_point_'+str(p_no)+'.json'  #鄉鎮選單
        select_point=json.load(open(json_name,'r',encoding='utf-8')) #讀取縣市選單-套用json模版的選單
        num=0
        #ex:三民區->開始為您查詢即時天氣-高雄市三民區
        #2-嘉義市、3-新竹市、4-連江縣、6-澎湖縣、金門縣、7-基隆市、12-台北市、宜蘭縣、
        #13-桃園市、新竹縣、南投縣、花蓮縣、16-臺東縣、18-苗栗縣、嘉義縣、20-雲林縣、26-彰化縣、29-新北市、台中市
        if p_no<=29: #一頁
            for i in range(len(select_point['body']['contents'])):  # 2
                for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                    select_point['hero']['contents'][0]['text']=city_name+'地區選單'
                    select_point['body']['contents'][i]['contents'][j]['action']['label']=point_list[num]
                    select_point['body']['contents'][i]['contents'][j]['action']['text']='開始為您查詢即時天氣-'+city_name+point_list[num]
                    num+=1
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(city_name+'的地區選單',select_point))
        #33-屏東縣、37-台南市、38-高雄市
        else:   #輪播
            for i in range(len(select_point['contents'])): #3
                for j in range(len(select_point['contents'][i]['body']['contents'])): #3
                    for k in range(len(select_point['contents'][i]['body']['contents'][j]['contents'])): #6
                        select_point['contents'][0]['hero']['contents'][0]['text']=city_name+'地區選單'
                        select_point['contents'][i]['body']['contents'][j]['contents'][k]['action']['label']=point_list[num]
                        select_point['contents'][i]['body']['contents'][j]['contents'][k]['action']['text']='開始為您查詢即時天氣-'+city_name+point_list[num]
                        num+=1
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(city_name+'的地區選單',select_point))
        return 0
    
    # show即天氣查詢結果-第1項即時天氣、第3-2項休閒漁港
    # 開始為您查詢即時天氣-高雄市三民區/XX漁港
    if event.message.text[:6]=='開始為您查詢':
        pointName=event.message.text[11:]     #取-高雄市三民區/XX漁港/XX海水浴場
        if mat_d[uid]=='即時天氣':
            line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的即時天氣，請稍候..."))
            content=get_now_weather(pointName,uid)  #呼叫def程式-查詢即時天氣
            if content !='':
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此縣市區鄉鎮名稱，請重新輸入。'))
        elif mat_d[uid]=='休閒漁港即時天氣':
            pointName=pointName.strip('漁港')
            line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}漁港的即時天氣，請稍候..."))
            content=get_fishing_port_now_weather(pointName,uid)  #呼叫def程式-休閒漁港即時天氣查詢
            if content !='':
                line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
            else: 
                line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此漁港名稱，請重新輸入。'))
        return 0
    #######################2.天氣預報-OK#######################
    # 2.第二層-預測天氣->呼叫quick_reply
    if re.match('天氣預報|氣象預報',emsg):
        mat_d[uid]='天氣預報'
        content=place.quick_reply_weather(mat_d[uid])  #呼叫quick_reply
        line_bot_api.reply_message(event.reply_token,content)
        return 0
    # 2.第三層-縣市選單
    if event.message.text.endswith('天氣預報'):  #if結尾＝天氣預報
        mat_d[uid]='天氣預報'
        content=place.select_city(mat_d[uid])          #呼叫縣市選單
        line_bot_api.reply_message(event.reply_token,content) #ex:高雄市->我要查詢高雄市的預報天氣
        return 0
    # 2.show 預報天氣結果
    if event.message.text.endswith('預報天氣'):  #if結尾＝預報天氣
        mat_d[uid]='天氣預報'
        city_name=event.message.text[4:7] #高雄市
        if (city_name[0]=='台'):
            city_name=city_name.replace('台','臺')
        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{city_name}未來 36 小時的天氣預測，請稍候..."))
        content=get_36h_weather(city_name,uid)
        if content !='':
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(city_name+'未來 36 小時天氣預測',content))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此縣市名稱，請重新輸入。'))
        return 0
    #######################3.港口即時天氣查詢-OK#######################
    # 3.第二層-港口天氣->呼叫選擇圖片轉盤Flex Message-img_port(主要港口/休閒漁港/海水浴場)
    if re.match('港口天氣|港口即時天氣',emsg):
        content=place.img_port()  #呼叫圖片轉盤Flex Message-港口清單->主要港口、休閒漁港、海水浴場
        line_bot_api.reply_message(event.reply_token,content)
        return 0
    ##########################3-1.主要港口-OK##########################
    # 3-1.第三層-主要港口quick_reply
    if re.match('主要港口',emsg):
        mat_d[uid]='主要港口即時天氣'
        content=place.quick_reply_port(mat_d[uid])  #呼叫quick_reply
        line_bot_api.reply_message(event.reply_token,content) #主要港口quick_reply
        return 0
    # 3-1第四層-主要港口選單
    if re.match('台灣主要港口選單',emsg):
        mat_d[uid]='主要港口即時天氣'
        #呼叫主要港口選單
        content=json.load(open('./json/select_mainport_10.json','r',encoding='utf-8'))  
        line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢的主要港口：',content))
        #ex:澎湖港(馬公)->我要查詢澎湖港(馬公)的天氣現況 
        return 0
    # 3-1.show 主要港口即時天氣結果
    if event.message.text[:4]=='我要查詢':
        mat_d[uid]='主要港口即時天氣'
        portName=event.message.text[4:] #澎湖港(馬公)
        #取出港口名稱
        index_no=portName.index('的')
        portName=portName[:index_no]
        portNum=place.port_nameNo(portName)  #呼叫place.主要港口清單-port_nameNo，取出對應的代碼
        if portNum !="查無此港口":
            line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{portName}的即時天氣，請稍候..."))
            content=get_port_now_weather(portNum,portName,uid)  #呼叫查詢港口即時天氣的def
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(portName+'的天氣現況',content))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此港口名稱，請重新輸入。'))
        return 0
    #######################3-2.休閒漁港-OK#######################
    # 3-2.第三層-休閒漁港quick_reply
    if re.match('休閒漁港',emsg):
        mat_d[uid]='休閒漁港即時天氣'
        content=place.quick_reply_port(mat_d[uid])  #呼叫quick_reply
        line_bot_api.reply_message(event.reply_token,content) #我想查詢休閒漁港
        return 0
    # 3-2.第四層-我想查詢休閒漁港->秀縣市選單-17個縣市->請問要查詢高雄市的那個休閒漁港
    if re.match('我想查詢休閒漁港',emsg):
        mat_d[uid]='休閒漁港即時天氣'
        #計算休閒漁港共有幾個縣市，用來選擇呼叫那個縣市選單
        df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5') #讀取port和潮汐的csv
        city_list=list(df[df['sort']=='休閒漁港']['city'].drop_duplicates())
        citylist_no=str(len(city_list))
        json_name='./json/select_point_'+citylist_no+'.json'
        select_point=json.load(open(json_name,'r',encoding='utf-8')) #呼叫縣市選單-18
        num=0
        for i in range(len(select_point['body']['contents'])):  # 2
            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                select_point['hero']['contents'][0]['text']='休閒漁港縣市選單'
                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'    #換按鈕顏色
                select_point['body']['contents'][i]['contents'][j]['action']['label']=city_list[num]
                select_point['body']['contents'][i]['contents'][j]['action']['text']='請問要查詢'+city_list[num]+'的那個漁港天氣'
                num+=1
        line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢的縣市：',select_point))
        #ex:高雄市->請問要查詢高雄市的那個漁港天氣
        return 0
    # 3-2.第五層-休閒漁港地點選單
    if event.message.text.endswith('漁港天氣'):  #if結尾=漁港天氣
        mat_d[uid]='休閒漁港即時天氣'
        city_name=event.message.text[5:8]   #高雄市
        df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5') #讀取port和潮汐的csv
        #為了計算該縣市有幾個休閒漁港，用來選擇呼叫那個個數的選單
        port_list=list(df[(df['sort']=='休閒漁港')&(df['city']==city_name)]['web_name'])
        portlist_no=str(len(port_list))
        json_name='./json/select_point_'+portlist_no+'.json'
        select_point=json.load(open(json_name,'r',encoding='utf-8')) #呼叫休閒漁港選單
        num=0
        for i in range(len(select_point['body']['contents'])):  # 2
            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                select_point['hero']['contents'][0]['text']=city_name+'漁港選單'
                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                select_point['body']['contents'][i]['contents'][j]['color']='#232641'  #換按鈕顏色
                select_point['body']['contents'][i]['contents'][j]['action']['label']=port_list[num]+'漁港'  #休閒漁港名稱
                select_point['body']['contents'][i]['contents'][j]['action']['text']='開始為您查詢即時天氣-'+port_list[num]+'漁港'
                num+=1
        line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢那個休閒漁港：',select_point))
        #ex:高雄市->開始為您查詢即時天氣-七美漁港
        return 0
    ##########################3-3.海水浴場-OK##########################
    # 3-3.第三層-休閒漁港quick_reply
    if re.match('海水浴場',emsg):
        mat_d[uid]='海水浴場即時天氣'
        content=place.quick_reply_port(mat_d[uid])  #呼叫quick_reply
        line_bot_api.reply_message(event.reply_token,content) #我想查詢海水浴場
        return 0
    # 3-3.第四層-我想查詢海水浴場->三區list輪播選單->高雄市西子灣海水浴場->送出後實際取data資料查詢
    if re.match('我想查詢海水浴場',emsg):
        mat_d[uid]='海水浴場即時天氣'
        content=json.load(open('./json/select_beachport.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢的海水浴場：',content))
    ##########################4.潮汐預報-OK##########################
    # 4.第二層-潮汐預報->地方鄉鎮、休閒漁港、海水浴場
    if re.match('潮汐預報|潮汐查詢',emsg):
        content=place.img_tidal()  #呼叫圖片轉盤Flex Message-潮汐預報->地方鄉鎮、休閒漁港、海水浴場
        line_bot_api.reply_message(event.reply_token,content)  #我想知道'地方鄉鎮'的潮汐預報
        return 0
    #####################4-1~3.縣市選單/海水浴場list選單-OK#####################
    # 4-1~3.第三層-縣市選單(地方鄉鎮、休閒漁港)/海水浴場->三區list輪播選單->高雄市西子灣海水浴場
    if event.message.text[:4]=='我想知道':
        #取出要查詢的地點種類
        sort=event.message.text[4:8]
        if sort!='海水浴場':
            if sort=='地方鄉鎮':
                mat_tidal[uid]='潮汐鄉鎮'  #當讀取潮汐csv時用來判斷sort
                mat_d[uid]='潮汐鄉鎮'
                message='那個鄉鎮的潮汐預報'
            elif sort=='休閒漁港':
                mat_tidal[uid]='休閒漁港'  #當讀取潮汐csv時用來判斷sort
                mat_d[uid]='休閒漁港潮汐'
                message='那個休閒漁港的潮汐預報'
            #計算潮汐鄉鎮/休閒漁港共有幾個縣市，用來選擇呼叫符合數量的縣市選單
            df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5') #讀取port和潮汐的csv
            city_list=list(df[df['sort']==mat_tidal[uid]]['city'].drop_duplicates())
            citylist_no=str(len(city_list))
            json_name='./json/select_point_'+citylist_no+'.json'
            select_point=json.load(open(json_name,'r',encoding='utf-8')) #呼叫縣市選單-鄉鎮19、漁港18
            num=0
            for i in range(len(select_point['body']['contents'])):  # 2
                for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                    select_point['hero']['contents'][0]['text']=mat_tidal[uid]+'縣市選單'
                    select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                    select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'  #換按鈕顏色
                    select_point['body']['contents'][i]['contents'][j]['action']['label']=city_list[num]
                    select_point['body']['contents'][i]['contents'][j]['action']['text']='請問要查詢'+city_list[num]+message
                    num+=1
            line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢的縣市：',select_point))
            #ex:高雄市->請問要查詢高雄市那個"鄉鎮/休閒漁港"的潮汐預報
        else:
            mat_tidal[uid]='海水浴場'  #當讀取潮汐csv時用來判斷sort
            mat_d[uid]='海水浴場潮汐'
            message='那個休閒漁港的潮汐預報'
            # 套用海水浴場三區list輪播選單->高雄市西子灣海水浴場->送出後實際取data資料查詢
            content=json.load(open('./json/select_beachport.json','r',encoding='utf-8'))
            for i in range(len(content['contents'])):  # 3
                for j in range(len(content['contents'][i]['body']['contents'])): #i=0->j=9;i=1->7;i=2->6
                    content['contents'][i]['body']['contents'][j]['action']['data']='beach=海水浴場'+content['contents'][i]['body']['contents'][j]['action']['displayText'][3:].strip('海水浴場')
            line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢的海水浴場：',content))
        return 0
    #####################4-1~2.地點選單-OK######################
    # 4-1～2.第四層-地方鄉鎮選單/休閒漁港選單
    if event.message.text.endswith('潮汐預報'):  #if結尾＝潮汐預報
        # 請問要查詢高雄市那個'鄉鎮/休閒漁港'的潮汐預報
        city_name=event.message.text[5:8]   #高雄市
        df=pd.read_csv('./file/port_tidal_list.csv',encoding='big5') #讀取port和潮汐的csv
        #計算該縣市有幾個鄉鎮潮汐觀測點，用來選擇呼叫那個個數的選單
        port_list=list(df[(df['sort']==mat_tidal[uid])&(df['city']==city_name)]['locationName'])
        portlist_no=str(len(port_list))
        json_name='./json/select_point_'+portlist_no+'.json'
        select_point=json.load(open(json_name,'r',encoding='utf-8')) #依數量呼叫地點選單
        if mat_d[uid]=='潮汐鄉鎮':
            num=0
            for i in range(len(select_point['body']['contents'])):  # 2
                for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                    select_point['hero']['contents'][0]['text']=city_name+'地區選單'
                    select_point['body']['contents'][i]['contents'][j]['action']['label']=port_list[num][3:]      #鄉鎮名稱
                    select_point['body']['contents'][i]['contents'][j]['action']['text']='請稍候，正在為您查詢潮汐預報-'+port_list[num]
                    num+=1
            line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢那個'+city_name+'的那個鄉鎮：',select_point))
            #ex:澎湖縣七美鄉->請稍候，正在為您查詢潮汐預報-澎湖縣七美鄉
        elif mat_d[uid]=='休閒漁港潮汐':
            num=0
            for i in range(len(select_point['body']['contents'])):  # 2
                for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                    select_point['hero']['contents'][0]['text']=city_name+'漁港選單'
                    select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                    select_point['body']['contents'][i]['contents'][j]['color']='#232641'  #換按鈕顏色-港口/漁港
                    select_point['body']['contents'][i]['contents'][j]['action']['label']=port_list[num][2:]      #鄉鎮名稱
                    select_point['body']['contents'][i]['contents'][j]['action']['text']='請稍候，正在為您查詢潮汐預報-'+port_list[num][2:]+'漁港'
                    num+=1
            line_bot_api.reply_message(event.reply_token,FlexSendMessage('請選擇想查詢那個休閒漁港：',select_point))
        #ex:漁港白沙->請稍候，正在為您查詢潮汐預報-白沙漁港
        return 0
    #####################4-1~2.show 潮汐預報結果-OK######################
    # 4.show 潮汐預報結果-地方鄉鎮、休閒漁港
    if event.message.text[:4]=='請稍候，':
        mat_t=mat_tidal.get(uid)
        #取出鄉鎮名稱或漁港名稱
        pointName=event.message.text[15:]   #澎湖縣七美鄉
        if mat_t=='休閒漁港':
            mat_d[uid]=='休閒漁港潮汐'
            pointName='漁港'+pointName.strip('漁港') #白沙漁港->漁港白沙
        content=get_tidal(pointName,mat_t,uid)  #呼叫def程式-查詢潮汐預報
        if content !='':
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(f'{pointName}的潮汐預報',content))
        else: 
            line_bot_api.reply_message(event.reply_token,TextSendMessage(f'查無此{pointName}的潮汐預報，請重新輸入。'))
        return 0
    #####################查詢已關注的即時天氣、天氣預報-OK######################
    if re.match('我關注的天氣',emsg):
        mat=mat_d.get(uid)
        if mat=='':
            line_bot_api.reply_message(event.reply_token,TextSendMessage('無法確認您目前想做什麼，請重新擇。'))
        else:
            dataList=database.get_love_weather(uid,mat)
            if dataList[:2]=='查無':
                line_bot_api.reply_message(event.reply_token,TextSendMessage(dataList))
            else:
                list_no=len(dataList)
                if list_no>1:
                    json_name='./json/select_point_'+str(list_no)+'.json'  #數量選單
                    select_point=json.load(open(json_name,'r',encoding='utf-8')) #讀取數量選單-套用json模版的選單
                if dataList==None:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage('目前無您關注的天氣，請新增您想關注的天氣喔！！'))
                #開始查詢
                if mat=='即時天氣':
                    mat_d[uid]='即時天氣'
                    if list_no!=0 and list_no>1:
                        num=0
                        for i in range(len(select_point['body']['contents'])):  # 2
                            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                                select_point['hero']['contents'][0]['text']='我關注的'+mat+'清單'
                                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                                select_point['hero']['contents'][0]['offsetStart']='15px' #調整字的位置
                                select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'  #換按鈕顏色
                                select_point['body']['contents'][i]['contents'][j]['action']['label']=dataList[num][2]
                                select_point['body']['contents'][i]['contents'][j]['action']['text']='開始為您查詢即時天氣-'+dataList[num][2]
                                num+=1
                        line_bot_api.reply_message(event.reply_token,FlexSendMessage('我關注的'+mat+'清單',select_point))
                    elif list_no==1:
                        pointName=dataList[0][2]
                        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的即時天氣，請稍候..."))
                        content=get_now_weather(pointName,uid)  #呼叫def程式-查詢即時天氣
                        if content !='':
                            line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
                        else:
                            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此縣市區鄉鎮名稱，請重新輸入。'))
                elif mat=="天氣預報":
                    mat_d[uid]='天氣預報'
                    if list_no!=0 and list_no>1:
                        num=0
                        for i in range(len(select_point['body']['contents'])):  # 2
                            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                                select_point['hero']['contents'][0]['text']='我關注的'+mat+'清單'
                                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                                select_point['hero']['contents'][0]['offsetStart']='15px' #調整字的位置
                                select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'  #換按鈕顏色
                                select_point['body']['contents'][i]['contents'][j]['action']['label']=dataList[num][2]
                                select_point['body']['contents'][i]['contents'][j]['action']['text']='我要查詢'+dataList[num][2]+'的預報天氣'
                                num+=1
                        line_bot_api.reply_message(event.reply_token,FlexSendMessage('我關注的'+mat+'清單',select_point))
                    elif list_no==1:
                        pointName=dataList[0][2]
                        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}未來 36 小時的天氣預測，請稍候..."))
                        content=get_36h_weather(pointName,uid)
                        if content !='':
                            line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'未來 36 小時天氣預測',content))
                        else:
                            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此縣市名稱，請重新輸入。'))
                elif mat=="主要港口即時天氣":
                    mat_d[uid]='主要港口即時天氣'
                    if list_no!=0 and list_no>1:
                        num=0
                        for i in range(len(select_point['body']['contents'])):  # 2
                            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                                select_point['hero']['contents'][0]['text']='我關注的主要港口清單'
                                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                                select_point['hero']['contents'][0]['offsetStart']='15px' #調整字的位置
                                select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'  #換按鈕顏色
                                select_point['body']['contents'][i]['contents'][j]['action']['label']=dataList[num][2]
                                select_point['body']['contents'][i]['contents'][j]['action']['text']='我要查詢'+dataList[num][2]+'的天氣現況'
                                num+=1
                        line_bot_api.reply_message(event.reply_token,FlexSendMessage('我關注的主要港口清單',select_point))
                    elif list_no==1:
                        pointName=dataList[0][2]
                        pointNum=dataList[0][3]
                        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}的即時天氣，請稍候..."))
                        content=get_port_now_weather(pointNum,pointName,uid)  #呼叫查詢港口即時天氣的def
                        if content !='':
                            line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
                        else: 
                            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此港口名稱，請重新輸入。'))
                elif mat=="休閒漁港即時天氣":
                    mat_d[uid]='休閒漁港即時天氣'
                    if list_no!=0 and list_no>1:
                        num=0
                        for i in range(len(select_point['body']['contents'])):  # 2
                            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                                select_point['hero']['contents'][0]['text']='我關注的休閒漁港清單'
                                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                                select_point['hero']['contents'][0]['offsetStart']='15px' #調整字的位置
                                select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'  #換按鈕顏色
                                select_point['body']['contents'][i]['contents'][j]['action']['label']=dataList[num][2]
                                select_point['body']['contents'][i]['contents'][j]['action']['text']='開始為您查詢即時天氣-'+dataList[num][2]+'漁港'
                                num+=1
                        line_bot_api.reply_message(event.reply_token,FlexSendMessage('我關注的休閒漁港清單',select_point))
                    elif list_no==1:
                        pointName=dataList[0][2]
                        line_bot_api.push_message(uid, TextSendMessage(f"正在為您查詢{pointName}漁港的即時天氣，請稍候..."))
                        content=get_fishing_port_now_weather(pointName,uid)  #呼叫def程式-休閒漁港即時天氣查詢
                        if content !='':
                            line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'的即時天氣',content))
                        else: 
                            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此漁港名稱，請重新輸入。'))
                elif mat=='海水浴場即時天氣':
                    mat_d[uid]='海水浴場即時天氣'
                    pointName=dataList[0][2]
                    pointNum=dataList[0][3]
                    if list_no!=0 and list_no>1:
                        num=0
                        for i in range(len(select_point['body']['contents'])):  # 2
                            for j in range(len(select_point['body']['contents'][i]['contents'])): # j=0->7,j=1->6
                                select_point['hero']['contents'][0]['text']='我關注的海水浴場清單'
                                select_point['hero']['contents'][0]['color']='#4493A3'    #換字的顏色
                                select_point['hero']['contents'][0]['offsetStart']='15px' #調整字的位置
                                select_point['body']['contents'][i]['contents'][j]['color']='#7EB5A6'  #換按鈕顏色
                                select_point['body']['contents'][i]['contents'][j]['action']['type']='postback'
                                select_point['body']['contents'][i]['contents'][j]['action']['label']=dataList[num][2]  #海水浴場名稱
                                select_point['body']['contents'][i]['contents'][j]['action'].pop('text')
                                select_point['body']['contents'][i]['contents'][j]['action']['data']='PID='+dataList[num][3]
                                select_point['body']['contents'][i]['contents'][j]['action']['displayText']='查詢'+dataList[num][2]+'海水浴場'
                                num+=1
                        line_bot_api.reply_message(event.reply_token,FlexSendMessage('我關注的海水浴清單',select_point))
                    elif list_no==1:
                        line_bot_api.push_message(uid, TextSendMessage(f'正在為您查詢'+pointName+'海水浴場的即時天氣，請稍候...'))
                        content=get_beach_port_now_weather(pointNum,uid)  #呼叫def程式-查詢海水浴場即時天氣
                        if content !='':
                            line_bot_api.reply_message(event.reply_token,FlexSendMessage(pointName+'海水浴場的即時天氣',content))
                        else: 
                            line_bot_api.reply_message(event.reply_token,TextSendMessage('查無此海水浴場名稱，請重新輸入。'))

    if re.match('我的最愛|我的清單|我關注的清單',emsg):
        dataList=database.show_allList_weather(uid)
        list_all=''
        for i in range(len(dataList)):
            if dataList[i][1]=='主要港口即時天氣' or dataList[i][1]=='休閒漁港即時天氣' or dataList[i][1]=='海水浴場即時天氣':
                list_all+=dataList[i][1][:4]+'\t\t'
                if dataList[i][1]=='休閒漁港即時天氣': 
                    list_all+=dataList[i][2]+'漁港'+'\n'
                elif dataList[i][1]=='海水浴場即時天氣':
                    list_all+=dataList[i][2]+'海水浴場'+'\n'
                else: list_all+=dataList[i][2]+'\n'
            else:
                list_all+=dataList[i][1]+'\t\t'
                list_all+=dataList[i][2]+'\n'
        love_list=json.load(open('./json/love_list.json','r',encoding='utf-8')) #套用json模版-我的最愛清單
        love_list['body']['contents'][2]['contents'][0]['text']=list_all
        line_bot_api.reply_message(event.reply_token,FlexSendMessage('我的最愛清單',love_list))

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊商城用＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    cart = Cart(user_id=event.source.user_id)
    input_information = Input_Information(user_id=event.source.user_id)
    if message_text in ['漁夫裝備']:#產品選單
        check_stor()
        mat_d[uid]='漁夫裝備'
        message = Products.list_all()
    elif '輸入數量'in message_text:#更改產品數量時啟動的頁面中數量手動填寫
        forma_t=message_text.split(',')[0]
        num=int(message_text.rsplit('：')[1])
        cart.add(forma_t=forma_t,num=num) 
        if cart.bucket():
            message = cart.display() 
        else:
            message = TextSendMessage(text='您的購物車是空的')
    elif '☛'in message_text:#收件資料的手動填寫
        All = message_text.rsplit('•')
        buy_list=[]
        for i in All:
            element = i.split('：')[1]
            buy_list.append(element)
        nam = buy_list[0][:-1]
        pho = buy_list[1][:-1]
        num = buy_list[2][:-1]
        addr= buy_list[3]
        input_information.add(name=nam,phone=pho,address=addr,addr_number=num)
        if input_information.find():
            message = P_Informations.information_show(nam=nam,pho=pho,num=num,addr=addr)
            a = []
            b = [] 
            for i,j in input_information.find().items():
                a.append(i)
                b.append(j)
            print(a)
            print(b)
        else:
            message = TextSendMessage(text = '請填寫正確的個人資訊')
    if message:
        line_bot_api.reply_message(event.reply_token,message)

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊知識＋＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊#
    if '釣手知識+' in emsg:
        check_stor()
        mat_d[uid]='釣手知識+'
        message = Message.learn()
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '魚類百科' in emsg:
        message = Message.fish_encyclopedia()
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '台灣常見魚類' in emsg:
        message = Message.quick_reply_taiwanese_fish()
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '繼續探索' in emsg:
        message = Message.quick_reply_taiwanese_fish()
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '先不要' in emsg:
        message = TextSendMessage(text='好吧~掰掰')
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '有毒魚類' in emsg or '經濟性魚類' in emsg or '可食用魚類' in emsg or '觀賞魚類' in emsg or '瀕危魚類' in emsg:
        message = Message.fish_type(emsg)
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif emsg[:1] == "@":
        message = Message.fish_search_action(emsg[1:])
        line_bot_api.reply_message(event.reply_token, message)
    elif '知識+' in emsg:
        message = Message.quick_reply_FB_hashtag()
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '政府公告' in emsg or '釣魚知識' in emsg or '釣魚點' in emsg or '釣魚資訊' in emsg or '漁獲日誌' in emsg:
        message = Message.FbHashTag_flex_message(emsg)
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '愛釣客' in emsg:
        message = TextSendMessage(text=r'https://www.facebook.com/Fishx12345/')
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    elif '呼叫' in emsg:
        message=Message.FbHashTag_flex_message('政府公告')
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    else:
        return 0

@app.before_first_request
def init_product():
    result = init_db()
    if result:
        init_data = [
            Products(
                type='船釣鐵板',
                product1='HR SLOW JIGGING III R',
                price1='$5,600 - $6,100',
                product_image_url1='https://cf.shopee.tw/file/c4e955e33a7d0923cd7ec84be0347ab3',
                product2='SHIMANO 20 GAME TYPE J',
                price2='$8,370 - $9,140',
                product_image_url2='https://cf.shopee.tw/file/f292d64a9aab0097a5c2ac683b54f291',
                product3='HR SKY WALKER J JIGGING',
                price3='$5,600 - $6,000',
                product_image_url3='https://cf.shopee.tw/file/52ebad22de30743fac82da0be3f63c74')]
        db_session.bulk_save_objects(init_data)#一次寫入list
        db_session.commit()

@handler.add(FollowEvent)
def handle_follow(event):
    #同樣取得user_id
    get_or_create_user(event.source.user_id)
    print('followevent')
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text = '感恩您,讚嘆您,歡迎你回來...'))

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    #先執行封鎖在解除就會出現print的東西
    unfollowuser = get_or_create_user(event.source.user_id)
    print('Got Unfollow event :'+ unfollowuser.id)

#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)