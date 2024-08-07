import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import delete, text
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.preferences import Preferences
from app.database.schemas.user import User
from app.database.schemas.author import Author
from app.database.schemas.book_author_association import book_author_association 

def delete_and_reset_all_data():
    engine, SessionLocal = connect_to_db() 
    
    session = SessionLocal()
    try:
        with session.begin():
            session.execute(delete(book_author_association)) 
            session.execute(delete(Preferences)) 
            session.execute(delete(User))
            session.execute(delete(Author)) 
            session.execute(delete(Book)) 
            session.commit()
            print("All data deleted successfully.")
        
        sequences = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'"))
            sequences = [row[0] for row in result]  
        
        for seq in sequences:
            try:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))
                    print(f"Sequence {seq} reset successfully.")
            except ProgrammingError as e:
                print(f"Sequence {seq} does not exist and cannot be reset: {e}")
            except SQLAlchemyError as e:
                print(f"Error executing sequence reset for {seq}: {e}")
    
    except Exception as e:
        session.rollback()
        print(f"Error deleting data: {e}")
    finally:
        session.close()

# Main execution
if __name__ == "__main__":
    delete_and_reset_all_data()
