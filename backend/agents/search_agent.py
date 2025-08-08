import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from graph.state import AgentState
from tools.web_search import web_search_tool
from dotenv import load_dotenv

load_dotenv()
# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class SearchAgent:
    """
    This agent is a specialist in using tools to find information on the web.
    """
    def __init__(self):
        # the tools this agent can use
        self.tools = [web_search_tool]

        # prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful research assistant. You have access to a web search tool."),
            ("user", "{question}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Set up the LLM
        llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)

        # Create agent
        agent = create_tool_calling_agent(llm, self.tools, prompt)

        # Create Agent Executor
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def search_node(self, state: AgentState):
        """
        The main node for the search agent.
        """
        print("---SEARCH AGENT---")
        result = self.agent_executor.invoke({"question": state["question"]})
        return {"answer": result["output"]}