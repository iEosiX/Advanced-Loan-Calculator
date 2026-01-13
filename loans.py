import pandas as pd
import numpy as np
from numpy_financial import pmt, ipmt, ppmt, npv, irr
import warnings
warnings.filterwarnings('ignore')

def calculate_pmt(principal, rate, n_periods):
    """Calculate monthly payment for fixed-rate loan"""
    monthly_rate = rate / 100 / 12
    if monthly_rate == 0:
        return principal / n_periods
    return -pmt(monthly_rate, n_periods, principal)

def calculate_balance(principal, payment, rate, periods_paid):
    """Calculate remaining balance after n periods"""
    monthly_rate = rate / 100 / 12
    if monthly_rate == 0:
        return principal - (payment * periods_paid)
    future_value = principal * ((1 + monthly_rate) ** periods_paid)
    payment_factor = payment * (((1 + monthly_rate) ** periods_paid) - 1) / monthly_rate
    return future_value - payment_factor

def calculate_true_apr(principal, monthly_payment, term_months, fees=0):
    """Calculate true APR including fees using IRR method"""
    try:
        # Cash flows: negative initial (principal - fees), positive payments
        cash_flows = [-(principal - fees)]
        cash_flows.extend([monthly_payment] * term_months)
        
        monthly_rate = irr(cash_flows)
        if monthly_rate is None:
            return None
        
        apr = ((1 + monthly_rate) ** 12 - 1) * 100
        return round(apr, 3)
    except:
        return None

# ---------- FIXED RATE LOAN ----------
def amortization_fixed(principal, rate, years, fees=0):
    r = rate / 100 / 12
    n = years * 12
    
    # Calculate monthly payment
    if r == 0:
        payment = principal / n
    else:
        payment = -pmt(r, n, principal)
    
    balance = float(principal)
    rows = []
    
    for m in range(1, n + 1):
        interest = balance * r
        principal_paid = payment - interest
        
        if principal_paid > balance:
            principal_paid = balance
            
        balance -= principal_paid
        
        rows.append([
            m,
            round(payment, 2),
            round(interest, 2),
            round(principal_paid, 2),
            round(max(balance, 0), 2),
            rate  # Annual rate column for consistency
        ])
        
        if abs(balance) < 0.01:  # Account for floating point errors
            balance = 0
            break
    
    return pd.DataFrame(
        rows,
        columns=["Month", "Payment", "Interest", "Principal", "Balance", "Annual_Rate"]
    )

# ---------- VARIABLE RATE LOAN ----------
def amortization_variable(principal, rates_input, years):
    """Variable rate loan with ANNUAL payments and ANNUAL schedule"""
    # Parse rates input
    if isinstance(rates_input, str):
        rates_list = [float(r.strip()) for r in rates_input.split(",") if r.strip()]
    else:
        rates_list = rates_input
    
    # Validate and extend rates
    if not rates_list:
        raise ValueError("At least one rate must be provided")
    
    if len(rates_list) < years:
        rates_list.extend([rates_list[-1]] * (years - len(rates_list)))
    elif len(rates_list) > years:
        rates_list = rates_list[:years]
    
    balance = float(principal)
    rows = []
    
    for year in range(1, years + 1):
        annual_rate = rates_list[year - 1] / 100  # Convert to decimal
        remaining_years = years - year + 1
        
        # Calculate annual payment using the formula: PMT = PV * r / (1 - (1 + r)^(-n))
        if annual_rate == 0:
            annual_payment = balance / remaining_years
        else:
            annual_payment = balance * annual_rate / (1 - (1 + annual_rate) ** (-remaining_years))
        
        # Annual interest
        interest = balance * annual_rate
        
        # Annual principal
        principal_paid = annual_payment - interest
        
        # Adjust for final payment
        if year == years:
            principal_paid = balance
            annual_payment = interest + principal_paid
        
        # Update balance
        balance -= principal_paid
        
        rows.append([
            year,  # Year number
            round(annual_payment, 2),
            round(interest, 2),
            round(principal_paid, 2),
            round(max(balance, 0), 2),
            rates_list[year - 1]  # Annual rate in percentage
        ])
        
        if abs(balance) < 0.01:
            balance = 0
            break
    
    return pd.DataFrame(
        rows,
        columns=["Year", "Payment", "Interest", "Principal", "Balance", "Annual_Rate"]
    )

# ---------- INTEREST ONLY LOAN ----------
def amortization_interest_only(principal, rate, years, interest_only_years=None):
    monthly_rate = rate / 100 / 12
    balance = float(principal)
    rows = []
    
    if interest_only_years is None or interest_only_years >= years:
        # Interest-only for entire term
        for m in range(1, years * 12 + 1):
            interest = principal * monthly_rate
            payment = interest
            rows.append([
                m,
                round(payment, 2),
                round(interest, 2),
                0,
                principal,
                rate
            ])
    else:
        # Interest-only period
        for m in range(1, interest_only_years * 12 + 1):
            interest = principal * monthly_rate
            payment = interest
            rows.append([
                m,
                round(payment, 2),
                round(interest, 2),
                0,
                principal,
                rate
            ])
        
        # Amortization period
        remaining_months = (years - interest_only_years) * 12
        if remaining_months > 0:
            payment = -pmt(monthly_rate, remaining_months, principal)
            
            for i in range(1, remaining_months + 1):
                m = interest_only_years * 12 + i
                interest = balance * monthly_rate
                principal_paid = payment - interest
                
                if principal_paid > balance:
                    principal_paid = balance
                    
                balance -= principal_paid
                
                rows.append([
                    m,
                    round(payment, 2),
                    round(interest, 2),
                    round(principal_paid, 2),
                    round(max(balance, 0), 2),
                    rate
                ])
                
                if abs(balance) < 0.01:
                    balance = 0
                    break
    
    return pd.DataFrame(
        rows,
        columns=["Month", "Payment", "Interest", "Principal", "Balance", "Annual_Rate"]
    )

# ---------- BALLOON LOAN ----------
def amortization_balloon(principal, rate, years, balloon_percent):
    balloon_amount = principal * (balloon_percent / 100)
    monthly_rate = rate / 100 / 12
    total_months = years * 12
    
    # Calculate monthly payment
    if monthly_rate == 0:
        payment = (principal - balloon_amount) / total_months
    else:
        numerator = (principal * monthly_rate * ((1 + monthly_rate) ** total_months)) - (balloon_amount * monthly_rate)
        denominator = ((1 + monthly_rate) ** total_months) - 1
        payment = numerator / denominator
    
    balance = float(principal)
    rows = []
    
    for m in range(1, total_months + 1):
        interest = balance * monthly_rate
        
        if m == total_months:
            principal_paid = balance - balloon_amount
            payment = interest + principal_paid
            balance = balloon_amount
            
            rows.append([
                m,
                round(payment + balloon_amount, 2),
                round(interest, 2),
                round(principal_paid + balloon_amount, 2),
                0,
                rate
            ])
            break
        else:
            principal_paid = payment - interest
            
            if principal_paid > balance:
                principal_paid = balance
                
            balance -= principal_paid
            
            rows.append([
                m,
                round(payment, 2),
                round(interest, 2),
                round(principal_paid, 2),
                round(max(balance, 0), 2),
                rate
            ])
    
    return pd.DataFrame(
        rows,
        columns=["Month", "Payment", "Interest", "Principal", "Balance", "Annual_Rate"]
    )

# ---------- DISPATCHER ----------
def loan_dispatcher(data):
    loan_type = data.get("type", "fixed")
    principal = float(data.get("principal", 0))
    fees = float(data.get("fees", 0))
    
    if principal <= 0:
        raise ValueError("Principal must be greater than 0")
    
    if loan_type == "fixed":
        rate = float(data.get("rate", 0))
        years = int(data.get("years", 1))
        df = amortization_fixed(principal, rate, years, fees)
        
    elif loan_type == "variable":
        rates = data.get("rates", "")
        years = int(data.get("years", 1))
    
        if not rates:
            raise ValueError("Variable rates are required")
        
        df = amortization_variable(principal, rates, years)
        
    elif loan_type == "interest_only":
        rate = float(data.get("rate", 0))
        years = int(data.get("years", 1))
        interest_only_years = data.get("interest_only_years", years)
        if interest_only_years is not None:
            interest_only_years = int(interest_only_years)
        df = amortization_interest_only(principal, rate, years, interest_only_years)
        
    elif loan_type == "balloon":
        rate = float(data.get("rate", 0))
        years = int(data.get("years", 1))
        balloon_percent = float(data.get("balloon", 20))
        df = amortization_balloon(principal, rate, years, balloon_percent)
        
    else:
        raise ValueError(f"Invalid loan type: {loan_type}")
    
    # Calculate summary metrics
    total_paid = df["Payment"].sum()
    total_interest = df["Interest"].sum()
    
    # Calculate APR (true APR including fees)
    apr_percent = None
    if loan_type in ["fixed", "interest_only", "balloon"]:
        monthly_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
        apr_percent = calculate_true_apr(principal, monthly_payment, years * 12, fees) or rate
    elif loan_type == "variable":
        rates_list = [float(r.strip()) for r in rates.split(",") if r.strip()]
        if rates_list:
            weighted_avg_rate = sum(rates_list) / len(rates_list)
            apr_percent = weighted_avg_rate
        else:
            apr_percent = 0
    
    # Initialize summary
    summary = {
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "apr": round(apr_percent, 2) if apr_percent else 0,
        "total_months": len(df),
        "principal": principal,
        "fees": fees
    }
    
    # Add payment information
    if loan_type == "fixed":
        monthly_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
        summary.update({
            "monthly_payment": round(monthly_payment, 2),
            "average_payment": round(df["Payment"].mean(), 2)
        })
    
    elif loan_type == "variable":
        monthly_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
        summary.update({
            "monthly_payment": round(monthly_payment, 2),
            "average_payment": round(df["Payment"].mean(), 2)
        })
    
    elif loan_type == "interest_only":
        interest_only_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
        if data.get("interest_only_years", years) < years:
            amortizing_payment = df["Payment"].iloc[int(data.get("interest_only_years", years) * 12)] if len(df) > int(data.get("interest_only_years", years) * 12) else 0
            summary.update({
                "interest_only_payment": round(interest_only_payment, 2),
                "amortizing_payment": round(amortizing_payment, 2) if amortizing_payment > 0 else 0
            })
        else:
            summary["interest_only_payment"] = round(interest_only_payment, 2)
    
    elif loan_type == "balloon":
        monthly_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
        balloon_amount = principal * (float(data.get("balloon", 20)) / 100)
        summary.update({
            "monthly_payment": round(monthly_payment, 2),
            "balloon_payment": round(balloon_amount, 2),
            "average_payment": round(df["Payment"].mean(), 2)
        })
    
    return df, summary