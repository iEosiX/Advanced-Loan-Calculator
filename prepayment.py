import pandas as pd
import numpy as np
from numpy_financial import pmt

def calculate_balance_after_months(principal, rate, years, months_paid):
    """Calculate remaining balance after specified months"""
    monthly_rate = rate / 100 / 12
    total_months = years * 12
    
    if monthly_rate == 0:
        payment = principal / total_months
        return max(principal - (payment * months_paid), 0)
    else:
        payment = -pmt(monthly_rate, total_months, principal)
        future_value = principal * ((1 + monthly_rate) ** months_paid)
        payment_factor = payment * (((1 + monthly_rate) ** months_paid) - 1) / monthly_rate
        return max(future_value - payment_factor, 0)

def prepayment_scenarios(principal, rate, years, prepayment_amount, prepayment_start, prepayment_frequency):
    """
    Analyze impact of prepayments on loan
    
    Args:
        principal: Loan amount
        rate: Interest rate (%)
        years: Loan term (years)
        prepayment_amount: Additional payment amount
        prepayment_start: Month to start prepayments (1-based)
        prepayment_frequency: 'monthly', 'yearly', 'one_time', 'quarterly'
    """
    
    monthly_rate = rate / 100 / 12
    total_months = years * 12
    
    # Original schedule without prepayment
    if monthly_rate == 0:
        base_payment = principal / total_months
    else:
        base_payment = -pmt(monthly_rate, total_months, principal)
    
    # Original total interest
    total_interest_original = 0
    balance = principal
    for month in range(1, total_months + 1):
        interest = balance * monthly_rate
        total_interest_original += interest
        principal_paid = base_payment - interest
        balance -= principal_paid
        if balance <= 0:
            break
    
    # Scenario with prepayment
    scenarios = []
    
    for freq in [prepayment_frequency] if prepayment_frequency != 'all' else ['monthly', 'yearly', 'quarterly', 'one_time']:
        balance = principal
        total_interest = 0
        month = 1
        schedule = []
        
        while balance > 0.01 and month <= total_months:
            interest = balance * monthly_rate
            total_interest += interest
            
            # Base principal payment
            principal_paid = base_payment - interest
            
            # Add prepayment if applicable
            should_prepay = False
            if freq == 'monthly' and month >= prepayment_start:
                should_prepay = True
            elif freq == 'yearly' and month >= prepayment_start and (month - prepayment_start) % 12 == 0:
                should_prepay = True
            elif freq == 'quarterly' and month >= prepayment_start and (month - prepayment_start) % 3 == 0:
                should_prepay = True
            elif freq == 'one_time' and month == prepayment_start:
                should_prepay = True
            
            if should_prepay:
                principal_paid += prepayment_amount
            
            # Ensure we don't overpay
            if principal_paid > balance:
                principal_paid = balance
            
            balance -= principal_paid
            
            schedule.append({
                'month': month,
                'payment': base_payment + (prepayment_amount if should_prepay else 0),
                'interest': interest,
                'principal': principal_paid,
                'balance': balance
            })
            
            month += 1
        
        # Calculate savings
        interest_savings = total_interest_original - total_interest
        months_saved = total_months - (month - 1)
        payback_period = prepayment_amount / (interest_savings / (month - 1)) if interest_savings > 0 else None
        
        scenarios.append({
            'frequency': freq,
            'total_months': month - 1,
            'months_saved': max(months_saved, 0),
            'interest_savings': round(interest_savings, 2),
            'total_interest': round(total_interest, 2),
            'payback_period': round(payback_period, 1) if payback_period else None,
            'final_payment': round(schedule[-1]['payment'], 2) if schedule else 0,
            'recommendation': 'Good' if interest_savings > prepayment_amount * 0.5 else 'Moderate'
        })
    
    # Find optimal prepayment amount
    optimal_results = []
    amounts = [100, 200, 500, 1000, principal * 0.01]
    
    for amount in amounts:
        balance = principal
        total_interest = 0
        month = 1
        
        while balance > 0.01 and month <= total_months:
            interest = balance * monthly_rate
            total_interest += interest
            principal_paid = base_payment - interest
            
            if month >= prepayment_start and prepayment_frequency == 'monthly':
                principal_paid += amount
            
            if principal_paid > balance:
                principal_paid = balance
            
            balance -= principal_paid
            month += 1
        
        interest_savings = total_interest_original - total_interest
        roi = (interest_savings / amount) * 100 if amount > 0 else 0
        
        optimal_results.append({
            'prepayment_amount': amount,
            'interest_savings': round(interest_savings, 2),
            'months_saved': total_months - (month - 1),
            'roi_percent': round(roi, 1),
            'efficiency': 'High' if roi > 50 else 'Medium' if roi > 20 else 'Low'
        })
    
    return {
        'original': {
            'total_interest': round(total_interest_original, 2),
            'total_months': total_months,
            'monthly_payment': round(base_payment, 2)
        },
        'scenarios': scenarios,
        'optimal_prepayments': optimal_results,
        'summary': {
            'best_scenario': max(scenarios, key=lambda x: x['interest_savings']),
            'highest_roi': max(optimal_results, key=lambda x: x['roi_percent']) if optimal_results else None
        }
    }

def lump_sum_prepayment(principal, rate, years, lump_sum_amount, lump_sum_month):
    """Analyze effect of a single lump sum prepayment"""
    
    # Calculate balance before lump sum
    balance_before = calculate_balance_after_months(principal, rate, years, lump_sum_month - 1)
    
    # Apply lump sum
    balance_after = max(balance_before - lump_sum_amount, 0)
    
    # Recalculate remaining payments
    remaining_months = years * 12 - lump_sum_month + 1
    monthly_rate = rate / 100 / 12
    
    if monthly_rate == 0:
        new_payment = balance_after / remaining_months if remaining_months > 0 else 0
    else:
        new_payment = -pmt(monthly_rate, remaining_months, balance_after)
    
    # Calculate savings
    original_balance = calculate_balance_after_months(principal, rate, years, lump_sum_month)
    interest_savings = (original_balance - balance_after) * monthly_rate * remaining_months
    
    return {
        'balance_before': round(balance_before, 2),
        'balance_after': round(balance_after, 2),
        'new_monthly_payment': round(new_payment, 2),
        'interest_savings': round(interest_savings, 2),
        'effective_roi': round((interest_savings / lump_sum_amount) * 100, 1) if lump_sum_amount > 0 else 0,
        'months_eliminated': int((lump_sum_amount / new_payment) if new_payment > 0 else 0)
    }