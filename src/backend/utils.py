import os
import json
import logging
import PyPDF2
import fitz  # PyMuPDF - alternative PDF library
from pathlib import Path
from .config import TOPICS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def identify_topics(query):
    """
    Identify security topics in the query based on keywords
    Returns a list of topics found in the query
    """
    query_lower = query.lower()
    detected_topics = []

    for topic, details in TOPICS.items():
        keywords = details["keywords"]
        if any(keyword in query_lower for keyword in keywords):
            detected_topics.append(topic)

    # If no specific topic is detected, default to basic security
    if not detected_topics:
        detected_topics.append("basic_security")

    return detected_topics


def check_rank_access(topics, user_rank):
    """
    Check if the user's rank allows access to all detected topics
    Returns True if access is granted, False otherwise
    """
    for topic in topics:
        required_rank = TOPICS.get(topic, {"rank": 1})["rank"]
        if user_rank < required_rank:
            return False

    return True


def extract_text_from_pdf_pypdf2(pdf_path):
    """
    Extract text from PDF using PyPDF2 library
    """
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path} using PyPDF2: {str(e)}")
        return None


def extract_text_from_pdf_pymupdf(pdf_path):
    """
    Extract text from PDF using PyMuPDF (fitz) library
    Better for complex PDFs with images and formatting
    """
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path} using PyMuPDF: {str(e)}")
        return None


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using multiple methods as fallback
    """
    # Try PyMuPDF first (generally better results)
    text = extract_text_from_pdf_pymupdf(pdf_path)
    
    # If PyMuPDF fails, try PyPDF2
    if not text or len(text.strip()) < 100:
        logger.info(f"PyMuPDF extraction poor for {pdf_path}, trying PyPDF2...")
        text = extract_text_from_pdf_pypdf2(pdf_path)
    
    if not text:
        logger.error(f"Failed to extract text from {pdf_path}")
        return None
    
    return text.strip()


def process_pdf_documents(pdf_directory="./data/pdf_documents"):
    """
    Process all PDF documents in the specified directory and convert them to text files
    """
    knowledge_base_dir = "./data/knowledge_base"
    os.makedirs(knowledge_base_dir, exist_ok=True)
    
    pdf_dir = Path(pdf_directory)
    if not pdf_dir.exists():
        logger.error(f"PDF directory {pdf_directory} does not exist")
        return False
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_directory}")
        return False
    
    processed_count = 0
    
    for pdf_file in pdf_files:
        logger.info(f"Processing PDF: {pdf_file.name}")
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(str(pdf_file))
        
        if extracted_text:
            # Create output filename (replace .pdf with .txt)
            output_filename = pdf_file.stem + ".txt"
            output_path = os.path.join(knowledge_base_dir, output_filename)
            
            # Write extracted text to file
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Security Document: {pdf_file.name}\n\n")
                    f.write(extracted_text)
                
                logger.info(f"Successfully converted {pdf_file.name} to {output_filename}")
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error writing text file for {pdf_file.name}: {str(e)}")
        else:
            logger.error(f"Failed to extract text from {pdf_file.name}")
    
    logger.info(f"Processed {processed_count} PDF documents out of {len(pdf_files)} found")
    return processed_count > 0


def clean_extracted_text(text):
    """
    Clean and format extracted text from PDFs
    """
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]  # Remove empty lines
    
    # Join lines and clean up spacing
    cleaned_text = '\n'.join(lines)
    
    # Remove multiple consecutive newlines
    import re
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    return cleaned_text


def create_knowledge_base_from_pdfs(pdf_directory="./data/pdf_documents"):
    """
    Main function to create knowledge base from PDF documents
    """
    logger.info("Starting PDF to knowledge base conversion...")
    
    # Create PDF directory if it doesn't exist
    os.makedirs(pdf_directory, exist_ok=True)
    
    if not os.listdir(pdf_directory):
        logger.warning(f"PDF directory {pdf_directory} is empty. Please add your PDF documents there.")
        return False
    
    # Process PDF documents
    success = process_pdf_documents(pdf_directory)
    
    if success:
        logger.info("Knowledge base creation from PDFs completed successfully!")
    else:
        logger.error("Failed to create knowledge base from PDFs")
    
    return success


# In src/backend/utils.py

def create_env_file(destination_folder="."):
    """
    Create a sample .env file in the specified folder.
    """
    # Ensure the destination folder exists, create it if it doesn't
    os.makedirs(destination_folder, exist_ok=True)
    
    # Construct the full path for the .env file
    env_path = os.path.join(destination_folder, ".env")

    env_content = """# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True

# Database Configuration
DB_DIRECTORY=./data/chroma_db

# Knowledge Base Configuration
KNOWLEDGE_BASE_DIR=./data/knowledge_base

# PDF Documents Directory
PDF_DOCUMENTS_DIR=./data/pdf_documents

# LLM Configuration
DEFAULT_MODEL=gpt-4o
"""

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)

    logger.info(f"Created sample .env file at '{env_path}'. Please update with your actual API keys.")






