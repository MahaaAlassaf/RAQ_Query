from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage
from typing import Dict, Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.author import Author
from llm2.intent_extraction import IntentExtractor
from llm2.vector_data_manager import VectorDataManager
import logging

ollama_model = OllamaLLM(model="llama3.1")

memory = ConversationBufferMemory(memory_key="chat_history")

# Define the GraphState class
class GraphState(TypedDict):
    question: Optional[str]
    intent_number: Optional[int]
    entity_name: Optional[str]
    num_recommendations: int
    response: Optional[str]
    book_info: Optional[Dict[str, str]]

def get_db_session():
    engine, SessionLocal = connect_to_db()
    return SessionLocal()

def classify_input_node(state: GraphState) -> GraphState:
    question = state.get('question', '').strip()
    if not question:
        state["response"] = "Please ask a valid question about books."
        return state

    intent_extractor = IntentExtractor()
    try:
        intent_response = intent_extractor.classify_intent_and_extract_entities(question)
        logging.info(f"Intent Number: {intent_response.intent_number}, Entity: {intent_response.entity_name}, Num Recommendations: {intent_response.num_recommendations}")
        state.update({
            "intent_number": intent_response.intent_number,
            "entity_name": intent_response.entity_name,
            "num_recommendations": intent_response.num_recommendations or 2,
        })
    except Exception as e:
        logging.error(f"Failed to classify intent: {e}")
        state["response"] = "Sorry, I couldn't understand your question. Please try again."
    return state

def retrieve_book_info(state: GraphState) -> GraphState:
    entity_name = state.get('entity_name', '')
    if not entity_name:
        state["response"] = "Please provide a book title to search for."
        return state

    with get_db_session() as db:
        logging.info(f"Fetching book info for: {entity_name}")
        book = db.query(Book).filter(Book.title.ilike(f"%{entity_name}%")).first()
        if book:
            state["book_info"] = {
                "title": book.title,
                "authors": ', '.join([author.name for author in book.authors]),
                "published_year": book.published_year,
                "genre": book.genre,
                "description": book.description,
            }
            logging.info(f"Book info retrieved: {state['book_info']}")
        else:
            logging.warning(f"No information found for book: {entity_name}")
            state["response"] = "No information found for the specified book."
    return state

def get_author_info_node(state: GraphState) -> GraphState:
    entity_name = state.get('entity_name', '').strip()
    logging.info(f"Fetching author name for book: '{entity_name}'")
    
    with get_db_session() as db:
        try:
            book = db.query(Book).filter(Book.title.ilike(f"%{entity_name}%")).first()
            if book:
                authors = ', '.join([author.name for author in book.authors])
                state["response"] = f"Author(s): {authors}"
                logging.info(f"Authors retrieved: {authors}")
            else:
                logging.warning("No matching book found for author query.")
                state["response"] = "No author information found for the specified book."
        except Exception as e:
            logging.error(f"Error fetching author information: {e}")
            state["response"] = "An error occurred while retrieving author information."
    
    return state


def get_publication_year_node(state: GraphState) -> GraphState:
    book_info = state.get("book_info")
    logging.info(f"Retrieving publication year for book: '{state.get('entity_name')}'")
    
    if book_info:
        logging.info(f"Book info found: {book_info}")
        published_year = book_info.get('published_year')
        if published_year:
            state["response"] = f"Published Year: {published_year}"
        else:
            logging.warning("Publication year not available in book info.")
            state["response"] = "No publication year found for the specified book."
    else:
        logging.warning("No book info available to retrieve publication year.")
        state["response"] = "No publication year found for the specified book."
    
    return state


def get_book_info_node(state: GraphState) -> GraphState:
    book_info = state.get("book_info")
    if book_info:
        state["response"] = (
            f"Book Title: {book_info['title']}\n"
            f"Author(s): {book_info['authors']}\n"
            f"Published Year: {book_info['published_year']}\n"
            f"Genre: {book_info['genre']}\n"
            f"Summary: {book_info['description']}"
        )
    else:
        state["response"] = "No information found for the specified book."
    return state

def get_author_name_node(state: GraphState) -> GraphState:
    book_info = state.get("book_info")
    if book_info:
        state["response"] = f"Author(s): {book_info['authors']}"
    else:
        state["response"] = "No author information found for the specified book."
    return state

def summarize_book_node(state: GraphState) -> GraphState:
    book_info = state.get("book_info")
    if book_info:
        description = book_info['description']
        prompt_message = HumanMessage(
            content=f"Summarize the following book description in 3-4 sentences: {description}"
        )
        logging.info("Generating Summary ...")
        response = ollama_model.invoke([prompt_message]).strip()
        state["response"] = f"Summary of {book_info['title']}:\n{response}"
    else:
        state["response"] = "No summary found for the specified book."
    return state

def recommend_books_node(state: GraphState) -> GraphState:
    entity_name = state.get('entity_name', '')
    num_recommendations = state.get('num_recommendations', 2)
    with get_db_session() as db:
        logging.info(f"Recommending {num_recommendations} books based on: {entity_name}")
        vector_manager = VectorDataManager()
        recommended_titles = vector_manager.recommend_books(entity_name, num_recommendations)

        if not recommended_titles:
            state["response"] = "No recommendations found."
        else:
            book_details = []
            for title in recommended_titles:
                book = db.query(Book).filter(Book.title == title).first()
                if book:
                    book_details.append({
                        "title": book.title,
                        "description": book.description,
                        "published_year": book.published_year,
                        "average_rating": book.average_rating,
                        "num_pages": book.num_pages,
                        "ratings_count": book.ratings_count
                    })

            if book_details:
                response = f"Recommended {min(num_recommendations, len(book_details))} Books:\n" + "\n".join(
                    f"Title: {book['title']}\nDescription: {book['description']}\nPublished Year: {book['published_year']}\nAverage Rating: {book['average_rating']}\nNumber of Pages: {book['num_pages']}\nRatings Count: {book['ratings_count']}\n"
                    for book in book_details[:num_recommendations]
                )
                state["response"] = response
            else:
                state["response"] = "No detailed information found for the recommendations."
    return state

def handle_greeting_node(state: GraphState) -> GraphState:
    state["response"] = "Hello! How can I help you today?"
    return state

def route_question(state: GraphState) -> str:
    intent_number = state.get('intent_number')
    if intent_number == 1:
        return "get_book_info"
    elif intent_number == 2:
        return "get_author_name"
    elif intent_number == 3:
        return "summarize_book"
    elif intent_number == 4:
        return "recommend_books"
    elif intent_number == 5:
        return "get_publication_year"
    elif intent_number == 6:
        return "get_author_info"
    else:
        return "handle_greeting"

workflow = StateGraph(GraphState)

workflow.add_node("classify_input", classify_input_node)
workflow.add_node("retrieve_book_info", retrieve_book_info)
workflow.add_node("get_book_info", get_book_info_node)
workflow.add_node("get_author_name", get_author_name_node)
workflow.add_node("get_publication_year", get_publication_year_node)
workflow.add_node("summarize_book", summarize_book_node)
workflow.add_node("recommend_books", recommend_books_node)
workflow.add_node("get_author_info", get_author_info_node)
workflow.add_node("handle_greeting", handle_greeting_node)

workflow.add_edge(START, "classify_input")
workflow.add_conditional_edges(
    "classify_input",
    route_question,
    {
        "get_book_info": "retrieve_book_info",
        "get_author_name": "retrieve_book_info",
        "summarize_book": "retrieve_book_info",
        "recommend_books": "recommend_books",
        "get_publication_year": "retrieve_book_info",
        "get_author_info": "get_author_info",
        "handle_greeting": "handle_greeting",
    }
)

workflow.add_conditional_edges(
    "retrieve_book_info",
    lambda state: route_question(state),
    {
        "get_book_info": "get_book_info",
        "get_author_name": "get_author_name",
        "summarize_book": "summarize_book",
        "get_publication_year": "get_publication_year",
    }
)

workflow.add_edge("get_book_info", END)
workflow.add_edge("get_author_name", END)
workflow.add_edge("get_publication_year", END)
workflow.add_edge("summarize_book", END)
workflow.add_edge("recommend_books", END)
workflow.add_edge("get_author_info", END)
workflow.add_edge("handle_greeting", END)

app = workflow.compile()

if __name__ == "__main__":
    inputs = {"question": "List books written by Sidney Sheldon"}
    result = app.invoke(inputs)
    print(result["response"])



# from http import client
# from pyexpat import model
# from typing import Collection, Dict, Optional
# from chromadb.config import Settings

# import chromadb
# from langchain_ollama import OllamaLLM
# from llama_cpp import llama_model_p
# from sentence_transformers import SentenceTransformer
# from app.database.connector import connect_to_db
# from app.database.schemas.books import Book
# from app.database.schemas.author import Author
# from intent_extraction import IntentExtractor
# from vector_data_manager import VectorDataManager
# from langgraph.graph import END, StateGraph, START
# from langchain_core.messages import HumanMessage

# # Assuming you have an instance of OllamaLLM already initialized
# ollama_model = OllamaLLM(model="llama3.1")  # Ensure correct model usage

# # Define the GraphState class
# class GraphState:
#     def __init__(self, question=None, intent_number=None, entity_name=None, response=None):
#         self.question = question
#         self.intent_number = intent_number
#         self.entity_name = entity_name
#         self.response = response

# # Initialize the workflow
# workflow = StateGraph(GraphState)

# # Define node handlers
# def classify_input_node(state: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
#     question = state.get('question', '').strip()
#     intent_extractor = IntentExtractor()
#     intent_number, entity_name = intent_extractor.classify_intent_and_extract_entities(question)
#     print(f"Intent Number: {intent_number}, Entity: {entity_name}")
#     return {"intent_number": intent_number, "entity_name": entity_name}

# def get_book_info_node(entity_name: str, db) -> Dict[str, str]:
#     print(f"Fetching book info for: {entity_name}")
#     book = db.query(Book).filter(Book.title.ilike(f"%{entity_name}%")).first()
#     if book:
#         response = (
#             f"Book Title: {book.title}\n"
#             f"Author(s): {', '.join([author.name for author in book.authors])}\n"
#             f"Published Year: {book.published_year}\n"
#             f"Genre: {book.genre}\n"  # Ensure this matches your database field
#             f"Summary: {book.description}"
#         )
#         print(f"Generated response: {response}")
#         return {"response": response}
#     return {"response": "No information found for the specified book."}


# def get_author_info_node(state: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
#     entity_name = state.get('entity_name', '')
#     if not entity_name:
#         return {"response": "No author name provided."}

#     engine, SessionLocal = connect_to_db()
#     db = SessionLocal()

#     try:
#         print(f"Looking up author information for: {entity_name}")
#         author = db.query(Author).filter(Author.name.ilike(f"%{entity_name}%")).first()
#         print(f"Fetched author: {author}")

#         if author:
#             book_titles = ', '.join(book.title for book in author.books)
#             response = (
#                 f"Author Name: {author.name}\n"
#                 f"Books: {book_titles}\n"
#             )
#             return {"response": response}
#         else:
#             return {"response": "No information found for the specified author."}
#     except Exception as e:
#         return {"response": f"Error retrieving author information: {str(e)}"}
#     finally:
#         db.close()


# def summarize_book_node(entity_name: str, db) -> Dict[str, str]:
#     print(f"Summarizing book: {entity_name}")
#     book = db.query(Book).filter(Book.title.ilike(f"%{entity_name}%")).first()
#     if book:
#         # Use the book's description to create a summary
#         description = book.description
#         prompt_message = HumanMessage(
#             content=(
#                 f"Summarize the following book description in 3-4 sentences. Focus on the main themes, plot points, and any notable characters:\n\n{description}"
#             )
#         )

#         # Invoke the model to generate the summary
#         response = ollama_model.invoke([prompt_message]).strip()

#         # Log generated summary for debugging
#         print(f"Generated summary: {response}")
#         return {"response": f"Summary of {book.title}:\n{response}"}
#     else:
#         # Log if no book is found
#         print(f"No book found for: {entity_name}")
#         return {"response": "No summary found for the specified book."}



# # -------------------------------------------------------
# # Initialize the ChromaDB PersistentClient
# client = chromadb.PersistentClient(
#     path="app/pgAdmi4/chroma_db",
#     settings=Settings(),
# )

# # Create or get a collection within ChromaDB
# collection = client.get_or_create_collection(name="book_collection")

# def recommend_books_node(entity_name: str, db, num_recommendations: int = 2) -> Dict[str, str]:
#     print(f"Recommending {num_recommendations} books based on: {entity_name}")
#     vector_manager = VectorDataManager()
#     recommended_titles = vector_manager.recommend_books(entity_name, num_recommendations)

#     if not recommended_titles:
#         return {"response": "No recommendations found."}

#     book_details = []
#     for title in recommended_titles[:num_recommendations]:  # Limit to requested number
#         book = db.query(Book).filter(Book.title == title).first()
#         if book:
#             book_details.append({
#                 "title": book.title,
#                 "description": book.description,
#                 "published_year": book.published_year,
#                 "average_rating": book.average_rating,
#                 "num_pages": book.num_pages,
#                 "ratings_count": book.ratings_count
#             })

#     if book_details:
#         response = f"Recommended {len(book_details)} Books:\n" + "\n".join(
#             f"Title: {book['title']}\nDescription: {book['description']}\nPublished Year: {book['published_year']}\nAverage Rating: {book['average_rating']}\nNumber of Pages: {book['num_pages']}\nRatings Count: {book['ratings_count']}\n"
#             for book in book_details
#         )
#         return {"response": response}
#     else:
#         return {"response": "No detailed information found for the recommendations."}


# def handle_greeting_node(state: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
#     return {"response": "Hello! How can I help you today?"}

# def handle_search_node(state: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
#     intent_number = state.get('intent_number')
#     if intent_number == 1:
#         return get_book_info_node(state)
#     elif intent_number == 2:
#         return get_author_info_node(state)
#     elif intent_number == 3:
#         return summarize_book_node(state)
#     elif intent_number == 4:
#         return recommend_books_node(state)
#     return {"response": "Intent not handled."}

# # Add nodes to the graph
# workflow.add_node("classify_input", classify_input_node)
# workflow.add_node("get_book_info", get_book_info_node)
# workflow.add_node("get_author_info", get_author_info_node)
# workflow.add_node("summarize_book", summarize_book_node)
# workflow.add_node("recommend_books", recommend_books_node)
# workflow.add_node("handle_greeting", handle_greeting_node)
# workflow.add_node("handle_search", handle_search_node)

# # Define routing logic
# def route_question(state: Dict[str, Optional[str]]) -> str:
#     intent_number = state.get('intent_number')
#     if intent_number == 0:
#         return "handle_greeting"
#     else:
#         return "handle_search"

# # Build the graph
# workflow.add_edge(START, "classify_input")
# workflow.add_edge("classify_input", "handle_search")
# workflow.add_conditional_edges(
#     "handle_search",
#     route_question,
#     {
#         "handle_greeting": "handle_greeting",
#         "get_book_info": "get_book_info",
#         "get_author_info": "get_author_info",
#         "summarize_book": "summarize_book",
#         "recommend_books": "recommend_books"
#     }
# )
# workflow.add_edge('handle_greeting', END)
# workflow.add_edge('get_book_info', END)
# workflow.add_edge('get_author_info', END)
# workflow.add_edge('summarize_book', END)
# workflow.add_edge('recommend_books', END)

# # Compile the workflow
# graph_app = workflow.compile()
