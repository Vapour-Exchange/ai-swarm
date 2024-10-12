from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.models.agent import AgentCreate, AgentRun, Message
from app.dependencies import templates
from app.services.agent_service import AgentService

router = APIRouter()

# We'll use dependency injection to get the AgentService instance
def get_agent_service():
    from app.main import agent_service
    return agent_service

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/agents", response_class=HTMLResponse)
async def get_agents(request: Request, agent_service: AgentService = Depends(get_agent_service)):
    agents = agent_service.get_all_agents()
    return templates.TemplateResponse("agents.html", {"request": request, "agents": agents})

@router.post("/agents")
async def create_agent(
    name: str = Form(...),
    instructions: str = Form(...),
    agent_service: AgentService = Depends(get_agent_service)
):
    agent = AgentCreate(name=name, instructions=instructions)
    return agent_service.create_agent(agent)

@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str, agent_service: AgentService = Depends(get_agent_service)):
    agent = agent_service.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"agent": agent}

@router.get("/run", response_class=HTMLResponse)
async def run_agent_form(request: Request, agent_service: AgentService = Depends(get_agent_service)):
    agents = agent_service.get_all_agents()
    return templates.TemplateResponse("run_agent.html", {"request": request, "agents": agents})

@router.post("/run")
async def run_agent(request: Request, agent_name: str = Form(...), message: str = Form(...)):
    agent_service = request.app.state.agent_service
    run = AgentRun(agent_name=agent_name, messages=[Message(role="user", content=message)])
    
    try:
        result = agent_service.run_agent(run)
        return JSONResponse({
            "response": result["response"],
            "agent_name": result["agent_name"],
            "next_agent": result["next_agent"]
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/agent-connections", response_class=HTMLResponse)
async def agent_connections(request: Request, agent_service: AgentService = Depends(get_agent_service)):
    agents = agent_service.get_all_agents()
    connections = agent_service.get_agent_connections()
    return templates.TemplateResponse("agent_connections.html", {"request": request, "agents": agents, "connections": connections})

@router.post("/update-connections")
async def update_connections(
    from_agent: str = Form(...),
    to_agent: str = Form(...),
    action: str = Form(...),
    agent_service: AgentService = Depends(get_agent_service)
):
    try:
        if action == "connect":
            agent_service.connect_agents(from_agent, to_agent)
        elif action == "disconnect":
            agent_service.disconnect_agents(from_agent, to_agent)
        else:
            raise ValueError("Invalid action")
        
        return JSONResponse({"status": "success"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
