from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
from datetime import timedelta

from requests import Session
from app.database.connector import connect_to_db, get_db
from app.middleware.request_logger import setup_middleware
from llm2.langgraph_integration import app as langgraph_app
# Import necessary services and modules
from app.database.schemas.query import Query
from app.services.author_services import (
    retrieve_single_author,
    retrieve_authors_from_db,
    add_author_to_database,
    edit_author_info,
    delete_author_from_db
)
from app.services.user_services import (
    delete_user,
    retrieve_all_users,
    retrieve_single_user,
    authenticate_user,
    edit_user_info,
    register_user
)
from app.services.book_services import (
    retrieve_single_book,
    retrieve_books_from_db,
    add_book_to_db,
    delete_book_from_db,
    edit_book_info,
    search_books_by_title,
    add_to_favourites,
    remove_from_favourites
)
from app.services.token_services import create_access_token
from app.schemas.login_info import Login
from app.schemas.author import Author, AuthorUpdateCurrent
from app.schemas.book import BookUpdateCurrent, Book
from app.schemas.user import User, UserUpdateCurrent
from app.utils.config import ACCESS_TOKEN_EXPIRE_MINUTES

# Import custom modules
from app.pgAdmi4.SaveDataToVectorstore import similarity_text
from llm2.intent_extraction import IntentExtractor

# Token verification
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.services.token_services import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

app = FastAPI()

# Temporary test user
test_user = {"role": 1, "email": "test@example.com"}
class FavoriteRequest(BaseModel):
    book_id: int

@app.get("/")
def read_root(current_user: dict = test_user):
    return {"Hello": "World"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Add custom middleware
setup_middleware(app)

@app.get("/books")
def get_books(
    db: Session = Depends(get_db),
    token: str = Security(oauth2_scheme),
    title: str = "", 
    limit: int = 10, 
    offset: int = 0  
):  
    user_email = None
    if token:
        print("Token received:", token)
        try:
            payload = verify_token(token)
            user_email = payload.get("email")
            if user_email is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            print(f"Authenticated user: {user_email}")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token verification failed")
    else:
        print("No token received")
        
    if title != "":
        print("Searching for books with title:", title)
        success, message, books = search_books_by_title(db, title=title, limit=limit, offset=offset, email=user_email)
    else:
        success, message, books = retrieve_books_from_db(db, limit=limit, offset=offset, email=user_email)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    return {"message": message, "books": books, "limit": limit, "offset": offset}


@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db), current_user: dict = test_user):
    success, message, book = retrieve_single_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message, "book": book}

@app.post("/books/add_to_favorites")
def add_book_to_favorites(request: FavoriteRequest,
                          db: Session = Depends(get_db),
                          token: str = Security(oauth2_scheme)):
    book_id = request.book_id
    if token:
        print("Token received:", token)
        try:
            payload = verify_token(token)
            user_email = payload.get("email")
            if user_email is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            print(f"Authenticated user: {user_email}")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token verification failed")
    else:
        raise HTTPException(status_code=401, detail="Token is required to add book to favorites")
    success, message = add_to_favourites(db, user_email, book_id)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    return {"message": message, "book_id": book_id, "user_email": user_email}

@app.post("/books/remove_from_favorites")
def remove_book_from_favorites(request: FavoriteRequest,
                                 db: Session = Depends(get_db),
                                 token: str = Security(oauth2_scheme)):
    book_id = request.book_id
    if token:
        print("Token received:", token)
        try:
            payload = verify_token(token)
            user_email = payload.get("email")
            if user_email is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            print(f"Authenticated user: {user_email}")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token verification failed")
    else:
        raise HTTPException(status_code=401, detail="Token is required to remove book from favorites")
    success, message = remove_from_favourites(db, user_email, book_id)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    return {"message": message, "book_id": book_id, "user_email": user_email}

@app.get("/chat")
def chat_with_bot(query: str):
    model_input = {
        "question": query
    }
    try:
        result = langgraph_app.invoke(model_input)
        output = result.get('response', 'No response generated.')
        return {"message": "Response Generated Successfully", "response": output}
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/books")
def add_book(book: Book, current_user: dict = test_user):
    success, message, book_id = add_book_to_db(book)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_id": book_id}

@app.put("/books/{book_id}")
def update_book(book_id: int, new_book: BookUpdateCurrent, current_user: dict = test_user):
    success, message = edit_book_info(book_id, new_book)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book_id": book_id}

@app.delete("/books/{book_id}")
def delete_book_route(book_id: int, current_user: dict = test_user):
    success, message = delete_book_from_db(book_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "book": book_id}

@app.get("/authors")
def get_authors(current_user: dict = test_user):
    return retrieve_authors_from_db()

@app.get("/authors/{author_id}")
def get_author(author_id: int, current_user: dict = test_user):
    success, message, author = retrieve_single_author(author_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author": author}

@app.post("/authors")
def add_author(author: Author, current_user: dict = test_user):
    success, message, author_id = add_author_to_database(author)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author_id": author_id}

@app.put("/authors/{author_id}")
def update_author(author_id: int, new_author: AuthorUpdateCurrent, current_user: dict = test_user):
    success, message = edit_author_info(author_id, new_author)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author_id": author_id}

@app.delete("/authors/{author_id}")
def delete_author(author_id: int, current_user: dict = test_user):
    success, message = delete_author_from_db(author_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "author_id": author_id}

@app.post("/users/register")
def add_user(user: User):
    print("Received user data:", user)
    success, message = register_user(user)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "user": user.email}

@app.post("/users/login")
async def auth_user(login_data: Login, db: Session = Depends(get_db)):
    # Unpack the three values returned by authenticate_user
    auth, message, user_info = authenticate_user(login_data.email, login_data.password, db)
    
    if not auth:
        raise HTTPException(status_code=401, detail=message)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user_info["email"], "role": user_info["role"]},  # Include role in token
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": user_info
    }

@app.get("/users/me")
def get_user(current_user: dict = test_user):
    return {"user": current_user}

@app.put("/users/me")
async def update_user(user_update: UserUpdateCurrent, current_user: dict = test_user):
    email = current_user["email"]
    success, message = edit_user_info(email, user_update)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    success, message, user = retrieve_single_user(email)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    return {"message": message, "token": access_token}

@app.post("/query")
async def query_books(query: Query):
    # Validate and extract the query description
    description = query.description
    if not description:
        raise HTTPException(status_code=400, detail="Description is required.")

    # Initialize the database session
    db_session = connect_to_db()

    # Extract intent and entity
    intent_extractor = IntentExtractor()
    intent_response = intent_extractor.classify_intent_and_extract_entities(description)
    intent_number = intent_response.intent_number
    entity_name = intent_response.entity_name

    try:
        if intent_number and entity_name:
            initial_state = {"question": description, "intent_number": intent_number, "entity_name": entity_name}

            # Run the compiled workflow with the initial state
            response_state = app.invoke(initial_state)

            response = response_state.get('response', 'No response generated.')
            return {"response": response}
        else:
            return {"response": "Could not determine intent or entity from the description."}
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {"response": f"Error processing query: {str(e)}"}
    finally:
        db_session.close()


@app.post("/recommendations")
def get_recommendations(description: str):
    try:
        similar_books_metadata = similarity_text(description)
        if not similar_books_metadata:
            raise HTTPException(status_code=404, detail="No recommendations found")

        book_recommendations = [book['title'] for book in similar_books_metadata]
        return {"message": "Recommendations fetched successfully", "book_recommendations": book_recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthcheck")
def health_check():
    return {"status": "healthy"}

@app.post("/favorites/{book_id}")
def add_favorite(book_id: int, current_user: dict = test_user, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    book = db.query(User).filter(User.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book not in user.favorite_books:
        user.favorite_books.append(book)
        db.commit()
        return {"message": "Book added to favorites"}
    else:
        return {"message": "Book is already in favorites"}

@app.delete("/favorites/{book_id}")
def remove_favorite(book_id: int, current_user: dict = test_user, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    book = db.query(User).filter(User.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book in user.favorite_books:
        user.favorite_books.remove(book)
        db.commit()
        return {"message": "Book removed from favorites"}
    else:
        return {"message": "Book is not in favorites"}

#-----------------------------------------------------------------------------------

# Admin-only endpoint to retrieve all users and their roles
@app.get("/admin/users")
def get_all_users(db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    payload = verify_token(token)
    if payload.get("role") != 1: 
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    
    users = retrieve_all_users(db)
    return users  # Return users directly instead of {"users": users}

# Admin-only endpoint to delete a user
@app.delete("/admin/users/{email}")
def remove_user(email: str, db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    payload = verify_token(token)
    if payload.get("role") != 1:
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    success, message = delete_user(db, email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "User deleted successfully"}

# Admin-only endpoint to add a new book
@app.post("/admin/books")
def admin_add_book(book: Book, db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    payload = verify_token(token)
    if payload.get("role") != 1:
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    success, message, book_id = add_book_to_db(book, db)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "Book added successfully", "book_id": book_id}

# Admin-only endpoint to delete a book
@app.delete("/admin/books/{book_id}")
def admin_delete_book(book_id: int, db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    payload = verify_token(token)
    if payload.get("role") != 1:
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    success, message = delete_book_from_db(db, book_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": "Book deleted successfully"}

# run the server
if __name__ == "__main__":
    import uvicorn
    # auto reload the server when code changes
    uvicorn.run("api:app", host="localhost", port=6969, reload=True)

# # favorites 
# @app.post("/favorites/{book_id}")
# def add_favorite(book_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == current_user.email).first()
#     book = db.query(Book).filter(Book.id == book_id).first()

#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")

#     if book in user.favorite_books:
#         raise HTTPException(status_code=400, detail="Book is already in favorites")

#     user.favorite_books.append(book)
#     db.commit()
#     return {"message": "Book added to favorites"}

# @app.delete("/favorites/{book_id}")
# def remove_favorite(book_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == current_user.email).first()
#     book = db.query(Book).filter(Book.id == book_id).first()

#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")

#     if book not in user.favorite_books:
#         raise HTTPException(status_code=400, detail="Book is not in favorites")

#     user.favorite_books.remove(book)
#     db.commit()
#     return {"message": "Book removed from favorites"}

    
# Should Autheric
# from fastapi import FastAPI, HTTPException, Depends
# from typing import Annotated
# from datetime import timedelta
# from app.services.author_services import (
#     retrieve_single_author,
#     retrieve_authors_from_db,
#     add_author_to_database,
#     edit_author_info,
#     delete_author_from_db
# )
# from app.services.user_services import (-
#     retrieve_single_user,
#     authenticate_user,
#     edit_user_info,
#     register_user
# )
# from app.services.book_services import (
#     get_book_recommendations,
#     retrieve_single_book,
#     retrieve_books_from_db,
#     add_book_to_db,
#     delete_book_from_db,
#     edit_book_info
# )
# from app.services.token_services import create_access_token
# from app.schemas.login_info import Login
# from app.schemas.author import Author, AuthorUpdateCurrent
# from app.schemas.book import BookUpdateCurrent, Book
# from app.schemas.user import User, UserUpdateCurrent
# from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
# from app.utils.get_current_user import get_current_user
# from llm.SaveDataToVectorstore import similarity_text

# app = FastAPI()

# @app.get("/")
# def read_root(current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     return {"Hello": "World"}

# @app.get("/books")
# def get_books(current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     success, message, books = retrieve_books_from_db()
#     if not success:
#         raise HTTPException(status_code=401, detail=message)
#     return {"message": message, "books": books}

# @app.get("/books/{book_id}")
# def get_book(book_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     success, message, book = retrieve_single_book(book_id)
#     if not success:
#         raise HTTPException(status_code=404, detail=message)
#     return {"message": message, "book": book}

# @app.post("/books")
# def add_book(book: Book, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user or current_user["role"] != 1:
#         raise HTTPException(status_code=403, detail="Not get_current_user")
#     success, message, book_id = add_book_to_db(book)
#     if not success:
#         raise HTTPException(status_code=400, detail=message)
#     return {"message": message, "book_id": book_id}

# @app.put("/books/{book_id}")
# def update_book(book_id: int, new_book: BookUpdateCurrent, current_user: dict = Depends(get_current_user)):
#     if not current_user or current_user["role"] != 1:
#         return HTTPException(status_code=403, detail="Not authorized")
#     success, message = edit_book_info(book_id, new_book)
#     if not success:
#         return HTTPException(status_code=400, detail=message)
#     return {"message": message, "book_id": book_id}

# @app.delete("/books/{book_id}")
# def delete_book_route(book_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
#     if current_user["role"] != 1:
#         raise HTTPException(status_code=403, detail="Not Authorized")
#     success, message = delete_book_from_db(book_id)
#     if not success:
#         return HTTPException(status_code=400, detail=message)
#     return {"message": message, "book": book_id}

# @app.get("/authors")
# def get_authors(current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     return retrieve_authors_from_db()

# @app.get("/authors/{author_id}")
# def get_author(author_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     success, message, author = retrieve_single_author(author_id)
#     if not success:
#         raise HTTPException(status_code=400, detail=message)
#     return {"message": message, "author": author}

# @app.post("/authors")
# def add_author(author: Author, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user or current_user["role"] != 1:
#         return HTTPException(status_code=403, detail="Not authorized")
#     success, message, author_id = add_author_to_database(author)
#     if not success:
#         return HTTPException(status_code=400, detail=message)
#     return {"message": message, "author_id": author_id}

# @app.put("/authors/{author_id}")
# def update_author(author_id: int, new_author: AuthorUpdateCurrent, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user or current_user["role"] != 1:
#         return HTTPException(status_code=403, detail="Not authorized")
#     success, message = edit_author_info(author_id, new_author)
#     if not success:
#         return HTTPException(status_code=400, detail=message)
#     return {"message": message, "author_id": author_id}

# @app.delete("/authors/{author_id}")
# def delete_author(author_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user or current_user["role"] != 1:
#         return HTTPException(status_code=403, detail="Not authorized")
#     success, message = delete_author_from_db(author_id)
#     if not success:
#         return HTTPException(status_code=400, detail=message)
#     return {"message": message, "author_id": author_id}

# @app.post("/users/register")
# def add_user(user: User):
#     success, message = register_user(user)
#     if not success:
#         raise HTTPException(status_code=400, detail=message)
#     return {"message": message, "user": user.email}

# @app.post("/users/login")
# async def auth_user(login_data: Login):
#     auth, message = authenticate_user(login_data.username, login_data.password)
#     if not auth:
#         return HTTPException(status_code=401, detail=message)
#     success, message, user_info = retrieve_single_user(login_data.username)
#     if not success:
#         raise HTTPException(status_code=400, detail=message)

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user_info}, expires_delta=access_token_expires
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user_info": user_info
#     }

# @app.get("/users/me")
# def get_user(current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     return {"user": current_user}

# @app.put("/users/me")
# async def update_user(user_update: UserUpdateCurrent, current_user: Annotated[dict, Depends(get_current_user)]):
#     if not current_user:
#         return HTTPException(status_code=403, detail="Invalid Authorization")
#     email = current_user["email"]
#     success, message = edit_user_info(email, user_update)
#     if not success:
#         return HTTPException(status_code=400, detail=message)
#     success, message, user = retrieve_single_user(email)
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user}, expires_delta=access_token_expires
#     )
#     return {"message": message, "token": access_token}

# @app.post("/recommendations")
# def get_recommendations(description: str):
#     try:
#         similar_books_metadata = similarity_text(description)
#         if not similar_books_metadata:
#             raise HTTPException(status_code=404, detail="No recommendations found")
        
#         book_recommendations = [book['title'] for book in similar_books_metadata]
#         return {"message": "Recommendations fetched successfully", "book_recommendations": book_recommendations}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/healthcheck")
# def health_check():
#     return True
