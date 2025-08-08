from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Represents the state of our agentic graph. This is the shared memory.
    """
    question: str # user original question
    answer: str   # final answer to be returned
    history: Annotated[List[BaseMessage], operator.add] # conversation history allows appending
    next_node: str # next node to call in the graph decided by the supervisor