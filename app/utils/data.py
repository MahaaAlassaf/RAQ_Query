# import pandas as pd
# from sqlalchemy import delete, text
# from app.database.schemas.books import Book
# from app.database.schemas.author import Author
# from app.database.connector import connect_to_db

# # Function to delete all rows in books and authors tables and reset sequences
# def reset_database():
#     engine, SessionLocal = connect_to_db()
#     session = SessionLocal()
#     try:
#         session.execute(delete(Book))
#         session.execute(delete(Author))
#         session.execute(text("ALTER SEQUENCE books_id_seq RESTART WITH 1"))
#         session.execute(text("ALTER SEQUENCE authors_id_seq RESTART WITH 1"))
#         session.commit()
#         print("All rows deleted and sequences reset successfully in books and authors tables.")
#     except Exception as e:
#         session.rollback()
#         print(f"An error occurred while resetting the database: {e}")
#     finally:
#         session.close()

# def get_or_create_author(session, author_name, biography=None):
#     author = session.query(Author).filter_by(name=author_name).first()
#     if not author:
#         author = Author(name=author_name, biography=biography)
#         session.add(author)
#         session.commit()
#         session.refresh(author)
#     return author

# def add_books_from_csv(csv_file_path):
#     df = pd.read_csv(csv_file_path)

#     engine, SessionLocal = connect_to_db()
#     session = SessionLocal()

#     try:
#         for index, row in df.iterrows():
#             author_name = row['authors']
#             biography = None 
#             author = get_or_create_author(session, author_name, biography)
            
#             book = Book(
#                 title=row['title'],
#                 genre=row['categories'],
#                 description=row['description'],
#                 year=row['published_year'],
#                 author_id=author.id 
#             )
            
#             session.add(book)
        
#         session.commit()
#         print("Books and authors added successfully.")

#     except Exception as e:
#         session.rollback()
#         print(f"An error occurred: {e}")

#     finally:
#         session.close()

# if __name__ == "__main__":
#     csv_file_path = '/Users/mahassaf004/Desktop/books.csv'
#     reset_database()  
#     add_books_from_csv(csv_file_path)  
