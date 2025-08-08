import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "lms_collection"

class QAAgent:
    """
    This is the QA Agent. It answers questions based on the textbook context.
    It's the core RAG (Retrieve-Augment-Generate) pipeline.
    """

    def __init__(self):
        # the components needed for RAG
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        qdrant_client = QdrantClient(url=QDRANT_URL)
        self.vectorstore = Qdrant(
            client=qdrant_client,
            collection_name=QDRANT_COLLECTION,
            embeddings=self.embeddings
        )
        
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
        self.llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)
        
        system_prompt = (
            "You are an expert at answering questions using the provided context. "
            "Your answers must be concise and directly based on the information given. "
            "Do not use any external knowledge. If the context does not contain the answer, "
            "say 'The provided context does not contain information on this topic.'"
            "\n\nHere is the context:\n{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{history}"),
                ("human", "{question}"),
            ]
        )
        
        self.runnable = self.prompt | self.llm

    def qa_node(self, state: AgentState):
        """
        The main node for the QA agent. It performs the RAG process.
        """
        print("---QA AGENT---")
        question = state["question"]
        
        # Retrieve
        docs = self.retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Generate
        answer = self.runnable.invoke({"context": context, "question": question})
        
        return {"answer": answer.content}