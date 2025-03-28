from flask import render_template, request, redirect, url_for, session, jsonify, flash
from app.visualize import bp
from app.utils.storage import get_parsed_data
import json

@bp.route('/table/<data_id>')
def table_view(data_id):
    # Get the parsed data
    data = get_parsed_data(data_id)
    
    if data is None:
        flash('No data found. Please upload a CSV file first.', 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get selected columns (if any)
    selected_columns = request.args.getlist('columns')
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', '')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Get filter parameters
    filters = {}
    for key, value in request.args.items():
        if key.startswith('filter_') and value:
            column = key.replace('filter_', '')
            filters[column] = value
    
    # Apply filters
    filtered_data = data
    if filters:
        filtered_data = [row for row in data if all(str(filters[col]).lower() in str(row.get(col, '')).lower() for col in filters)]
    
    # Apply sorting
    if sort_by:
        reverse = sort_order == 'desc'
        filtered_data = sorted(filtered_data, key=lambda x: x.get(sort_by, ''), reverse=reverse)
    
    # Calculate total pages
    total_items = len(filtered_data)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Paginate the data
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_data = filtered_data[start_idx:end_idx]
    
    # Get all column names
    if data:
        columns = list(data[0].keys())
    else:
        columns = []
    
    # Use only selected columns if specified
    if selected_columns:
        # Filter paginated data to include only selected columns
        paginated_data = [{col: row[col] for col in selected_columns if col in row} for row in paginated_data]
    
    return render_template('visualize/table.html',
                           title='Data Table',
                           data=paginated_data,
                           all_columns=columns,
                           selected_columns=selected_columns,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           filters=filters,
                           data_id=data_id)

@bp.route('/chart/<data_id>')
def chart_view(data_id):
    # Get the parsed data
    data = get_parsed_data(data_id)
    
    if data is None:
        flash('No data found. Please upload a CSV file first.', 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Get all column names
    columns = list(data[0].keys()) if data else []
    
    # Get chart parameters
    chart_type = request.args.get('chart_type', 'bar')
    x_axis = request.args.get('x_axis', columns[0] if columns else '')
    y_axis = request.args.get('y_axis', columns[1] if len(columns) > 1 else '')
    
    # Prepare data for the chart
    chart_data = {
        'labels': [row.get(x_axis, '') for row in data],
        'datasets': [{
            'label': y_axis,
            'data': [row.get(y_axis, 0) for row in data],
        }]
    }
    
    return render_template('visualize/chart.html',
                           title='Data Chart',
                           chart_data=json.dumps(chart_data),
                           chart_type=chart_type,
                           columns=columns,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           data_id=data_id)

@bp.route('/download/<data_id>')
def download(data_id):
    from flask import Response
    import csv
    from io import StringIO
    
    # Get the parsed data
    data = get_parsed_data(data_id)
    
    if data is None:
        flash('No data found. Please upload a CSV file first.', 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Get selected columns (if any)
    selected_columns = request.args.getlist('columns')
    
    # Filter by selected columns if specified
    if selected_columns:
        filtered_data = [{col: row[col] for col in selected_columns if col in row} for row in data]
        columns = selected_columns
    else:
        filtered_data = data
        columns = list(data[0].keys()) if data else []
    
    # Create a CSV string
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(filtered_data)
    
    # Return the CSV as a response
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=data_{data_id}.csv"}
    )

@bp.route('/stats/<data_id>')
def statistics(data_id):
    import numpy as np
    
    # Get the parsed data
    data = get_parsed_data(data_id)
    
    if data is None:
        flash('No data found. Please upload a CSV file first.', 'error')
        return redirect(url_for('upload.upload_file'))
    
    # Calculate statistics for numerical columns
    stats = {}
    
    # Get all column names
    columns = list(data[0].keys()) if data else []
    
    for col in columns:
        # Extract values for the column
        values = [row.get(col) for row in data]
        
        # Try to convert to float for numerical analysis
        try:
            numerical_values = [float(v) for v in values if v is not None and v != '']
            
            if numerical_values:
                stats[col] = {
                    'count': len(numerical_values),
                    'min': min(numerical_values),
                    'max': max(numerical_values),
                    'mean': np.mean(numerical_values),
                    'median': np.median(numerical_values),
                    'std': np.std(numerical_values)
                }
        except (ValueError, TypeError):
            # Not a numerical column, skip
            pass
    
    return render_template('visualize/stats.html',
                           title='Data Statistics',
                           stats=stats,
                           data_id=data_id)
