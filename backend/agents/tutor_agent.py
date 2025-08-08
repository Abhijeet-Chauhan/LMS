import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState

#  Configuration 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "lms_collection"

class TutorAgent:
    """
    This is the Tutor Agent. It explains concepts from the textbook in a simple,
    easy-to-understand way, like a friendly teacher.
    """
    def __init__(self):
        # RAG setup
        self.retriever = self._setup_retriever()
        self.llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)

        system_prompt = (
            "You are a friendly and patient tutor. Your goal is to explain concepts to a student "
            "using the provided context from their textbook. Break down complex ideas into simple steps. "
            "Use analogies and simple examples to help them understand. Always be encouraging."
            "\n\nHere is the context from the textbook:\n{context}"
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{history}"),
                ("human", "My question is: {question}"),
            ]
        )

        self.runnable = self.prompt | self.llm

    def _setup_retriever(self):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        qdrant_client = QdrantClient(url=QDRANT_URL)
        vectorstore = Qdrant(
            client=qdrant_client,
            collection_name=QDRANT_COLLECTION,
            embeddings=embeddings
        )
        return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    def tutor_node(self, state: AgentState):
        """
        The main node for the Tutor agent.
        """
        print("---TUTOR AGENT---")
        question = state["question"]

        # Retrieve context
        docs = self.retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])

        # generate tutoring answer
        answer = self.runnable.invoke({"context": context, "question": question})

        return {"answer": answer.content}