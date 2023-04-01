# -*- coding: utf-8 -*-
from cachelib import SimpleCache
from sqlalchemy import Column, Integer, DateTime, LargeBinary, String, Text,  func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import column
from database import Base
from linebot.models import *
from config import Config
from urllib.parse import quote

cache = SimpleCache()   #繼承類別

class Buffer(object):
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id

    def report(self):
        return cache.get(key=self.user_id) or {} #透過User_id查詢使用者的購物車如果沒有就會回傳空字典

    def add(self, key, val):
        report = self.report()
        #如果購物車為空字典,就直接加入
        if report == None:
            cache.add(key=self.user_id, value={key:val})
        
        else:
            #如果不是空的,就更新字典
            report.update({key:val})
            #更新到購物車中
            cache.set(key= self.user_id, value=report)

    def reset(self): #清空購物車
        cache.set(key= self.user_id, value= {})

    def display(self):#計算購物車內容及價格
        report_detail_component = []#放置產品明細

        for key, val in self.report().items():#透過for迴圈抓取購物車內容
            #透過 TextComponent 顯示產品明細，透過BoxComponent包起來，再append到product_box_component中
            if key== 'photo': continue
            report_detail_component.append(
                TextComponent(
                    text='{KEY} : {VAL}'.format(KEY=key, VAL=val),
                    size='md', 
                    color='#4D4D4D', 
                    flex=0
                )
            )

        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='你的回報細節如下:',
                                  color= '#86340A',
                                  wrap=True,
                                  size='lg'),
                    SeparatorComponent(margin='xl'),#顯示分隔線
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=report_detail_component)
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=PostbackAction(label='🙏確認回報🙏',
                                              data='action=reportdone')
                    )
                ]
            )
        )

        message = FlexSendMessage(alt_text='Repoet Detail', contents=bubble)

        return message