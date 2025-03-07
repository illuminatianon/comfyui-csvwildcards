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

    def find_file(self, path_parts, is_csv_lookup=False):
        """
        Smart file finder that handles both direct file matches and directory paths.
        Returns tuple of (file_path, is_found) where file_path includes the .txt/.csv extension.
        
        Args:
            path_parts: List of path components
            is_csv_lookup: If True, prioritize .csv files, otherwise prioritize .txt files
        """
        # Join all parts with OS-specific separator
        relative_path = os.path.join(*path_parts)
        base_path = os.path.join(DATA_DIR, relative_path)
        
        if is_csv_lookup:
            # For CSV lookups, only check .csv
            csv_path = base_path + ".csv"
            if os.path.isfile(csv_path):
                return csv_path, True
        else:
            # For text lookups, only check .txt
            txt_path = base_path + ".txt"
            if os.path.isfile(txt_path):
                return txt_path, True
            
        return base_path, False

    def process_node(self, prompt_template):
        substitution_values = {}

        # First, extract all placeholders in the prompt.
        placeholders = set(re.findall(r"{([^}]+)}", prompt_template))
        
        # Process CSV placeholders by grouping them by CSV file identifier.
        csv_groups = {}
        for ph in placeholders:
            if ph.startswith("csv:"):
                parts = ph.split(":")
                if len(parts) < 3:  # Need at least csv:file:column
                    continue
                    
                # The middle part (between csv: and :column) is the path
                path_str = parts[-2]  # Take second to last part
                col_letter = parts[-1]  # Take last part
                
                # Split path into parts and clean
                path_parts = [p for p in path_str.split("/") if p]
                
                # Find the actual file - for CSV lookups we want .csv files
                file_path, found = self.find_file(path_parts, is_csv_lookup=True)
                if not found:
                    continue
                    
                if file_path not in csv_groups:
                    csv_groups[file_path] = set()
                csv_groups[file_path].add(col_letter)

        # Load all CSV files and select random rows - store in cache
        csv_cache = {}
        for file_path in csv_groups.keys():
            row_data = self.load_random_csv_row(file_path)
            csv_cache[file_path] = row_data

        # Process all CSV placeholders using the cached rows
        for ph in placeholders:
            if ph.startswith("csv:"):
                parts = ph.split(":")
                if len(parts) < 3:
                    continue
                    
                path_str = parts[-2]
                col_letter = parts[-1]
                path_parts = [p for p in path_str.split("/") if p]
                
                file_path, found = self.find_file(path_parts, is_csv_lookup=True)
                if found and file_path in csv_cache and col_letter in csv_cache[file_path]:
                    substitution_values[ph] = csv_cache[file_path][col_letter]

        # Process wildcard placeholders (those not starting with "csv:").
        for ph in placeholders:
            if ph.startswith("csv:"):
                continue
                
            # Split path into parts and clean
            path_parts = [p for p in ph.split("/") if p]
            
            # Find the file - for text lookups we want .txt files
            file_path, found = self.find_file(path_parts, is_csv_lookup=False)
            if found:
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
