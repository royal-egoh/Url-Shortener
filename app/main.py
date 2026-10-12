from fastapi import FastAPI
from app.database import engine, Base
from app.routers import routers
from app.models.short_link import *
from app.models.users import *


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(routers.router)