import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "lms_collection"

class PlannerAgent:
    """
    This agent creates structured study plans and outlines from the textbook
    """
    def __init__(self):
        # We need a retriever to get a broad overview of the textbook content
        self.retriever = self._setup_retriever()
        
        system_prompt = (
            "You are an expert academic planner. Your primary task is to create a structured outline or study plan from a collection of text chunks from a textbook. "
            "The text chunks you receive may be out of order or incomplete."

            "\n\n## Your Process:"
            "\n1. First, carefully read all the provided text chunks to mentally assemble them and understand the document's overall structure and flow."
            "\n2. Identify the main topics, key headings, and important sub-points from the assembled context."
            "\n3. Based on your analysis, generate a clear, logical, and well-structured study plan or outline."
            "\n4. Format your output using markdown headings (#, ##) and bullet points (-) for readability."

            "\n\nHere is the textbook content you must analyze:\n{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{history}"),
                ("human", "User request: {question}"),
            ]
        )
        
        self.llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)
        self.runnable = self.prompt | self.llm

    def _setup_retriever(self):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        qdrant_client = QdrantClient(url=QDRANT_URL)
        vectorstore = Qdrant(
            client=qdrant_client, collection_name=QDRANT_COLLECTION, embeddings=embeddings
        )
        # Fetch more documents to get a better overview of the text
        return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 15})

    def planner_node(self, state: AgentState):
        """
        The main node for the planner agent.
        """
        print("---PLANNER AGENT---")
        question = state["question"]
        
        docs = self.retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        result = self.runnable.invoke({"context": context, "question": question})
        return {"answer": result.content}