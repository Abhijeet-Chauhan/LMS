import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class SupervisorAgent:
    """
    This is the supervisor agent. It decides which specialist agent should act next.
    """

    def __init__(self):
        # define the prompt template for the supervisor
        system_prompt = (
            "You are an expert router for a Learning Management System. Your primary function is to analyze the user's question and route it to the correct specialist agent. You must respond with *only* the name of the agent to use."

            "\n\n## AGENT ROSTER AND SPECIALTIES:"

            "\n1. **Planner Agent**: Use for any request related to creating a study plan, outlining the document's structure, or summarizing key topics and modules from the textbook. "
            "Examples: 'Create a study plan for this chapter.', 'Outline the main ideas in the document.', 'What are the key concepts I should learn?'"

            "\n2. **Tutor Agent**: Use for broad, conceptual, or explanatory questions where the user wants to understand a topic from their textbook in a simple, educational manner. "
            "Examples: 'Can you explain photosynthesis to me like I'm 10?', 'Help me understand the causes of the Cold War.'"

            "\n3. **QA Agent**: Use ONLY for specific, factual questions that can be answered directly by quoting or referencing the provided textbook context. "
            "Examples: 'What was the date of the signing of the Declaration of Independence according to the text?', 'What is the formula for the area of a circle mentioned in chapter 3?'"

            "\n4. **Reasoning Agent**: Use for logic puzzles, math word problems, or any question that requires step-by-step logical deduction to solve. This agent does not use the textbook. "
            "Examples: 'If a train leaves Station A at 3 PM traveling at 60 mph, and a second train leaves Station B at 4 PM traveling at 70 mph, when will they meet?', 'If all cats are mammals, and a poodle is not a cat, is a poodle a mammal?'"
            
            "\n5. **Web Search Agent**: Use ONLY if the question requires real-time, up-to-date information, or knowledge about current events, people, or topics that are clearly outside the scope of a standard textbook. "
            "Examples: 'Who won the 2024 presidential election?', 'What is the latest news on the Artemis program?'"


            "\n\n## ROUTING DECISION:"
            "\nAnalyze the user's question below and determine the single best agent to handle it based on the specialties described above. Your response must be one of the following exact names: `Planner Agent`, `Tutor Agent`, `QA Agent`, `Reasoning Agent`, or `Web Search Agent`."
        )

        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "User Question: {question}"),
            ]
        )
        
        # Initialize the Groq LLM
        llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)
        
        # Create the runnable agent chain
        self.runnable = prompt | llm

    def supervisor_node(self, state: AgentState):
        """
        The main node for the supervisor. It invokes the agent and updates the state.
        """
        print("---SUPERVISOR---")
        result = self.runnable.invoke({"question": state["question"]})
        
        # The result from the LLM will be the name of the agent
        # We will use this to decide the next node in the graph
        next_node_mapping = {
            "QA Agent": "qa_agent",
            "Tutor Agent": "tutor_agent",
            "Reasoning Agent": "reasoning_agent",
            "Planner Agent": "planner_agent",
        }
        
        next_node_key = result.content.strip()
        next_node = next_node_mapping.get(next_node_key, "qa_agent") # Default to qa_agent if not found
        
        print(f"Supervisor decided the next node is: {next_node}")
        
        return {"next_node": next_node}