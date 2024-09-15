import os
import spacy
from pyresparser import ResumeParser
import sys
import re
import PyPDF2
import docx2txt
def extract_resume_info(resume_file):
    try:
        print(f"spaCy version: {spacy.__version__}")
        # print(f"pyresparser version: {pyresparser.__version__}")
        print(f"Python version: {sys.version}")
        
        # Save the uploaded file temporarily
        temp_file_path = 'temp_resume'
        with open(temp_file_path, 'wb+') as destination:
            for chunk in resume_file.chunks():
                destination.write(chunk)
        
        print(f"Temporary file saved at: {temp_file_path}")
        
        # Load spaCy model without custom config
        nlp = spacy.load("en_core_web_sm")
        print("SpaCy model loaded successfully")
        
        # Parse the resume
        parser = ResumeParser(temp_file_path, custom_nlp=nlp)
        data = parser.get_extracted_data()
        
        print(f"Extracted data type: {type(data)}")
        print(f"Extracted data: {data}")
        
        # Check if data is a dictionary
        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary, got {type(data)}")
        
        # Extract required information
        return {
            'first_name': data.get('name', '').split()[0] if data.get('name') else '',
            'email': data.get('email', ''),
            'mobile_number': data.get('mobile_number', '')
        }
    except Exception as e:
        print(f"Error extracting resume information: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        return {
            'first_name': '',
            'email': '',
            'mobile_number': '',
            'error': str(e)
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Temporary file removed: {temp_file_path}")

def fallback_extract_resume_info(resume_file):
    try:
        # Read the file content based on its type
        if resume_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(resume_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif resume_file.name.endswith('.docx'):
            text = docx2txt.process(resume_file)
        else:
            text = resume_file.read().decode('utf-8')

        # Simple regex patterns for email and phone
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        # Extract information
        email = re.search(email_pattern, text)
        phone = re.search(phone_pattern, text)
        
        # Assume the first line might contain the name
        name = text.split('\n')[0].strip()
        
        return {
            'first_name': name.split()[0] if name else '',
            'email': email.group(0) if email else '',
            'mobile_number': phone.group(0) if phone else ''
        }
    except Exception as e:
        print(f"Error in fallback extraction: {str(e)}")
        return {
            'first_name': '',
            'email': '',
            'mobile_number': '',
            'error': str(e)
        }