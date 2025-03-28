import csv
import os
import chardet

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Read a sample of the file
    result = chardet.detect(raw_data)
    return result['encoding']

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
    
    # Detect encoding
    encoding = detect_encoding(file_path)
    
    try:
        with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
            # Try to determine if the file has a header
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)
            
            if has_header:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                data = [row for row in reader]
            else:
                # If no header, use column numbers as field names
                reader = csv.reader(csvfile, delimiter=delimiter)
                rows = list(reader)
                
                if not rows:
                    return []
                
                headers = [f"column_{i}" for i in range(len(rows[0]))]
                data = []
                
                for row in rows:
                    data.append({headers[i]: value for i, value in enumerate(row)})
            
            return data
    except Exception as e:
        raise Exception(f"Error parsing CSV file: {str(e)}")
