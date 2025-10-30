from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas,database,models, token
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import datetime


router = APIRouter(tags=["Authentication"])
get_db = database.get_db
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
# create user 
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
@router.post("/create",response_model=schemas.ShowUser)
def create_user(request : schemas.User, db: Session = Depends(get_db)):
    hashedPassword = pwd_context.hash(request.password)
    new_user = models.User(name = request.name,email = request.email, password = hashedPassword, isadmin = request.isadmin)
    if db.query(models.User).filter(models.User.email == request.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with the email {request.email} already exists")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#login user
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends() , db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password")
    if not user.isActive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your account has been deleted! To restore contact Admin")
    
    access_token = token.create_access_token(data={"sub": user.email,
                                                   "id": user.id,
                                                   "isadmin": user.isadmin})
    try:
        login_log = models.loginlog(user_id=user.id, token=access_token, created_at=datetime.datetime.now())
        db.add(login_log)
        db.commit()
        db.refresh(login_log)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login log creation failed")
    return {"access_token":access_token, "token_type":"bearer"}


