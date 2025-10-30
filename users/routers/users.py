from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database
from typing import List
from .. import models, schemas
from ..oaut2 import get_current_user, get_admin_user
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

router = APIRouter(tags=["Users"])
get_db = database.get_db

# user can get their logedin logs
@router.get("/loginlogs", response_model=List[schemas.loginLog])
def get_login_logs(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    logs = db.query(models.loginlog).filter(models.loginlog.user_id == current_user.id).all()
    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Login logs for user with the id {current_user.id} are not available")
    return logs

# user can get their own details
@router.get("/me", response_model=schemas.ShowUser)
def get_me(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    user =db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the email {current_user.id} is not available")
    return user

# admin & user can get all users
@router.get("/list", response_model=List[schemas.ShowUser])
def get_all_user(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.isadmin == False, models.User.isActive == True)
    return user

#admin can see admin list
@router.get("/admin/list", response_model= list[schemas.ShowUser])
def get_all_admin(db : Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_admin_user)):
    user = db.query(models.User).filter(models.User.isadmin == True, models.User.isActive == True)
    return user

# admin & user can get user by id
@router.get("/{id}", response_model=schemas.ShowUser, )
def get_user(id:int, db: Session = Depends(get_db),get_admin_user: schemas.TokenData = Depends(get_current_user) ):
    user =db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    return user


# user can update their own details
@router.patch("/update/me")
def update_me(request: schemas.UpdateUser, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    
    update_data = request.model_dump(exclude_unset=True, exclude={'isadmin'})
    if update_data.get('password'):
        hashed_password = pwd_context.hash(update_data['password'])
        update_data['password'] = hashed_password

    user = db.query(models.User).filter(models.User.id == current_user.id)
    user_updated = user.update(update_data, synchronize_session=False)
    db.commit()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {current_user.id} is not available")
    return "updated successfully" 


# admin can update any user details
@router.patch("/update/{id}")
def update_user(id:int, request: schemas.UpdateUser, db: Session =Depends(get_db),get_admin_user: schemas.TokenData = Depends(get_admin_user)):
    update_data = request.model_dump(exclude_unset=True, exclude={'id'})
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update."
        )
    
    if update_data.get('password'):
        hashed_password = pwd_context.hash(update_data['password'])
        update_data['password'] = hashed_password

    user = db.query(models.User).filter(models.User.id == id)
    user_updated = user.update(update_data, synchronize_session=False)
    db.commit()

    if user_updated == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    
    return "updated Successfully"

# user can delete their own account
@router.delete("/delete/me")
def delete_me(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    user =db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {current_user.id} is not available")
    else:
        user.isActive = False
        user.deleteTime = datetime.now()
        db.commit()
        return "deleted successfully"

# admin can delete any user
@router.delete("/delete/{id}")
def delete_user(id:int, db: Session = Depends(get_db),get_admin_user: schemas.TokenData = Depends(get_admin_user)):
    user =db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    user.isActive = False
    user.deleteTime = datetime.now()
    db.commit()
    return "deleted successfully"


# admin logedin logs of users by id
@router.get("/loginlogs/{id}", response_model=List[schemas.loginLog])
def admin_get_login_logs(id:int , db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_admin_user)):
    logs = db.query(models.loginlog).filter(models.loginlog.user_id == id).all()
    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Login logs for user with the id {id} are not available")
    return logs
# -----------------------




















