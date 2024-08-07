import pandas as pd
from sqlalchemy.orm import Session
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.author import Author
from app.database.schemas.book_author_association import book_author_association
import os

def main():
    engine, SessionLocal = connect_to_db()
    session = SessionLocal()

    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        books_path = os.path.join(curr_dir, '../../books.csv')
        df = pd.read_csv(books_path)

        df.columns = df.columns.str.strip().str.lower()

        expected_cols = {'title', 'subtitle', 'thumbnail', 'categories', 'published_year', 
                         'description', 'average_rating', 'num_pages', 'ratings_count', 'authors'}
        if not expected_cols.issubset(set(df.columns)):
            missing_cols = expected_cols - set(df.columns)
            raise ValueError(f"Missing columns in CSV: {missing_cols}")

        # Data cleaning and preparation
        df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce').fillna(0.0)
        df['published_year'] = pd.to_numeric(df['published_year'], errors='coerce').fillna(0).astype(int)
        df['num_pages'] = pd.to_numeric(df['num_pages'], errors='coerce').fillna(0).astype(int)
        df['ratings_count'] = pd.to_numeric(df['ratings_count'], errors='coerce').fillna(0).astype(int)
        df.fillna('', inplace=True)

        for _, row in df.iterrows():
            book = Book(
                title=row['title'],
                subtitle=row['subtitle'],
                thumbnail=row['thumbnail'],
                genre=row['categories'],  
                published_year=row['published_year'],
                description=row['description'],
                average_rating=row['average_rating'],
                num_pages=row['num_pages'],
                ratings_count=row['ratings_count']
            )
            session.add(book)
            session.flush()  
            
            author_names = row['authors'].split(';')
            for name in author_names:
                author = session.query(Author).filter_by(name=name.strip()).first()
                if not author:
                    print(f"Creating new author: {name}")
                    author = Author(name=name.strip())
                    session.add(author)
                    session.flush()
                book.authors.append(author)
                print(f"Added author: {author.name} to book: {book.title}")
            session.add(book)
            print(f"Added book: {book.title}")

        session.commit()
        print("Books and authors added successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    main()

