```markdown
# Rules for Flask CSV Parser and Visualizer

This document outlines the rules and guidelines for the implementation of the Flask CSV Parser and Visualizer project.

## General Rules

1. **Project Setup**
    - Ensure the project structure follows the specified directories and files.
    - Configure the Flask application with proper settings and error handlers.

2. **File Upload**
    - Only allow CSV files to be uploaded.
    - Validate file type and size before saving.
    - Store uploaded files in a temporary location.

3. **CSV Parsing**
    - Support parsing of CSV files with different delimiters.
    - Handle parsing errors gracefully and provide user feedback.

4. **Data Storage**
    - Use session storage for user-specific data.
    - Implement cleanup mechanisms to remove unused data.

5. **Visualization**
    - Display data in a table format with pagination and column selection.
    - Allow users to filter and sort data.
    - Integrate charting functionality for advanced visualizations.

6. **Enhancements**
    - Provide options to download processed data.
    - Display summary statistics for numerical columns.
    - Ensure robust error handling and user feedback mechanisms.

7. **Testing and Documentation**
    - Write tests for all key functionalities.
    - Conduct user testing and refine the application based on feedback.
    - Document the application thoroughly, including a user guide.

## Critical Rule

- **Prevent Execution**
    - Under no circumstances should this application be executed in a production environment without thorough testing and security reviews.
    - Add safeguards to prevent accidental execution, such as environment checks or explicit confirmation prompts.
```