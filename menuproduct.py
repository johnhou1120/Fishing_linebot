from os import WIFEXITED
from product import Products
from sqlalchemy import Column,String,Integer
from linebot.models import *
from sqlalchemy.sql.expression import text
from database import Base,db_session
from urllib.parse import quote #使用者自動輸入專用，可避免空白輸入
#產品規格的表格
class Menuproducts(Base):
    __tablename__ = 'menuproducts'
    
    id = Column(Integer,primary_key=True)
    type = Column(String)
    product = Column(String)
    price = Column(Integer)
    forma_t = Column(String)

    @staticmethod
    def format_list(x='HR SLOW JIGGING III R'):
        menuproducts = db_session.query(Menuproducts).all()
        qr1=QuickReplyButton(
                    action=PostbackAction(
                        label='VHC-672L',
                        data='VHC-672L', 
                        text='VHC-672L'))
        items=[qr1]
        for menuproduct in menuproducts:
            if x ==menuproduct.product:
                if items !=[]:
                    qr2=QuickReplyButton(
                    action=PostbackAction(
                        label=menuproduct.forma_t,
                        data=menuproduct.forma_t, 
                        text=menuproduct.forma_t))
                    items.append(qr2)
        items.remove(qr1)
        remov_e= QuickReplyButton(
                    action=PostbackAction(
                        label='返回',
                        data='返回產品選單',
                        text='返回'))
        items.append(remov_e)
        message= TextSendMessage(text="◉◡◉ 滑動選擇規格  ↓",quick_reply=QuickReply(items=items))

        return message
    #確認選擇規格
    def forat_check(x='紡車 2本竿 VHS-692L'):
        menuproducts = db_session.query(Menuproducts).all()
        for menuproduct in menuproducts:
            if x ==menuproduct.forma_t:
                template=ConfirmTemplate(
                    text="確定選擇1組"+str(menuproduct.price)+'元的'+menuproduct.forma_t+'嗎？',
                    actions=[
                            PostbackAction(
                                label='確定',
                                data='加入{forma_t}'.format(forma_t=x),
                                text='確定'),
                            PostbackAction(
                                label='重新選擇',
                                data=menuproduct.product,
                                text='重新選擇')])
        message=TemplateSendMessage(alt_text='format_check',template=template)
        return message
    #幫我把format資料庫的規格全部寫入
    def all_format():
        menuproducts = db_session.query(Menuproducts).all()
        format_list=[]
        for menuproduct in menuproducts:
            format_list.append(menuproduct.forma_t)
        return format_list