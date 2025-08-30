#!/usr/bin/env python3
"""GitHub Models API helper functions.

Contains analyze_with_github_models(image_path, token, animal_species) which
wraps the lower-level request logic and parsing.
"""
import base64
import requests


def analyze_with_github_models(image_path: str, token: str, animal_species: list):
    """Attempt analysis with several endpoints/models and return parsed tuple.

    Returns: (animals, location, time_str, date_str)
    """
    endpoints_and_models = [
        ("https://models.inference.ai.azure.com", "gpt-5"),
        ("https://models.inference.ai.azure.com", "gpt-4o"),
        ("https://api.github.com/models", "gpt-5"),
        ("https://api.github.com/models", "gpt-4o"),
    ]

    for api_base, model_name in endpoints_and_models:
        try:
            result = _try_api_call(image_path, token, api_base, model_name, animal_species)
            if result != ("Error in analysis", "", "", ""):
                return result
        except Exception:
            continue

    return "Error in analysis", "", "", ""


def _try_api_call(image_path: str, token: str, api_base: str, model_name: str, animal_species: list):
    """Make a single API request and parse the response."""
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    prompt = f"""Analyze this camera trap image and provide the following information:

1. ANIMALS: Identify any animals visible in the image. Choose only from this list: {', '.join(animal_species)}
   - For Bearded Vultures: just say "Bearded Vulture" (no count needed)
   - For all other animals: include the count (e.g., "2 Ravens", "1 Fox", "3 Chamois")
   - If no animals visible, say "None detected"

2. METADATA: Read the text at the bottom of the image and extract:
   - Location: Look for FP1, FP2, FP3, or Nische (ignore any "NLP" prefix)
   - Time: Extract time in HH:MM:SS format (with seconds)
   - Date: Extract date in DD.MM.YYYY format (German format with dots)

Please format your response exactly like this:
ANIMALS: [animal name with count or "None detected"]
LOCATION: [FP1/FP2/FP3/Nische only]
TIME: [time in HH:MM:SS]
DATE: [date in DD.MM.YYYY]"""

    if model_name == "gpt-5":
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
            "max_completion_tokens": 500
        }
    else:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
            "max_tokens": 500,
            "temperature": 0.1
        }

    response = requests.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        analysis_text = result['choices'][0]['message']['content']
        return parse_analysis_response(analysis_text)
    else:
        raise Exception(f"API returned {response.status_code}: {response.text}")


def parse_analysis_response(analysis_text: str):
    """Parse the structured response from the AI model into fields."""
    animals = "None detected"
    location = ""
    time_str = ""
    date_str = ""

    lines = analysis_text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('ANIMALS:'):
            animals = line.replace('ANIMALS:', '').strip()
        elif line.startswith('LOCATION:'):
            location = line.replace('LOCATION:', '').strip()
            if 'FP1' in location.upper():
                location = 'FP1'
            elif 'FP2' in location.upper():
                location = 'FP2'
            elif 'FP3' in location.upper():
                location = 'FP3'
            elif 'NISCHE' in location.upper():
                location = 'Nische'
        elif line.startswith('TIME:'):
            time_str = line.replace('TIME:', '').strip()
            if len(time_str.split(':')) == 2:
                time_str = f"{time_str}:00"
        elif line.startswith('DATE:'):
            date_str = line.replace('DATE:', '').strip()
            if '-' in date_str and '.' not in date_str:
                date_str = date_str.replace('-', '.')

    return animals, location, time_str, date_str
