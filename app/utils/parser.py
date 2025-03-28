import csv
import os
import chardet
from io import TextIOWrapper

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()  # Read the entire file for better detection
    result = chardet.detect(raw_data)
    return result['encoding'] or 'utf-8'  # Default to utf-8 if detection fails

def parse_csv(file_path, delimiter=','):
    """
    Parse a CSV file and return the data as a list of dictionaries.
    
    Args:
        file_path (str): Path to the CSV file
        delimiter (str): CSV delimiter character
        
    Returns:
        list: List of dictionaries, where each dictionary represents a row
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # List of encodings to try in order
    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    # First try with detected encoding
    detected_encoding = detect_encoding(file_path)
    if detected_encoding and detected_encoding.lower() not in encodings_to_try:
        encodings_to_try.insert(0, detected_encoding)
    
    last_exception = None
    
    # Try each encoding until one works
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'rb') as f:
                # Use TextIOWrapper for better encoding handling
                text_file = TextIOWrapper(f, encoding=encoding, newline='')
                
                # Try to determine if the file has a header
                sample = text_file.read(1024)
                text_file.seek(0)
                
                try:
                    sniffer = csv.Sniffer()
                    has_header = sniffer.has_header(sample)
                except:
                    # If sniffing fails, assume there is a header
                    has_header = True
                
                if has_header:
                    reader = csv.DictReader(text_file, delimiter=delimiter)
                    data = [row for row in reader]
                else:
                    # If no header, use column numbers as field names
                    reader = csv.reader(text_file, delimiter=delimiter)
                    rows = list(reader)
                    
                    if not rows:
                        return []
                    
                    headers = [f"column_{i}" for i in range(len(rows[0]))]
                    data = []
                    
                    for row in rows:
                        data.append({headers[i]: value for i, value in enumerate(row)})
                
                return data
        except UnicodeDecodeError as e:
            # Keep track of the exception but continue trying other encodings
            last_exception = e
            continue
        except Exception as e:
            # For other exceptions, raise immediately
            raise Exception(f"Error parsing CSV file: {str(e)}")
    
    # If we've tried all encodings and none worked, raise the last exception
    if last_exception:
        raise Exception(f"Failed to decode the CSV file with any of the supported encodings. Last error: {str(last_exception)}")
    
    # This should never happen
    raise Exception("Unknown error parsing CSV file")
