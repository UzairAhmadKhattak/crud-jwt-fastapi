from pydantic import BaseModel
from typing import List,Optional

class UserSchema(BaseModel):
    username:str
    first_name:str
    last_name:str
    email:str
    password:str
    is_active:bool


class UserReturnSchema(BaseModel):
    first_name: str
    last_name: str
    email: str

    class Config:
        orm_mode = True
class ItemSchema(BaseModel):
    title:str
    description:str
    owner_id:int
    owner:Optional[UserReturnSchema]
    class Config:
        orm_mode = True

class ItemInsertSchema(BaseModel):
    title:str
    description:str
    owner_id:int

class ItemUpdateSchema(BaseModel):
    title: str
    description: str


class TokenSchema(BaseModel):
    access_token:str
    token_type:str


