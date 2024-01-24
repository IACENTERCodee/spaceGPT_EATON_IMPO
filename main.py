import gradio as gr
from utils import reader, is_pdf_readable, execute_sql,convert_json_to_dataframe_invoice,convert_json_to_dataframe_invoice,convert_json_to_dataframe_items
import api_openai
import asyncio
import time
from db import insert_invoice_data
import json
import pandas as pd


tokens_processed = 0
token_limit_per_minute = 90000



async def process_file(file):
    global tokens_processed

    text, numTokens = reader(file)  # Assuming reader returns the number of tokens
    if tokens_processed + numTokens > token_limit_per_minute:
        await asyncio.sleep(60 - time.time() % 60)
        tokens_processed = 0

    tokens_processed += numTokens
    OpenAIHelper = api_openai.OpenAIHelper()
    extracted_text = await OpenAIHelper.extract_fields_from_invoice(text, numTokens)
    
    if extracted_text is not None:
        json_data = json.loads(extracted_text)
        if is_pdf_readable(file):
            insert_invoice_data(json_data)
            invoices = convert_json_to_dataframe_invoice(json_data)
            items = convert_json_to_dataframe_items(json_data)
        else:
            invoices = pd.DataFrame()
            items = pd.DataFrame()
    else:
        invoices = pd.DataFrame()
        items = pd.DataFrame()

    return extracted_text, invoices, items


async def process_files_in_batches(files):
    global tokens_processed
    batch = []
    text_results = []
    invoices_results = []
    items_results = []

    for file in files:
        text, numTokens = reader(file)
        if tokens_processed + numTokens <= token_limit_per_minute:
            batch.append(file)
            tokens_processed += numTokens
        else:
            batch_results = await asyncio.gather(*[process_file(f) for f in batch])
            for text, invoices, items in batch_results:
                text_results.append(text)
                invoices_results.append(invoices)
                items_results.append(items)
            batch = [file]
            tokens_processed = numTokens
            await asyncio.sleep(60 - time.time() % 60)

    if batch:
        batch_results = await asyncio.gather(*[process_file(f) for f in batch])
        for text, invoices, items in batch_results:
            text_results.append(text)
            invoices_results.append(invoices)
            items_results.append(items)

    return text_results, invoices_results, items_results


if __name__ == '__main__':
    with gr.Blocks(theme=gr.themes.Soft()) as ui:
        with gr.Row():
            with gr.Column(scale=0.5):
                gr.Markdown("# Invoice Reader")
                gr.Markdown("## Upload PDF")
                # markdown image syntax: ![alt text](image.png)
                gr.Markdown("![](https://i.imgur.com/VFsGQT8.jpeg)")
                file = gr.File(label="Upload PDF", type='filepath', file_count="multiple", file_types=["pdf"])
                click = gr.Button(value="Extract")
            with gr.Column():
                gr.Markdown("## Invoice Data")
                output = gr.Textbox(label="Output Box",visible=False)
                invoices = gr.DataFrame(show_label=True,wrap=True)
                items = gr.DataFrame(show_label=True,wrap=True)
            
            outputs=[output,invoices, items]
            click.click(fn=process_files_in_batches, inputs=file, outputs=outputs, api_name='extractor')
            
    ui.launch()
