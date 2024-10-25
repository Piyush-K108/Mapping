import gradio as gr
import json
import os
import time
import pandas as pd
import requests

systemMessage = "You are a server API that receives document information and returns specific document Headers/Colums as a JSON object."
jsonContentStarter = "```json"

from extraction_contracts import *


def call_mistral(extraction_contract,dynamic_list):
    url = "http://localhost:11434/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    
    content = f"""
    Your task is to match the list I provide with the JSON structure.

    1) Carefully understand the columns/headers from my list.

    2) My JSON structure is: {extraction_contract} and my list is: {dynamic_list}

    3) Populate the JSON with the matching columns from the list.

    4) Place any columns from the list that do not have a match in the JSON inside the 'not_found' key under 'additional_fields'.

    5) Return only the corrected and filled JSON, without any extra text or comments.

    6) Your response should look like this: '''json <Corrected JSON> '''

    7) Do not include any additional text outside of the JSON format.
    """


    message = {
        "role": "user",
        "content": content
    }
    payload = {
        "model": "mistral:latest",
        "messages": [message],
        "temperature": 0.1,
        "top_p": 1,
        "max_tokens": 4000,
        "stream": False,
        "safe_prompt": False,
    }
    print(message)

    payload_json = json.dumps(payload)

    # Start the timer
    start_time = time.time()

    # Send the request
    response = requests.post(url, headers=headers, data=payload_json)

    end_time = time.time()
    # End the timer
    delta_time = end_time - start_time

    minutes, seconds = divmod(delta_time, 60)
    formatted_time = f"{int(minutes):02d}:{int(seconds):02d}"

    response_text = eval(response.text)

    # print(type(response_text))
    choice_dict = response_text["choices"][0]
    msg_dict = choice_dict["message"]
    response_content = msg_dict["content"]

    try:
        json_response = json.loads(response_content)
        json_response['time'] = formatted_time
      
    except Exception as e:
        json_response = {
            'data': response_content,
            'time': formatted_time
        }

    return json_response


def json_to_file(json_data,file_dir, output_file):
    try:
        
        output_dir = 'json_outputs' + "/" + file_dir

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        data = []
        output_path = output_dir + "/" + output_file +".json"
        # Check if the file exists
        file_exists = os.path.isfile(output_path)
        if file_exists:
            with open(output_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
          
        data.append(json_data)
            
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Data successfully written to {output_path}")
       
    

    except Exception as e:
        print(f"Error occurred: {str(e)}")


def clean_json(json_str):

    print(json_str)
    # Remove backticks and unnecessary characters
    cleaned_str = json_str.strip().replace('```json', '').replace('```', '').strip()
    
    # Replace single quotes with double quotes (for valid JSON)
    cleaned_str = cleaned_str.replace("'", '"')
    
    # Load the cleaned string into a JSON object
    try:
        json_obj = json.loads(cleaned_str)
        return json_obj
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None


def Mapping_Process(files, entity):
    # Dictionary mapping each entity to its respective extraction contract
    extraction_contract_map = {
        'Invoices': extraction_contract_invoice,
        'Bill': extraction_contract_bill,
        'Customer': extraction_contract_customer,
        'invoices-Payments': extraction_contract_invoices_payments,
        'Item-Inventory': extraction_contract_item_inventory,
        'Item-Services': extraction_contract_item_services,
        'Journal-Entry': extraction_contract_journal_entry,
        'Sales-Order': extraction_contract_sales_order
    }
    
    # Get the correct extraction contract based on the selected entity
    extraction_contract = extraction_contract_map.get(entity)

    extraction_contract_key = [i for i in extraction_contract_map if extraction_contract_map[i]==extraction_contract]

    
    if extraction_contract:
        pass
    else:
        return

    results = {}

    for file in files:
        file_name = os.path.basename(file)

        if file_name.endswith('.csv'):
            df = pd.read_csv(file, encoding='ISO-8859-1')
            
        elif file_name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)

        else:
            return {"error": f"Unsupported file format: {file_name}"}


        my_file_headers = str(list(df.columns))

        output = call_mistral(extraction_contract,my_file_headers)
        
        raw_data = output.get('data')
        Time = output.get('time')
       
        # invoice_data = correct_json_format(raw_data)
        invoice_data = clean_json(raw_data)

        if invoice_data:
            results[file_name] = invoice_data
            results[file_name]['Time']=Time
            file_data = []
            file_data.append(invoice_data)
            json_to_file(file_data,str(extraction_contract_key[0]),os.path.splitext(file_name)[0])
            
        else:
            print(f"Failed to parse or correct JSON for file: {file_name}")
            
    
    return results



Mapping_Interface = gr.Interface(
    fn=Mapping_Process,
    inputs=[gr.File(label="Upload CSV/XLSX Files", file_count="multiple"), gr.Dropdown(
            ['Invoices','Bill','Customer','invoices-Payments','Item-Inventory','Item-Services','Journal-Entry','Sales-Order'], label="Enter Qucik Book entity"
        )],
    outputs=gr.JSON(label="Extracted JSON Data (CSV/XLSX Files)"),
    description="Upload CSV or XLSX files to extract structured data for a Mapping."
)


app = gr.TabbedInterface(
    interface_list=[Mapping_Interface],
    tab_names=["Mapping Data Json"]
)


if __name__ == "__main__":
    app.launch()
