from chromadb import PersistentClient
import numpy as np
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

class VectorDataManager:
    def __init__(self):
        self.client = PersistentClient(
            path="chroma_db",
            settings=Settings(),
        )
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(name="book_collection")
        print("VectorDataManager initialized.")

    def recommend_books(self, query: str, num_results: int = 2):
        print("Querying ChromaDB for recommendations...")
        query_vector = self.model.encode(query).tolist()

        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=num_results  
            )
            recommended_titles = [metadata['title'] for metadata in results['metadatas'][0]]
            print(f"Recommended Titles: {recommended_titles}")
            return recommended_titles
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return []

    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def search_similar_book(self, query: str, similarity_threshold: float = 0.5, num_results: int = 1):
        print("Searching for similar books in ChromaDB...")
        query_vector = self.model.encode(query).tolist()

        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=num_results  
            )
            print(f"Raw results from ChromaDB: {results}")
            
            if results and 'metadatas' in results and results['metadatas']:
                # Safely attempt to get the embeddings
                embeddings = results.get('embeddings', [None])[0]
                if embeddings is None or not embeddings:
                    print("No embeddings found, skipping similarity calculation.")
                    return "No similar book found in the vector database."

                similarities = [
                    self.cosine_similarity(query_vector, result_embedding)
                    for result_embedding in embeddings
                ]

                similar_titles = [
                    (metadata['title'], similarity)
                    for metadata, similarity in zip(results['metadatas'][0], similarities)
                    if similarity >= similarity_threshold
                ]
                
                if similar_titles:
                    return similar_titles
                else:
                    return "No similar book found with a high enough similarity score."
            else:
                print("No similar titles found.")
                return "No similar book found in the vector database."
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return "Error processing query."
