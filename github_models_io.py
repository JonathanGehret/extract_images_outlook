#!/usr/bin/env python3
"""I/O helpers: image listing, renaming/backups, and Excel writes.
This module exposes functions that operate on explicit paths/params so they
can be used from the GUI without carrying state.
"""
import os
import shutil
import pandas as pd


def get_image_files(images_folder: str):
    if not images_folder:
        return []
    try:
        files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    except FileNotFoundError:
        return []
    return sorted(files)


def refresh_image_list(images_folder: str, old_list: list, current_index: int):
    try:
        all_files = os.listdir(images_folder)
        image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('.') and 'backup' not in f.lower()]
        image_files.sort()

        old_current_file = old_list[current_index] if current_index < len(old_list) else None
        if old_current_file and old_current_file in image_files:
            current_index = image_files.index(old_current_file)
        elif current_index >= len(image_files):
            current_index = max(0, len(image_files) - 1)

        return image_files, current_index
    except Exception:
        return old_list, current_index


def create_backup_and_rename_image(images_folder: str, image_file: str, location: str, date: str, species1: str, count1: str, species2: str, count2: str, new_id: int, generl_checked: bool=False, luisa_checked: bool=False):
    try:
        old_path = os.path.join(images_folder, image_file)
        if not os.path.exists(old_path):
            return None

        backup_dir = os.path.join(images_folder, "backup_originals")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, image_file)
        if not os.path.exists(backup_path):
            shutil.copy2(old_path, backup_path)

        animals = []
        if species1:
            animals.append(f"{species1}_{count1 or '1'}")
        if species2:
            animals.append(f"{species2}_{count2 or '1'}")

        animal_str = "_".join(animals) if animals else "Unknown"

        try:
            if '.' in date:
                day, month, year = date.split('.')
                short_year = year[-2:] if len(year) == 4 else year
                date_str = f"{month}.{day}.{short_year}"
            else:
                date_str = date
        except Exception:
            date_str = date

        special_names = []
        if generl_checked:
            special_names.append("Generl")
        if luisa_checked:
            special_names.append("Luisa")

        special_str = "_".join(special_names) if special_names else ""

        if special_str:
            new_name = f"{location}_{new_id:04d}_{date_str}_{special_str}_{animal_str}.jpeg"
        else:
            new_name = f"{location}_{new_id:04d}_{date_str}_{animal_str}.jpeg"

        new_path = os.path.join(images_folder, new_name)

        counter = 1
        base_new_name = new_name
        while os.path.exists(new_path) and new_path != old_path:
            name_without_ext = base_new_name.replace('.jpeg', '')
            new_name = f"{name_without_ext}_{counter}.jpeg"
            new_path = os.path.join(images_folder, new_name)
            counter += 1

        if old_path != new_path:
            os.rename(old_path, new_path)
        return new_name
    except Exception:
        return None


def get_next_id_for_location(output_excel: str, location: str):
    try:
        df = pd.read_excel(output_excel, sheet_name=location)
        if not df.empty and 'Nr. ' in df.columns:
            numeric_ids = []
            for id_val in df['Nr. ']:
                try:
                    if pd.notna(id_val):
                        numeric_ids.append(int(float(id_val)))
                except (ValueError, TypeError):
                    continue
            if numeric_ids:
                return max(numeric_ids) + 1
            return 1
        return 1
    except Exception:
        return 1


def save_single_result(output_excel: str, location: str, data: dict):
    expected_columns = [
        'Nr. ', 'Standort', 'Datum', 'Uhrzeit', 'Dagmar', 'Recka', 'Unbestimmt',
        'Aktivität', 'Art 1', 'Anzahl 1', 'Art 2', 'Anzahl 2', 'Interaktion', 
        'Sonstiges', 'General', 'Luisa', 'Korrektur'
    ]

    try:
        filtered_data = {col: data.get(col, '') for col in expected_columns}
        new_row = pd.DataFrame([filtered_data])
        try:
            existing_df = pd.read_excel(output_excel, sheet_name=location)
            existing_df = existing_df.reindex(columns=expected_columns, fill_value='')
            combined_df = pd.concat([existing_df, new_row], ignore_index=True)
        except Exception:
            combined_df = new_row

        with pd.ExcelWriter(output_excel, mode='a', if_sheet_exists='replace') as writer:
            combined_df.to_excel(writer, sheet_name=location, index=False)
        return True
    except Exception:
        return False
