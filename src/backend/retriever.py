import os
import chromadb
from chromadb.utils import embedding_functions
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv(dotenv_path="config/.env", override=True)

class DocumentRetriever:
    def __init__(self, db_directory="./data/chroma_db"):
        """Initialize the document retriever with a vector database"""
        self.db_directory = db_directory

        # Initialize OpenAI client for embeddings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Set up embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.openai_api_key,
            model_name="text-embedding-ada-002"
        )

        # Create Chroma client and collection
        self.client = chromadb.PersistentClient(path=db_directory)

        # Try to get the collection if it exists, otherwise create it
        try:
            self.collection = self.client.get_collection(
                name="security_documents",
                embedding_function=self.embedding_function
            )
        except Exception:
            # Collection not found, create it
            self.collection = self.client.create_collection(
                name="security_documents",
                embedding_function=self.embedding_function
            )
            print("Created new document collection")
        else:
            print("Loaded existing document collection")


    def add_document(self, doc_path, doc_id):
        """Add a document to the vector store after chunking"""
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(content)

        # Add chunks to collection
        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                metadatas=[{"source": doc_path, "chunk": i}],
                ids=[f"{doc_id}_chunk_{i}"]
            )

        return len(chunks)

    def query_documents(self, query, n_results=3):
        """Retrieve relevant document chunks for a query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Format results for prompt injection
        retrieved_contexts = []
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            source = metadata['source']
            retrieved_contexts.append(f"SOURCE: {source}\nCONTENT: {doc}\n")

        return "\n".join(retrieved_contexts)

    def add_security_knowledge_base(self, knowledge_dir="./data/knowledge_base"):
        """Add all documents from the security knowledge base directory"""
        if not os.path.exists(knowledge_dir):
            os.makedirs(knowledge_dir)
            print(f"Created directory {knowledge_dir}")
            print("Please add security documents to this directory and run this method again")
            return False

        doc_count = 0
        for filename in os.listdir(knowledge_dir):
            if filename.endswith('.txt') or filename.endswith('.md'):
                file_path = os.path.join(knowledge_dir, filename)
                chunks_added = self.add_document(file_path, filename)
                doc_count += 1
                print(f"Added {filename} with {chunks_added} chunks")

        if doc_count == 0:
            print("No documents found in knowledge base directory")
            return False

        return True