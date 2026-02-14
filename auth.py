import jwt
from datetime import datetime, timedelta, timezone
import consts
from typing import Union

# 新しいアクセストークンを生成する
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=consts.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, consts.SECRET_KEY, algorithm=consts.ALGORITHM)
    return encoded_jwt