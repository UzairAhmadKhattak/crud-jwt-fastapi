from fastapi import Depends
from database import SessionLocal
from schemas import UserSchema
from sqlalchemy.orm import session
from models import User
from fastapi import status
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from schemas import TokenSchema
from fastapi.exceptions import HTTPException
from datetime import timedelta
import datetime
from jose import jwt,JWTError

router = APIRouter(prefix="/auth",tags=["Auth"])

class CustomeOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

secret_key = "my_secret_key"
algorithm = "HS256"

bycrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "auth/token")



@router.post("/create_user")
async def create_user(user:UserSchema,
                      db:session = Depends(get_db),
                      status_code=status.HTTP_201_CREATED):
    user_exist = db.query(User).filter(User.first_name == user.first_name).first()
    try:
        if user_exist:
            return {"msg":"user already created"}
        else:
            new_user = User(
                first_name = user.first_name,
                last_name = user.last_name,
                username = user.username,
                email = user.email,
                hashed_password = bycrypt_context.hash(user.password),
                is_active = user.is_active
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return {"msg":"user created","user_id":new_user.id}
    except:    
        return {"msg":status.HTTP_304_NOT_MODIFIED}


def authenticate_user(username:str,
                      password:str,
                      db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bycrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(username:str,
                        user_id:int,
                        expire_delta:timedelta):
    encode = {"username":username,"id":user_id,
              "exp":datetime.datetime.now(datetime.UTC) + expire_delta}
    return jwt.encode(encode,secret_key,algorithm)


@router.post("/token",response_model=TokenSchema)
async def login(form_data:OAuth2PasswordRequestForm = Depends(),
                db:session=Depends(get_db)):
    
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Username or Password not matched.")
    token = create_access_token(user.username,user.id,timedelta(seconds=20))
    return {"access_token":token,"token_type":"bearer"}


async def get_current_user(token:str= Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token,secret_key,algorithm)
        username:str = payload.get("username")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="couldnt validate user.")
        return {"username":username,"user_id":user_id}
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,"couldnt validate user.")
