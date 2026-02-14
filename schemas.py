# schemas.py
from pydantic import BaseModel

# レスポンス用の User スキーマ
class UserResponse(BaseModel):
    id: int
    username: str
    password: str
    email: str

class UserCrud(BaseModel):
    username: str
    password: str
    email: str

class TokenResponse(BaseModel):
    id: int
    username: str
    accessToken: str
    tokenType: str

class SpecificUser(BaseModel):
    username: str

class loginUser(BaseModel):
    username: str
    password: str    

class AllUserResponse(BaseModel):
    id: int
    username: str
    email: str

class PagingRequest(BaseModel):
    skip: int
    limit: int
    search: str

class PagingResponse(BaseModel):
    id: int
    username: str
    email: str

class totalMembersRequest(BaseModel):
    search: str

class totalMembersResponse(BaseModel):
    total: int