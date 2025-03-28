from flask import render_template, request, redirect, url_for, session, jsonify, flash, current_app
from app.visualize import bp
from app.utils.storage import get_parsed_data
import json

@bp.route('/table/<file_id>')
def table_view(file_id):
    # Get the parsed data
    data = get_parsed_data(file_id)
    
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
                           data_id=file_id)

@bp.route('/chart/<file_id>', methods=['GET', 'POST'])
def chart_view(file_id):
    """Display chart visualization of the data."""
    data_session = current_app.config['SESSION_STORAGE'].get(file_id)
    if not data_session:
        flash('Dataset not found or session expired. Please upload the file again.', 'warning')
        return redirect(url_for('upload.index'))
    
    data = data_session.get('data', None)
    if data is None or data.empty:
        flash('No data available for visualization.', 'warning')
        return redirect(url_for('upload.index'))
    
    columns = data.columns.tolist()
    
    # Get chart parameters from form
    chart_type = request.form.get('chart_type', 'bar')
    x_axis = request.form.get('x_axis', columns[0] if columns else None)
    y_axis = request.form.get('y_axis', columns[1] if len(columns) > 1 else columns[0])
    
    chart_div = None
    chart_title = f"{y_axis} by {x_axis}"
    
    if request.method == 'POST' and x_axis and y_axis:
        try:
            import plotly.express as px
            import plotly.io as pio
            import plotly.graph_objects as go
            
            # Create a subset of data to prevent browser overload
            plot_data = data.head(1000)  # Limit to 1000 rows for performance
            
            # Handle different chart types
            if chart_type == 'bar':
                fig = px.bar(plot_data, x=x_axis, y=y_axis, title=chart_title)
            elif chart_type == 'line':
                fig = px.line(plot_data, x=x_axis, y=y_axis, title=chart_title)
            elif chart_type == 'scatter':
                fig = px.scatter(plot_data, x=x_axis, y=y_axis, title=chart_title)
            elif chart_type == 'pie':
                # For pie charts, we may need to aggregate data
                value_counts = plot_data[x_axis].value_counts().reset_index()
                value_counts.columns = [x_axis, 'count']
                fig = px.pie(value_counts, names=x_axis, values='count', title=f"Distribution of {x_axis}")
            else:
                fig = px.bar(plot_data, x=x_axis, y=y_axis, title=chart_title)
                
            # Make charts responsive
            fig.update_layout(
                autosize=True,
                height=500,  # Fixed height
                margin=dict(l=50, r=50, b=100, t=100, pad=4),
                paper_bgcolor="white",
                plot_bgcolor="white",
            )
            
            # Add gridlines for better readability
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            # Convert the figure to HTML with optimal settings
            chart_div = pio.to_html(
                fig, 
                full_html=False,
                include_plotlyjs=False,
                config={
                    'responsive': True,
                    'displayModeBar': True,
                    'displaylogo': False,
                    'scrollZoom': True
                }
            )
            
            current_app.logger.info(f"Chart generated successfully with type: {chart_type}")
        except Exception as e:
            flash(f"Error generating chart: {str(e)}", 'danger')
            current_app.logger.error(f"Chart generation error: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
    
    return render_template('visualize/chart.html',
                           file_id=file_id,
                           columns=columns,
                           chart_type=chart_type,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           chart_div=chart_div,
                           chart_title=chart_title)

@bp.route('/download/<file_id>')
def download(file_id):
    from flask import Response
    import csv
    from io import StringIO
    
    # Get the parsed data
    data = get_parsed_data(file_id)
    
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
        headers={"Content-disposition": f"attachment; filename=data_{file_id}.csv"}
    )

@bp.route('/stats/<file_id>')
def statistics(file_id):
    import numpy as np
    
    # Get the parsed data
    data = get_parsed_data(file_id)
    
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
                           file_id=file_id)  # Use file_id consistently
