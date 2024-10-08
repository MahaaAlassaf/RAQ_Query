import re
import json
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field, ValidationError
from langchain.memory import ConversationBufferMemory

class IntentResponseModel(BaseModel):
    intent_number: int = Field(description="The intent number ranging from 1 to 6")
    entity_name: str = Field(description="The extracted entity related to the intent")
    num_recommendations: int = Field(default=2, description="Number of recommendations requested")

    class Config:
        extra = "forbid"

memory = ConversationBufferMemory(memory_key="chat_history")

# Function to save chat history to a file
def save_chat_history(memory):
    try:
        history = memory.load_memory_variables({})
        with open('chat_history.json', 'w') as file:
            json.dump(history, file, indent=4)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history(memory):
    try:
        with open('chat_history.json', 'r') as file:
            history = json.load(file)
            memory.chat_memory.add_user_message(history['chat_history'])
    except FileNotFoundError:
        print("No previous history found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from chat history.")
    except Exception as e:
        print(f"Error loading chat history: {e}")


class IntentExtractor:
    def __init__(self, model_name="llama3.1"):
        self.llm = OllamaLLM(model=model_name)
        print(f"Loaded model: {model_name}")
        load_chat_history(memory) 

    def classify_intent_and_extract_entities(self, document: str) -> IntentResponseModel:
        memory.chat_memory.add_user_message(document)

        number_pattern = re.compile(r'\b(\d+)\b')
        number_match = number_pattern.search(document)
        num_recommendations = int(number_match.group(1)) if number_match else 2

        prompt_message = HumanMessage(
            content=(
                f"""
                You are an AI model specializing in book-related queries. You have access to previous conversations with the user.

                Previous conversation:
                {memory.load_memory_variables({})['chat_history']}

                Based on the user's current input, determine the intent number and extract the relevant entity (book title or author name).
                Classify the user's intent into the following categories and return the number corresponding to the user's intent along with the extracted entity name.
                Intent Categories:

                1. Get Book Information: User asking about a detailed overview of a book, including title, author, publication year, genre, and summary.
                Example Query: "Give details of [book title]."

                2. Get Book Author Information: User asking about the author of a specific book.
                Example Query: "Who wrote [book title]?"

                3. Summarize Book: User asking for a concise and accurate summary of a book's content, highlighting key themes and plot points.
                Example Query: "Tell me about the [book title] book."

                4. Recommend Books: user seeks book recommendations based on preferences like genre or descriptions. Directly explain why these books are ideal choices, without prefacing your reasoning with any introductory phrases.
                Example Query: "Recommend 5 books like [book title]."

                5. Get Book Publication Year: User asking for the publication year of a specific book.
                Example Query: "When was [book title] published?"

                6. List Books by Author: User asking to list books written by a specific author.
                Example Query: "List books by [author name]."
                
                7. Anything else: User asking for general information or making a statement not related to the above categories.

                Response Format: 
                Intent Number: [1-6]
                Entity: [Entity Name]
                
                Entity name must not contain any extra information of context. For example, if the user input "Who is the author of harry potter?" the entity name should be "harry potter" only.
                '{document}'
                """
            )
        )
        try:
            print("Extracting Intent...")
            response = self.llm.invoke([prompt_message]).strip()
        except Exception as e:
            print(f"Error invoking model: {e}")
            response = ""
            raise e
        print(f"Prompt: {prompt_message.content}")
        print(f"Response: {response}")

        try:
            # Clean up the response to remove any unnecessary formatting like ** or ""
            response = re.sub(r'\*\*', '', response).strip()
            response = response.replace('"', '')

            intent_match = re.search(r"Intent Number: (\d+)", response)
            entity_match = re.search(r"Entity: ([^\n]+)", response)

            cleaned_entity_name = re.sub(r'[^\w\s]', '', entity_match.group(1).strip()) if entity_match else ""

            intent_response = IntentResponseModel(
                intent_number=int(intent_match.group(1)) if intent_match else 0,
                entity_name=cleaned_entity_name,
                num_recommendations=num_recommendations
            )

            memory.chat_memory.add_ai_message(response)
            save_chat_history(memory)  # Save history after every interaction

            return intent_response
        except (ValueError, IndexError, AttributeError, ValidationError) as e:
            print(f"Error parsing response: {e}")
            # Re-invoke the model if validation fails
            return self.classify_intent_and_extract_entities(document)


if __name__ == "__main__":
    extractor = IntentExtractor(model_name="llama3.1")
    question = "Who wrote Harry Potter?"
    response = extractor.classify_intent_and_extract_entities(question)
    print(response)