from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True)
    password = Column(String(255))
    refresh_token = Column(String(255), nullable=True)

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    email = Column(String(100), index=True) 
    phone = Column(String(20))
    birthday = Column(Date)
    additional_data = Column(Text, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="contacts")