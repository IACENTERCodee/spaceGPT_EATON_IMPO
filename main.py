import gradio as gr
from utils import reader, parse_json_to_sql, execute_sql
import api_openai
import asyncio
import time
from aiolimiter import AsyncLimiter


tokens_processed = 0

async def process_file(file):
    global tokens_processed
    token_limit_per_minute = 90000

    # Check if the token limit is reached
    if tokens_processed >= token_limit_per_minute:
        await asyncio.sleep(60 - time.time() % 60)  # Sleep until the start of the next minute
        tokens_processed = 0  # Reset token count for the new minute

    # Implement the processing for each file
    text, numTokens = reader(file)  # Assuming reader returns the number of tokens
    tokens_processed += numTokens

    if tokens_processed >= token_limit_per_minute:
        await asyncio.sleep(60 - time.time() % 60)  # Sleep if the limit is reached within processing
        tokens_processed = 0

    OpenAIHelper = api_openai.OpenAIHelper()
    extracted_text = await OpenAIHelper.extract_fields_from_invoice(text, numTokens)
    return parse_json_to_sql(extracted_text)

def insert_data_to_db(output):
    output = output[1:-1].rstrip(", ")
    execute_sql(output)

if __name__ == '__main__':
    with gr.Blocks() as ui:
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Invoice Reader")
                file = gr.File(label="Upload PDF", type='filepath', file_count="multiple", file_types=["pdf"])
                click = gr.Button(value="Extract")
            with gr.Column():
                gr.Markdown("## Invoice Data")
                output = gr.Textbox(label="Output Box")
                insert = gr.Button(value="Insert to DB")
            
            insert.click(fn=insert_data_to_db, inputs=output)
            click.click(fn=extractor, inputs=file, outputs=output, api_name='extractor')
            
    ui.launch()
