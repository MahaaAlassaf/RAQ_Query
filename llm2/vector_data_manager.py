from chromadb import PersistentClient
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
        print("Query:", query) 
        query_vector = self.model.encode(query).tolist()

        try:
            results = self.collection.query(
                # query_texts=[query],
                query_embeddings=[query_vector],
                n_results=num_results  
            )
            print(results)
            recommended_titles = [metadata['title'] for metadata in results['metadatas'][0]]
            print(f"Recommended Titles: {recommended_titles}")
            return recommended_titles
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return []
