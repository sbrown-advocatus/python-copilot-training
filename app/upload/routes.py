import os
from flask import render_template, request, redirect, url_for, current_app, session, flash
from werkzeug.utils import secure_filename
from app.upload import bp
from app.utils.parser import parse_csv
from app.utils.storage import save_parsed_data

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get delimiter from form
            delimiter = request.form.get('delimiter', ',')
            
            try:
                # Parse the CSV file
                parsed_data = parse_csv(filepath, delimiter)
                
                # Save the parsed data
                data_id = save_parsed_data(parsed_data)
                
                # Redirect to the visualization page
                return redirect(url_for('visualize.table_view', data_id=data_id))
            
            except Exception as e:
                flash(f'Error parsing CSV file: {str(e)}', 'error')
                return redirect(request.url)
    
    return render_template('upload/upload.html', title='Upload CSV')
