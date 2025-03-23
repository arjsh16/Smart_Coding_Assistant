
from fastapi import FastAPI
from pydantic import BaseModel
from stack_gemini import main as get_code_suggestions  
import uvicorn
import os 

app = FastAPI()

class CodeRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "FastAPI is running!"}

@app.post("/get_code")
def generate_code(request: CodeRequest):
    return {"output" : get_code_suggestions(request.prompt)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
