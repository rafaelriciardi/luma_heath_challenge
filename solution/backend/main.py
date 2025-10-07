import os
import uvicorn
import warnings
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from agents import MedicalAgent

warnings.filterwarnings("ignore")

load_dotenv()

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

app = FastAPI()
agent = MedicalAgent(model=llm)

@app.get("/")
async def root():
    return {"message": "Im Alive"}

class MessageInput(BaseModel):
    content: str

@app.post("/get_answer/")
async def get_answer(input_data: MessageInput):
    content = input_data.content

    response = agent.invoke(content)

    return response['messages'][-1].content

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)