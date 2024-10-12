import json
import re
from typing import Dict, List, Callable
from swarm import Swarm, Agent
from app.models.agent import AgentCreate, AgentRun

class AgentService:
    def __init__(self, json_file: str = "agents.json"):
        self.client = Swarm()
        self.agents: Dict[str, Agent] = {}
        self.json_file = json_file
        self.load_agents_from_json()

    def load_agents_from_json(self):
        try:
            with open(self.json_file, 'r') as f:
                agent_data = json.load(f)
            
            self.agents = {}
            for name, data in agent_data.items():
                # Handle both old and new formats
                connections = data.get('connections', [])
                if 'functions' in data:
                    # Convert old 'functions' format to 'connections'
                    connections = [f.replace('transfer_to_', '').replace('_', ' ') for f in data['functions'] if f.startswith('transfer_to_')]
                
                agent = Agent(
                    name=name,
                    instructions=data['instructions'],
                    functions=self.create_transfer_functions(connections)
                )
                self.agents[name] = agent
            
            # Save in new format to ensure future compatibility
            self.save_agents_to_json()
        except FileNotFoundError:
            print(f"No {self.json_file} found. Starting with an empty agent set.")

    def save_agents_to_json(self):
        agent_data = {}
        for name, agent in self.agents.items():
            agent_data[name] = {
                'instructions': agent.instructions,
                'connections': [f.__name__.replace('transfer_to_', '').replace('_', ' ') for f in agent.functions if f.__name__.startswith('transfer_to_')]
            }
        
        with open(self.json_file, 'w') as f:
            json.dump(agent_data, f, indent=2)

    def create_transfer_functions(self, connections: List[str]) -> List[Callable]:
        def create_transfer(target: str):
            def transfer():
                return self.agents[target]
            # Sanitize the function name
            sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', target)
            transfer.__name__ = f"transfer_to_{sanitized_name}"
            return transfer
        
        return [create_transfer(conn) for conn in connections]

    def get_all_agents(self) -> List[str]:
        return list(self.agents.keys())

    def get_agent(self, agent_name: str) -> Agent:
        return self.agents.get(agent_name)

    def create_agent(self, agent: AgentCreate):
        if agent.name in self.agents:
            raise ValueError("Agent already exists")
        
        new_agent = Agent(
            name=agent.name,
            instructions=agent.instructions,
            functions=self.create_transfer_functions(agent.connections)
        )
        self.agents[agent.name] = new_agent
        self.save_agents_to_json()
        return {"message": f"Agent {agent.name} created successfully"}

    def update_agent(self, agent_name: str, instructions: str = None, connections: List[str] = None):
        if agent_name not in self.agents:
            raise ValueError("Agent not found")
        
        agent = self.agents[agent_name]
        if instructions:
            agent.instructions = instructions
        if connections is not None:
            agent.functions = self.create_transfer_functions(connections)
        
        self.save_agents_to_json()
        return {"message": f"Agent {agent_name} updated successfully"}

    def delete_agent(self, agent_name: str):
        if agent_name not in self.agents:
            raise ValueError("Agent not found")
        
        del self.agents[agent_name]
        self.save_agents_to_json()
        return {"message": f"Agent {agent_name} deleted successfully"}

    def run_agent(self, run: AgentRun):
        agent = self.agents.get(run.agent_name)
        if not agent:
            raise ValueError("Agent not found")
        
        messages = [dict(m) for m in run.messages]
        response = self.client.run(agent=agent, messages=messages)
        
        next_agent = None
        for function in agent.functions:
            if function.__name__.startswith('transfer_to_'):
                next_agent = function.__name__.replace('transfer_to_', '')
                break
        
        return {
            "response": response.messages[-1]["content"],
            "agent_name": run.agent_name,
            "next_agent": next_agent
        }

    def get_agent_connections(self):
        connections = []
        for agent_name, agent in self.agents.items():
            for function in agent.functions:
                if function.__name__.startswith('transfer_to_'):
                    target = function.__name__.replace('transfer_to_', '').replace('_', ' ')
                    connections.append({"source": agent_name, "target": target})
        return connections
