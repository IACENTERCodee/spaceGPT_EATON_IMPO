import fitz
import json
import sqlite3
import tiktoken

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding_name = "cl100k_base"
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def reader(pdf_path):
    with fitz.open(pdf_path) as doc:  # Open the PDF file
        text = ""
        for page in doc:  # Iterate over each page in the PDF
            text += page.get_text() 
        numTokens= num_tokens_from_string(text)
        numTokens+50
    return text,numTokens

def execute_sql(sql, parameters=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    try:
        if parameters:
            cursor.execute(sql, parameters)
        else:
            cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        conn.close()

# Función para insertar los datos en la base de datos
def insert_data_to_db(json_data):
    sql_invoice, sql_items = parse_json_to_sql(json_data)

    if sql_invoice and sql_items:
        execute_sql(sql_invoice)
        for sql_item in sql_items:
            execute_sql(sql_item)

def normalize_keys(data):
    """Convierte todas las claves del diccionario a minúsculas."""
    if isinstance(data, dict):
        return {k.lower(): normalize_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_keys(v) for v in data]
    else:
        return data
    
    
def parse_json_to_sql(json_data):
    try:
        # Convierte la cadena JSON a un diccionario
        data = normalize_keys(json.loads(json_data))

        # Extrae los datos de la factura
        invoice_number = data.get("invoice_number")
        invoice_date = data.get("invoice_date")
        country_of_origin = data.get("country_of_origin")
        supplier = data.get("supplier")
        total = data.get("total").replace("$", "")  # Elimina el signo de dólar si está presentes

        # Prepara la instrucción SQL para la tabla Invoice
        sql_invoice = f"INSERT INTO Invoice (InvoiceNumber, InvoiceDate, CountryOfOrigin, Supplier,Total) VALUES ('{invoice_number}', '{invoice_date}', '{country_of_origin}', '{supplier}','{total}');"

        # Prepara las instrucciones SQL para la tabla Item
        sql_items = []
        for item in data.get("items", []):
            part_number = item.get("part_number")
            description = item.get("description")
            quantity = item.get("quantity")
            unit_of_measure = item.get("unit_of_measure")
            cost = item.get("cost").replace("$", "")  # Elimina el signo de dólar si está presente
            weight = item.get("weight")

            sql_item = f"INSERT INTO Item (InvoiceNumber, PartNumber, Description, Quantity, UnitOfMeasure, Cost, Weight) VALUES ('{invoice_number}', '{part_number}', '{description}', {quantity}, '{unit_of_measure}', {cost}, {weight});"
            sql_items.append(sql_item)

        return sql_invoice, sql_items

    except json.JSONDecodeError:
        print("Error al parsear el JSON")
        return None, None
    except KeyError as e:
        print(f"Clave no encontrada en el JSON: {e}")
        return None, None
