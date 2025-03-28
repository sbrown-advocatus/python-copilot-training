import os
from flask import render_template, request, redirect, url_for, current_app, session, flash
from werkzeug.utils import secure_filename
from app.upload import bp
import pandas as pd
import uuid
import chardet

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, the browser submits an empty file
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Save the file temporarily
            temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            
            # Determine delimiter (auto-detect or from form)
            delimiter = request.form.get('delimiter', '')
            if not delimiter or delimiter == 'auto':
                # Try to detect the delimiter
                with open(temp_path, 'rb') as f:
                    result = chardet.detect(f.read(1024))
                    encoding = result['encoding']
                
                with open(temp_path, 'r', encoding=encoding) as f:
                    sample = f.readline()
                    if sample.count(',') > sample.count(';'):
                        delimiter = ','
                    else:
                        delimiter = ';'
            
            try:
                # Parse the CSV file with pandas
                df = pd.read_csv(temp_path, delimiter=delimiter)
                
                # Generate a unique ID for this dataset
                file_id = str(uuid.uuid4())
                
                # Store in server-side session
                if 'SESSION_STORAGE' not in current_app.config:
                    current_app.config['SESSION_STORAGE'] = {}
                
                current_app.config['SESSION_STORAGE'][file_id] = {
                    'filename': filename,
                    'data': df
                }
                
                # Clean up the temporary file
                os.remove(temp_path)
                
                flash(f'File {filename} uploaded and parsed successfully!', 'success')
                return redirect(url_for('visualize.table_view', file_id=file_id))
            
            except Exception as e:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                flash(f'Error parsing CSV file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Only CSV files are allowed', 'error')
            return redirect(request.url)
    
    return render_template('upload/upload.html', title='Upload CSV File')
