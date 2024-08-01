
from database import Base
from sqlalchemy import Column,String,Integer,Boolean,ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True)
    username = Column(String(10),unique=True)
    first_name = Column(String(10))
    last_name = Column(String(10))
    email = Column(String(20),unique=True)
    hashed_password = Column(String(64))
    is_active = Column(Boolean)
    items = relationship("Item", back_populates="owner")

    def __reper__(self):
        return f"Username - {self.first_name} {self.last_name}"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String(10), index=True)
    description = Column(String(20), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")