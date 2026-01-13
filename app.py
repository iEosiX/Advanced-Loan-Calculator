from flask import Flask, render_template, request, jsonify, send_file
from loans import loan_dispatcher, calculate_true_apr
from analysis import (
    compare_loans,
    sensitivity_analysis,
    affordability,
    refinancing,
    tax_implications
)
from prepayment import prepayment_scenarios
from documentation import generate_html_report, generate_text_report
import pandas as pd
import io
import traceback
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json
        
        # Handle missing or invalid data
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        df, summary = loan_dispatcher(data)
        
        # For variable rate loans, we need different visualization data
        if data.get("type") == "variable":
            visualization_data = generate_annual_visualization_data(df)
        else:
            visualization_data = generate_visualization_data(df)
        
        return jsonify({
            "summary": summary,
            "schedule": df.to_dict(orient="records"),
            "visualization": visualization_data,
            "loan_type": data.get("type", "fixed")  # Add loan type to response
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 400

@app.route("/compare", methods=["POST"])
def compare():
    try:
        return jsonify(compare_loans(request.json["offers"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/sensitivity", methods=["POST"])
def sensitivity():
    try:
        return jsonify(sensitivity_analysis(request.json))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/affordability", methods=["POST"])
def affordability_api():
    try:
        return jsonify(affordability(request.json))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/refinance", methods=["POST"])
def refinance():
    try:
        return jsonify(refinancing(request.json))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/tax", methods=["POST"])
def tax():
    try:
        return jsonify(tax_implications(request.json))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/prepayment", methods=["POST"])
def prepayment():
    try:
        data = request.json
        result = prepayment_scenarios(
            data.get("principal", 100000),
            data.get("rate", 5),
            data.get("years", 30),
            data.get("prepayment_amount", 0),
            data.get("prepayment_start", 1),
            data.get("prepayment_frequency", "monthly")
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/export", methods=["POST"])
def export_csv():
    try:
        data = request.json.get("data", [])
        if not data:
            return jsonify({"error": "No data to export"}), 400
            
        df = pd.DataFrame(data)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="amortization_schedule.csv"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/export/html", methods=["POST"])
def export_html():
    try:
        data = request.json
        schedule = data.get("schedule", [])
        summary = data.get("summary", {})
        loan_data = data.get("loan_data", {})
        
        if not schedule:
            return jsonify({"error": "No data to export"}), 400
            
        html_report = generate_html_report(loan_data, schedule, summary)
        
        return send_file(
            io.BytesIO(html_report.encode()),
            mimetype="text/html",
            as_attachment=True,
            download_name="loan_report.html"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/export/text", methods=["POST"])
def export_text():
    try:
        data = request.json
        schedule = data.get("schedule", [])
        summary = data.get("summary", {})
        loan_data = data.get("loan_data", {})
        
        if not schedule:
            return jsonify({"error": "No data to export"}), 400
            
        text_report = generate_text_report(loan_data, schedule, summary)
        
        return send_file(
            io.BytesIO(text_report.encode()),
            mimetype="text/plain",
            as_attachment=True,
            download_name="loan_report.txt"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/calculate/apr", methods=["POST"])
def calculate_apr():
    try:
        data = request.json
        principal = data.get("principal", 0)
        rate = data.get("rate", 0)
        years = data.get("years", 0)
        fees = data.get("fees", 0)
        
        if not principal or not years:
            return jsonify({"error": "Missing required parameters"}), 400
            
        df = loan_dispatcher({"type": "fixed", "principal": principal, "rate": rate, "years": years})[0]
        monthly_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
        
        apr = calculate_true_apr(principal, monthly_payment, years * 12, fees)
        
        return jsonify({
            "nominal_rate": rate,
            "apr": apr,
            "monthly_payment": monthly_payment,
            "fees_impact": round(apr - rate, 3) if apr else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def generate_visualization_data(df):
    """Generate simple visualization data without matplotlib"""
    if df.empty:
        return {}
    

    # Check if this is annual data (variable rate) or monthly data
    if 'Year' in df.columns:
        # This is annual data (variable rate loan)
        return generate_annual_visualization_data(df)
    
    
    # Generate data points for simple charts
    months = df['Month'].tolist()
    balances = df['Balance'].tolist()
    interests = df['Interest'].tolist()
    principals = df['Principal'].tolist()
    
    # Summary statistics for visualization
    total_interest = sum(interests)
    total_principal = sum(principals)
    
    # Calculate cumulative data
    cumulative_interest = []
    cumulative_principal = []
    ci = 0
    cp = 0
    
    for i, p in zip(interests, principals):
        ci += i
        cp += p
        cumulative_interest.append(ci)
        cumulative_principal.append(cp)
    
    # Yearly summary
    yearly_data = []
    for year in range(1, (len(months) // 12) + 2):
        start_idx = (year - 1) * 12
        end_idx = min(year * 12, len(months))
        
        if start_idx < len(months):
            year_interest = sum(interests[start_idx:end_idx])
            year_principal = sum(principals[start_idx:end_idx])
            year_end_balance = balances[min(end_idx, len(balances)-1)]
            
            yearly_data.append({
                "year": year,
                "interest": year_interest,
                "principal": year_principal,
                "balance": year_end_balance
            })
    
    return {
        "monthly_data": {
            "months": months[:60],  # First 60 months
            "balances": balances[:60],
            "interests": interests[:60],
            "principals": principals[:60]
        },
        "cumulative_data": {
            "months": months[:60],
            "cumulative_interest": cumulative_interest[:60],
            "cumulative_principal": cumulative_principal[:60]
        },
        "yearly_data": yearly_data,
        "totals": {
            "total_interest": total_interest,
            "total_principal": total_principal,
            "interest_ratio": total_interest / (total_interest + total_principal) * 100
        }
    }

def generate_annual_visualization_data(df):
    """Generate visualization data for annual loan schedule"""
    if df.empty:
        return {}
    
    # For variable rate loans, we already have annual data
    years = df['Year'].tolist()
    balances = df['Balance'].tolist()
    interests = df['Interest'].tolist()
    principals = df['Principal'].tolist()
    payments = df['Payment'].tolist()
    rates = df['Annual_Rate'].tolist()
    
    # Calculate cumulative data
    cumulative_interest = []
    cumulative_principal = []
    ci = 0
    cp = 0
    
    for i, p in zip(interests, principals):
        ci += i
        cp += p
        cumulative_interest.append(ci)
        cumulative_principal.append(cp)
    
    # Calculate totals
    total_interest = sum(interests)
    total_principal = sum(principals)
    total_paid = sum(payments)
    
    return {
        "annual_data": {
            "years": years,
            "balances": balances,
            "interests": interests,
            "principals": principals,
            "payments": payments,
            "rates": rates
        },
        "cumulative_data": {
            "years": years,
            "cumulative_interest": cumulative_interest,
            "cumulative_principal": cumulative_principal
        },
        "totals": {
            "total_interest": total_interest,
            "total_principal": total_principal,
            "total_paid": total_paid,
            "interest_ratio": total_interest / total_paid * 100 if total_paid > 0 else 0
        }
    }

if __name__ == "__main__":
    app.run(debug=True, port=5001)