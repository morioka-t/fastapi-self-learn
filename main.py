from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from db import SessionLocal, Base, engine
from models import User, TokenData
from schemas import UserResponse, UserCrud, TokenResponse, SpecificUser, loginUser, AllUserResponse, PagingResponse, PagingRequest, totalMembersRequest, totalMembersResponse
import json
import jwt
import sys
import consts
from utils import verify_password, get_password_hash
from auth import create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# テーブルを作成
#Base.metadata.drop_all(bind=engine)  # すべてのテーブルを削除
Base.metadata.create_all(bind=engine)  # すべてのテーブルを再作成

# DBセッションを取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2スキーマの定義
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 受け取ったトークンを復号して検証し、現在のユーザーを返す
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{consts.TOKEN_VALIDATE}")
    try:
        # トークンからユーザ名を抽出
        payload = jwt.decode(token, consts.SECRET_KEY, algorithms=[consts.ALGORITHM])
        username: str = payload.get("sub")
        # ユーザ名が抽出できなかった場合、認証エラー
        if username is None:
            raise credentials_exception
        token_data = db.query(TokenData).filter(TokenData.username == username, TokenData.accessToken == token).first()
    except InvalidTokenError:
        raise credentials_exception
    # DBから有効なトークンかどうかを判断
    if token_data is None:
        raise credentials_exception
    return token_data.username

# ログイン認証（ユーザ名とパスワードを入力して、トークンを発行する）
@app.post("/login", response_model=TokenResponse)
def login(user: loginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    # ユーザ名または、パスワードどちらかが一致しない場合、400エラーを返却
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail=f"{consts.LOGIN_INCORRECT}")
    access_token_expires = timedelta(minutes=consts.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": user.username}, expires_delta=access_token_expires)
    token_data = db.query(TokenData).filter(TokenData.username == user.username).first()
    # 既にトークンが発行されているユーザに対し、トークンを更新
    # トークンが発行されていないユーザは、そのまま登録
    if token_data:
        token_data.accessToken = access_token
    else:
        token_data = TokenData(username=user.username, accessToken=access_token, tokenType=consts.TOKEN_TYPE)
    db.add(token_data)
    db.commit()
    db.refresh(db_user)
    return token_data

# 全ユーザーを取得
@app.get("/all-users", response_model=list[AllUserResponse])
def all_users(db: Session = Depends(get_db)):
    try:
        all_user = db.query(User).all()
        if all_user is None:
            print(f"{consts.USER_NOT_FONUND}{user.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return all_user

# 全ユーザのトークン情報を取得
@app.get("/all-token-data", response_model=list[TokenResponse])
def all_users(db: Session = Depends(get_db)):
    try:
        token_data = db.query(TokenData).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return token_data

# 特定のユーザーを取得
@app.post("/specific-user", response_model=UserResponse)
def specific_users(user: SpecificUser, db: Session = Depends(get_db), current_username: str = Depends(get_current_user)):
    try:
        search_user = db.query(User).filter(User.username == user.username).first()
        if search_user is None:
            print(f"{consts.USER_NOT_FONUND}{user.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return search_user

# ユーザーを追加
@app.post("/create-users", response_model=UserResponse)
def create_user(user: UserCrud, db: Session = Depends(get_db)):
    try:
        search_user = db.query(User).filter(User.username == user.username).first()
        # 既に登録されているユーザ名は登録できないようにする
        if search_user is not None:
            raise HTTPException(status_code=409)
        # パスワードをハッシュ化
        hashed_pw = get_password_hash(user.password)
        new_user = User(username=user.username, password=hashed_pw, email=user.email)
        db.add(new_user)
        db.commit()
    except HTTPException as e:
        raise HTTPException(status_code=409, detail=f"{consts.USER_ALREADY}{user.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return new_user

@app.post("/delete-users", response_model=list[UserResponse])
def delete_user(users: list[SpecificUser], db: Session = Depends(get_db), current_username: str = Depends(get_current_user)):
    try:
        delete_user_list = []
        for user in users:
            # データベースからユーザーを検索
            delete_user = db.query(User).filter(User.username == user.username).first()
            # ユーザーが存在しない場合はエラーレスポンスを返す
            if delete_user is None:
                raise HTTPException(status_code=404)
            # 削除したユーザのトークン情報を削除
            delete_token_data = db.query(TokenData).filter(TokenData.username == user.username).first()
            if delete_token_data is not None:
                db.delete(delete_token_data)
            db.delete(delete_user)
            delete_user_list.append(delete_user)
        db.commit()
    except HTTPException as e:
        raise HTTPException(status_code=404, detail=f"{consts.USER_NOT_FONUND}{user.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return delete_user_list

@app.post("/update-users", response_model=UserResponse)
def update_user(user: UserCrud, db: Session = Depends(get_db), current_username: str = Depends(get_current_user)):
    try:
        # データベースからユーザーを検索
        db_user = db.query(User).filter(User.username == user.username).first()
        # ユーザーが存在しない場合はエラーレスポンスを返す
        if db_user is None:
            raise HTTPException(status_code=404)
        if user.password and user.email:
            db_user.password = get_password_hash(user.password)
            db_user.email = user.email
        # データを保存
        db.commit()
        db.refresh(db_user)
    except HTTPException:
        raise HTTPException(status_code=404, detail=f"{consts.USER_NOT_FONUND}{user.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return db_user

@app.post("/all-delete-users", response_model=list[UserResponse])
def all_delete_user(user: UserCrud, db: Session = Depends(get_db), current_username: str = Depends(get_current_user)):
    try:
        all_user = db.query(User).all()
        delete_user_list = []
        for user in all_user:
            # データベースからユーザーを検索
            delete_user = db.query(User).filter(User.id == user.id).first()
            # ユーザーが存在しない場合はエラーレスポンスを返す
            if delete_user is None:
                print(f"{consts.USER_NOT_FONUND}{user.id}", file=sys.stderr)
                continue
            db.delete(delete_user)
            delete_user_list.append(delete_user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return delete_user_list

# ユーザの総件数を取得
@app.post("/total-members", response_model=totalMembersResponse)
def total_members(total: totalMembersRequest, db: Session = Depends(get_db), current_username: str = Depends(get_current_user)):
    try:
        if total.search:
          query = db.query(User)
          search = f"%{total.search}%"
          query = query.filter(
            or_(
              User.username.ilike(search),
              User.email.ilike(search)
            )
          )
          search_user = query.all()
        else:
          search_user = db.query(User).all()
        if search_user is None:
            print(f"{consts.USER_NOT_FONUND}{user.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {'total': len(search_user)}

# ページごとにユーザーを取得
@app.post("/paging-users", response_model=list[PagingResponse])
def paging_users(paging: PagingRequest, db: Session = Depends(get_db), current_username: str = Depends(get_current_user)):
    try:
        users = []
        if paging.search:
          query = db.query(User)
          search = f"%{paging.search}%"
          query = query.filter(
            or_(
              User.username.ilike(search),
              User.email.ilike(search)
            )
          )
          search_user = query.offset(paging.skip).limit(paging.limit).all()
        else:
          search_user = db.query(User).offset(paging.skip).limit(paging.limit).all()
        if search_user is None:
            print(f"{consts.USER_NOT_FONUND}{user.username}")
        for info in search_user:
            usersInfo = {}
            usersInfo['id'] = info.id
            usersInfo['username'] = info.username
            usersInfo['email'] = info.email
            users.append(usersInfo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return users