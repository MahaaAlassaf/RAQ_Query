import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os

from llm.vector_data_manager import VectorDataManager

client = chromadb.PersistentClient(
    path="chroma_db", 
    settings=Settings(),
)

collection = client.get_or_create_collection(name="book_collection")

def store_books_in_vectorDB():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    books_path = os.path.join(curr_dir, '../../books.csv')
    df = pd.read_csv(books_path)

    df.columns = df.columns.str.strip().str.lower()
    documents = []
    metadatas = []
    ids = []
    for index, row in df.iterrows():
        text = f"{row['title']}; {row['authors']}; {row['categories']}; {row['description']}"
        metadata = {
            'isbn13': row['isbn13'],
            'isbn10': row['isbn10'],
            'title': row['title'],
            'subtitle': row['subtitle'],
            'authors': row['authors'],
            'categories': row['categories'],
            'thumbnail': row['thumbnail'],
            'description': row['description'],
            'published_year': row['published_year'],
            'average_rating': row['average_rating'],
            'num_pages': row['num_pages'],
            'ratings_count': row['ratings_count']
        }
        documents.append(text)
        metadatas.append(metadata)
        ids.append(str(row['isbn13']))
        print(f"Processed book: {row['title']}")
        # Add the book to the collection
    collection.add(
        documents=documents,
        ids=ids,  
        metadatas=metadatas
    )

def main():
    store_books_in_vectorDB()
    print("Books have been successfully added to the ChromaDB collection.")

if __name__ == '__main__':
    main()

def similarity_text(query: str):
    vector_manager = VectorDataManager()
    return vector_manager.recommend_books(query)
