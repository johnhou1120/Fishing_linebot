# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship
from database import Base
#使用者資料
class Users(Base):
    __tablename__= 'users'

    id = Column(String, primary_key=True) #line用戶ID
    nick_name = Column(String) #line用戶name
    image_url = Column(String(length=256)) #line用戶大頭貼
    created_time = Column(DateTime, default= func.now()) #line用戶建立的時間