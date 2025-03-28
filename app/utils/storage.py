import uuid
from flask import session

def save_parsed_data(data):
    """
    Save the parsed data in the session.
    
    Args:
        data (list): List of dictionaries representing the parsed CSV data
        
    Returns:
        str: Unique ID for the saved data
    """
    # Generate a unique ID for this dataset
    data_id = str(uuid.uuid4())
    
    # Store the data in the session
    if 'csv_data' not in session:
        session['csv_data'] = {}
    
    session['csv_data'][data_id] = data
    session.modified = True
    
    return data_id

def get_parsed_data(data_id):
    """
    Retrieve the parsed data from the session.
    
    Args:
        data_id (str): Unique ID for the data
        
    Returns:
        list: The parsed data, or None if not found
    """
    if 'csv_data' not in session or data_id not in session['csv_data']:
        return None
    
    return session['csv_data'][data_id]

def delete_parsed_data(data_id):
    """
    Delete the parsed data from the session.
    
    Args:
        data_id (str): Unique ID for the data
        
    Returns:
        bool: True if the data was deleted, False otherwise
    """
    if 'csv_data' in session and data_id in session['csv_data']:
        del session['csv_data'][data_id]
        session.modified = True
        return True
    
    return False
