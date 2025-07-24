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
            "You are an expert Sudoku assistant helping players improve their solving skills. "
            "Analyze the current puzzle state and provide helpful guidance using standard Sudoku solving techniques. "
            "When giving hints or explanations, work through the logic step by step using techniques like: "
            "elimination, naked singles, hidden singles, pointing pairs, box/line reduction, naked pairs/triples, etc. "
            "Format your responses using markdown for better readability (use **bold** for emphasis, bullet points for steps, etc.). "
            "Never mention that you have access to the solution - instead, present your reasoning as if you're solving it naturally. "
            "Only at the very end of your explanation, if providing a specific move, you may briefly mention verification."
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
        input_text = f"Analyze this Sudoku puzzle and suggest the next logical move:\n\nCurrent state: {current_board}\n\nPlease identify the best next move and explain the reasoning using standard Sudoku techniques."
        
        try:
            results = self.rag_chain.invoke({"input": input_text})
            return results['answer']
        except Exception as e:
            return f"Error getting hint: {str(e)}"
    
    def get_hint_with_position(self, current_board, solution_board):
        """Get a hint with specific position and value from the AI"""
        # Find the first empty cell that can be filled
        for row in range(9):
            for col in range(9):
                if current_board[row][col] is None:
                    correct_value = solution_board[row][col]
                    if correct_value is not None:
                        # Get explanation from AI
                        input_text = f"Analyze this Sudoku puzzle state: {current_board}\n\nI'm looking at the cell in row {row+1}, column {col+1}. Walk me through the logical reasoning for what number should go there using standard Sudoku solving techniques. At the end, you can verify that {correct_value} is indeed the correct answer."
                        
                        try:
                            results = self.rag_chain.invoke({"input": input_text})
                            explanation = results['answer']
                            
                            return {
                                'row': row,
                                'col': col,
                                'value': correct_value,
                                'explanation': explanation
                            }
                        except Exception as e:
                            return {
                                'row': row,
                                'col': col,
                                'value': correct_value,
                                'explanation': f"Place {correct_value} here. Error getting detailed explanation: {str(e)}"
                            }
        
        # If no empty cells found, return general hint
        return self.get_hint(current_board, solution_board)
    
    def chat(self, message, current_board=None, solution_board=None):
        """General chat functionality with optional puzzle context"""
        if current_board and solution_board:
            context = f"Current Sudoku puzzle state: {current_board}\n\nUser question: {message}\n\nPlease help with this Sudoku-related question, providing guidance based on logical solving techniques."
        else:
            context = message
            
        try:
            results = self.rag_chain.invoke({"input": context})
            return results['answer']
        except Exception as e:
            return f"Error in chat: {str(e)}"