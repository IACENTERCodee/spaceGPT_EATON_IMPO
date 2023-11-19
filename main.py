import gradio as gr
from utils import reader,parse_json_to_sql,execute_sql
from openai import OpenAI
from api_openai import extract_fields_with_openai

def extractor(file):
    text = reader(file)
    text = extract_fields_with_openai(text)
    #text = parse_json_to_sql(text)
    return text    
def insert_data_to_db(output):
    output = output[1:-1]
    #remove last 2 characters from output
    output = output[:-2]
    execute_sql(output)
    
if __name__ == '__main__':
    with gr.Blocks() as ui:
        gr.Markdown("## Invoice Reader")
        file=gr.File(label="Upload PDF", type='filepath',file_types=["pdf"]) 
        click=gr.Button(value="Extract")
        output = gr.Textbox(label="Output Box")
        insert=gr.Button(value="Insert to DB")
        insert.click(fn=insert_data_to_db,inputs=output)
        click.click(fn=extractor, inputs=file,outputs=output,api_name='extractor')
    ui.launch()