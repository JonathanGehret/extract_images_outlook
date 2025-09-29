#!/usr/bin/env python3
"""GitHub Models API helper functions.

Contains analyze_with_github_models(image_path, token, animal_species) which
wraps the lower-level request logic and parsing.
"""
import base64
from datetime import datetime
from pathlib import Path
import json
import re
import traceback
import requests


LOG_DIR = Path.home() / ".kamerafallen-tools"
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

LOG_PATH = LOG_DIR / "analyzer_debug.log"


def _log_debug(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [API] {message}"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(log_line + "\n")
    except Exception:
        # Last resort: print to stdout (may be captured by callers)
        try:
            print(log_line)
        except Exception:
            pass


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
        _log_debug(f"Raw analysis response from {model_name}@{api_base} ->\n{analysis_text}")
        return parse_analysis_response(analysis_text)
    else:
        raise Exception(f"API returned {response.status_code}: {response.text}")


def parse_analysis_response(analysis_text: str):
    """Parse the structured response from the AI model into fields."""
    # Handle JSON-style responses first
    stripped = analysis_text.strip()
    if stripped.startswith('{'):
        try:
            payload = json.loads(stripped)
            return _parse_from_mapping(payload)
        except Exception as exc:
            _log_debug(f"Failed to parse JSON response: {exc}\n{traceback.format_exc()}")

    animals_value, location_value, time_value, date_value = _parse_from_lines(analysis_text)
    _log_debug(
        "Parsed fields -> animals=%r, location=%r, time=%r, date=%r"
        % (animals_value, location_value, time_value, date_value)
    )
    return animals_value, location_value, time_value, date_value


def _parse_from_mapping(payload):
    """Extract fields from dict-like payloads."""
    # Normalize keys to lowercase without accents for easier lookup
    def _normalized_keys(source):
        items = []
        for key, value in source.items():
            if isinstance(value, dict):
                items.extend(_normalized_keys(value))
            else:
                items.append((str(key).lower(), value))
        return items

    mapping = dict(_normalized_keys(payload))

    animals_value = mapping.get('tiere') or mapping.get('animals') or ''
    location_value = mapping.get('standort') or mapping.get('location') or ''
    time_value = mapping.get('uhrzeit') or mapping.get('time') or ''
    date_value = mapping.get('datum') or mapping.get('date') or ''

    animals_value = _normalize_animals(animals_value)
    location_value = _normalize_location(location_value)
    time_value = _normalize_time(time_value)
    date_value = _normalize_date(date_value)

    return animals_value, location_value, time_value, date_value


def _parse_from_lines(analysis_text: str):
    """Parse free-form Markdown / text responses."""
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
        line = re.sub(r'^\d+\.\s*', '', line)
        line = line.strip()

        # Attempt to split "KEY: value" or "KEY - value"
        match = re.match(r'^(?P<key>[A-Za-zÄÖÜäöü\s]+)\s*[:\-\u2013\u2014]\s*(?P<value>.+)$', line)

        if match:
            key_raw = match.group('key').strip().lower()
            key_raw = key_raw.replace('*', '').strip()
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

    animals_value = _normalize_animals(collected['animals'])
    location_value = _normalize_location(collected['location'])
    time_value = _normalize_time(collected['time'])
    date_value = _normalize_date(collected['date'])

    return animals_value, location_value, time_value, date_value


def _normalize_animals(raw):
    if isinstance(raw, list):
        animals_value = ', '.join(filter(None, raw))
    else:
        animals_value = str(raw) if raw is not None else ''

    animals_value = animals_value.strip()
    if not animals_value:
        animals_value = 'Keine erkannt'
    return animals_value


def _normalize_location(location_value):
    location_value = str(location_value or '').strip()
    location_upper = location_value.upper()
    if 'FP1' in location_upper:
        return 'FP1'
    if 'FP2' in location_upper:
        return 'FP2'
    if 'FP3' in location_upper:
        return 'FP3'
    if 'NISCHE' in location_upper:
        return 'Nische'
    return location_value


def _normalize_time(time_value):
    time_value = str(time_value or '').strip()
    if not time_value:
        return ''
    time_value = time_value.replace('Uhr', '').replace('uhr', '').strip()
    time_digits = re.findall(r'\d+', time_value)
    if len(time_digits) >= 2:
        hours = time_digits[0].zfill(2)
        minutes = time_digits[1].zfill(2)
        seconds = time_digits[2].zfill(2) if len(time_digits) >= 3 else '00'
        return f"{hours}:{minutes}:{seconds}"
    return time_value


def _normalize_date(date_value):
    date_value = str(date_value or '').strip()
    if not date_value:
        return ''
    date_value = date_value.replace('/', '.').replace('-', '.').replace(' ', '')
    for fmt in ('%d.%m.%Y', '%Y.%m.%d', '%d.%m.%y', '%d.%m.%Y', '%Y%m%d'):
        try:
            parsed_date = datetime.strptime(date_value, fmt)
            return parsed_date.strftime('%d.%m.%Y')
        except ValueError:
            continue
    # Try extracting numeric components manually
    digits = re.findall(r'\d+', date_value)
    if len(digits) >= 3:
        day = digits[0].zfill(2)
        month = digits[1].zfill(2)
        year = digits[2]
        if len(year) == 2:
            year = '20' + year
        return f"{day}.{month}.{year}"
    return date_value
