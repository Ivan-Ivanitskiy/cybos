#!/usr/bin/env python3
"""
CSV Diff Visualizer
Creates an HTML file showing differences between two CSV files
Uses the same dark theme as the CSV preview tool
"""

import csv
import sys
import os
from pathlib import Path
from datetime import datetime

def parse_date(date_str):
    """Parse date string in DD.MM.YYYY format"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str.strip(), '%d.%m.%Y')
    except ValueError:
        return None

def read_csv_data(csv_path):
    """Read CSV data and return headers and rows"""
    headers = []
    data = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        data = list(reader)
    
    return headers, data

def find_differences(old_data, new_data, headers):
    """Find differences between old and new data"""
    differences = []
    
    # Create a map of old data by ID (assuming first column is ID)
    old_map = {}
    for row in old_data:
        if row and row[0]:  # If ID exists
            old_map[row[0]] = row
    
    # Compare with new data
    for i, new_row in enumerate(new_data):
        if not new_row or not new_row[0]:  # Skip rows without ID
            continue
            
        row_id = new_row[0]
        if row_id in old_map:
            old_row = old_map[row_id]
            row_diffs = []
            
            # Compare each field
            for j, (old_val, new_val) in enumerate(zip(old_row, new_row)):
                if old_val != new_val:
                    row_diffs.append({
                        'column': headers[j] if j < len(headers) else f'Column {j}',
                        'old_value': old_val,
                        'new_value': new_val,
                        'column_index': j
                    })
            
            if row_diffs:
                differences.append({
                    'row_index': i,
                    'row_id': row_id,
                    'changes': row_diffs,
                    'old_row': old_row,
                    'new_row': new_row
                })
        else:
            # New row added
            differences.append({
                'row_index': i,
                'row_id': row_id,
                'type': 'added',
                'new_row': new_row
            })
    
    # Check for deleted rows
    new_ids = {row[0] for row in new_data if row and row[0]}
    for old_row in old_data:
        if old_row and old_row[0] and old_row[0] not in new_ids:
            differences.append({
                'row_id': old_row[0],
                'type': 'deleted',
                'old_row': old_row
            })
    
    return differences

def format_cell_value(value, header):
    """Format a cell value with appropriate styling"""
    if not value:
        return ""
    
    if header.lower() == "status" and value.lower() == "done":
        return f'<span class="status-done">✓ Done</span>'
    elif header.lower() == "priority":
        if value.lower() == "high":
            return f'<span class="priority-high">{value}</span>'
        elif value.lower() == "med":
            return f'<span class="priority-med">{value}</span>'
        elif value.lower() == "low":
            return f'<span class="priority-low">{value}</span>'
    elif header.lower() == "tag" and value:
        # Split tags and format them
        tags = [tag.strip() for tag in value.split(',')]
        return ''.join(f'<span class="tag">{tag}</span>' for tag in tags)
    
    return value

def create_task_row_html(row_data, headers, highlight_changes=None):
    """Create HTML for a task row with optional highlighting"""
    html = '<div class="task-row">'
    
    for i, (header, value) in enumerate(zip(headers, row_data)):
        cell_class = "task-cell"
        if highlight_changes and i in highlight_changes:
            if highlight_changes[i] == 'removed':
                cell_class += " highlight-removed"
            elif highlight_changes[i] == 'added':
                cell_class += " highlight-added"
        
        formatted_value = format_cell_value(value, header)
        html += f'<div class="{cell_class}">{formatted_value}</div>'
    
    html += '</div>'
    return html

def create_diff_html(old_csv_path, new_csv_path, output_path=None):
    """Create an HTML file showing differences between two CSV files"""
    
    if output_path is None:
        output_path = f"diff_{os.path.basename(new_csv_path).replace('.csv', '')}.html"
    
    # Read both CSV files
    old_headers, old_data = read_csv_data(old_csv_path)
    new_headers, new_data = read_csv_data(new_csv_path)
    
    # Find differences
    differences = find_differences(old_data, new_data, new_headers)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Diff - {os.path.basename(new_csv_path)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            min-height: 100vh;
            color: #e0e0e0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #2d2d2d;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            overflow: hidden;
            border: 1px solid #404040;
        }}
        
        .header {{
            background: #2d2d2d;
            color: #e0e0e0;
            padding: 15px 20px;
            text-align: center;
            border-bottom: 2px solid #404040;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 20px;
            font-weight: 600;
        }}
        
        .header p {{
            margin: 5px 0 0 0;
            color: #a0a0a0;
            font-size: 14px;
        }}
        
        .summary {{
            padding: 15px 20px;
            background: #3a3a3a;
            border-bottom: 2px solid #404040;
            display: flex;
            justify-content: space-around;
            text-align: center;
        }}
        
        .summary-item {{
            color: #e0e0e0;
        }}
        
        .summary-number {{
            font-size: 24px;
            font-weight: bold;
            color: #4a90e2;
        }}
        
        .summary-label {{
            font-size: 12px;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .diff-section {{
            margin: 20px;
        }}
        
        .diff-item {{
            background: #2d2d2d;
            border: 2px solid #404040;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .diff-header {{
            background: #3a3a3a;
            padding: 12px 15px;
            border-bottom: 1px solid #404040;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .diff-title {{
            font-weight: 600;
            color: #e0e0e0;
        }}
        
        .diff-type {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .type-modified {{
            background: #ffa726;
            color: #000;
        }}
        
        .type-added {{
            background: #28a745;
            color: #fff;
        }}
        
        .type-deleted {{
            background: #dc3545;
            color: #fff;
        }}
        
        .diff-content {{
            padding: 15px;
        }}
        
        .change-item {{
            margin-bottom: 10px;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 4px;
            border-left: 4px solid #4a90e2;
        }}
        
        .change-column {{
            font-weight: 600;
            color: #4a90e2;
            margin-bottom: 5px;
        }}
        
        .change-values {{
            display: flex;
            gap: 15px;
        }}
        
        .change-old, .change-new {{
            flex: 1;
            padding: 8px;
            border-radius: 4px;
        }}
        
        .change-old {{
            background: #dc3545;
            color: #fff;
        }}
        
        .change-new {{
            background: #28a745;
            color: #fff;
        }}
        
        .change-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 3px;
            opacity: 0.8;
        }}
        
        .task-comparison {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 15px;
        }}
        
        .task-version {{
            background: #1a1a1a;
            border-radius: 6px;
            overflow: hidden;
        }}
        
        .task-version-header {{
            background: #3a3a3a;
            padding: 8px 12px;
            font-weight: 600;
            color: #e0e0e0;
            border-bottom: 1px solid #404040;
        }}
        
        .task-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1px;
            background: #404040;
        }}
        
        .task-cell {{
            background: #2d2d2d;
            padding: 8px;
            font-size: 12px;
        }}
        
        .task-cell-header {{
            background: #3a3a3a;
            font-weight: 600;
            color: #4a90e2;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .highlight-removed {{
            background: rgba(255, 193, 7, 0.3);
            border-left: 3px solid #ffc107;
        }}
        
        .highlight-added {{
            background: rgba(40, 167, 69, 0.2);
            border-left: 3px solid #28a745;
        }}
        
        .tag {{
            display: inline-block;
            background: #4a90e2;
            color: #ffffff;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            margin: 1px;
        }}
        
        .status-done {{
            background-color: #28a745;
            color: #ffffff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .priority-high {{
            color: #ff6b6b;
            font-weight: 600;
        }}
        
        .priority-med {{
            color: #ffa726;
            font-weight: 500;
        }}
        
        .priority-low {{
            color: #a0a0a0;
        }}
        
        .no-changes {{
            text-align: center;
            padding: 40px;
            color: #a0a0a0;
            font-style: italic;
        }}
        
        .row-preview {{
            margin-top: 10px;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            color: #a0a0a0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CSV Changes Report</h1>
            <p>Comparing {os.path.basename(old_csv_path)} → {os.path.basename(new_csv_path)}</p>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-number">{len(differences)}</div>
                <div class="summary-label">Total Changes</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len([d for d in differences if d.get('type') != 'added' and d.get('type') != 'deleted'])}</div>
                <div class="summary-label">Modified Rows</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len([d for d in differences if d.get('type') == 'added'])}</div>
                <div class="summary-label">Added Rows</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len([d for d in differences if d.get('type') == 'deleted'])}</div>
                <div class="summary-label">Deleted Rows</div>
            </div>
        </div>
        
        <div class="diff-section">
"""
    
    if not differences:
        html_content += '''
            <div class="no-changes">
                No changes found between the two CSV files.
            </div>
        '''
    else:
        for diff in differences:
            if diff.get('type') == 'added':
                html_content += f'''
            <div class="diff-item">
                <div class="diff-header">
                    <div class="diff-title">Row Added: {diff['row_id']}</div>
                    <div class="diff-type type-added">ADDED</div>
                </div>
                <div class="diff-content">
                    <div class="row-preview">
                        {', '.join(diff['new_row'])}
                    </div>
                </div>
            </div>
                '''
            elif diff.get('type') == 'deleted':
                html_content += f'''
            <div class="diff-item">
                <div class="diff-header">
                    <div class="diff-title">Row Deleted: {diff['row_id']}</div>
                    <div class="diff-type type-deleted">DELETED</div>
                </div>
                <div class="diff-content">
                    <div class="row-preview">
                        {', '.join(diff['old_row'])}
                    </div>
                </div>
            </div>
                '''
            else:
                # Create highlight mapping for changed columns
                old_highlight_changes = {}
                new_highlight_changes = {}
                for change in diff['changes']:
                    old_highlight_changes[change['column_index']] = 'removed'  # Yellow for old
                    new_highlight_changes[change['column_index']] = 'added'    # Green for new
                
                html_content += f'''
            <div class="diff-item">
                <div class="diff-header">
                    <div class="diff-title">Task Modified: {diff['row_id']}</div>
                    <div class="diff-type type-modified">MODIFIED</div>
                </div>
                <div class="diff-content">
                    <div class="task-comparison">
                        <div class="task-version old">
                            <div class="task-version-header">BEFORE</div>
                            {create_task_row_html(diff['old_row'], new_headers, old_highlight_changes)}
                        </div>
                        <div class="task-version new">
                            <div class="task-version-header">AFTER</div>
                            {create_task_row_html(diff['new_row'], new_headers, new_highlight_changes)}
                        </div>
                    </div>
                </div>
            </div>
                '''
    
    html_content += '''
        </div>
    </div>
</body>
</html>
'''
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python csv_diff.py <old_csv_file> <new_csv_file> [output_html]")
        print("Example: python csv_diff.py data/tasks/tasks.csv data/temp/tasks_updated.csv")
        sys.exit(1)
    
    old_csv_path = sys.argv[1]
    new_csv_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(old_csv_path):
        print(f"Error: File '{old_csv_path}' not found")
        sys.exit(1)
    
    if not os.path.exists(new_csv_path):
        print(f"Error: File '{new_csv_path}' not found")
        sys.exit(1)
    
    try:
        output_file = create_diff_html(old_csv_path, new_csv_path, output_path)
        print(f"✅ CSV diff visualization created: {output_file}")
        print(f"🌐 Open it in your browser to view the changes!")
    except Exception as e:
        print(f"❌ Error creating diff visualization: {e}")
        sys.exit(1)
