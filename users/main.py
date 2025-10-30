from fastapi import FastAPI
from .database import engine
from .import models
from .routers import users, authentication

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .delete import scheduled_cleanup_job

models.Base.metadata.create_all(bind=engine)

app = FastAPI() 
scheduler = AsyncIOScheduler()

app.include_router(authentication.router)
app.include_router(users.router)

#Scheduler
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(scheduled_cleanup_job, trigger=IntervalTrigger(seconds=5), id="my_interval_job")
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()