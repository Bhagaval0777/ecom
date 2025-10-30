from pydantic import BaseModel, Field
from typing import Optional
import datetime

class User(BaseModel):
    name : str
    email : str
    password : str
    isadmin : bool = Field(default=False)

    

class ShowUser(BaseModel):
    id : int
    name : str
    email : str
    isadmin : bool

    class Config:
        from_attributes = True
        

class UpdateUser(BaseModel):
    
    name : Optional[str] = None      
    email : Optional[str] = None     
    isadmin : Optional[bool] = None 
    password : Optional[str] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    id: Optional[int] = None 
    isadmin: Optional[bool] = None

class loginLog(BaseModel):
    user_id: int
    token: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


