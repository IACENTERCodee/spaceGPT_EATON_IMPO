import fitz  # PyMuPDF
import os
import glob
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from shutil import move

# Load the .env file where your OPENAI_API_KEY is stored
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Define the directory path where your PDF files are located
pdf_folder_path = 'files/'
output_csv_path = 'g.csv'

# Directory where processed files will be moved to
processed_files_dir = 'processed_files/'

# Ensure the processed files directory exists
os.makedirs(processed_files_dir, exist_ok=True)

# Function to read PDF and extract text
def reader(pdf_path):
    with fitz.open(pdf_path) as doc:  # Open the PDF file
        text = ""
        for page in doc:  # Iterate over each page in the PDF
            text += page.get_text()  # Append text from each page
    return text

# Function to prompt OpenAI to extract fields from the invoice text
def extract_fields_with_openai(invoice_text):
    # Divide el texto en segmentos si es demasiado largo
    segments = []
    if len(invoice_text) > 4096:  # Aproximadamente 4096 caracteres, ajustar según sea necesario
        words = invoice_text.split()
        segment = ""
        for word in words:
            if len(segment) + len(word) + 1 < 4096:
                segment += word + " "
            else:
                segments.append(segment)
                segment = word + " "  # Comienza un nuevo segmento con la palabra actual
        segments.append(segment)  # Agrega el último segmento
    else:
        segments = [invoice_text]
    prompt = "Please list the following fields from the invoice, including multiple entries for parts, quantities, unit of measure, costs, and weights if they are present:"
    
    fields = "Invoice Number, Invoice Date, Part Numbers, Descriptions, Quantities, Units of Measure, Costs, Weights, Country of Origin, Supplier."
        # Procesa cada segmento con la API
    responses = []
    for segment in segments:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant skilled in extracting specific information from structured documents like invoices."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{fields}\n\n{invoice_text}"                }
            ]
        )
        responses.append(response.choices[0].message.content)
    # Combina las respuestas, si es necesario, o devuelve la única respuesta
    return " ".join(responses) if len(responses) > 1 else responses[0]


# Check if the CSV already exists, if not, create it with the header
if not os.path.isfile(output_csv_path):
    pd.DataFrame(columns=['File Name', 'Extracted Data']).to_csv(output_csv_path, index=False)

# Main process
# Iterate over each subdirectory in the main directory
for subdir, dirs, files in os.walk(pdf_folder_path):
    # Take only the first 5 PDF files from each subdirectory
    for file_name in sorted(files)[:5]:
        if file_name.lower().endswith('.pdf'):
            pdf_path = os.path.join(subdir, file_name)
            invoice_text = reader(pdf_path)
            extracted_data = extract_fields_with_openai(invoice_text)
            
            # Append the data to the CSV file
            df = pd.DataFrame([[file_name, extracted_data]], columns=['File Name', 'Extracted Data'])
            df.to_csv(output_csv_path, mode='a', header=False, index=False)
            
            # Move the processed PDF file to the processed_files_dir
            move(pdf_path, os.path.join(processed_files_dir, file_name))

print(f"Data extracted from all invoices has been saved to {output_csv_path}")
