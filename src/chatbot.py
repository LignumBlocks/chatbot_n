import os
import time
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from prompts_templates import PROMPTS
from post_mail import send_email_to_api

# Constants for retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  
PINECONE_INDEX_NAME = "flowise-gemini"
PINECONE_WOODXEL_NS = "woodxel-info"
PINECONE_LIGNUM_NS = "lignum-info"

EMBEDDING_MODELS = ['models/embedding-001', 'models/text-embedding-004']
MODELS = ['gemini-1.5-flash-8b', 'gemini-2.0-flash-lite']

class Chatbot:
    namespace = 'default'
    def __init__(self, user_name, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.6):
        """
        Initializes the Chat with the specified model and temperature.
            
        Args:
            model_name (str): The name of the LLM model to use (default is "gemini-2.0-flash-lite").
            temperature (float): Controls the randomness of model outputs (default is 0.6).
        """
        self.user_name = user_name
        self.model_name = model_name if model_name else MODELS[0]
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=self.temperature)
        self.small_llm = ChatGoogleGenerativeAI(model=MODELS[0], temperature=0.5)
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODELS[1])
        
        self.vector_store = PineconeVectorStore(index_name=PINECONE_INDEX_NAME,
                                                embedding=self.embeddings,
                                                namespace=self.namespace)

    def _retrieve_context(self, query: str, k: int = 8):
        """Safe context retrieval with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                results = self.vector_store.similarity_search(query, k=k)
                if not results:
                    raise ValueError("Empty results from vector store")
                return results
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    print(f"Vector search failed: {str(e)}")
                    return []
                time.sleep(RETRY_DELAY * (attempt + 1))
                
    def run(self, user_input, system_prompt='', max_retries=MAX_RETRIES):
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(f"{system_prompt}\n{user_input}").content
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM invocation failed after {max_retries} attempts") from e
                time.sleep(RETRY_DELAY * (attempt + 1))
            
    def _intent_classifier(self, user_input:str, history:list) -> dict:
        """Classify user intent with error handling for JSON parsing"""
        intent_prompt_template = PROMPTS["intent_detection"]
        intent_prompt = intent_prompt_template.format(chat_history=str(history), question=user_input)
        for attempt in range(MAX_RETRIES):
            try:
                result = self.small_llm.invoke(intent_prompt)
                cleaned_string = result.content.replace("```json\n", "").replace("```","").strip()
                return json.loads(cleaned_string)
            except Exception as e:
                print(f"Intent classification failed: {str(e)}")
                time.sleep(RETRY_DELAY * (attempt + 1))
        return {"intent": "other", "contact_information": []}

    def condense_question(self, user_input:str, history:list):
        condense_question_prompt_template = PROMPTS["get_standalone_query"] 
        condense_question_prompt = condense_question_prompt_template.format(chat_history=str(history), question=user_input)
        for attempt in range(MAX_RETRIES):
            try:
                result = self.small_llm.invoke(condense_question_prompt)
                cleaned_string = result.content.replace("```json\n", "").replace("```","").strip()
                return json.loads(cleaned_string)
            except Exception as e:
                print(f"Pre-processing failed: {str(e)}")
                time.sleep(RETRY_DELAY * (attempt + 1))
        return {"language": "", "modified_query": user_input}
    
class WoodxelChatbot(Chatbot):
    namespace = PINECONE_WOODXEL_NS    
        
    def chat_with_history(self, user_input: str, chat_history: list):
        """Main chat processing with comprehensive error handling"""
        
        condensed_question_json = self.condense_question(user_input, chat_history)
        language = condensed_question_json.get("language", "")
        condensed_question = condensed_question_json.get("modified_query", user_input)
        # print(f"Condensed question: {condensed_question_json}")
        relevant_info = self._retrieve_context(condensed_question, k=8)
        context = ""
        for chunk in relevant_info:
            source = chunk.metadata.get('source', '')
            if source:
                context += f"From {source}: {chunk.page_content}\n\n"
            else: context += f"Unknown source: {chunk.page_content}\n\n"
        # print(f"Context: {context}")        
        if language: language = f"The user question is in {language}. Your answer must be only in {language}.\n"
        if len(chat_history) < 2:
            extra_info = f"You can refer to the user as: {self.user_name}. That was the name they provided. But avoid overusing the name; don't use it in all interactions. {language}"
        else: extra_info = language
        
        system_prompt = PROMPTS["woodxel_system_prompt"]
    
        answer_prompt_template = PROMPTS["woodxel_prompt"]  
        answer_prompt = answer_prompt_template.format(context=context, chat_history=chat_history, 
                                                      extra_info=extra_info, question=user_input)       
                 
        # print(f"Prompt: {system_prompt}\n{answer_prompt}")
        for attempt in range(MAX_RETRIES):
            try:
                result = self.llm.invoke(f"{system_prompt}\n{answer_prompt}").content
                # print(f'result: {result}')
                return result     
            except Exception as e:
                print(f"LLM invocation error ({attempt+1}/{MAX_RETRIES}): {str(e)}")
                time.sleep(RETRY_DELAY * (attempt + 1)) 
        return "Sorry, I'm having trouble generating a response. Please try again later."
        
class LignumChatbot(Chatbot):
    namespace = PINECONE_LIGNUM_NS
    def chat_with_history(self, user_input: str, chat_history: list):
        """Main chat processing with comprehensive error handling"""
        
        condensed_question_json = self.condense_question(user_input, chat_history)
        language = condensed_question_json.get("language", "")
        condensed_question = condensed_question_json.get("modified_query", user_input)
        # print(f"Condensed question: {condensed_question}")
        relevant_info = self._retrieve_context(condensed_question, k=8)
        context = ""
        for chunk in relevant_info:
            source = chunk.metadata.get('source', '')
            if source:
                context += f"From {source}: {chunk.page_content}\n\n"
            else: context += f"Unknown source: {chunk.page_content}\n\n"
        # print(f"Context: {context}")
        if language: language = f"The user question is in {language}. Your answer must be only in {language}.\n"
        if len(chat_history) < 2:
            extra_info = f"You can refer to the user as: {self.user_name}. That was the name they provided. But avoid overusing the name; don't use it in all interactions. {language}"
        else: extra_info = language
        
        system_prompt = PROMPTS["lignum_system_prompt"]
    
        answer_prompt_template = PROMPTS["lignum_prompt"]  
        answer_prompt = answer_prompt_template.format(context=context, chat_history=chat_history, 
                                                      extra_info=extra_info, question=user_input)    
        for attempt in range(MAX_RETRIES):
            try:         
                result = self.llm.invoke(f"{system_prompt}\n{answer_prompt}").content
                # print(f'result: {result}')
                return result      
            except Exception as e:
                print(f"LLM invocation error ({attempt+1}/{MAX_RETRIES}): {str(e)}")
                time.sleep(RETRY_DELAY * (attempt + 1)) 
        return "Sorry, I'm having trouble generating a response. Please try again later."
        
