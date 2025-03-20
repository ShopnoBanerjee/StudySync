from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import aiofiles
import os

###
from app.services.summarization import summarize
from sqlalchemy.orm import Session
from app.schemas.note import NoteCreate, NoteResponse
from app.models.note import Note
from app.api.dependencies import get_db
###

router = APIRouter()

@router.post("/upload")
async def upload_summarize_persist(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if  not file.filename.endswith((".txt","pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and pdf files allowed")

    os.makedirs("temp", exist_ok=True)
    
    file_location = f"temp/{file.filename}"
    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # summarize the content of the file
    async with aiofiles.open(file_location, "r") as in_file:
        text = await in_file.read()
    
    summary = summarize(text)
    title = file.filename.replace('.txt', '').replace('_', ' ')
    
    note = Note(filename=file.filename, summary=summary, title=title, content=text)
    db.add(note)
    db.commit()
    db.refresh(note)
        
    return {summary}