import csv
import random
import re
import os

# Define the directory where data files are stored.
# Assumes files are located in "lumi_wildcards/data" relative to this Python file.
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class CSVWildcardNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_template": ("STRING", {
                    "multiline": True,
                    "default": "The {csv:monster:color} {animal}-like monster has {csv:monster:size} {appendage} with a {csv:monster:texture} texture."
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "process_node"
    CATEGORY = "Custom"

    def process_node(self, prompt_template):
        substitution_values = {}

        # First, extract all placeholders in the prompt.
        placeholders = set(re.findall(r"{([^}]+)}", prompt_template))
        
        # Process CSV placeholders by grouping them by CSV file identifier.
        csv_groups = {}
        for ph in placeholders:
            if ph.startswith("csv:"):
                parts = ph.split(":")
                if len(parts) == 3:  # Standard CSV format: csv:file:column
                    _, file_id, col_letter = parts
                    if file_id not in csv_groups:
                        csv_groups[file_id] = set()
                    csv_groups[file_id].add(col_letter)
                elif len(parts) == 4:  # Directory CSV format: csv:dir/file:column
                    _, file_path, file_name, col_letter = parts
                    full_path = os.path.join(file_path, file_name)
                    if full_path not in csv_groups:
                        csv_groups[full_path] = set()
                    csv_groups[full_path].add(col_letter)

        # First load all CSV files and select random rows - store in cache
        csv_cache = {}
        for file_id in csv_groups.keys():
            # Handle both directory and non-directory paths
            if '/' in file_id or '\\' in file_id:
                csv_file_path = os.path.join(DATA_DIR, f"{file_id}.csv")
            else:
                csv_file_path = os.path.join(DATA_DIR, f"{file_id}.csv")
            row_data = self.load_random_csv_row(csv_file_path)
            csv_cache[file_id] = row_data  # May be empty dict if file not found.

        # Now process all CSV placeholders using the cached rows
        for ph in placeholders:
            if ph.startswith("csv:"):
                parts = ph.split(":")
                if len(parts) == 3:  # Standard CSV format
                    _, file_id, col_letter = parts
                    if file_id in csv_cache and col_letter in csv_cache[file_id]:
                        substitution_values[ph] = csv_cache[file_id][col_letter]
                elif len(parts) == 4:  # Directory CSV format
                    _, file_path, file_name, col_letter = parts
                    full_path = os.path.join(file_path, file_name)
                    if full_path in csv_cache and col_letter in csv_cache[full_path]:
                        substitution_values[ph] = csv_cache[full_path][col_letter]

        # Process wildcard placeholders (those not starting with "csv:").
        for ph in placeholders:
            if ph.startswith("csv:"):
                continue
                
            # Check if the placeholder contains a directory path
            if '/' in ph or '\\' in ph:
                # This is a directory path
                file_path = os.path.join(DATA_DIR, f"{ph}.txt")
            else:
                # Try as directory first, then fallback to file
                dir_path = os.path.join(DATA_DIR, ph)
                if os.path.isdir(dir_path):
                    # If it's a directory, we need a file specified with /
                    continue
                file_path = os.path.join(DATA_DIR, f"{ph}.txt")
            
            value = self.get_random_line(file_path)
            if value:
                substitution_values[ph] = value

        # Use custom substitution instead of Python's format
        prompt = prompt_template
        for placeholder, value in substitution_values.items():
            prompt = prompt.replace("{" + placeholder + "}", value)
        
        # For any remaining unsubstituted placeholders, leave them as is
        return (prompt,)

    def load_random_csv_row(self, file_path):
        """
        Opens the CSV file at file_path, selects a random row, and returns a dictionary
        mapping column names from the header row to the corresponding cell values.
        """
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Get header row first
                headers = next(reader, None)
                if not headers:
                    return {}
                
                # Clean up header names - remove spaces and special characters
                headers = [h.strip().lower() for h in headers]
                
                # Read remaining rows
                rows = list(reader)
                if not rows:
                    return {}
                
                # Select random row and create dictionary using header names
                selected_row = random.choice(rows)
                return {header: value.strip() for header, value in zip(headers, selected_row)}
                
        except Exception as e:
            print(f"Error reading CSV {file_path}: {str(e)}")
            return {}

    def get_random_line(self, file_path):
        """
        Opens a text file and returns a random non-empty line.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            if lines:
                return random.choice(lines)
        except Exception:
            return ""
        return ""

class DisplayTextNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),  # Force this to be an input connection
            }
        }

    RETURN_TYPES = ("STRING",)  # Pass-through the input
    FUNCTION = "display_text"
    CATEGORY = "Custom"
    OUTPUT_NODE = True

    def display_text(self, text):
        print(f"\n=== Text Display ===\n{text}\n==================")
        return (text,)  # Pass-through the input

# Registration (adjust as needed for your ComfyUI setup)
NODE_CLASS_MAPPINGS = {
    "CSVWildcardNode": CSVWildcardNode,
    "DisplayTextNode": DisplayTextNode
}
