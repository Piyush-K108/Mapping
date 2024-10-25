from collections.abc import MutableMapping
import gradio as gr
import concurrent.futures
import imghdr
import json
import os
import tempfile
import time
from io import BytesIO
from pathlib import Path
import pandas as pd
import pandas as pd
import pypdfium2 as pdfium
from pytesseract import image_to_string
import requests
from PIL import Image
from fastapi import Form
from openai import OpenAI

client = OpenAI()

def create_assistance():
    assistant = client.beta.assistants.create(
        name="Financial Analyst Assistant",
        instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )


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


def send_request_to_gpt():
    pass


def extract_data_from_pdf(file, extraction_contract):

    with open(file, 'rb') as f:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(f.read())
            file_path = temp_file.name

    content = send_request_to_gpt()

    temp_file.close()

    return content


def gradio_app(pdfs, column_headers):
    all_data = []
    overall_total_values_count = 0
    overall_missing_values_count = 0
    file_missing_stats = []

    for pdf in pdfs:
        extracted_data = extract_data_from_pdf(pdf)
        data_row = []
        file_missing_values_count = 0
        file_total_values_count = 0

        for key, value in extracted_data.items():
            column_headers.append(key)
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

# Gradio UI
demo = gr.Interface(
    fn=gradio_app,
    inputs=gr.File(label="Upload PDF(s)", file_count="multiple"),
    outputs=[
        gr.Dataframe(label="Extracted Data", datatype="str"),
        gr.JSON(label="File-Level Missing Values Stats"),
        gr.Label(label="Overall Missing Values Count"),
        gr.Label(label="Overall Missing Values Percentage")
    ],
    description="Upload multiple PDFs to extract structured data and analyze missing values on a per-file basis and overall."
)


if __name__ == "__main__":
    demo.launch()
