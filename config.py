import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-flask-csv-visualizer'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(Path(__file__).parent, 'app', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'csv', 'txt'}
    
    # Session settings for storing parsed data
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
