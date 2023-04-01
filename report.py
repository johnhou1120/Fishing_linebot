# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, DateTime, String, Text,  func, ForeignKey
from linebot.models import *
from sqlalchemy.util.langhelpers import format_argspec_init
from database import Base, db_session
from urllib.parse import quote
from config import Config

class Reports(Base):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True, autoincrement = True)
    user_id = Column("user_id", ForeignKey("users.id"))
    Location = Column(String)
    Type = Column(String)
    Address = Column(String)
    Latitude = Column(String)
    Longitude = Column(String)
    Fish_type = Column(String)
    Photo = Column(Text)
    Time = Column(DateTime, default= func.now())

    def report_step1_location():
        bubbles = []
        BoxComps = []
        ButtonComps = []
        for locate in Config.REPORT_LOCATION_LIST:
            ButtonComp = ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=PostbackAction(label=locate,
                                              data='action=ReportStep1&location='+locate)
                    )
            ButtonComps.append(ButtonComp)

            if len(ButtonComps) == 3:
                BoxComps.append(Reports.AddButtonsToBox(ButtonComps))
                ButtonComps = []

            if len(BoxComps) == 4:
                bubbles.append(Reports.AddBoxsToBubble(BoxComps, '回報流程一', '選擇所在縣市'))
                BoxComps = []

        if len(ButtonComps) > 0:
            BoxComps.append(Reports.AddButtonsToBox(ButtonComps))
        if len(BoxComps) > 0:
            bubbles.append(Reports.AddBoxsToBubble(BoxComps, '回報流程一', '選擇所在縣市'))

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='Report Location Selection', contents=carousel_container)

        return message

    def report_step2_type():
        bubbles = []
        BoxComps = []
        ButtonComps = []
        for type in Config.REPORT_TYPE_LIST:
            ButtonComp = ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=PostbackAction(label=type,
                                              data='action=ReportStep2&type='+type)
                    )
            ButtonComps.append(ButtonComp)

            if len(ButtonComps) == 2:
                BoxComps.append(Reports.AddButtonsToBox(ButtonComps))
                ButtonComps = []

            if len(BoxComps) == 5:
                bubbles.append(Reports.AddBoxsToBubble(BoxComps, '回報流程二', '選擇垂釣類型'))
                BoxComps = []

        if len(ButtonComps) > 0:
            BoxComps.append(Reports.AddButtonsToBox(ButtonComps))
        if len(BoxComps) > 0:
            bubbles.append(Reports.AddBoxsToBubble(BoxComps, '回報流程二', '選擇垂釣類型'))

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='Report Type Selection', contents=carousel_container)

        return message

    def report_step3_fish():
        bubbles = []
        BoxComps = []
        ButtonComps = []
        for type in Config.REPORT_FISH_LIST:
            ButtonComp = ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        adjust_mode = "shrink-to-fit",
                        action=MessageAction(label=type, 
                                             text='回報流程三,獵物名稱:'+type),
                    )
            ButtonComps.append(ButtonComp)

            if len(ButtonComps) == 2:
                BoxComps.append(Reports.AddButtonsToBox(ButtonComps))
                ButtonComps = []

            if len(BoxComps) == 4:
                bubbles.append(Reports.AddBoxsToBubble_withFooter(BoxComps, '回報流程三', '選擇獵物類型', '其他:自行輸入'))
                BoxComps = []
        if len(ButtonComps) >0:
            BoxComps.append(Reports.AddButtonsToBox(ButtonComps))
        if len(BoxComps) >0:
            bubbles.append(Reports.AddBoxsToBubble_withFooter(BoxComps, '回報流程三', '選擇獵物名稱', '其他:自行輸入'))

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='Report Type Selection', contents=carousel_container)

        return message

    def AddButtonsToBox(buttons):
        return BoxComponent(
                    layout='horizontal',
                    spacing='md',
                    contents=buttons)
    
    def AddBoxsToBubble(boxs, strtitle, strsubtitle):
        bubble = BubbleContainer(
            size= 'giga',
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=strtitle,
                        wrap=True,
                        color = '#86340A',
                        size='lg'),
                    TextComponent(text='\t{0}:'.format(strsubtitle),
                        wrap=True,
                        color = '#E88400',
                        size='xl'),
                    SeparatorComponent(margin='xl'),    
                ]
            ),
            body=BoxComponent(
                layout='vertical',
                spacing='md',
                padding_all= 'sm',
                contents=boxs,
            )
        )
        return bubble

    def AddBoxsToBubble_withFooter(box, strtitle, strsubtitle, footerText):
        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=strtitle,
                        wrap=True,
                        color = '#86340A',
                        size='lg'),
                    TextComponent(text='\t{0}:'.format(strsubtitle),
                        wrap=True,
                        color = '#E88400',
                        size='xl'),
                    SeparatorComponent(margin='xl'),
                ],
            ),
            body=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=box,
            ), 
            footer = BoxComponent(
                layout='vertical',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#232641',
                        action=URIAction(label=footerText,
                                             uri='line://oaMessage/{base_id}/?{message}'.format(base_id= Config.BASE_ID,
                                                                                                message=quote('回報流程三,獵物名稱:')))
                    )
                ],
            )
        )
        return bubble

    def report_step4_sharelocation():
        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='回報流程四',
                        wrap=True,
                        color = '#86340A',
                        size='lg'),
                    TextComponent(text='\t是否願意分享您的定位:',
                        wrap=True,
                        color = '#E88400',
                        size='xl'),
                    SeparatorComponent(margin='xl'),
                ],
            ),
            body=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=URITemplateAction(
                                label="分享我的定位",
                                uri="line://nv/location")
                    ),
                    ButtonComponent(
                        style='primary',
                        color='#232641',
                        action=PostbackAction(label='我不想分享我的定位',
                                              data='action=我不想分享我的定位')                                              
                    ),
                ],
            )
        )

        return FlexSendMessage(alt_text='Report Type Selection', contents=bubble)

    def report_step5_sharephoto():
        bubble = BubbleContainer(
            direction='ltr',
            header=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='回報流程五',
                        wrap=True,
                        color = '#86340A',
                        size='lg'),
                    TextComponent(text='\t上傳您獵物的照片:',
                        wrap=True,
                        color = '#E88400',
                        size='xl'),
                    SeparatorComponent(margin='xl'),
                ],
            ),
            body=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=URITemplateAction(
                                label="開啟相機拍照",
                                uri="line://nv/camera"
                            )
                    ),
                    ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=URITemplateAction(
                                label="選取照片上傳",
                                uri="line://nv/cameraRoll/single"
                            )
                    ),
                    ButtonComponent(
                        style='primary',
                        color='#232641',
                        action=PostbackAction(label='我不想上傳圖片',
                                            data='action=我不想上傳圖片')   
                    ),
                ],
            )
        )
        return FlexSendMessage(alt_text='Report Type Selection', contents=bubble)