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

    prompt = f"""Analysiere dieses Kamerafallen-Bild und gib die folgenden Informationen:

    1. TIERE: Identifiziere alle sichtbaren Tiere im Bild. Wähle nur aus dieser Liste: {', '.join(animal_species)}
    - Für Bartgeier: Wenn möglich, identifiziere die Individuen basierend auf diesen Merkmalen:
      - Luisa: Hellere braune Federn mit mehr weißen Flecken, dunklerer Kopf, gelber Ring am rechten Bein, grüner Ring am linken Bein, gebleichte Federn am linken Flügel (nur sichtbar bei geöffnetem Flügel) und am Schwanz (sichtbar beim Sitzen).
      - Generl: Dunkelbraune Federn mit weniger Flecken, gebleichte Federn am linken Flügel (sichtbar beim Sitzen) und an den rechten Fingern (nur bei geöffnetem Flügel). Schwarzer Ring am linken Bein, roter Ring am rechten Bein.
      - Wenn das Individuum identifiziert werden kann, füge es in Klammern hinzu, z.B., "Bartgeier (Luisa)". Wenn unsicher, sage nur "Bartgeier (unbestimmt)".
    - Für alle anderen Tiere: inklusive die Anzahl (z.B., "2 Rabenvögel", "1 Fuchs", "3 Gämsen")
    - Wenn Kolkrabe oder Rabenkrähe erkannt wird: Gib "Rabenvogel/Rabenvögel" aus.
    - Wenn keine Tiere sichtbar sind, sage "Keine erkannt"

    2. METADATEN: Lies den Text am unteren Rand des Bildes und extrahiere:
    - Standort: Suche nach FP1, FP2, FP3 oder Nische (ignoriere jegliches "NLP"-Präfix)
    - Uhrzeit: Extrahiere die Uhrzeit im HH:MM:SS-Format (mit Sekunden)
    - Datum: Extrahiere das Datum im DD.MM.YYYY-Format (deutsches Format mit Punkten)

    Bitte formatiere deine Antwort genau wie folgt:
    TIERE: [Tiername mit Anzahl oder "Keine erkannt"]
    STANDORT: [FP1/FP2/FP3/Nische]
    UHRZEIT: [Uhrzeit in HH:MM:SS]
    DATUM: [Datum in DD.MM.YYYY]"""

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
    animals = "Keine erkannt"  # Default to German for consistency
    location = ""
    time_str = ""
    date_str = ""

    lines = analysis_text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('TIERE:') or line.startswith('ANIMALS:'):  # Support both
            animals = line.replace('TIERE:', '').replace('ANIMALS:', '').strip()
        elif line.startswith('STANDORT:') or line.startswith('LOCATION:'):
            location = line.replace('STANDORT:', '').replace('LOCATION:', '').strip()
            if 'FP1' in location.upper():
                location = 'FP1'
            elif 'FP2' in location.upper():
                location = 'FP2'
            elif 'FP3' in location.upper():
                location = 'FP3'
            elif 'NISCHE' in location.upper():
                location = 'Nische'
        elif line.startswith('UHRZEIT:') or line.startswith('TIME:'):
            time_str = line.replace('UHRZEIT:', '').replace('TIME:', '').strip()
            if len(time_str.split(':')) == 2:
                time_str = f"{time_str}:00"
        elif line.startswith('DATUM:') or line.startswith('DATE:'):
            date_str = line.replace('DATUM:', '').replace('DATE:', '').strip()
            if '-' in date_str and '.' not in date_str:
                date_str = date_str.replace('-', '.')

    return animals, location, time_str, date_str
