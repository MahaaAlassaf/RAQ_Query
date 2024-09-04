import re
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage
from typing import Dict, Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.author import Author
from llm.intent_extraction import IntentExtractor
from llm.vector_data_manager import VectorDataManager
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
        logging.info(f"Raw Intent Number: {intent_response.intent_number}, Raw Entity: {intent_response.entity_name}")

        # Clean the entity name to remove unwanted characters like **, *, or ""
        cleaned_entity_name = re.sub(r'[^\w\s]', '', intent_response.entity_name).strip()

        logging.info(f"Cleaned Entity: {cleaned_entity_name}")

        state.update({
            "intent_number": intent_response.intent_number,
            "entity_name": cleaned_entity_name,
            "num_recommendations": intent_response.num_recommendations or 2,
        })
    except Exception as e:
        logging.error(f"Failed to classify intent: {e}")
        state["response"] = "Sorry, I couldn't understand your question. Please try again."
    return state

def retrieve_book_info(state: GraphState) -> GraphState:
    entity_name = state.get('entity_name', '').strip()
    if not entity_name:
        state["response"] = "Please provide a book title to search for."
        return state

    logging.info(f"Entity Name being queried: {repr(entity_name)}")

    with get_db_session() as db:
        try:
            logging.info(f"Querying database for exact title match: '{entity_name}'")
            book = db.query(Book).filter(Book.title == entity_name).first()

            if not book:
                logging.info(f"No exact match found. Trying ilike with partial matching for: '{entity_name}'")
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
                logging.warning(f"No information found for book: {repr(entity_name)} in DB. Trying vector database.")
                vector_manager = VectorDataManager()
                similar_books = vector_manager.search_similar_book(entity_name)

                if similar_books and isinstance(similar_books, list):
                    best_match, similarity = similar_books[0]
                    logging.info(f"Best match found: '{best_match}' with similarity: {similarity:.2f}")

                    if similarity >= 0.5:  # similarity is 50% or higher
                        book = db.query(Book).filter(Book.title == best_match).first()
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
                            state["response"] = "No information found for the specified book in either database."
                    else:
                        state["response"] = "No similar book found with a high enough similarity score."
                else:
                    state["response"] = "No similar book found in the vector database."
        except Exception as e:
            logging.error(f"Error retrieving book info: {e}")
            state["response"] = "An error occurred while retrieving the book information."

    return state


def get_author_info_node(state: GraphState) -> GraphState:
    entity_name = state.get('entity_name', '').strip()
    if not entity_name:
        state["response"] = "Please provide a book title to search for."
        return state

    logging.info(f"Fetching author name for book: '{entity_name}'")
    
    with get_db_session() as db:
        try:
            # Query to match the book title exactly or with partial matching
            book = db.query(Book).filter(Book.title.ilike(f"%{entity_name}%")).first()
            if book and book.authors:
                # Ensure that author information exists and is correctly retrieved
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
            f"description: {book_info['description']}"
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
        description = book_info.get('description', '').strip()
        
        if description:
            # if less than 50 words as "brief"
            word_count = len(description.split())
            
            if word_count <= 50:  # Adjust this threshold based on your preference
                # Ifshort, summarize it into one line
                prompt_message = HumanMessage(
                    content=f"Please provide a concise one-line summary of the following brief book description:\n\n{description}"
                )
            else:
                # For longer descriptions, generate a 3-4 sentence summary
                prompt_message = HumanMessage(
                    content=f"Please provide a concise and engaging summary of the following book description in 3-4 sentences:\n\n{description}\n\nFocus on the key themes, the significance of the author's arguments, and the impact of the book. Highlight any notable praise or recognition it has received, especially from influential figures."
                )
            
            logging.info("Generating Summary ...")
            response = ollama_model.invoke([prompt_message]).strip()
            state["response"] = response
        else:
            state["response"] = "No description found for the specified book in the database."
    else:
        state["response"] = "No information found for the specified book."
    
    return state

def recommend_books_node(state: GraphState) -> GraphState:
    entity_name = state.get('entity_name', '').strip()
    num_recommendations = state.get('num_recommendations', 2)
    
    if not entity_name:
        state["response"] = "Please provide a genre, description, or title to base the recommendations on."
        return state
    vector_manager = VectorDataManager()

    with get_db_session() as db:
        target_book = db.query(Book).filter(Book.title.ilike(f"%{entity_name}%")).first()
        if target_book:
            book_description = target_book.description
            recommended_titles = vector_manager.recommend_books(book_description, num_recommendations)
        else:
            recommended_titles = vector_manager.recommend_books(entity_name, num_recommendations)
        recommended_books = db.query(Book).filter(Book.title.in_(recommended_titles)).all()

        if recommended_books:
            limited_books = recommended_books[:num_recommendations]
            response = f"Recommended {len(limited_books)} Books:\n" + "\n".join(
                f"Title: {book.title}\nDescription: {book.description}\nPublished Year: {book.published_year}\nAverage Rating: {book.average_rating}\nNumber of Pages: {book.num_pages}\nRatings Count: {book.ratings_count}\n"
                for book in limited_books
            )
            state["response"] = response
        else:
            state["response"] = "No recommendations found."
    return state
  
def general_chat_node(state: GraphState) -> GraphState:
    question = state.get('question', '').strip()
    if not question:
        state["response"] = "Feel free to ask anything about our book inventory."
        return state

    # Filtering out requests for specific book details
    if any(word in question.lower() for word in ['book', 'author', 'title', 'read']):
        state["response"] = "I can help with general questions about our services, but for book details, please specify which book you are interested in."
        return state

    prompt_message = HumanMessage(content=f"As a Book Inventory Assistant, I'm here to assist you. Here's what someone is asking: {question}")
    
    try:
        response = ollama_model.invoke([prompt_message]).strip()
        state["response"] =  response + " Is there anything else you would like to know?"
    except Exception as e:
        logging.error(f"Error invoking model for general chat: {e}")
        state["response"] = "Sorry, I encountered an issue while processing your request. Please try again."

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
        return "general_chat"

workflow = StateGraph(GraphState)

workflow.add_node("classify_input", classify_input_node)
workflow.add_node("retrieve_book_info", retrieve_book_info)
workflow.add_node("get_book_info", get_book_info_node)
workflow.add_node("get_author_name", get_author_name_node)
workflow.add_node("get_publication_year", get_publication_year_node)
workflow.add_node("summarize_book", summarize_book_node)
workflow.add_node("recommend_books", recommend_books_node)
workflow.add_node("get_author_info", get_author_info_node)
workflow.add_node("general_chat", general_chat_node)

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
        "general_chat": "general_chat",
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
workflow.add_edge("general_chat", END)

app = workflow.compile()

if __name__ == "__main__":
    inputs = {"question": "List books written by Sidney Sheldon"}
    result = app.invoke(inputs)
    print(result["response"])
