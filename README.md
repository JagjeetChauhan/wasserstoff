# PDF Processing Pipeline

## Overview
This project implements a **PDF Processing Pipeline** that automates the ingestion, summarization, and keyword extraction of PDF documents. The processed data is stored in **MongoDB** for querying and further analysis. The pipeline includes error handling, logging, and reporting features, making it scalable and robust.

The project is split into multiple stages, from **Day 1** to **Day 4**, each introducing key features and improvements to the pipeline.

## Features

### **PDF Parsing:**
- Extracts text content from PDFs using **PyPDF2**.
- Stores metadata (file name, size, content) in **MongoDB**.

### **Summarization & Keyword Extraction:**
- Summarizes PDF content using **TF-IDF**.
- Extracts the top keywords from the document.

### **Error Handling & Logging:**
- Logs errors encountered during PDF processing.
- Skips invalid or empty PDFs with appropriate error messages.

### **Reporting:**
- Generates a report after processing all PDFs, including:
  - Total PDFs processed
  - Total PDFs failed
  - Average file size
- Retrieves data from MongoDB to display a summary of stored documents.

### **Multiprocessing Support:**
- Uses Python's **multiprocessing** library to process multiple PDFs concurrently.

---

## Project Structure

```plaintext
PDF_Summarization_Project/
│
├── main.py                      # Main script to run the PDF processing pipeline
├── pdf_pipeline.log              # Log file for error tracking
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies for the project
└── PDF_Folder/                   # Folder where PDF files are stored
```
## Prerequisites
- Python 3.7+
- MongoDB (Ensure MongoDB is running locally, or use a remote instance)

## Python Dependencies
```Install the required Python packages by running the following command:

pip install -r requirements.txt
```
The following Python packages are required:

- PyMuPDF (for PDF parsing)
- PyPDF2 (for alternative PDF parsing)
- pymongo (for MongoDB connection)
- nltk (for natural language processing)
- scikit-learn (for TF-IDF and keyword extraction)

## MongoDB Setup
``` Before running the script, ensure that MongoDB is running locally or remotely. By default, the MongoDB connection URI is set to:

mongodb://localhost:27017/
```
If necessary, modify this in the main.py file to point to your MongoDB instance.

## Usage
### **Running the Script**
- Ensure that your MongoDB server is running.
- Place your PDF files in the PDF_Folder/.
- Run the script using the following command:
```
python main.py
```
### **Process Overview**
The script will:

- Parse all PDF files in the PDF_Folder/.
- Summarize and extract keywords using TF-IDF.
- Store the results in a MongoDB collection (pdf_documents).
- Generate a report after processing, displaying the total PDFs processed, failed, and the average file size.
### **Reporting**
After processing, the script will output a report similar to this:

```
--------- PDF Processing Report ---------
Total PDFs processed: 10
Total PDFs failed: 2
Total file size processed: 125.34 KB
Average file size: 12.53 KB
----------------------------------------

--------- MongoDB Summary ---------
Total documents in MongoDB: 10
Average file size in MongoDB: 12.53 KB
-----------------------------------
```
Additionally, a pdf_pipeline.log file will log any errors that occur during processing.

## Example Folder Structure
```
PDF_Summarization_Project/
│
├── main.py
├── pdf_pipeline.log
├── README.md
├── requirements.txt
└── PDF_Folder/
    ├── example1.pdf
    ├── example2.pdf
    └── ...
```
## Code Details
### **process_pdf() Function**
- Extracts text from a PDF file.
- Summarizes the text using TF-IDF to score the top sentences.
- Extracts keywords from the text using TF-IDF.
- Logs errors during processing and stores valid results in MongoDB.
### **Error Handling**
- If any issues arise during parsing or extraction, errors are logged in pdf_pipeline.log.
- PDFs with no content are skipped and logged as failed.
### **MongoDB Ingestion**
All processed PDFs are inserted into MongoDB with metadata fields, including:

- filename: Name of the PDF file.
- path: Path to the PDF file.
- size: File size in bytes.
- content: The full extracted text.
- summary: The summarized content.
- keywords: A list of extracted keywords.
### **Report Generation**
After processing, the script calculates statistics on processed PDFs (total files, failed files, total size, etc.) and displays this in a report. MongoDB is queried to display the total number of stored documents and the average file size.

## Customization
### **TF-IDF Parameters**
- You can adjust the number of sentences in the summary or the number of keywords by modifying the summarize_text() and extract_keywords() functions in the code.

### **Directory Path**
- Update the pdf_dir in the script to point to your own folder containing PDFs.
