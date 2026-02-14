from sqlalchemy import Column, Integer, String
from db import Base

# トークンに含まれるデータモデル
class TokenData(Base):
    __tablename__ = "users-token"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    accessToken = Column(String)
    tokenType = Column(String)

# ユーザーのデータモデル
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)
    email = Column(String)