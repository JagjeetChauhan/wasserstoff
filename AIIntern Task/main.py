import os
import logging
import time
from multiprocessing import Pool
from pymongo import MongoClient
from PyPDF2 import PdfReader
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from collections import defaultdict

# Download required NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['pdf_database']
collection = db['pdf_documents']

# Configure logging to track errors
logging.basicConfig(filename='pdf_pipeline.log', level=logging.ERROR)

# Stop words for keyword extraction
STOPWORDS = set(stopwords.words('english'))

# Global variable to collect report data
report_data = defaultdict(int)


# ----------------------------------------
# PDF Ingestion, Summarization, and Keyword Extraction
# ----------------------------------------

# Function to list all PDF files in the specified folder
def list_pdfs(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

# Function to parse text from a PDF using PyPDF2
def parse_pdf(file_path):
    text = ''
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + ' '
    except Exception as e:
        logging.error(f"Error reading PDF {file_path}: {e}")
    return text

# Function to store PDF metadata and content in MongoDB
def store_pdf_metadata(file_path, parsed_text, summary, keywords):
    metadata = {
        'filename': os.path.basename(file_path),
        'path': file_path,
        'size': os.path.getsize(file_path),  # File size in bytes
        'content': parsed_text,
        'summary': summary,
        'keywords': keywords
    }
    collection.insert_one(metadata)
    print(f"Stored metadata for {os.path.basename(file_path)}")


# ----------------------------------------
# Summarization and Keyword Extraction
# ----------------------------------------

# Function to extract a summary from the text
def summarize_text(text, num_sentences=3):
    sentences = sent_tokenize(text)
    
    # If text has fewer sentences than num_sentences, return all
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    # Use TF-IDF to score sentences for summary
    vectorizer = TfidfVectorizer()
    sentence_vectors = vectorizer.fit_transform(sentences)
    
    # Rank sentences based on the TF-IDF score
    sentence_ranks = sentence_vectors.sum(axis=1).A1
    ranked_sentences = [sentences[i] for i in sentence_ranks.argsort()[-num_sentences:]]
    
    # Return top-ranked sentences as the summary
    return " ".join(ranked_sentences)

# Function to extract keywords using TF-IDF
def extract_keywords(text, num_keywords=5):
    words = word_tokenize(text)
    
    # Remove stopwords and non-alphabetic tokens
    words = [word.lower() for word in words if word.isalpha() and word.lower() not in STOPWORDS]
    
    # Use TF-IDF to score words
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([" ".join(words)])
    feature_array = vectorizer.get_feature_names_out()
    
    # Get top keyword indices
    tfidf_sorting = vectors.toarray().flatten().argsort()[::-1]
    
    # Extract top-n keywords
    keywords = [feature_array[i] for i in tfidf_sorting[:num_keywords]]
    return keywords


# ----------------------------------------
# Full PDF Processing Flow with Error Tracking
# ----------------------------------------

# Function to process a single PDF
def process_pdf(file_path):
    try:
        # Day 1: Parse the PDF text
        text = parse_pdf(file_path)

        # If PDF is empty, skip processing
        if not text.strip():
            raise ValueError("Parsed PDF content is empty")

        # Day 3: Summarize the text
        summary = summarize_text(text)

        # Day 3: Extract keywords
        keywords = extract_keywords(text)

        # Create document with filename, content, summary, and keywords
        store_pdf_metadata(file_path, text, summary, keywords)

        # Track success in the report
        report_data['processed_files'] += 1
        report_data['total_size'] += os.path.getsize(file_path)

    except Exception as e:
        # Log error and update report
        logging.error(f"Error processing {file_path}: {e}")
        report_data['failed_files'] += 1
        print(f"Error processing {file_path}: {e}")

# Function to process all PDFs in a directory
def process_all_pdfs(pdf_dir):
    # Ensure the directory exists
    if not os.path.exists(pdf_dir):
        print(f"Directory does not exist: {pdf_dir}")
        return
    
    # Get list of all PDF files in the directory
    pdf_files = list_pdfs(pdf_dir)

    # Use multiprocessing to handle multiple PDFs concurrently
    with Pool() as pool:
        pool.map(process_pdf, [os.path.join(pdf_dir, pdf_file) for pdf_file in pdf_files])

    # After processing all PDFs, generate the report
    generate_report()


# ----------------------------------------
# Reporting and MongoDB Querying (Day 4)
# ----------------------------------------

# Function to generate a report after processing
def generate_report():
    total_processed = report_data['processed_files']
    total_failed = report_data['failed_files']
    total_size = report_data['total_size']

    avg_size = total_size / total_processed if total_processed else 0

    print("\n--------- PDF Processing Report ---------")
    print(f"Total PDFs processed: {total_processed}")
    print(f"Total PDFs failed: {total_failed}")
    print(f"Total file size processed: {total_size / 1024:.2f} KB")
    print(f"Average file size: {avg_size / 1024:.2f} KB")
    print("----------------------------------------")


# Function to query MongoDB and display a summary
def display_mongo_summary():
    total_docs = collection.count_documents({})
    avg_file_size = collection.aggregate([{"$group": {"_id": None, "avg_size": {"$avg": "$size"}}}])

    # Print summary from MongoDB
    print(f"\n--------- MongoDB Summary ---------")
    print(f"Total documents in MongoDB: {total_docs}")
    for result in avg_file_size:
        print(f"Average file size in MongoDB: {result['avg_size'] / 1024:.2f} KB")
    print("-----------------------------------")



# ----------------------------------------
# Example Usage
# ----------------------------------------

if __name__ == "__main__":
    # Directory containing the PDFs to process
    pdf_dir = r"PDF_Folder_Path"

    # Start time to track processing time
    start_time = time.time()

    # Process all PDFs in the specified directory
    process_all_pdfs(pdf_dir)

    # Print total time taken to process the PDFs
    end_time = time.time()
    print(f"Processed all PDFs in {end_time - start_time} seconds")

    # Display the MongoDB summary
    display_mongo_summary()
    pdf_files = list_pdfs(pdf_dir)
    print(f"PDFs found: {pdf_files}")

    # Close the MongoDB client connection after processing
    client.close()
