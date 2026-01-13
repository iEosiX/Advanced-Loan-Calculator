def generate_text_chart(data, width=50, height=20):
    """Generate ASCII art chart for terminal display"""
    
    if not data or 'months' not in data or 'balances' not in data:
        return "No data available for chart"
    
    months = data['months']
    balances = data['balances']
    
    if len(months) == 0 or len(balances) == 0:
        return "No data available for chart"
    
    # Find min and max values
    min_balance = min(balances)
    max_balance = max(balances)
    
    # Scale data to chart height
    scaled_data = []
    for balance in balances:
        if max_balance - min_balance > 0:
            scaled = int((balance - min_balance) / (max_balance - min_balance) * (height - 1))
        else:
            scaled = height // 2
        scaled_data.append(scaled)
    
    # Create chart
    chart_lines = []
    
    # Y-axis labels
    for i in range(height - 1, -1, -1):
        line = f"${(min_balance + (i / (height - 1)) * (max_balance - min_balance)):,.0f} "
        
        # Add chart points
        for j, scaled in enumerate(scaled_data):
            if j >= width:  # Limit width
                break
            
            if scaled == i:
                line += "●"
            elif i == 0:  # X-axis
                line += "─"
            else:
                line += " "
        
        chart_lines.append(line)
    
    # Add X-axis labels
    month_labels = ""
    for j in range(min(width, len(months))):
        if months[j] in [1, len(months)] or j == 0 or j == width - 1:
            month_labels += str(months[j])
        else:
            month_labels += " "
    
    chart_lines.append(" " * 8 + month_labels)
    chart_lines.append(" " * 8 + "Month")
    
    return "\n".join(chart_lines)

def generate_simple_visualization(visualization_data):
    """Generate simple HTML/CSS visualization for web display"""
    
    if not visualization_data:
        return "<p>No visualization data available</p>"
    
    html = """
    <div class="simple-visualization">
        <h4>Loan Balance Over Time</h4>
        <div class="chart-container">
    """
    
    # Create a simple bar chart using HTML/CSS
    if 'monthly_data' in visualization_data:
        months = visualization_data['monthly_data']['months']
        balances = visualization_data['monthly_data']['balances']
        
        if len(months) > 0 and len(balances) > 0:
            max_balance = max(balances)
            
            html += '<div class="bar-chart">'
            for i, (month, balance) in enumerate(zip(months[:24], balances[:24])):  # Show first 24 months
                height = (balance / max_balance * 100) if max_balance > 0 else 0
                html += f"""
                <div class="bar-container">
                    <div class="bar" style="height: {height}%" title="Month {month}: ${balance:,.0f}"></div>
                    <div class="bar-label">{month}</div>
                </div>
                """
            html += '</div>'
    
    html += """
        </div>
        
        <div class="summary-stats">
    """
    
    # Add summary statistics
    if 'totals' in visualization_data:
        totals = visualization_data['totals']
        html += f"""
            <div class="stat">
                <div class="stat-label">Total Interest</div>
                <div class="stat-value">${totals.get('total_interest', 0):,.2f}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Interest Ratio</div>
                <div class="stat-value">{totals.get('interest_ratio', 0):.1f}%</div>
            </div>
        """
    
    html += """
        </div>
    </div>
    
    <style>
    .simple-visualization {
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .chart-container {
        overflow-x: auto;
        margin: 20px 0;
    }
    .bar-chart {
        display: flex;
        align-items: flex-end;
        height: 200px;
        padding: 10px;
        background: white;
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    .bar-container {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100%;
        margin: 0 2px;
    }
    .bar {
        width: 80%;
        background: linear-gradient(to top, #3498db, #2980b9);
        border-radius: 3px 3px 0 0;
        transition: height 0.3s;
    }
    .bar:hover {
        background: linear-gradient(to top, #2980b9, #1c5a7a);
    }
    .bar-label {
        margin-top: 5px;
        font-size: 11px;
        color: #666;
    }
    .summary-stats {
        display: flex;
        gap: 20px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    .stat {
        flex: 1;
        min-width: 150px;
        padding: 15px;
        background: white;
        border-radius: 6px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .stat-label {
        font-size: 12px;
        color: #666;
        margin-bottom: 5px;
    }
    .stat-value {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
    """
    
    return html

def generate_year_summary_table(yearly_data):
    """Generate HTML table for yearly summary"""
    
    if not yearly_data or len(yearly_data) == 0:
        return "<p>No yearly data available</p>"
    
    html = """
    <table class="yearly-summary">
        <thead>
            <tr>
                <th>Year</th>
                <th>Interest Paid</th>
                <th>Principal Paid</th>
                <th>Year-End Balance</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for year_data in yearly_data:
        html += f"""
            <tr>
                <td>{year_data['year']}</td>
                <td>${year_data['interest']:,.2f}</td>
                <td>${year_data['principal']:,.2f}</td>
                <td>${year_data['balance']:,.2f}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    
    <style>
    .yearly-summary {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .yearly-summary th {
        background: #3498db;
        color: white;
        padding: 10px;
        text-align: left;
    }
    .yearly-summary td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    .yearly-summary tr:nth-child(even) {
        background: #f8f9fa;
    }
    </style>
    """
    
    return html