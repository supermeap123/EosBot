# agents.py
import threading

class Agent:
    def __init__(self, name, model_string, backend, temperature=0.7):
        self.name = name
        self.model_string = model_string
        self.backend = backend  # 'openrouter' or 'openpipe'
        self.temperature = temperature
        self.conversation_histories = {}
        self.system_prompt = f"You are {self.name}."  # Default system prompt

class AgentManager:
    def __init__(self):
        self.agents = {}
        self.lock = threading.Lock()

    def add_agent(self, agent_name, model_string, backend, temperature=0.7):
        with self.lock:
            if agent_name in self.agents:
                return False  # Agent already exists
            agent = Agent(agent_name, model_string, backend, temperature)
            self.agents[agent_name] = agent
            return True

    def remove_agent(self, agent_name):
        with self.lock:
            if agent_name in self.agents:
                del self.agents[agent_name]
                return True
            return False

    def get_agent(self, agent_name):
        with self.lock:
            return self.agents.get(agent_name)

    def set_backend(self, agent_name, backend):
        with self.lock:
            agent = self.agents.get(agent_name)
            if agent:
                agent.backend = backend
                return True
            return False

    def set_temperature(self, agent_name, temperature):
        with self.lock:
            agent = self.agents.get(agent_name)
            if agent:
                agent.temperature = temperature
                return True
            return False

    def set_model_string(self, agent_name, model_string):
        with self.lock:
            agent = self.agents.get(agent_name)
            if agent:
                agent.model_string = model_string
                return True
            return False

    def set_system_prompt(self, agent_name, system_prompt):
        with self.lock:
            agent = self.agents.get(agent_name)
            if agent:
                agent.system_prompt = system_prompt
                return True
            return False