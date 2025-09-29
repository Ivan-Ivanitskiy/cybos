#!/usr/bin/env python3
"""
Beautiful CSV Preview Generator
Creates an HTML file with a styled table from CSV data
Organizes tasks by: Today, This Week, All Tasks
"""

import csv
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import locale

def parse_date(date_str):
    """Parse date string in DD.MM.YYYY format"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str.strip(), '%d.%m.%Y')
    except ValueError:
        return None

def categorize_tasks(data, headers):
    """Categorize tasks into today, this week, and other tasks"""
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    # Find date column index
    date_col_idx = None
    for i, header in enumerate(headers):
        if 'due' in header.lower() or 'date' in header.lower():
            date_col_idx = i
            break
    
    today_tasks = []
    week_tasks = []
    other_tasks = []
    today_task_ids = set()
    week_task_ids = set()
    
    for row in data:
        if not row or not row[0]:  # Skip rows without ID
            continue
            
        task_id = row[0]
        
        if date_col_idx is not None and date_col_idx < len(row):
            task_date = parse_date(row[date_col_idx])
            if task_date:
                task_date_only = task_date.date()
                if task_date_only == today:
                    today_tasks.append(row)
                    today_task_ids.add(task_id)
                elif today <= task_date_only <= week_end:
                    week_tasks.append(row)
                    week_task_ids.add(task_id)
        
        # Add to other tasks if not in today or this week
        if task_id not in today_task_ids and task_id not in week_task_ids:
            other_tasks.append(row)
    
    return today_tasks, week_tasks, other_tasks

def create_html_preview(csv_path, output_path=None):
    """Create a beautiful HTML preview of a CSV file"""
    
    if output_path is None:
        output_path = csv_path.replace('.csv', '_preview.html')
    
    # Read CSV data
    data = []
    headers = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        data = list(reader)
    
    # Categorize tasks
    today_tasks, week_tasks, other_tasks = categorize_tasks(data, headers)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Preview - {os.path.basename(csv_path)}</title>
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
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-header {{
            background: #3a3a3a;
            color: #e0e0e0;
            padding: 10px 15px;
            font-size: 16px;
            font-weight: 600;
            border: 2px solid #404040;
            border-bottom: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .section-content {{
            border: 2px solid #404040;
            border-top: none;
            background: #2d2d2d;
        }}
        
        .table-container {{
            overflow-x: auto;
            padding: 15px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        th {{
            background: #3a3a3a;
            color: #e0e0e0;
            font-weight: 600;
            padding: 8px 6px;
            text-align: left;
            border-bottom: 2px solid #404040;
            border-right: 1px solid #404040;
            position: sticky;
            top: 0;
            font-size: 13px;
        }}
        
        td {{
            padding: 8px 6px;
            border-bottom: 1px solid #404040;
            border-right: 1px solid #404040;
            vertical-align: top;
            color: #e0e0e0;
        }}
        
        tr:hover {{
            background-color: #3a3a3a;
        }}
        
        .status-done {{
            background-color: #28a745;
            color: #ffffff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
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
        
        .tag {{
            display: inline-block;
            background: #4a90e2;
            color: #ffffff;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin: 1px;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            background: #2d2d2d;
            padding: 12px;
            border-top: 2px solid #404040;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 20px;
            font-weight: bold;
            color: #e0e0e0;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .empty-section {{
            padding: 30px;
            text-align: center;
            color: #a0a0a0;
            font-style: italic;
        }}
        
        .section-count {{
            background: #404040;
            color: #e0e0e0;
            padding: 3px 6px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        .editable {{
            background: transparent;
            border: 1px solid transparent;
            color: inherit;
            padding: 2px 4px;
            border-radius: 3px;
            width: 100%;
            font-family: inherit;
            font-size: inherit;
        }}
        
        .editable:hover {{
            border-color: #4a90e2;
            background: rgba(74, 144, 226, 0.1);
        }}
        
        .editable:focus {{
            border-color: #4a90e2;
            background: rgba(74, 144, 226, 0.1);
            outline: none;
        }}
        
        .controls {{
            padding: 15px;
            background: #2d2d2d;
            border-top: 2px solid #404040;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .btn {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .btn:hover {{
            background: #5a6268;
        }}
        
        .btn:disabled {{
            background: #666;
            cursor: not-allowed;
        }}
        
        .status {{
            color: #a0a0a0;
            font-size: 14px;
        }}
        
        .status.success {{
            color: #28a745;
        }}
        
        .status.error {{
            color: #dc3545;
        }}
    </style>
    <script>
        let originalData = [];
        let headers = [];
        
        function initializeData() {{
            // Store original data structure
            headers = Array.from(document.querySelectorAll('th')).map(th => th.textContent);
            const rows = document.querySelectorAll('tbody tr');
            originalData = Array.from(rows).map(row => {{
                const cells = Array.from(row.querySelectorAll('td'));
                return cells.map(cell => {{
                    const input = cell.querySelector('input');
                    return input ? input.value : cell.textContent.trim();
                }});
            }});
        }}
        
        function makeEditable() {{
            const cells = document.querySelectorAll('td');
            cells.forEach(cell => {{
                if (!cell.querySelector('input')) {{
                    // Get the original text content, handling both plain text and formatted tags
                    let text = '';
                    if (cell.querySelector('.tag')) {{
                        // If it has formatted tags, extract the tag text
                        const tags = Array.from(cell.querySelectorAll('.tag')).map(tag => tag.textContent);
                        text = tags.join(', ');
                    }} else if (cell.querySelector('.status-done')) {{
                        // If it's a status-done element, get the original value
                        text = 'done';
                    }} else {{
                        text = cell.textContent.trim();
                    }}
                    
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = text;
                    input.className = 'editable';
                    cell.innerHTML = '';
                    cell.appendChild(input);
                }}
            }});
        }}
        
        function updateData() {{
            const rows = document.querySelectorAll('tbody tr');
            originalData = Array.from(rows).map(row => {{
                const cells = Array.from(row.querySelectorAll('td'));
                return cells.map(cell => {{
                    const input = cell.querySelector('input');
                    return input ? input.value : cell.textContent.trim();
                }});
            }});
        }}
        
        function downloadCSV() {{
            // Start with just the header once - use original headers
            const originalHeaders = ['ID', 'Task', 'Tag', 'Due date', 'Deadline', 'Recurring', 'Priority', 'Depends on', 'Status'];
            let csvContent = originalHeaders.join(',') + '\\n';
            
            // Get all data rows (not header rows) from all sections
            const allRows = [];
            const seenIds = new Set();
            
            // Get all tbody rows from all sections
            const allTbodyRows = document.querySelectorAll('tbody tr');
            
            allTbodyRows.forEach(row => {{
                const cells = Array.from(row.querySelectorAll('td'));
                
                // Skip if no cells or if first cell looks like a header
                if (cells.length === 0) return;
                
                const firstCellText = cells[0].textContent.trim();
                
                // Skip header rows - check if first cell contains header text
                if (firstCellText === 'ID' || firstCellText === 'Task' || firstCellText.includes('ID') || firstCellText.includes('Task')) {{
                    return;
                }}
                
                // Skip if first cell is not a valid ID (should be numeric)
                if (!firstCellText.match(/^\\d+$/)) {{
                    return;
                }}
                
                const rowData = cells.map(cell => {{
                    const input = cell.querySelector('input');
                    if (input) {{
                        return input.value;
                    }} else {{
                        // Handle formatted content
                        if (cell.querySelector('.tag')) {{
                            const tags = Array.from(cell.querySelectorAll('.tag')).map(tag => tag.textContent);
                            return tags.join(', ');
                        }} else if (cell.querySelector('.status-done')) {{
                            return 'done';
                        }} else {{
                            return cell.textContent.trim();
                        }}
                    }}
                }});
                
                // Only add if we have a valid ID and haven't seen it before
                if (rowData[0] && rowData[0] !== '' && !seenIds.has(rowData[0])) {{
                    allRows.push(rowData);
                    seenIds.add(rowData[0]);
                }}
            }});
            
            // Sort by ID
            allRows.sort((a, b) => {{
                const idA = parseInt(a[0]) || 0;
                const idB = parseInt(b[0]) || 0;
                return idA - idB;
            }});
            
            // Add rows to CSV
            allRows.forEach(row => {{
                const escapedRow = row.map(cell => {{
                    if (cell.includes(',') || cell.includes('"') || cell.includes('\\n') || cell.includes('\\r')) {{
                        return '"' + cell.replace(/"/g, '""') + '"';
                    }}
                    return cell;
                }});
                csvContent += escapedRow.join(',') + '\\n';
            }});
            
            // Create and download blob
            const blob = new Blob([csvContent], {{ 
                type: 'text/csv;charset=utf-8;',
                endings: 'native'
            }});
            
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'tasks_updated.csv';
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            setTimeout(() => {{
                URL.revokeObjectURL(url);
            }}, 100);
            
            const status = document.querySelector('.status');
            status.textContent = 'CSV file downloaded successfully!';
            status.className = 'status success';
            setTimeout(() => {{
                status.textContent = 'Ready';
                status.className = 'status';
            }}, 3000);
        }}
        
        function resetData() {{
            // Reset all inputs to original values
            const cells = document.querySelectorAll('td');
            cells.forEach((cell, index) => {{
                const input = cell.querySelector('input');
                if (input) {{
                    const rowIndex = Math.floor(index / headers.length);
                    const colIndex = index % headers.length;
                    if (originalData[rowIndex] && originalData[rowIndex][colIndex]) {{
                        input.value = originalData[rowIndex][colIndex];
                    }}
                }}
            }});
            
            const status = document.querySelector('.status');
            status.textContent = 'Data reset to original values';
            status.className = 'status';
            setTimeout(() => {{
                status.textContent = 'Ready';
                status.className = 'status';
            }}, 2000);
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            initializeData();
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Task Management Dashboard</h1>
            <p>{os.path.basename(csv_path)} • {len(data)} tasks</p>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="makeEditable()">Edit Tasks</button>
            <button class="btn" onclick="downloadCSV()">Download CSV</button>
            <button class="btn" onclick="resetData()">Reset Changes</button>
            <span class="status">Ready</span>
        </div>
        
        <div style="padding: 20px;">
"""
    
    def format_cell(cell, header):
        """Format a cell with appropriate styling"""
        cell_class = ""
        if header.lower() == "status" and cell.lower() == "done":
            return f'<span class="status-done">✓ Done</span>'
        elif header.lower() == "priority":
            if cell.lower() == "high":
                cell_class = "priority-high"
            elif cell.lower() == "med":
                cell_class = "priority-med"
            elif cell.lower() == "low":
                cell_class = "priority-low"
        elif header.lower() == "tag" and cell:
            # Split tags and format them
            tags = [tag.strip() for tag in cell.split(',')]
            return ''.join(f'<span class="tag">{tag}</span>' for tag in tags)
        
        return f'<span class="{cell_class}">{cell}</span>'
    
    def create_table_section(tasks, section_title, icon):
        """Create a table section for a specific set of tasks"""
        if not tasks:
            return f'''
            <div class="section">
                <div class="section-header">
                    <span>{icon}</span>
                    <span>{section_title}</span>
                    <span class="section-count">0</span>
                </div>
                <div class="section-content">
                    <div class="empty-section">
                        No tasks found for this period
                    </div>
                </div>
            </div>
            '''
        
        table_html = f'''
            <div class="section">
                <div class="section-header">
                    <span>{icon}</span>
                    <span>{section_title}</span>
                    <span class="section-count">{len(tasks)}</span>
                </div>
                <div class="section-content">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    {''.join(f'<th>{header}</th>' for header in headers)}
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        for row in tasks:
            table_html += "                                <tr>\n"
            for i, cell in enumerate(row):
                formatted_cell = format_cell(cell, headers[i])
                table_html += f"                                    <td>{formatted_cell}</td>\n"
            table_html += "                                </tr>\n"
        
        table_html += '''
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        '''
        return table_html
    
    # Add sections
    html_content += create_table_section(today_tasks, "Tasks for Today", "")
    html_content += create_table_section(week_tasks, "Tasks This Week", "")
    html_content += create_table_section(other_tasks, "Other Tasks", "")
    
    # Calculate stats
    total_tasks = len(data)
    done_tasks = len([row for row in data if row[-1].lower() == 'done'])
    high_priority = len([row for row in data if 'high' in str(row).lower()])
    
    html_content += f'''
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{total_tasks}</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            <div class="stat">
                <div class="stat-number">{done_tasks}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat">
                <div class="stat-number">{high_priority}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat">
                <div class="stat-number">{total_tasks - done_tasks}</div>
                <div class="stat-label">Remaining</div>
            </div>
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
    if len(sys.argv) < 2:
        print("Usage: python csv_preview.py <csv_file> [output_html]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found")
        sys.exit(1)
    
    try:
        output_file = create_html_preview(csv_path, output_path)
        print(f"✅ Beautiful HTML preview created: {output_file}")
        print(f"🌐 Open it in your browser to view the styled table!")
    except Exception as e:
        print(f"❌ Error creating preview: {e}")
        sys.exit(1)

