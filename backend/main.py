from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import sys
import os
import json
from typing import List, Dict, Any

# Import your existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.ner_processor import process_ner
from backend.chatbot import get_chatbot_response

app = FastAPI()

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

class ChatInput(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []

class NERResponse(BaseModel):
    entities: Dict[str, List[str]]
    counts: Dict[str, int]
    text: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float

@app.get("/")
async def root():
    return {"message": "NLP API Server is running"}

@app.post("/api/ner/text", response_model=NERResponse)
async def ner_text(input_data: TextInput):
    """Process NER on single text input"""
    try:
        result = process_ner(input_data.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ner/csv")
async def ner_csv(file: UploadFile = File(...)):
    """Process NER on uploaded CSV file"""
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Process each row
        results = []
        for idx, row in df.head(100).iterrows():  # Limit to 100 rows for performance
            text = str(row.get('text', ''))
            if text and text != 'nan':
                ner_result = process_ner(text)
                results.append({
                    'row': idx,
                    'text': text[:100],  # Truncate for display
                    'entities': ner_result['entities'],
                    'counts': ner_result['counts']
                })
        
        return {
            "success": True,
            "total_rows": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(input_data: ChatInput):
    """Process chat message and return response"""
    try:
        result = get_chatbot_response(
            input_data.message, 
            input_data.conversation_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)