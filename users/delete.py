from sqlalchemy.orm import Session
from . import models
import datetime

from .database import SessionLocal
from sqlalchemy import exc as sa_exc

DELETION_THRESHOLD_DAYS = 2 

def cleanup_stale_users(db: Session) -> int:
    time_period = datetime.timedelta(minutes=DELETION_THRESHOLD_DAYS)
    cutoff_time = datetime.datetime.now() - time_period
    users_to_delete_ids = db.query(models.User.id).filter(models.User.deleteTime < cutoff_time).all()

    user_ids = [user_id[0] for user_id in users_to_delete_ids]
    if not user_ids:
        return 0
    try:
        logs_deleted = db.query(models.loginlog).filter(models.loginlog.user_id.in_(user_ids)).delete(synchronize_session='fetch')
    except AttributeError:
        print("SCHEDULER WARNING: Login logs deletion skipped. Check if 'models.LoginLog' and 'models.LoginLog.user_id' are correctly defined.")
    except sa_exc.InvalidRequestError as e:
         # Catches configuration errors related to LoginLog model
         print(f"SCHEDULER ERROR during LoginLog deletion: {e}")
    rows_deleted = db.query(models.User).filter(models.User.deleteTime < cutoff_time).delete(synchronize_session='fetch')
    db.commit()
    
    return rows_deleted

# --- SCHEDULER WRAPPER (THE FIX) ---
def scheduled_cleanup_job():
    """
    Wrapper function that runs the core cleanup logic. 
    It manually creates and closes the database session.
    """
    db_session = SessionLocal() # CRITICAL: Manually creating the session
    
    try:
        deleted_count = cleanup_stale_users(db_session)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now}] SCHEDULER: Deleted {deleted_count} user(s) whose 'deleteTime' was older than {DELETION_THRESHOLD_DAYS} minutes.")
        
    except Exception as e:
        print(f"SCHEDULER ERROR: Cleanup job failed: {e}")
        db_session.rollback()
    finally:
        db_session.close()
    
