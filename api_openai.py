import os
from dotenv import load_dotenv
from openai import OpenAI


def extract_fields_with_openai(invoice_text):
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
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
        
    prompt = (
        "Please extract the following details from the invoice: "
        "1. Invoice number, invoice date, country of origin, and supplier. "
        "2. For each item in the invoice, list the part number, description, quantity, unit of measure, cost, and weight."
    )
    json="""{
    "invoice_number": "",
    "invoice_date": "",
    "country_of_origin": "",
    "supplier": "",
    "items": [
        {
        "part_number": "",
        "description": "",
        "quantity": "",
        "unit_of_measure": "",
        "cost": "",
        "weight": ""
        }
    ]}"""
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
                    "role": "system",
                    "content": "Return data in the following format: json with key-value pairs. f{json}"
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{invoice_text}"
                },
            ]
        )
        responses.append(response.choices[0].message.content)
    # Combina las respuestas, si es necesario, o devuelve la única respuesta
    return " ".join(responses) if len(responses) > 1 else responses[0]
