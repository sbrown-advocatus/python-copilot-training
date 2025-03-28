import uuid
from flask import session, current_app
import pandas as pd

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

def get_parsed_data(file_id):
    """
    Retrieve parsed data from session storage
    
    Args:
        file_id: Unique identifier for the stored data
        
    Returns:
        List of dictionaries representing the data or None if not found
    """
    try:
        # Get data from session storage
        data_session = current_app.config['SESSION_STORAGE'].get(file_id)
        if not data_session:
            return None
        
        # Get DataFrame from session
        df = data_session.get('data')
        if df is None or df.empty:
            return None
        
        # Convert DataFrame to list of dictionaries for template rendering
        return df.to_dict('records')
    except Exception as e:
        current_app.logger.error(f"Error retrieving parsed data: {str(e)}")
        return None

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
