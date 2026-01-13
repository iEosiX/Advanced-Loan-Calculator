from loans import amortization_fixed, calculate_balance
import numpy as np

def compare_loans(offers):
    """Compare multiple loan offers"""
    results = []
    for offer in offers:
        try:
            df = amortization_fixed(
                offer.get("principal", 100000),
                offer.get("rate", 5),
                offer.get("years", 30)
            )
            
            # Calculate APR with fees
            monthly_payment = df["Payment"].iloc[0] if len(df) > 0 else 0
            apr = offer.get("rate", 5)  # Simplified, could use true APR
            
            results.append({
                "name": offer.get("name", "Unnamed"),
                "monthly_payment": round(monthly_payment, 2),
                "total_interest": round(df["Interest"].sum(), 2),
                "total_cost": round(df["Payment"].sum(), 2),
                "apr": round(apr, 2),
                "term_years": offer.get("years", 30),
                "principal": offer.get("principal", 100000)
            })
        except Exception as e:
            results.append({
                "name": offer.get("name", "Unnamed"),
                "error": str(e)
            })
    
    # Sort by total cost (ascending)
    results = sorted(results, key=lambda x: x.get('total_cost', float('inf')) if 'total_cost' in x else float('inf'))
    
    # Add ranking
    for i, result in enumerate(results):
        if 'error' not in result:
            result['rank'] = i + 1
    
    return results

def sensitivity_analysis(data):
    """Analyze sensitivity to rate changes"""
    base_rate = data.get("rate", 5)
    principal = data.get("principal", 100000)
    years = data.get("years", 30)
    
    results = []
    base_df = amortization_fixed(principal, base_rate, years)
    base_payment = base_df["Payment"].iloc[0]
    base_total_interest = base_df["Interest"].sum()
    
    rate_changes = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
    
    for delta in rate_changes:
        test_rate = base_rate + delta
        if test_rate < 0.1:
            test_rate = 0.1
            
        df = amortization_fixed(principal, test_rate, years)
        test_payment = df["Payment"].iloc[0]
        test_total_interest = df["Interest"].sum()
        
        payment_change = test_payment - base_payment
        payment_change_pct = ((test_payment / base_payment - 1) * 100) if base_payment > 0 else 0
        interest_change = test_total_interest - base_total_interest
        
        results.append({
            "rate": round(test_rate, 2),
            "monthly_payment": round(test_payment, 2),
            "total_interest": round(test_total_interest, 2),
            "total_cost": round(df["Payment"].sum(), 2),
            "payment_change": round(payment_change, 2),
            "payment_change_pct": round(payment_change_pct, 2),
            "interest_change": round(interest_change, 2)
        })
    
    return results

def affordability(data):
    """Calculate debt-to-income ratio and affordability"""
    monthly_income = data.get("income", 5000)
    monthly_debts = data.get("debts", 500)
    proposed_payment = data.get("payment", 1000)
    housing_ratio = data.get("housing_ratio", 28)
    total_ratio = data.get("total_ratio", 36)
    
    front_end_ratio = (proposed_payment / monthly_income) * 100
    back_end_ratio = ((monthly_debts + proposed_payment) / monthly_income) * 100
    
    max_by_front = monthly_income * housing_ratio / 100
    max_by_back = monthly_income * total_ratio / 100 - monthly_debts
    
    affordable = front_end_ratio <= housing_ratio and back_end_ratio <= total_ratio
    
    recommendation = ""
    if not affordable:
        if front_end_ratio > housing_ratio:
            recommendation += f"Reduce housing payment to ${max_by_front:.2f} or less. "
        if back_end_ratio > total_ratio:
            recommendation += f"Reduce total debt payment to ${max_by_back:.2f} or less."
    else:
        recommendation = "Loan is affordable based on standard ratios."
    
    return {
        "front_end_ratio": round(front_end_ratio, 2),
        "back_end_ratio": round(back_end_ratio, 2),
        "affordable_front": front_end_ratio <= housing_ratio,
        "affordable_back": back_end_ratio <= total_ratio,
        "max_affordable_payment": round(min(max_by_front, max_by_back), 2),
        "affordable": affordable,
        "recommendation": recommendation.strip()
    }

def refinancing(data):
    """Analyze refinancing options"""
    old_principal = data.get("remaining_balance", 100000)
    old_rate = data.get("old_rate", 5)
    old_years = data.get("remaining_years", 25)
    new_rate = data.get("new_rate", 4)
    new_years = data.get("new_years", 30)
    closing_costs = data.get("closing_costs", 3000)
    roll_costs = data.get("roll_costs", False)
    
    old_df = amortization_fixed(old_principal, old_rate, old_years)
    
    # If rolling costs into loan
    if roll_costs:
        new_principal = old_principal + closing_costs
    else:
        new_principal = old_principal
    
    new_df = amortization_fixed(new_principal, new_rate, new_years)
    
    old_monthly = old_df["Payment"].iloc[0]
    new_monthly = new_df["Payment"].iloc[0]
    monthly_savings = old_monthly - new_monthly
    
    if monthly_savings > 0:
        break_even_months = closing_costs / monthly_savings
    else:
        break_even_months = None
    
    total_old_interest = old_df["Interest"].sum()
    total_new_interest = new_df["Interest"].sum()
    interest_savings = total_old_interest - total_new_interest
    
    # Net present value calculation
    if monthly_savings > 0:
        cash_flows = [-closing_costs] + [monthly_savings] * min(60, new_years * 12)
        discount_rate = new_rate / 100 / 12
        npv = sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows))
    else:
        npv = None
    
    recommendation = ""
    if monthly_savings > 0 and break_even_months and break_even_months < 36:
        recommendation = "Recommended - Good savings with reasonable break-even period"
    elif monthly_savings > 0:
        recommendation = "Consider - Positive savings but long break-even period"
    else:
        recommendation = "Not Recommended - No monthly savings"
    
    return {
        "old_monthly": round(old_monthly, 2),
        "new_monthly": round(new_monthly, 2),
        "monthly_savings": round(monthly_savings, 2),
        "break_even_months": round(break_even_months, 1) if break_even_months else "Never",
        "total_interest_savings": round(interest_savings, 2),
        "net_present_value": round(npv, 2) if npv else None,
        "recommendation": recommendation
    }

def tax_implications(data):
    """Calculate tax implications of mortgage interest"""
    annual_interest = data.get("annual_interest", 5000)
    tax_rate = data.get("tax_rate", 25)
    property_tax = data.get("property_tax", 0)
    filing_status = data.get("filing_status", "single")
    
    # Standard deductions by filing status
    standard_deductions = {
        "single": 12950,
        "married_joint": 25900,
        "married_separate": 12950,
        "head_of_household": 19400
    }
    
    standard_deduction = standard_deductions.get(filing_status, 12950)
    
    # Calculate deductions
    interest_deduction = min(annual_interest, 750000 * 0.06)  # Limitation for high mortgages
    property_tax_deduction = min(property_tax, 10000)
    
    total_deductions = interest_deduction + property_tax_deduction
    
    should_itemize = total_deductions > standard_deduction
    
    if should_itemize:
        tax_savings = total_deductions * (tax_rate / 100)
        effective_interest = annual_interest - (interest_deduction * (tax_rate / 100))
    else:
        tax_savings = 0
        effective_interest = annual_interest
    
    return {
        "annual_interest": round(annual_interest, 2),
        "tax_rate": tax_rate,
        "tax_savings": round(tax_savings, 2),
        "effective_interest": round(effective_interest, 2),
        "should_itemize": should_itemize,
        "itemized_deductions": round(total_deductions, 2),
        "standard_deduction": standard_deduction,
        "net_interest_cost": round(effective_interest, 2)
    }