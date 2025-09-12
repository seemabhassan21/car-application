from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from agents.agent_schema import AgentRequest
from agents.agents import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/", response_class=PlainTextResponse)
async def agent_endpoint(request: AgentRequest):
    try:
        result = await run_agent(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")
