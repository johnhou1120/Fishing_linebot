from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from database import Base

#訂單建立-->寫入items表格
class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    order_id = Column("order_id", ForeignKey("orders.id"))
    created_time = Column(DateTime, default=func.now())#訂單建立的時間
    product = Column(String)#產品名稱(產品-規格)
    number = Column(Integer)#產品訂購的數量
    price= Column(Integer)#產品價格