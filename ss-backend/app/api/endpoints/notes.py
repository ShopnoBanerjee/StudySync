from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import aiofiles
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

###
from app.services.summarization import summarize
from sqlalchemy.orm import Session
from app.schemas.note import NoteCreate, NoteResponse
from app.models.note import Note
from app.api.dependencies import get_db
###

router = APIRouter()

@router.post("/summarize_notes/", response_model=NoteResponse, status_code=201)
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

@router.post("/youtube_summarize/")
async def youtube_summarize(url: str, db: Session = Depends(get_db)):
    """
    Fetch YouTube transcript, chunk it into 5-minute segments, and summarize each chunk
    """
    # Extract video ID from URL
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if not video_id_match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    video_id = video_id_match.group(1)
    
    try:
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
        # Group into 5-minute chunks (300 seconds)
        chunks = {}
        chunk_duration = 300  # 5 minutes in seconds
        
        for entry in transcript:
            chunk_index = int(entry['start'] / chunk_duration)
            chunk_key = f"chunk{chunk_index + 1}"
            
            if chunk_key not in chunks:
                start_time = entry['start']
                min_start = int(start_time) // 60
                sec_start = int(start_time) % 60
                
                end_time = (chunk_index + 1) * chunk_duration
                min_end = int(end_time) // 60
                sec_end = int(end_time) % 60
                
                timestamp = f"{min_start}:{sec_start:02d} - {min_end}:{sec_end:02d}"
                chunks[chunk_key] = {
                    "time": timestamp,
                    "text": entry['text'],
                    "summary": ""
                }
            else:
                chunks[chunk_key]["text"] += " " + entry['text']
        
        # Summarize each chunk
        for chunk_key, chunk_data in chunks.items():
            chunk_data["summary"] = summarize(chunk_data["text"])
            # Remove the full text to save space in the response
            del chunk_data["text"]
            
        # Save to database
        title = f"YouTube: {video_id}"
        summary_json = {key: value for key, value in chunks.items()}
        note = Note(
            filename=f"{video_id}.json", 
            title=title, 
            summary=str(summary_json),  # Convert to string for storage
            content=url
        )
        
        # db.add(note)
        # db.commit()
        # db.refresh(note)
        
        return chunks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transcript: {str(e)}")
    