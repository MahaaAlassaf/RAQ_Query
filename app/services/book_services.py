
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, insert, update, join
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.user import User
from app.database.schemas.author import Author
from app.database.schemas.book_author_association import book_author_association
from app.services.author_services import retrieve_single_author
from app.schemas.book import BookUpdateCurrent

def insert_book(session: Session, title: str, genre: str, description: str, year: int):
    new_book = Book(title=title, genre=genre, description=description, year=year)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book.id

def create_book(db: Session, title: str, genre: str, description: str, year: int):
    db_book = Book(title=title, genre=genre, description=description, year=year)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def retrieve_single_book(session: Session, id: int):
    try:
        book = session.query(Book).filter(Book.id == id).first()
        if not book:
            return False, "Book not found", None
        book_data = {
            "id": book.id,
            "title": book.title,
            "subtitle": book.subtitle,
            "thumbnail": book.thumbnail,
            "genre": book.genre,
            "published_year": book.published_year,
            "description": book.description,
            "average_rating": book.average_rating,
            "num_pages": book.num_pages,
            "ratings_count": book.ratings_count,
            "authors": [author.name for author in book.authors]
        }
        return True, "Book retrieved successfully", book_data
    except Exception as e:
        print(f"Error retrieving book: {e}")
        return False, str(e), None
    

def retrieve_books_from_db(session: Session, limit: int, offset: int, email: str = None):
    try:
        books = session.query(Book).offset(offset).limit(limit).all()

        # Retrieve the user's favorite books if email is provided
        favorite_books_ids = []
        if email:
            user = session.query(User).filter(User.email == email).first()
            if user:
                favorite_books_ids = [book.id for book in user.favorite_books]

        book_list = [
            {
                "id": book.id,
                "title": book.title,
                "subtitle": book.subtitle,
                "thumbnail": book.thumbnail,
                "genre": book.genre,
                "published_year": book.published_year,
                "description": book.description,
                "average_rating": book.average_rating,
                "num_pages": book.num_pages,
                "ratings_count": book.ratings_count,
                "authors": [author.name for author in book.authors],
                "is_fav": book.id in favorite_books_ids  # Check if the book is in the user's favorites
            }
            for book in books
        ]
        
        return True, "Books retrieved successfully", book_list
    except Exception as e:
        print(f"Error retrieving books: {e}")
        return False, str(e), []

def search_books_by_title(session: Session, title: str, limit: int, offset: int, email: str = None):
    try:
        books = session.query(Book).filter(Book.title.ilike(f'%{title}%')).offset(offset).limit(limit).all()
        
        # Retrieve the user's favorite books if email is provided
        favorite_books_ids = []
        if email:
            user = session.query(User).filter(User.email == email).first()
            if user:
                favorite_books_ids = [book.id for book in user.favorite_books]

        book_list = [
            {
                "id": book.id,
                "title": book.title,
                "subtitle": book.subtitle,
                "thumbnail": book.thumbnail,
                "genre": book.genre,
                "published_year": book.published_year,
                "description": book.description,
                "average_rating": book.average_rating,
                "num_pages": book.num_pages,
                "ratings_count": book.ratings_count,
                "authors": [author.name for author in book.authors],
                "is_fav": book.id in favorite_books_ids  # Check if the book is in the user's favorites
            }
            for book in books
        ]
        
        return True, "Books retrieved successfully", book_list
    except Exception as e:
        print(f"Error searching books: {e}")
        return False, str(e), []

def delete_book_from_db(book_id):
    try:
        engine, session = connect_to_db()
        with session.begin():
            stmt = delete(Book).where(Book.id == book_id)
            result = session.execute(stmt)
            if result.rowcount > 0:
                return True, "Book deleted successfully" 
            else:
                return False, "Book could not be deleted"
    except Exception as e:
        print(e)
        session.rollback()
        return False, e
    finally:
        session.close()

def add_book_to_db(session: Session,book: Book):
    success, message, author = retrieve_single_author(book.author_id)
    if not success:
        return success, message, None
    
    to_add = Book(
        title=book.title, 
        genre=book.genre, 
        description=book.description, 
        year=book.year, 
        author_id=book.author_id
    )
    
    try:
        session.add(to_add)
        session.commit()
        book_id = to_add.book_id
        return True, "Book added Successfully", book_id
    except Exception as e:
        session.rollback()
        return False, e, None
    finally:
        session.close()
        
def edit_book_info(book_id: int, new_book: BookUpdateCurrent):
    success, message, book = retrieve_single_book(book_id)
    if not success:
        return success, message

    if new_book.author_id is not None:
        engine, session = connect_to_db()
        stmt = select(Author.author_id).where(Author.author_id == new_book.author_id)
        with engine.connect() as conn:
            results = conn.execute(stmt)
            output = results.fetchone()
            if not output:
                return False, "New author does not exist"
    
    updated_book_data = {
        "title": new_book.title if new_book.title is not None else book['title'],
        "author_id": new_book.author_id if new_book.author_id is not None else book['author_id'],
        "genre": new_book.genre if new_book.genre is not None else book['genre'],
        "description": new_book.description if new_book.description is not None else book['description'],
        "year": new_book.year if new_book.year is not None else book['year'],
    }

    stmt = (
        update(Book)
        .where(Book.id == book_id)
        .values(
            title=updated_book_data["title"],
            author_id=updated_book_data["author_id"],
            genre=updated_book_data["genre"],
            description=updated_book_data["description"],
            year=updated_book_data["year"]
        )
        .execution_options(synchronize_session="fetch")
    )

    try:
        engine, session = connect_to_db()
        with session.begin():
            session.execute(stmt)
            session.commit()
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

    return True, "Book information successfully updated"

def add_to_favourites(db: Session, email: str, book_id: int):
    # Retrieve the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False, "User not found"

    # Retrieve the book by ID
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return False, "Book not found"

    # Check if the book is already in the user's favorites
    if book in user.favorite_books:
        return False, "Book already in favorites"

    # Add the book to the user's favorites
    user.favorite_books.append(book)
    db.commit()

    return True, "Book added to favorites"

def remove_from_favourites(db: Session, email: str, book_id: int):
    # Retrieve the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False, "User not found"

    # Retrieve the book by ID
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return False, "Book not found"

    # Check if the book is in the user's favorites
    if book not in user.favorite_books:
        return False, "Book not in favorites"

    # Remove the book from the user's favorites
    user.favorite_books.remove(book)
    db.commit()

    return True, "Book removed from favorites"