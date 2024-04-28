from django.shortcuts import render
from django.http import HttpResponse
from PyPDF2 import PdfReader
import re

def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        text = extract_text_from_pdf(pdf_file)
        blood_test_results = compare_with_blood_test(text)
        return render(request, 'pdf_result.html', {'blood_test_results': blood_test_results})
    return render(request, 'pdf_form.html')

def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text
    
def extract_value_from_text(text, item):
    # Construct a pattern to match numeric value after 'g/dL'
    pattern = rf'g/dL\s*(\d+(\.\d+)?)'
    matches = re.findall(pattern, text)
    for match in matches:
        return float(match[0])
    return None


def extract_info_from_text(text):
    # Define patterns to extract name, age, and gender
    name_pattern = r'Name:\s*(\w+\s*\w+)'
    age_pattern = r'Age:\s*(\d+)'
    gender_pattern = r'Gender:\s*(\w+)'

    # Extract name, age, and gender from the text
    name_match = re.search(name_pattern, text)
    age_match = re.search(age_pattern, text)
    gender_match = re.search(gender_pattern, text)

    # Initialize variables to store extracted information
    name = name_match.group(1) if name_match else None
    age = int(age_match.group(1)) if (age_match and age_match.group(1).isdigit()) else None
    gender = gender_match.group(1) if gender_match else None
    
    # Construct patient info dictionary
    patient_info = {
        "name": name,
        "age": age,
        "gender": gender
    }

    return patient_info

def compare_with_blood_test(text):
    blood_test_items = {
        "Hemoglobin": {"low": 12, "high": 16},  # in g/dL
        "Hematocrit": {"low": 36, "high": 50},  # in %
        "RBC Count": {"low": 4.5, "high": 5.5},  # in million cells/mcL
        "MCV": {"low": 80, "high": 101},  # in fL
        "MCH": {"low": 27, "high": 32},  # in pg
        "MCHC": {"low": 31.5, "high": 34.5},  # in g/dL
        "RDW": {"low": 11.6, "high": 14},  # in %
        "White Blood Cells (WBC)": {"low": 4, "high": 10},  # in thou/mm3
        "Platelet Count": {"low": 150, "high": 410},  # in thou/mm3
        "MPV": {"low": 6.5, "high": 12},  # in fL
        "Packed Cell Volume (PCV)": {"low": 40, "high": 50},  # in fL
        "Total Leukocyte Count (TLC)": {"low": 4, "high": 10},  # in fL
        "Segmented Neutrophils": {"low": 40.00, "high": 80.00},  # in %
        "Lymphocytes": {"low": 20.00, "high": 40.00},  # in %
        "Monocytes": {"low": 2.00, "high": 10.00},  # in %
        "Eosinophils": {"low": 1.00, "high": 6.00},  # in %
        "Basophils": {"low": 0.00, "high": 2.00},  # in %
        "Neutrophils": {"low": 2.00, "high": 7.00},  # in thou/mm3
        "Lymphocytes": {"low": 1.00, "high": 3.00},  # in thou/mm3
        "Monocytes": {"low": 0.20, "high": 1.00},  # in thou/mm3
        "Eosinophils": {"low": 0.02, "high": 0.50},  # in thou/mm3
        "Basophils": {"low": 0.02, "high": 0.10} , # in thou/mm3
        "Mean Platelet Volume (Electrical Impedence)": {"low": 6.5, "high": 12.0} 
        # Add more items as needed
    }

    results = {}

    for item, ranges in blood_test_items.items():
        if item.lower() in text.lower():
            value = extract_value_from_text(text, item)

            if value is not None:
                if value < ranges["low"]:
                    results[item] = {"status": "low", "definition": "Below normal range", "symptoms": "Symptoms for low"}
                elif value > ranges["high"]:
                    results[item] = {"status": "high", "definition": "Above normal range", "symptoms": "Symptoms for high"}
                else:
                    results[item] = {"status": "normal", "definition": "Within normal range", "symptoms": "No specific symptoms"}
            else:
                results[item] = {"status": "not_detected", "definition": "Not detected in the text", "symptoms": "No specific symptoms"}
        else:
            results[item] = {"status": "not_mentioned", "definition": "Not mentioned in the text", "symptoms": "No specific symptoms"}

    return results
