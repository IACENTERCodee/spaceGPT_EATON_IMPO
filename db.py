import pyodbc
import json
import re
import os 
from dotenv import load_dotenv



def connect_db():
    """Create and return a connection to the database using environment variables."""
    load_dotenv()

    host = os.getenv("HOST")
    user = os.getenv("USER")
    password = os.getenv("PASS")
    database = os.getenv("DATABASE")

    try:
        # The driver name might vary depending on the SQL Server version and the operating system.
        # Common drivers are 'SQL Server', 'ODBC Driver 17 for SQL Server', etc.
        # Make sure to install the correct ODBC driver for your SQL Server version.
        connection_string = f'DRIVER={{SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password}'
        dbconection=pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',Server=host,Database=database,UID=user,PWD=password,autocommit=True)
        print("Connection to database successful")
        return dbconection
    except Exception as e:
        print(e)
        print("Connection to database failed")
def extract_float_from_string(s):
    """Extrae el primer número flotante de una cadena."""
    if s is None:
        return 0.0
    if isinstance(s, float):
        return s
    if isinstance(s, int):
        return float(s)
    
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", s)
    return float(matches[0]) if matches else 0.0

def convert_to_single_value(value):
    """Convierte una lista a un solo valor o devuelve el valor si no es una lista."""
    if isinstance(value, list):
        return value[0] if value else None
    return value

def process_and_convert_data(data):
    """Procesa y convierte los datos del JSON según su tipo esperado."""
    
    if isinstance(data, dict):
        processed_data = {}
        for key, value in data.items():
            if key == 'total':
                # Extrae un número flotante de una cadena
                processed_data[key] = extract_float_from_string(convert_to_single_value(value))
            elif key == 'items':
                # Procesa una lista de elementos
                processed_data[key] = [process_and_convert_data(item) for item in value[0]]
            else:
                # Convierte listas a un solo valor y mantiene otros tipos como están
                processed_data[key] = convert_to_single_value(value)
        return processed_data
    elif isinstance(data, list):
        return [process_and_convert_data(item) for item in data]
    else:
        return data


def insert_invoice_data(json_data):
    """Inserta datos de factura en la base de datos."""
    if json_data is None:
        return
    if json_data == '':
        return
    
    conn = connect_db()
    try:
        with conn:
            cur = conn.cursor()
            # Procesa y convierte los datos del JSON
            processed_data = process_and_convert_data(json_data)

            # Inserta en la tabla de facturas
            invoice_data = processed_data
            cur.execute("""
                INSERT INTO invoices (invoice_number, invoice_date, country_of_origin, supplier, total)
                VALUES (?, ?, ?, ?, ?);
            """, (invoice_data['invoice_number'], invoice_data['invoice_date'], 
                  invoice_data['country_of_origin'], invoice_data['supplier'], 
                  invoice_data['total']))
                  
            cur.execute("SELECT IDENT_CURRENT('invoices');")
            invoice_id = cur.fetchone()[0]

            # Inserta en la tabla de elementos de factura
            for item in invoice_data['items']:
                if item['weight'] == '':
                    item['weight'] = 0.0
                if item['cost'] == '':
                    item['cost'] = 0.0
                if item['quantity'] == '':
                    item['quantity'] = 0.0
                if item['unit_of_measure'] == '':
                    item['unit_of_measure'] = 'N/A'
                cur.execute("""
                    INSERT INTO line_items (invoice_id, part_number, description, quantity, unit_of_measure, cost, weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (invoice_id, item['part_number'], item['description'], 
                      item['quantity'], item['unit_of_measure'], item['cost'], item['weight']))
            conn.commit()
    except pyodbc.Error as e:
        print(f"Error de SQL Server: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
