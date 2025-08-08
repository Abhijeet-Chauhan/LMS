import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class StudyPlannerNode:
    """
    A specialist node that creates an actionable study plan based on a given topic.
    """
    def __init__(self):
        system_prompt = (
            "You are an expert study planning assistant. Your task is to take a user's question and the corresponding answer, "
            "and create a concise, actionable study plan to help the student master the topic. "
            "The plan should include key concepts to review, practice problems to try, and maybe a real-world application."
            "\n\nFormat the plan clearly with a title and bullet points."
            "\n\n## User's Question:\n{question}"
            "\n\n## Core Answer on the Topic:\n{answer}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
            ]
        )
        
        self.llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY, temperature=0.7)
        self.runnable = self.prompt | self.llm

    def create_plan_node(self, state: AgentState):
        """
        The main node for creating the study plan.
        """
        print("---STUDY PLANNER NODE---")
        
        # Generate the study plan
        study_plan = self.runnable.invoke({
            "question": state["question"],
            "answer": state["answer"]  # Use the answer from the previous agent
        }).content
        
        # Combine the original answer with the new study plan for the final output
        final_combined_answer = f"{state['answer']}\n\n---\n\n### Your Study Plan\n{study_plan}"
        
        return {"answer": final_combined_answer}