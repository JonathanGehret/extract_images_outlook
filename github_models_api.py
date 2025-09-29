#!/usr/bin/env python3
"""GitHub Models API helper functions.

Contains analyze_with_github_models(image_path, token, animal_species) which
wraps the lower-level request logic and parsing.
"""
import base64
from datetime import datetime
import re
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
        print("DEBUG: Raw analysis response:\n" + analysis_text)
        return parse_analysis_response(analysis_text)
    else:
        raise Exception(f"API returned {response.status_code}: {response.text}")


def parse_analysis_response(analysis_text: str):
    """Parse the structured response from the AI model into fields."""
    key_map = {
        'tiere': 'animals',
        'animals': 'animals',
        'standort': 'location',
        'location': 'location',
        'uhrzeit': 'time',
        'time': 'time',
        'datum': 'date',
        'date': 'date',
    }

    collected = {
        'animals': [],
        'location': '',
        'time': '',
        'date': '',
    }

    pending_key = None
    for raw_line in analysis_text.splitlines():
        line = raw_line.strip()
        if not line:
            pending_key = None
            continue

        # Remove typical bullet characters
        line = line.lstrip('•-*\t ').strip()

        # Attempt to split "KEY: value" or "KEY - value"
        match = re.match(r'^(?P<key>[A-Za-zÄÖÜäöü]+)\s*[:\-]\s*(?P<value>.+)$', line)

        if match:
            key_raw = match.group('key').strip().lower()
            value = match.group('value').strip()
            mapped_key = key_map.get(key_raw)

            if mapped_key:
                if value == '':
                    pending_key = mapped_key
                    continue

                if mapped_key == 'animals':
                    collected['animals'].append(value)
                    pending_key = mapped_key  # allow list continuation
                elif mapped_key == 'location':
                    collected['location'] = value
                    pending_key = None
                elif mapped_key == 'time':
                    collected['time'] = value
                    pending_key = None
                elif mapped_key == 'date':
                    collected['date'] = value
                    pending_key = None
                continue

        # Handle follow-up lines after a key declaration
        if pending_key:
            value = line.strip()
            if pending_key == 'animals':
                collected['animals'].append(value)
            elif pending_key == 'location' and not collected['location']:
                collected['location'] = value
            elif pending_key == 'time' and not collected['time']:
                collected['time'] = value
            elif pending_key == 'date' and not collected['date']:
                collected['date'] = value
            continue

        # Attempt fallback pattern "KEY value" without colon
        fallback_match = re.match(r'^(?P<key>[A-Za-zÄÖÜäöü]+)\s+(?P<value>.+)$', line)
        if fallback_match:
            key_raw = fallback_match.group('key').strip().lower()
            value = fallback_match.group('value').strip()
            mapped_key = key_map.get(key_raw)
            if mapped_key:
                if mapped_key == 'animals':
                    collected['animals'].append(value)
                    pending_key = mapped_key
                elif mapped_key == 'location' and not collected['location']:
                    collected['location'] = value
                elif mapped_key == 'time' and not collected['time']:
                    collected['time'] = value
                elif mapped_key == 'date' and not collected['date']:
                    collected['date'] = value

    animals_value = ', '.join(filter(None, collected['animals']))
    if not animals_value:
        animals_value = 'Keine erkannt'

    location_value = collected['location']
    location_upper = location_value.upper()
    if 'FP1' in location_upper:
        location_value = 'FP1'
    elif 'FP2' in location_upper:
        location_value = 'FP2'
    elif 'FP3' in location_upper:
        location_value = 'FP3'
    elif 'NISCHE' in location_upper:
        location_value = 'Nische'

    time_value = collected['time']
    if time_value:
        time_digits = re.findall(r'\d+', time_value)
        if len(time_digits) >= 2:
            hours = time_digits[0].zfill(2)
            minutes = time_digits[1].zfill(2)
            seconds = time_digits[2].zfill(2) if len(time_digits) >= 3 else '00'
            time_value = f"{hours}:{minutes}:{seconds}"

    date_value = collected['date']
    if date_value:
        date_value = date_value.replace('/', '.').replace('-', '.')
        try:
            parsed_date = datetime.strptime(date_value, '%d.%m.%Y')
        except ValueError:
            try:
                parsed_date = datetime.strptime(date_value, '%Y.%m.%d')
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_value, '%d.%m.%y')
                except ValueError:
                    parsed_date = None
        if parsed_date:
            date_value = parsed_date.strftime('%d.%m.%Y')

    return animals_value, location_value, time_value, date_value
