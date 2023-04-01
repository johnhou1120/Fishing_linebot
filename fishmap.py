# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from linebot.models import *
from sqlalchemy.util.langhelpers import format_argspec_init
from database import Base, db_session
from urllib.parse import quote
from config import Config
import googlemaps

class Fishingmaps(Base):
    __tablename__ = 'fishingmap'

    id = Column(Integer, primary_key=True)
    Location_name = Column(String)
    Location_type = Column(String)
    Latitude = Column(String)
    Longitude = Column(String)
    Address = Column(String)
    Commit = Column(String)
    # Like_count = Column(Integer, default=0)

    def GetLocationType():
        rtn_buff = []
        fishingmap_types = db_session.query(Fishingmaps.Location_type).distinct()
        for Ltype in fishingmap_types:
            rtn_buff.append(Ltype.Location_type)
        return rtn_buff

    def ShowFishingLocationType():
        types = Fishingmaps.GetLocationType()
        
        bubbles = []
        ButtonComps = []
        for atype in types:
            ButtonComp = ButtonComponent(
                        style='primary',
                        color='#7EB5A6',
                        action=PostbackAction(label=atype,
                                              data='action=showmapoption&type='+atype)
                    )
            ButtonComps.append(ButtonComp)

            if len(ButtonComps) == 3:
                bubble = BubbleContainer(
                    direction='ltr',
                    hero=ImageComponent(
                            size='full',
                            aspect_ratio='16:9',
                            aspect_mode='cover',
                            url='https://i.imgur.com/q8KhUU9.jpg'
                        ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text='請選擇釣點類型:',
                                        wrap=True,
                                        color='#E88400',
                                        size='xl'),
                            SeparatorComponent(margin='xl'),
                            BoxComponent(
                                layout='vertical',
                                margin = 'lg',
                                spacing = 'sm',
                                contents=ButtonComps)
                        ],
                    )
                )

                bubbles.append(bubble)
                ButtonComps = []

        if len(ButtonComps) != 0:
                bubble = BubbleContainer(
                    direction='ltr',
                    hero=ImageComponent(
                            size='full',
                            aspect_ratio='16:9',
                            aspect_mode='cover',
                            url='https://i.imgur.com/q8KhUU9.jpg'
                        ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text='請選擇釣點類型:',
                                        wrap=True,
                                        color='#E88400',
                                        size='xl'),
                            SeparatorComponent(margin='xl'),
                            BoxComponent(
                                layout='vertical',
                                contents=ButtonComps)
                        ],
                    )
                )
                bubbles.append(bubble)

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='Type Selection', contents=carousel_container)

        return message#會回傳到app.py message = cart.display()

    def ShowLocationOfSelectedType(strType):
        print(strType)
        maps = db_session.query(Fishingmaps).filter_by(Location_type=strType).all()

        bubbles = []
        
        for i in range(len(maps)//12+1):
            buttons = []
            for j in range(len(maps)):
                if (i-1)*12 +12 <= j < i*12+12:
                    ButtonComp = ButtonComponent(
                                style='primary',
                                color='#7EB5A6',
                                adjust_mode = "shrink-to-fit",
                                action=MessageAction(label=maps[j].Location_name,
                                                    text='Get Map:'+maps[j].Location_name),
                            )
                    buttons.append(ButtonComp)
                else: continue

            bubble = BubbleContainer(
                size= 'giga',
                header=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text=strType,
                                  wrap=True,
                                  color='#4493A3',
                                  size='xxl'),
                        TextComponent('\t釣點選擇:',
                                  wrap=True,
                                  color='#86340A',
                                  size='lg'),
                        SeparatorComponent(margin='xl'),
                    ]
                ),  
                body=BoxComponent(#最底端的地方
                    layout='horizontal',
                    spacing='md',
                    padding_all= 'sm',
                    contents=[
                        BoxComponent(
                            layout='vertical',
                            spacing='md',
                            padding_all= 'sm',
                            contents=buttons[0::2]
                        ),
                        BoxComponent(
                            layout='vertical',
                            spacing='md',
                            padding_all= 'sm',
                            contents=buttons[1::2]
                        )
                    ]
                )
            )

            bubbles.append(bubble)

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text=strType, contents=carousel_container)

        return message

    def GetMapMessage(strLocationName):
        map = db_session.query(Fishingmaps).filter_by(Location_name=strLocationName).first()
        message = None

        if map is None:
            message = TextSendMessage(text = '抱歉系統錯誤暫時無法查到您所指定的地點...')
        else:
            if map.Latitude != None and map.Longitude != None:
                message = LocationSendMessage(title=strLocationName, address=map.Address if map.Address is not None else strLocationName,
                            latitude= float(map.Latitude), longitude= float(map.Longitude))
            else:
                gmaps = googlemaps.Client(key=Config.GOOGLE_API)

                # Geocoding an address
                geocode_result = gmaps.geocode(map.Address)
                f_lat = float(geocode_result[0]['geometry']['location']['lat'])
                f_lng = float(geocode_result[0]['geometry']['location']['lng'])
                message = LocationSendMessage(title=strLocationName, address=map.Address if map.Address is not None else strLocationName,
                            latitude= f_lat, longitude= f_lng)
        return message