import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class ReasoningAgent:
    """
    This agent specializes in step-by-step reasoning to solve complex problems.
    It does not use RAG, as it relies on its own logical capabilities.
    """
    def __init__(self):
        system_prompt = (
            "You are an expert at logical reasoning. Given a user's question, "
            "your task is to break it down into a series of step-by-step thoughts. "
            "Think logically and show your work. After your reasoning, clearly state the final answer."
            "\n\nHere is the user's question:\n{question}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{history}"),
            ]
        )
        
        self.llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)
        self.runnable = self.prompt | self.llm

    def reasoning_node(self, state: AgentState):
        """
        The main node for the reasoning agent.
        """
        print("---REASONING AGENT---")
        result = self.runnable.invoke({"question": state["question"]})
        return {"answer": result.content}