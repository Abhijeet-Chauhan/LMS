from langgraph.graph import StateGraph, END
from .state import AgentState
from agents.supervisor import SupervisorAgent
from agents.qa_agent import QAAgent
from agents.tutor_agent import TutorAgent
from agents.search_agent import SearchAgent
from agents.reasoning_agent import ReasoningAgent 
from agents.planner_agent import PlannerAgent
from agents.study_planner_node import StudyPlannerNode

# Initialize agent classes
supervisor = SupervisorAgent()
qa_agent = QAAgent()
tutor_agent = TutorAgent()
search_agent = SearchAgent()
reasoning_agent = ReasoningAgent()
planner_agent = PlannerAgent()
study_planner = StudyPlannerNode() 

# Create new state graph
graph_builder = StateGraph(AgentState)

# Define nodes 
# Add the supervisor node which is the entry point
graph_builder.add_node("supervisor", supervisor.supervisor_node)
graph_builder.add_node("qa_agent", qa_agent.qa_node)
graph_builder.add_node("tutor_agent", tutor_agent.tutor_node)
graph_builder.add_node("search_agent", search_agent.search_node)
graph_builder.add_node("reasoning_agent", reasoning_agent.reasoning_node)
graph_builder.add_node("planner_agent", planner_agent.planner_node)
graph_builder.add_node("study_planner", study_planner.create_plan_node) 
# Define the edges 
# The supervisor is the starting point of the graph
graph_builder.set_entry_point("supervisor")

def route_to_specialist(state: AgentState):
    """
    This function reads the 'next_node' value from the state
    and decides which node to route to next.
    """
    return state["next_node"]

# Add the conditional edge from the supervisor
# This edge will use the output of the supervisor to decide which node to run next
graph_builder.add_conditional_edges(
    "supervisor",
    route_to_specialist,
    {
        "qa_agent": "qa_agent",
        "tutor_agent": "tutor_agent",
        "search_agent": "search_agent",
        "reasoning_agent": "reasoning_agent",
        "planner_agent": "planner_agent",      
    },
)

graph_builder.add_edge("search_agent", END)
graph_builder.add_edge("qa_agent", "study_planner")
graph_builder.add_edge("tutor_agent", "study_planner")
graph_builder.add_edge("study_planner", END)
graph_builder.add_edge("reasoning_agent", END) 
graph_builder.add_edge("planner_agent", END)


# Compile the graph into a runnable app
graph = graph_builder.compile()