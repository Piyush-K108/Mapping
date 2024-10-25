from collections.abc import MutableMapping
import re
import gradio as gr
import concurrent.futures
# import imghdr
import json
import os
import tempfile
import time
from io import BytesIO
from pathlib import Path
import pandas as pd
import pypdfium2 as pdfium
from pytesseract import image_to_string
import requests
from PIL import Image
from fastapi import Form

systemMessage = "You are a server API that receives document information and returns specific document Headers/Colums as a JSON object."
jsonContentStarter = "```json"

global extraction_contract
extraction_contract = {
    "invoice": {
        "memo": "",
        "due_date": "",
        "issue_date": "",
        "line_items": [
            {
                "item": {
                    "id": "",
                    "quantity": 0,
                    "item_name": "",
                    "unit_amount": 0
                },
                "class_name": "",
                "description": "",
                "total_amount": 0
            }
        ],
        "customer_id": "",
        "currency_code": "",
        "customer_name": "",
        "document_number": "",
        "additional_fields": {
            "addresses": [],
            "not_found": "",
        }
    }
}


def render_page(pdf_file, page_index, scale):
    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=[page_index],
        scale=scale,
    )
    image_list = list(renderer)
    image = image_list[0]
    image_byte_array = BytesIO()
    image.save(image_byte_array, format='jpeg', optimize=True)
    image_byte_array = image_byte_array.getvalue()
    return {page_index: image_byte_array}


def convert_pdf_to_images(file_path, scale=300/72):
    # Check if the file is already an image
    # if imghdr.what(file_path) is not None:
    #     # If it is, return it as is
    #     with open(file_path, 'rb') as f:
    #         return [{0: f.read()}]

    # If it's not an image, proceed with the conversion
    pdf_file = pdfium.PdfDocument(file_path)

    page_indices = [i for i in range(len(pdf_file))]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in page_indices:
            future = executor.submit(render_page, pdf_file, i, scale)
            futures.append(future)

        final_images = []
        for future in concurrent.futures.as_completed(futures):
            final_images.append(future.result())

    return final_images


def process_image(index, image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes))
        raw_text = str(image_to_string(image, 'eng', 'oem-3 --psm 4'))
        return raw_text
    except Exception as e:
        raise Exception(f"Error processing image {index}: {e}")


def extract_text_with_pytesseract(list_dict_final_images):

    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for index, image_bytes in enumerate(image_list):
            future = executor.submit(process_image, index, image_bytes)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                raw_text = future.result()
                image_content.append(raw_text)
            except Exception as e:
                raise Exception(f"Error processing image: {e}")

    return image_content


def json_to_csv(json_data, output_file='output.csv'):
    def flatten_json(data, parent_key='', sep='_'):
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_json(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    # Flatten the JSON data
    flat_data = flatten_json(json_data)

    # Convert to DataFrame
    df = pd.DataFrame([flat_data])

    # Check if the file exists
    file_exists = os.path.isfile(output_file)

    # Save to CSV, appending if file exists
    df.to_csv(output_file, mode='a', header=not file_exists, index=False)

    return 1


def send_request_to_mistral(content: str) -> str:
    # url = "https://api.mistral.ai/v1/chat/completions"
    url = "http://localhost:11434/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        # 'Authorization': f'Bearer {API_KEY}'
    }

    # message = Message(role="user", content=content)
    message = {
        "role": "user",
        "content": content
    }

    # payload = Payload(
    #     model="mistral",
    #     messages=[message.dict()],
    #     # temperature=0.7,
    #     temperature=0.1,
    #     top_p=1,
    #     max_tokens=2000,
    #     stream=False,
    #     safe_prompt=False
    # )

    payload = {
        "model": "mistral:latest",
        "messages": [message],
        # "response_format": {
        #     "type": "json_object"
        # },
        "temperature": 0.1,
        "top_p": 1,
        "max_tokens": 4000,
        "stream": False,
        "safe_prompt": False,
        # "random_seed": 1337
    }

    # response = requests.post(url, headers=headers, data=payload.json().encode('utf-8'))
    print(message)
    payload_json = json.dumps(payload)
    print("posting")
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
        print(json_response)
        json_to_csv(json_response, 'invoice_output.csv')
    except Exception as e:
        json_response = {
            'data': response_content,
            'time': formatted_time
        }
        print(response_content)

    # response = requests.post(url, headers=headers, json=payload.json())

    # response = requests.post(url, headers=headers, data=json_input)
    # print("--- Payload ---")
    # print(payload_json)
    # print("-- response --")
    # print(response.request.body)
    # print(response.request.headers)

    # print("--- Response ---")
    # response_text = response.text
    # response_text = response_text.replace("\n","")
    # print(response_text)
    # response_json = response.json()
    # decoder = json.JSONDecoder(strict=False)
    # response_json = decoder.decode(response_text)

    # Extract the content from the response and convert it to a string
    # content = str(response_json.get('choices', [{}])[0].get('message', {}).get('content', ''))

    # Extract the JSON substring from the content
    # json_content = extractJsonSubstring(jsonContentStarter, content)

    # json_content = extract_json(json_content)

    # return json_content
    return json_response


# Setting to True will print debug information
crumbs = True


def is_flat(dictionary):
    for value in dictionary.values():
        if isinstance(value, (MutableMapping, list)):
            return False
    return True


def flatten(dictionary, parent_key=False, separator='.'):

    # Check if the dictionary is already flat
    if is_flat(dictionary):
        if crumbs:
            print('Dictionary is already flat.')
        return dictionary

    items = []
    for key, value in dictionary.items():
        if crumbs:
            print('Checking:', key)
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            if crumbs:
                print(new_key, ': dict found')
            if not value.items():
                if crumbs:
                    print('Adding key-value pair:', new_key, None)
                items.append((new_key, None))
            else:
                items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            if crumbs:
                print(new_key, ': list found')
            if len(value):
                for k, v in enumerate(value):
                    items.extend(
                        flatten({str(k): v}, new_key, separator).items())
            else:
                if crumbs:
                    print('Adding key-value pair:', new_key, None)
                items.append((new_key, None))
        else:
            if crumbs:
                print('Adding key-value pair:', new_key, value)
            items.append((new_key, value))

    return dict(items)


def extract_data_from_pdf(file, extraction_contract):

    with open(file, 'rb') as f:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(f.read())
            file_path = temp_file.name

    extraction_contract = str(extraction_contract)

    # Convert PDF to images
    images = convert_pdf_to_images(file_path)

    # Extract text using different methods
    extracted_text = extract_text_with_pytesseract(images)

    # Join the extracted text into a single string
    extracted_text = "\n new page ---  \n".join(extracted_text)

    # add system message to the extracted text
    extracted_text = systemMessage + "\n####Content\n\n" + extracted_text

    # add contract to the extracted text
    extracted_text = extracted_text + "\n####Structure of the JSON output file\n\n" + extraction_contract + \
        """
        \n 1) Document Structure: The JSON object represents an invoice with various headers and fields that need to be matched to specific terms.
           2) Invoice Headers:

            •	memo: The memo or notes associated with the invoice.
            •	due_date: The date by which payment is due.
            •	issue_date: The date the invoice was issued.
            •	line_items: A list of items included in the invoice, where each item has:
                •	item: An object containing:
                    •	id: Identifier for the item.
                    •	quantity: The quantity of the item.
                    •	item_name: Description or name of the item.
                    •	unit_amount: Price per unit of the item.
                •	class_name: The unit of measure (U/M) for the item.
                •	description: A description of the line item.
                •	total_amount: The total amount for that line item.
            •	customer_id: Identifier for the customer.
            •	currency_code: The currency used for the invoice.
            •	customer_name: Name of the customer billed.
            •	document_number: The invoice number.
            •	additional_fields: A collection of extra fields, including:
                •	addresses: An array of address types (e.g., billing and shipping).
                •	PO or Ref. #: Purchase order or reference number.
                •	Financial Terms: Any specific financial terms related to the invoice.
            3) You hav to match the headers/Columns only ont the values 
            4) Example Output Format:
                {
                "invoice": {
                    "memo": "Memo",
                    "due_date": "Due Date",
                    "issue_date": "Invoice Date",
                    "line_items": [
                    {
                        "item": {
                        "id": "Item Code",
                        "quantity": "Quantity",
                        "item_name": "Description",
                        "unit_amount": "Unit Price"
                        },
                        "class_name": "U/M",
                        "description": "Description",
                        "total_amount": "Total Value"
                    }
                    ],
                    "customer_id": "Bill To",
                    "currency_code": "Currency",
                    "customer_name": "Bill To",
                    "document_number": "Invoice #",
                    "additional_fields": {
                    "addresses": [
                        "Bill To Address",
                        "Ship To Address"
                    ],
                    "PO or Ref. #": "",
                    "Financial Terms": ""
                    }
                }
                }

        \n"""
    extracted_text = extracted_text + "\n#### JSON Response\n\n" + jsonContentStarter

    # Send the extracted text and extraction contract to the Mistral API
    content = send_request_to_mistral(extracted_text)

    #

    # Close and remove the temporary file
    temp_file.close()

    return content


def gradio_app(pdfs):
    all_data = []
    overall_total_values_count = 0
    overall_missing_values_count = 0
    file_missing_stats = []

    for pdf in pdfs:
        extracted_data = extract_data_from_pdf(pdf, extraction_contract)
        data_row = []
        file_missing_values_count = 0
        file_total_values_count = 0

        for key, value in extracted_data.items():
            if value in ["N/A", "Not Available", None, "", " "]:
                file_missing_values_count += 1
            file_total_values_count += 1
            data_row.append(value)

        all_data.append(data_row)

        overall_missing_values_count += file_missing_values_count
        overall_total_values_count += file_total_values_count

        file_missing_percentage = (
            file_missing_values_count / file_total_values_count) * 100 if file_total_values_count > 0 else 0

        file_missing_stats.append({
            "file_name": os.path.basename(pdf.name),
            "missing_values_count": file_missing_values_count,
            "missing_values_percentage": f"{file_missing_percentage:.2f}%"
        })

    overall_missing_percentage = (overall_missing_values_count /
                                  overall_total_values_count) * 100 if overall_total_values_count > 0 else 0

    return all_data, file_missing_stats, f"Overall Missing Values Count: {overall_missing_values_count}", f"Overall Missing Values Percentage: {overall_missing_percentage:.2f}%"


# Generate column headers from extraction_contract keys
column_headers = list(extraction_contract.keys())
static_list = [
    "invoice.memo",
    "invoice.due_date",
    "invoice.issue_date",
    "invoice.line_items[0].item.id",
    "invoice.line_items[0].item.quantity",
    "invoice.line_items[0].item.item_name",
    "invoice.line_items[0].item.unit_amount",
    "invoice.line_items[0].class_name",
    "invoice.line_items[0].description",
    "invoice.line_items[0].total_amount",
    "invoice.customer_id",
    "invoice.currency_code",
    "invoice.customer_name",
    "invoice.document_number",
    "invoice.additional_fields.addresses",
    "invoice.additional_fields.not_found"
]


def call_mistral(dynamic_list):
    url = "http://localhost:11434/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


    content = f"""

        Your task is to compare two lists: one is dynamic (it changes with every query), and the other is static (remains the same for each query).

        1) Compare the lists: One list will always change (provided as {dynamic_list}), and the other will remain static (provided as {static_list}).

        2) Match the columns: Compare the columns of the dynamic list with the static list.

        3) Response: Your return should be a formatted string indicating:

        Which dynamic columns matched the static columns, in the format {{\"static_column\": \"dynamic_column\"}}.

        Format of the response:
    
        f"Matched: matched_pairs" # where matched_pairs is a dictionary with matching static columns as keys and dynamic columns as values.
        f"Not found: unmatched_columns only from dynamic_column" 
        Return only the formatted response—no additional text.

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
    print("posting")
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
        print(json_response)
        json_to_csv(json_response, 'invoice_output.csv')
    except Exception as e:
        json_response = {
            'data': response_content,
            'time': formatted_time
        }
        print(json_response)

    return json_response


def correct_json_format(raw_data):
    # Step 1: Extract the JSON string (cleaning extra characters)
    if '```json' in raw_data:
        json_string = raw_data.split('```json')[1].split('```')[0].strip()
    else:
        json_string = raw_data

    json_string = re.sub(
        r'"not_found":"([^"]+)"', r'"not_found": "\1"', json_string)

    # Fix misformatted key-value pairs like "customer_id": "not_found":"customer_id"
    json_string = re.sub(
        r'("[^"]+"): ("[^"]+")(?::"[^"]+")?', r'\1: \2', json_string)

    # Step 3: Attempt to load the JSON and return the corrected format
    try:
        result_json = json.loads(json_string)
        return result_json
    except json.JSONDecodeError as e:
        print(f"JSON parsing error after corrections: {e}")
        return None



def Mapping_Process(files):
    results = []
    outputs = []

    for file in files:
        df = pd.read_excel(file)
        my_file_headers = (str(list(df.columns)))
        print("List:", my_file_headers)

        # Call the LLM function to get the raw output
        output = call_mistral(my_file_headers)
        raw_data = output.get('data')
        Time = output.get('time')
        print("Processing time:", Time)

        # Extract matched and not found text
        matched_text = raw_data.split("Matched:")[1].split("Not found:")[0].strip()
        not_found_text = raw_data.split("Not found:")[1].strip()

        # Convert the matched_text into a dictionary of dynamic:static pairs
        matched_pairs = {}
        for pair in matched_text.split(","):
            if ":" in pair:
                dynamic_col, static_col = [item.strip() for item in pair.split(":")]
                matched_pairs[dynamic_col] = static_col

        # Convert the not found text into a list of unmatched fields
        not_found_fields = [field.strip() for field in not_found_text.split(",")]

        # Append results with the new structure
        outputs.append({"matched_fields": matched_pairs})
        outputs.append({"not_found_fields": not_found_fields})
        results.append({"File":outputs})

    return results


# Gradio UI
demo = gr.Interface(
    fn=gradio_app,
    inputs=gr.File(label="Upload PDF(s)", file_count="multiple"),
    outputs=[
        gr.Dataframe(label="Extracted Data",
                     headers=column_headers, datatype="str"),
        gr.JSON(label="File-Level Missing Values Stats"),
        gr.Label(label="Overall Missing Values Count"),
        gr.Label(label="Overall Missing Values Percentage")
    ],
    description="Upload multiple PDFs to extract structured data and analyze missing values on a per-file basis and overall."
)


Mapping = gr.Interface(
    fn=Mapping_Process,
    inputs=gr.File(label="Upload CSV/XLSX Files", file_count="multiple"),
    outputs=gr.JSON(label="Extracted JSON Data (CSV/XLSX Files)"),
    description="Upload CSV or XLSX files to extract structured data for a Mapping."
)


app = gr.TabbedInterface(
    interface_list=[Mapping,demo],
    tab_names=["Mapping Data Columns","General File Processing"]
)


if __name__ == "__main__":
    app.launch()
