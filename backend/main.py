import os
import shutil
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Dict, Any
from graph.builder import graph
from graph.state import AgentState
from rag.ingest import ingest_file

# environment variables
load_dotenv()

# initialize FastAPI app
app = FastAPI(title="LMS Agentic RAG API")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Data Models 
class IngestResponse(BaseModel):
    message: str

class QuestionRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]] = []

class AnswerResponse(BaseModel):
    answer: str

# API Endpoints
@app.get("/")
def root():
    return {"message": "LMS Agentic RAG Backend is running"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to ingest a PDF or TXT file into the vector database.
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_file(temp_path)
    os.remove(temp_path)
    return {"message": result}

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(req: QuestionRequest):
    """
    Endpoint to ask a question. This now invokes our agentic graph.
    """
    # Define the input for the graph
    inputs = AgentState(question=req.question, history=req.history)

    # Invoke the graph with the inputs
    result = graph.invoke(inputs)

    # Return the answer from the final state
    return {"answer": result.get("answer", "No answer could be generated.")}