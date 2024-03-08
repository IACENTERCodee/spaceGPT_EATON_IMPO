import os
from pdfminer.high_level import extract_text_to_fp
from io import BytesIO

def convertpdtext(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            output_buffer = BytesIO()
            with open(pdf_path, 'rb') as pdf_file:
                extract_text_to_fp(pdf_file, output_buffer, output_type='text')
                html_content = output_buffer.getvalue().decode('utf-8')
                print(html_content)

# Example usage:


def convert_pdf_to_text(pdf_path):
    output_buffer = BytesIO()
    with open(pdf_path, 'rb') as pdf_file:
        extract_text_to_fp(pdf_file, output_buffer, output_type='text')
        text_content = output_buffer.getvalue().decode('utf-8')
    return text_content



