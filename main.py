from fastapi import FastAPI
from database import engine
import models
from routers import transactions, credits

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(transactions.router)
app.include_router(credits.router)