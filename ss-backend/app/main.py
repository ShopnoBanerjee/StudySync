from fastapi import FastAPI
from app.api.endpoints import notes
import os
import logging

app = FastAPI()
app.include_router(notes.router, prefix ="/api")

@app.get("/")
def home():
    return {"message": "Welcome to StudySync Backend"}

if __name__ == "main":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
