Resume Processor
Overview
Resume Processor  is a sophisticated solution designed to extract critical information from resumes, including names, email addresses and phone numbers. This tool leverages advanced NLP techniques to process and analyze resume content, providing a reliable and accurate extraction service. It is built with a Django backend for processing and a React frontend for a seamless user experience.




Features
Text Extraction: Handles various resume formats, including PDF and DOCX.
Information Extraction: Identifies and extracts key details such as name, email and phone number.
User-Friendly Interface: A React-based frontend that allows users to upload resumes and view extracted information effortlessly.




Technologies Used
Backend: Django, Django REST Framework
Frontend: React
NLP: PyPDF2, pdfplumber, docx2txt, pyresparser, spacy
Database: PostgreSQL
Logging: Python logging



Installation
Prerequisites
Python 3.12 or higher
Node.js and npm
PostgreSQL




Backend Setup
Clone the repository:

bash
git clone https://github.com/Kee-rti/ResumeProcessor.git
cd ResumeProcessor
Create a virtual environment and activate it:

bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`


Install backend dependencies:

bash
pip install -r requirements.txt



Apply database migrations:

bash
python manage.py migrate


Start the Django server:

bash
python manage.py runserver


Frontend Setup
Navigate to the resume-frontend directory:



bash
cd resume-frontend
Install frontend dependencies:



bash
npm install
Start the React development server:

bash
npm start




Usage
Access the application via http://localhost:3000 in your web browser.
Upload a resume file using the provided interface.
View the extracted information displayed on the screen.
API Endpoints
/api/extract_resume/
Method: POST



Description: Extracts information from the uploaded resume file.
Request Body: Form-data with the resume file attached.
Response: JSON object containing the extracted information.