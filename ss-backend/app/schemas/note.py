from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str
    summary: str

class NoteResponse(NoteCreate):
    id: int
    
    class Config:
        from_attributes = True