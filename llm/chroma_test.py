from llm.vector_data_manager import VectorDataManager
vector_manager = VectorDataManager()
query = "recommend 5 book on Autobiography"
num_results = 5
recommended_titles = vector_manager.recommend_books(query, num_results)