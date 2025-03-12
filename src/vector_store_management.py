import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)                  
DOCS_DIR = os.path.join(BASE_DIR, 'documentation')  
DOCS_DIR_WOODXEL = os.path.join(DOCS_DIR, 'woodxel') 
DOCS_DIR_LIGNUM = os.path.join(DOCS_DIR, 'lignum') 
  
def custom_chunks(document:str, source:str):
    split = document.split('---') 
    documents = []
    for chunk in split:
        chunk = chunk.strip()
        documents.append(Document(page_content=chunk, metadata={"text":chunk, "source":source}))
    return documents

def upload_for_rag():
    with open(os.path.join(DOCS_DIR_WOODXEL, 'woodxel_general_info.md'), 'r', encoding='utf-8') as f:
        woodxel_gi = f.read()
        woodxel_gi_chunks = custom_chunks(woodxel_gi, "General Information")
    with open(os.path.join(DOCS_DIR_WOODXEL, 'woodxel_Privacy_policy.md'), 'r', encoding='utf-8') as f:
        woodxel_pp = f.read()
        woodxel_pp_chunks = custom_chunks(woodxel_pp, "Privacy Policy")
    with open(os.path.join(DOCS_DIR_WOODXEL, 'woodxel_Terms_of_service.md'), 'r', encoding='utf-8') as f:
        woodxel_ts = f.read()
        woodxel_ts_chunks = custom_chunks(woodxel_ts, "Terms of Service")
    with open(os.path.join(DOCS_DIR_LIGNUM, 'lignum_general_info.md'), 'r', encoding='utf-8') as f:
        lignum_gi = f.read()
        lignum_gi_chunks = custom_chunks(lignum_gi, "General Information")
    with open(os.path.join(DOCS_DIR_LIGNUM, 'lignum_Privacy_policy.md'), 'r', encoding='utf-8') as f:
        lignum_pp = f.read()
        lignum_pp_chunks = custom_chunks(lignum_pp, "Privacy Policy")
    with open(os.path.join(DOCS_DIR_LIGNUM, 'lignum_Terms_of_service.md'), 'r', encoding='utf-8') as f:
        lignum_ts = f.read()
        lignum_ts_chunks = custom_chunks(lignum_ts, "Terms of Service")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vector_store = PineconeVectorStore(index_name="flowise-gemini",
                                        embedding=embeddings,
                                        namespace='woodxel-info')
    vector_store.add_documents(woodxel_gi_chunks)
    vector_store.add_documents(woodxel_pp_chunks)
    vector_store.add_documents(woodxel_ts_chunks)
    vector_store = PineconeVectorStore(index_name="flowise-gemini",
                                        embedding=embeddings,
                                        namespace='lignum-info')
    vector_store.add_documents(lignum_gi_chunks)
    vector_store.add_documents(lignum_pp_chunks)
    vector_store.add_documents(lignum_ts_chunks)
    
    