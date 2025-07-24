import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

class SudokuAI:
    def __init__(self):
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")
        
        self.llm = ChatOpenAI(model="gpt-4o")
        self.rag_chain = None
        self._setup_rag()
    
    def _setup_rag(self):
        # Load and process the PDF
        file_path = "./solving_sudoku.pdf"
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Create vector store and retriever
        vectorstore = InMemoryVectorStore.from_documents(
            documents=splits, embedding=OpenAIEmbeddings()
        )
        retriever = vectorstore.as_retriever()
        
        # Create the RAG chain
        system_prompt = (
            "You are an assistant for solving sudoku. "
            "You will be provided with the current state of the puzzle as well as the solution of the puzzle. "
            "If there are any mistakes in the current puzzle, point them out and end. "
            "Otherwise, choose a random cell that you think can be deduced from the current state of the puzzle and decide which number belongs there. "
            "Explain the logic that led you to that number, without referencing the solution."
            "\n\n"
            "{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        self.rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    def get_hint(self, current_board, solution_board):
        """Get a hint for the next move from the AI"""
        input_text = f"Current puzzle state: {current_board}\nSolution: {solution_board}"
        
        try:
            results = self.rag_chain.invoke({"input": input_text})
            return results['answer']
        except Exception as e:
            return f"Error getting hint: {str(e)}"
    
    def chat(self, message, current_board=None, solution_board=None):
        """General chat functionality with optional puzzle context"""
        if current_board and solution_board:
            context = f"Current puzzle state: {current_board}\nSolution: {solution_board}\n\nUser message: {message}"
        else:
            context = message
            
        try:
            results = self.rag_chain.invoke({"input": context})
            return results['answer']
        except Exception as e:
            return f"Error in chat: {str(e)}"