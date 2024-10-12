from pydantic import BaseModel
from typing import List, Dict, Any
from swarm import Swarm, Agent

class AgentCreate(BaseModel):
    name: str
    instructions: str
    connections: List[str] = []

class Message(BaseModel):
    role: str
    content: str

class AgentRun(BaseModel):
    agent_name: str
    messages: List[Message]
