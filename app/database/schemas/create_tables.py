# create_tables.py

from app.database.connector import engine
from app.database.schemas.base import Base  # Import Base class
from app.database.schemas.author import Author
from app.database.schemas.book_author_association import book_author_association
from app.database.schemas.books import Book
from app.database.schemas.favorite_books import favorite_books
from app.database.schemas.logs import RequestLog
from app.database.schemas.preferences import Preferences
from app.database.schemas.user import User

# Create all tables in the database
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
