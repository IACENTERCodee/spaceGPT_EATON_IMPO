import streamlit as st
from utils import reader, extract_text_from_pdf, execute_sql,convert_json_to_dataframe_invoice,convert_json_to_dataframe_invoice,convert_json_to_dataframe_items
import api_openai
import asyncio
import time
from db import insert_invoice_data
import json

# Global variable to track the number of tokens processed
tokens_processed = 0
token_limit_per_minute = 90000



async def process_file(file):
    global tokens_processed

    text, num_tokens = extract_text_from_pdf(file)  # Assuming reader returns the number of tokens
    if tokens_processed + num_tokens > token_limit_per_minute:
        # Wait until the start of the next minute if this file would exceed the token limit
        await asyncio.sleep(60 - time.time() % 60)
        tokens_processed = 0  # Reset the token count for the new minute

    tokens_processed += num_tokens
    openai_helper = api_openai.OpenAIHelper()
    extracted_text = await openai_helper.extract_fields_from_invoice(text, num_tokens)
    
    if extracted_text is not None:
        json_data = json.loads(extracted_text)
        insert_invoice_data(json_data)
        invoices = convert_json_to_dataframe_invoice(json_data)
        items = convert_json_to_dataframe_items(json_data)
    else:
        invoices = None
        items = None
    
    return extracted_text, invoices, items

async def process_files():
    global tokens_processed

    files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if not files:
        return None, None, None  # Return a default value if no files are uploaded
        
    results = {}
    for file in files:
        try:
            st.info(f"Processing file {file.name}...")
            st.info(f"Number of tokens processed: {tokens_processed}")  
            st.info(f"Number of tokens remaining: {token_limit_per_minute - tokens_processed}")
            extracted_text, invoices, items = await process_file(file)
            results[file.name] = {"extracted_text": extracted_text, "invoices": invoices, "items": items}
        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}")
            return None, None, None  # Return a default value in case of an error

    st.success("Files processed successfully!")

    return results.get("extracted_text"), results.get("invoices"), results.get("items")

if 'invoices' not in st.session_state:
    st.session_state['invoices'] = None

if 'invoice_items' not in st.session_state:  # Renamed 'items' to 'invoice_items'
    st.session_state['invoice_items'] = None 

extracted_text, new_invoices, new_items = asyncio.run(process_files()) or (None, None, None)
st.title("Invoice Parser")

if new_invoices is not None:
    st.session_state['invoices'] = new_invoices
                                                                    
if new_items is not None:
    st.session_state['invoice_items'] = new_items

# Display data using session_state
if extracted_text:
    st.write("Extracted text:")
    st.markdown(extracted_text)

if st.session_state.invoices is not None:
    st.write("Invoices:")
    st.dataframe(data=st.session_state.invoices)

if st.session_state.invoice_items is not None:
    st.write("Items:")
    st.dataframe(data=st.session_state.invoice_items)
