import io
import pandas as pd
from datetime import datetime

def generate_html_report(loan_data, schedule, summary):
    """Generate HTML report without external libraries"""
    
    # Create HTML string
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Loan Amortization Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #3498db;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .section {{
                margin: 30px 0;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .loan-details, .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .detail-item {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }}
            .detail-label {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 14px;
                margin-bottom: 5px;
            }}
            .detail-value {{
                font-size: 18px;
                color: #2c3e50;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            .highlight {{
                background-color: #fffacd;
            }}
            .positive {{
                color: #27ae60;
                font-weight: bold;
            }}
            .negative {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Loan Amortization Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Loan Details</h2>
            <div class="loan-details">
    """
    
    # Add loan details
    details = [
        ("Loan Amount", f"${loan_data.get('principal', 0):,.2f}"),
        ("Interest Rate", f"{loan_data.get('rate', 0)}%"),
        ("Loan Term", f"{loan_data.get('years', 0)} years"),
        ("Loan Type", loan_data.get('type', 'fixed').title()),
        ("Start Date", loan_data.get('start_date', datetime.now().strftime('%Y-%m-%d')))
    ]
    
    for label, value in details:
        html += f"""
                <div class="detail-item">
                    <div class="detail-label">{label}</div>
                    <div class="detail-value">{value}</div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>Payment Summary</h2>
            <div class="summary">
    """
    
    # Add summary details
    summary_items = [
        ("Total Paid", f"${summary.get('total_paid', 0):,.2f}"),
        ("Total Interest", f"${summary.get('total_interest', 0):,.2f}"),
        ("APR", f"{summary.get('apr', 0)}%"),
        ("Term", f"{summary.get('total_months', 0)} months")
    ]
    
    if 'monthly_payment' in summary:
        summary_items.insert(0, ("Monthly Payment", f"${summary.get('monthly_payment', 0):,.2f}"))
    
    for label, value in summary_items:
        html += f"""
                <div class="detail-item">
                    <div class="detail-label">{label}</div>
                    <div class="detail-value">{value}</div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>Amortization Schedule (First 12 Months)</h2>
    """
    
    # Add table
    if schedule and len(schedule) > 0:
        html += """
            <table>
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Payment</th>
                        <th>Interest</th>
                        <th>Principal</th>
                        <th>Balance</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, row in enumerate(schedule[:12]):
            html += f"""
                    <tr>
                        <td>{row.get('Month', i+1)}</td>
                        <td>${row.get('Payment', 0):,.2f}</td>
                        <td>${row.get('Interest', 0):,.2f}</td>
                        <td>${row.get('Principal', 0):,.2f}</td>
                        <td>${row.get('Balance', 0):,.2f}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        """
        
        if len(schedule) > 12:
            html += f"""
            <p><em>Showing first 12 of {len(schedule)} payments. Full schedule available in CSV export.</em></p>
            """
    
    # Add key metrics
    html += """
        <div class="section">
            <h2>Key Financial Metrics</h2>
    """
    
    if schedule and len(schedule) > 0:
        # Calculate metrics
        total_interest = sum(row.get('Interest', 0) for row in schedule)
        total_principal = sum(row.get('Principal', 0) for row in schedule)
        interest_ratio = (total_interest / (total_interest + total_principal) * 100) if (total_interest + total_principal) > 0 else 0
        
        first_year_interest = sum(row.get('Interest', 0) for row in schedule[:12])
        first_year_principal = sum(row.get('Principal', 0) for row in schedule[:12])
        
        metrics = [
            ("Interest to Principal Ratio", f"{interest_ratio:.1f}%", "Lower is better"),
            ("Average Monthly Interest", f"${total_interest/len(schedule):,.2f}", "Declines over time"),
            ("First Year Interest", f"${first_year_interest:,.2f}", "Tax deductible (may apply)"),
            ("First Year Principal", f"${first_year_principal:,.2f}", "Builds equity")
        ]
        
        html += """
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Interpretation</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for label, value, interpretation in metrics:
            html += f"""
                    <tr>
                        <td>{label}</td>
                        <td>{value}</td>
                        <td>{interpretation}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        """
    
    # Add disclaimer
    html += """
        <div class="footer">
            <p>This report is for informational purposes only. Consult with a financial advisor for personalized advice.</p>
            <p>Rates and terms may vary. All calculations are estimates.</p>
            <p>Report generated by Advanced Loan Calculator</p>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_text_report(loan_data, schedule, summary):
    """Generate plain text report"""
    
    text = f"""
LOAN AMORTIZATION REPORT
=======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

LOAN DETAILS
------------
Loan Amount: ${loan_data.get('principal', 0):,.2f}
Interest Rate: {loan_data.get('rate', 0)}%
Loan Term: {loan_data.get('years', 0)} years
Loan Type: {loan_data.get('type', 'fixed').title()}
Start Date: {loan_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))}

PAYMENT SUMMARY
---------------
"""
    
    # Add summary items
    if 'monthly_payment' in summary:
        text += f"Monthly Payment: ${summary.get('monthly_payment', 0):,.2f}\n"
    
    text += f"""Total Paid: ${summary.get('total_paid', 0):,.2f}
Total Interest: ${summary.get('total_interest', 0):,.2f}
APR: {summary.get('apr', 0)}%
Term: {summary.get('total_months', 0)} months

AMORTIZATION SCHEDULE (First 12 Months)
--------------------------------------
Month  Payment      Interest    Principal   Balance
-----  -----------  ----------  ----------  -----------
"""
    
    # Add schedule data
    for i, row in enumerate(schedule[:12]):
        month = row.get('Month', i+1)
        payment = row.get('Payment', 0)
        interest = row.get('Interest', 0)
        principal = row.get('Principal', 0)
        balance = row.get('Balance', 0)
        
        text += f"{month:5d}  ${payment:10,.2f}  ${interest:10,.2f}  ${principal:10,.2f}  ${balance:12,.2f}\n"
    
    if len(schedule) > 12:
        text += f"\n... showing first 12 of {len(schedule)} payments\n"
    
    # Add key metrics
    if schedule and len(schedule) > 0:
        total_interest = sum(row.get('Interest', 0) for row in schedule)
        total_principal = sum(row.get('Principal', 0) for row in schedule)
        interest_ratio = (total_interest / (total_interest + total_principal) * 100) if (total_interest + total_principal) > 0 else 0
        
        first_year_interest = sum(row.get('Interest', 0) for row in schedule[:12])
        first_year_principal = sum(row.get('Principal', 0) for row in schedule[:12])
        
        text += f"""
KEY FINANCIAL METRICS
---------------------
Interest to Principal Ratio: {interest_ratio:.1f}%
Average Monthly Interest: ${total_interest/len(schedule):,.2f}
First Year Interest: ${first_year_interest:,.2f}
First Year Principal: ${first_year_principal:,.2f}

NOTES
-----
- This report is for informational purposes only.
- Consult with a financial advisor for personalized advice.
- Rates and terms may vary.
- All calculations are estimates.

Report generated by Advanced Loan Calculator
"""
    
    return text

def generate_csv_report(loan_data, schedule, summary):
    """Generate CSV report - simple wrapper for DataFrame"""
    df = pd.DataFrame(schedule)
    
    # Add summary information as a separate DataFrame
    summary_df = pd.DataFrame([{
        'Loan Amount': loan_data.get('principal', 0),
        'Interest Rate': loan_data.get('rate', 0),
        'Term Years': loan_data.get('years', 0),
        'Total Paid': summary.get('total_paid', 0),
        'Total Interest': summary.get('total_interest', 0),
        'APR': summary.get('apr', 0)
    }])
    
    return df, summary_df