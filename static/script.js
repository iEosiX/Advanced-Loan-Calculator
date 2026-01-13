let currentSchedule = [];
let currentLoanData = {};
let currentSummary = {};
let loanOfferCounter = 2;
let visualizationData = {};

// Initialize date input
document.addEventListener('DOMContentLoaded', function() {
    // Set default start date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').value = today;
    
    toggleLoanInputs();
    openToolTab('compare-tab');
    
    // Add custom CSS
    const style = document.createElement('style');
    style.textContent = `
        .affordable { color: #27ae60; font-weight: bold; }
        .not-affordable { color: #e74c3c; font-weight: bold; }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        .highlight { background-color: #fffacd; }
        .warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        .success { background-color: #d4edda; border-left: 4px solid #28a745; }
        .simple-bar-chart { display: flex; align-items: flex-end; height: 200px; gap: 2px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .simple-bar { flex: 1; background: linear-gradient(to top, #3498db, #2980b9); border-radius: 4px 4px 0 0; position: relative; }
        .simple-bar:hover { background: linear-gradient(to top, #2980b9, #1c5a7a); }
        .simple-bar-label { position: absolute; bottom: -25px; left: 0; right: 0; text-align: center; font-size: 11px; color: #666; }
        .simple-bar-value { position: absolute; top: -25px; left: 0; right: 0; text-align: center; font-size: 10px; color: #333; }
    `;
    document.head.appendChild(style);
});

// Tab Management
function openToolTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Activate corresponding button
    event.target.classList.add('active');
}

// Loan Input Management
function toggleLoanInputs() {
    const type = document.getElementById("type").value;
    
    // Hide all optional inputs
    document.getElementById("variableGroup").classList.add("input-hidden");
    document.getElementById("interestOnlyGroup").classList.add("input-hidden");
    document.getElementById("balloonGroup").classList.add("input-hidden");
    
    // Show rate input for most loan types
    document.getElementById("fixedRateGroup").classList.remove("input-hidden");
    
    // Show specific inputs based on loan type
    if (type === "variable") {
        document.getElementById("variableGroup").classList.remove("input-hidden");
        document.getElementById("fixedRateGroup").classList.add("input-hidden");
    } else if (type === "interest_only") {
        document.getElementById("interestOnlyGroup").classList.remove("input-hidden");
    } else if (type === "balloon") {
        document.getElementById("balloonGroup").classList.remove("input-hidden");
    }
}

// Loan Comparison Management
function addLoanOffer() {
    loanOfferCounter++;
    const comparisonInputs = document.querySelector('.comparison-inputs');
    
    const newOffer = document.createElement('div');
    newOffer.className = 'loan-offer';
    newOffer.id = `loan-offer-${loanOfferCounter}`;
    
    newOffer.innerHTML = `
        <div class="offer-header">
            <span>Loan Offer ${loanOfferCounter}</span>
            <button type="button" onclick="removeLoanOffer(${loanOfferCounter})" class="remove-btn">×</button>
        </div>
        <div class="offer-fields">
            <input type="text" placeholder="Bank Name" class="offer-name" value="Bank ${String.fromCharCode(64 + loanOfferCounter)}">
            <input type="number" placeholder="Amount" class="offer-principal" value="100000">
            <input type="number" placeholder="Rate %" class="offer-rate" step="0.1" value="5">
            <input type="number" placeholder="Years" class="offer-years" value="30">
            <input type="number" placeholder="Fees" class="offer-fees" value="0">
        </div>
    `;
    
    comparisonInputs.appendChild(newOffer);
    
    // Show remove buttons for all offers except first
    document.querySelectorAll('.remove-btn').forEach((btn, index) => {
        btn.style.display = index === 0 ? 'none' : 'block';
    });
}

function removeLoanOffer(id) {
    const offer = document.getElementById(`loan-offer-${id}`);
    if (offer && id > 1) {
        offer.remove();
        // Renumber remaining offers
        const offers = document.querySelectorAll('.loan-offer');
        offers.forEach((offer, index) => {
            const header = offer.querySelector('.offer-header span');
            header.textContent = `Loan Offer ${index + 1}`;
            offer.id = `loan-offer-${index + 1}`;
            const removeBtn = offer.querySelector('.remove-btn');
            removeBtn.onclick = () => removeLoanOffer(index + 1);
            removeBtn.style.display = index === 0 ? 'none' : 'block';
        });
        loanOfferCounter = offers.length;
    }
}

// Main Calculation Function
async function calculate() {
    const type = document.getElementById("type").value;
    const principal = parseFloat(document.getElementById("principal").value);
    const years = parseFloat(document.getElementById("years").value);
    const fees = parseFloat(document.getElementById("fees").value) || 0;
    const startDate = document.getElementById("startDate").value;
    
    if (!principal || !years || principal <= 0 || years <= 0) {
        alert("Please enter valid loan amount and years");
        return;
    }
    
    let payload = {
        type: type,
        principal: principal,
        years: years,
        fees: fees,
        start_date: startDate
    };
    
    if (type === "variable") {
        const ratesRaw = document.getElementById("variableRates").value;
        if (!ratesRaw) {
            alert("Please enter variable rates (e.g. 4,4.5,5)");
            return;
        }
        payload.rates = ratesRaw;
    } else {
        const rate = parseFloat(document.getElementById("rate").value);
        if (isNaN(rate)) {
            alert("Please enter interest rate");
            return;
        }
        payload.rate = rate;
        
        if (type === "interest_only") {
            const interestOnlyYears = parseFloat(document.getElementById("interestOnlyYears").value);
            if (!isNaN(interestOnlyYears) && interestOnlyYears >= 0) {
                payload.interest_only_years = interestOnlyYears;
            }
        } else if (type === "balloon") {
            const balloon = parseFloat(document.getElementById("balloonPercent").value);
            if (isNaN(balloon)) {
                alert("Please enter balloon percentage");
                return;
            }
            payload.balloon = balloon;
        }
    }
    
    // Save loan data for export
    currentLoanData = payload;
    
    // Show loading
    document.getElementById("result").innerHTML = `
        <div style="text-align: center; padding: 30px;">
            <div class="loading-spinner"></div>
            <p>Calculating amortization schedule...</p>
        </div>
    `;
    
    try {
        const response = await fetch("/calculate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Calculation failed");
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        currentSchedule = data.schedule;
        currentSummary = data.summary;
        visualizationData = data.visualization || {};
        
        // Build summary HTML with grid layout
        let summaryHTML = `<h3><i class="fas fa-chart-pie"></i> Loan Summary</h3>
            <div class="summary-grid">`;
        
        // Common summary items
        summaryHTML += `
    <div class="summary-item">
        <span class="summary-label">Total Paid:</span>
        <span class="summary-value">$${data.summary.total_paid.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
    </div>
    <div class="summary-item">
        <span class="summary-label">Total Interest:</span>
        <span class="summary-value">$${data.summary.total_interest.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
    </div>
    <div class="summary-item">
        <span class="summary-label">APR:</span>
        <span class="summary-value">${data.summary.apr}%</span>
    </div>`;

// Term display - years for variable rate, months for others
if (type === "variable") {
    summaryHTML += `
        <div class="summary-item">
            <span class="summary-label">Term:</span>
            <span class="summary-value">${years} years</span>
        </div>`;
} else {
    summaryHTML += `
        <div class="summary-item">
            <span class="summary-label">Term:</span>
            <span class="summary-value">${data.summary.total_months} months</span>
        </div>`;
}
        
        // Payment information based on loan type
        if (data.summary.monthly_payment !== undefined) {
            summaryHTML += `
                <div class="summary-item">
                    <span class="summary-label">Monthly Payment:</span>
                    <span class="summary-value">$${data.summary.monthly_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                </div>`;
        }
        
        // Average payment (not for interest-only loans)
        if (data.summary.average_payment !== undefined && type !== "interest_only") {
            summaryHTML += `
                <div class="summary-item">
                    <span class="summary-label">Average Payment:</span>
                    <span class="summary-value">$${data.summary.average_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                </div>`;
        }
        
        // Loan-specific details
        if (type === "interest_only" && data.summary.interest_only_payment) {
            summaryHTML += `
                <div class="summary-item">
                    <span class="summary-label">Interest-Only Payment:</span>
                    <span class="summary-value">$${data.summary.interest_only_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                </div>`;
            if (data.summary.amortizing_payment) {
                summaryHTML += `
                    <div class="summary-item">
                        <span class="summary-label">Amortizing Payment:</span>
                        <span class="summary-value">$${data.summary.amortizing_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                    </div>`;
            }
        }
        
        if (type === "balloon" && data.summary.balloon_payment) {
            summaryHTML += `
                <div class="summary-item">
                    <span class="summary-label">Balloon Payment:</span>
                    <span class="summary-value">$${data.summary.balloon_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                </div>`;
        }
        
        // Interest ratio
        const interestRatio = (data.summary.total_interest / data.summary.total_paid * 100).toFixed(1);
        summaryHTML += `
            <div class="summary-item">
                <span class="summary-label">Interest Ratio:</span>
                <span class="summary-value">${interestRatio}%</span>
            </div>`;
        
        summaryHTML += `</div>`;
        
        // Add key insights
        summaryHTML += `
            <div class="metric-card">
                <div class="metric-title">Key Insights</div>
                <div class="metric-value">${getLoanInsights(data.summary, type)}</div>
                <div class="metric-description">Based on your loan parameters</div>
            </div>`;
        
        document.getElementById("result").innerHTML = summaryHTML;
        
        // Display simple visualization 
        displaySchedule(data.schedule);
        document.getElementById("scheduleContainer").style.display = "block";
        
    } catch (err) {
        alert("Error: " + err.message);
        console.error(err);
        document.getElementById("result").innerHTML = `<p class="error">Error: ${err.message}</p>`;
    }
}

function getLoanInsights(summary, type) {
    const interestRatio = summary.total_interest / summary.total_paid;
    
    if (interestRatio > 0.5) {
        return "High interest cost - consider shorter term or lower rate";
    } else if (interestRatio > 0.3) {
        return "Moderate interest cost - typical for long-term loans";
    } else {
        return "Low interest cost - favorable loan terms";
    }
}

// Simple Visualization Display
function displaySimpleVisualization() {
    const chartContainer = document.getElementById('simpleChart');
    const yearlyContainer = document.getElementById('yearlySummary');
    
    if (!visualizationData || Object.keys(visualizationData).length === 0) {
        chartContainer.innerHTML = '<p>No visualization data available</p>';
        yearlyContainer.innerHTML = '';
        return;
    }
    
    // Create simple bar chart
    if (visualizationData.monthly_data && visualizationData.monthly_data.balances) {
        const months = visualizationData.monthly_data.months;
        const balances = visualizationData.monthly_data.balances;
        
        let chartHTML = '<div class="simple-bar-chart">';
        const maxBalance = Math.max(...balances);
        
        for (let i = 0; i < Math.min(24, months.length); i++) {
            const height = (balances[i] / maxBalance * 100) || 0;
            chartHTML += `
                <div class="simple-bar" style="height: ${height}%" 
                     title="Month ${months[i]}: $${balances[i].toLocaleString(undefined, {minimumFractionDigits: 0})}">
                    <div class="simple-bar-value">$${(balances[i]/1000).toFixed(0)}k</div>
                    <div class="simple-bar-label">${months[i]}</div>
                </div>
            `;
        }
        chartHTML += '</div>';
        chartContainer.innerHTML = chartHTML;
    }
    
    // Create yearly summary table
    if (visualizationData.yearly_data && visualizationData.yearly_data.length > 0) {
        let yearlyHTML = '<h4>Yearly Summary</h4><table class="yearly-summary"><tr><th>Year</th><th>Interest</th><th>Principal</th><th>Balance</th></tr>';
        
        visualizationData.yearly_data.forEach(year => {
            yearlyHTML += `
                <tr>
                    <td>${year.year}</td>
                    <td>$${year.interest.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>$${year.principal.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>$${year.balance.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                </tr>
            `;
        });
        
        yearlyHTML += '</table>';
        yearlyContainer.innerHTML = yearlyHTML;
    }
}

// Calculate True APR
async function calculateAPR() {
    const principal = parseFloat(document.getElementById("principal").value);
    const rate = parseFloat(document.getElementById("rate").value);
    const years = parseFloat(document.getElementById("years").value);
    const fees = parseFloat(document.getElementById("fees").value) || 0;
    
    if (!principal || !years || principal <= 0 || years <= 0) {
        alert("Please enter valid loan amount and years");
        return;
    }
    
    try {
        const response = await fetch("/calculate/apr", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({principal, rate, years, fees})
        });
        
        if (!response.ok) throw new Error("APR calculation failed");
        
        const data = await response.json();
        
        let html = `
            <div class="metric-card">
                <div class="metric-title">Annual Percentage Rate (APR)</div>
                <div class="metric-value">${data.apr}%</div>
                <div class="metric-description">
                    Nominal Rate: ${data.nominal_rate}% | 
                    Fees Impact: ${data.fees_impact}%
                </div>
            </div>
            <p><strong>Note:</strong> APR includes all loan costs (fees, points, etc.) and represents the true cost of borrowing.</p>
        `;
        
        // Show in result area
        document.getElementById("result").innerHTML = html;
        
    } catch (err) {
        alert("Error calculating APR: " + err.message);
    }
}

// Display Amortization Schedule
function displaySchedule(schedule) {
    const table = document.getElementById("schedule");
    table.innerHTML = "";
    
    if (!schedule || schedule.length === 0) {
        return;
    }
    
    // Determine if this is a variable rate loan (check first row for 'Year' key)
    const isVariableRate = schedule[0].Year !== undefined;
    
    // Create header
    const header = table.createTHead();
    const headerRow = header.insertRow();
    
    // Determine columns based on available data
    const firstRow = schedule[0];
    const columns = Object.keys(firstRow);
    
    columns.forEach(key => {
        const th = document.createElement("th");
        // For variable rate loans, change "Year" to "Year" (already), for others "Month" stays "Month"
        if (key === 'Month' && isVariableRate) {
            th.textContent = 'Year';
        } else if (key === 'Year' && !isVariableRate) {
            th.textContent = 'Month';
        } else {
            th.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        headerRow.appendChild(th);
    });
    
    // Create body - limit to 100 rows for performance
    const maxRows = Math.min(100, schedule.length);
    const tbody = table.createTBody();
    
    for (let i = 0; i < maxRows; i++) {
        const row = schedule[i];
        const tr = tbody.insertRow();
        
        columns.forEach((key, index) => {
            const td = tr.insertCell();
            let value = row[key];
            
            // For variable rate loans, adjust the year/month display
            if (isVariableRate && key === 'Year') {
                // Show as Year
                td.textContent = value;
            } else if (!isVariableRate && key === 'Month') {
                // Show as Month
                td.textContent = value;
            } else if (typeof value === 'number') {
                // Format numbers
                if (key === 'Year' || key === 'Month') {
                    td.textContent = value;
                } else {
                    td.textContent = value.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    });
                    
                    // Add dollar sign for currency columns
                    if (['Payment', 'Interest', 'Principal', 'Balance'].includes(key)) {
                        td.textContent = '$' + td.textContent;
                    }
                }
            } else {
                td.textContent = value;
            }
            
            // Highlight current year/month
            if ((isVariableRate && key === 'Year' && value === 1) || 
                (!isVariableRate && key === 'Month' && value === 1)) {
                tr.classList.add('highlight');
            }
        });
    }
    
    // Show message if rows were truncated
    if (schedule.length > maxRows) {
        const tr = tbody.insertRow();
        const td = tr.insertCell();
        td.colSpan = columns.length;
        if (isVariableRate) {
            td.textContent = `... showing first ${maxRows} of ${schedule.length} years`;
        } else {
            td.textContent = `... showing first ${maxRows} of ${schedule.length} months`;
        }
        td.style.textAlign = 'center';
        td.style.fontStyle = 'italic';
        td.style.color = '#666';
        td.style.padding = '20px';
    }
}

// Export Functions
function exportToCSV() {
    if (!currentSchedule || currentSchedule.length === 0) {
        alert("No data to export");
        return;
    }
    
    fetch("/export", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({data: currentSchedule})
    })
    .then(res => {
        if (!res.ok) throw new Error("Export failed");
        return res.blob();
    })
    .then(blob => {
        downloadFile(blob, "loan_schedule.csv");
    })
    .catch(err => {
        alert("Error exporting: " + err.message);
    });
}

function exportToHTML() {
    if (!currentSchedule || currentSchedule.length === 0) {
        alert("No data to export");
        return;
    }
    
    const exportData = {
        schedule: currentSchedule,
        summary: currentSummary,
        loan_data: currentLoanData
    };
    
    fetch("/export/html", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(exportData)
    })
    .then(res => {
        if (!res.ok) throw new Error("HTML export failed");
        return res.blob();
    })
    .then(blob => {
        downloadFile(blob, "loan_report.html");
    })
    .catch(err => {
        alert("Error exporting HTML: " + err.message);
    });
}

function exportToText() {
    if (!currentSchedule || currentSchedule.length === 0) {
        alert("No data to export");
        return;
    }
    
    const exportData = {
        schedule: currentSchedule,
        summary: currentSummary,
        loan_data: currentLoanData
    };
    
    fetch("/export/text", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(exportData)
    })
    .then(res => {
        if (!res.ok) throw new Error("Text export failed");
        return res.blob();
    })
    .then(blob => {
        downloadFile(blob, "loan_report.txt");
    })
    .catch(err => {
        alert("Error exporting text: " + err.message);
    });
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Analysis Functions (same as before, but using simplified version)
async function compareLoans() {
    const loanOffers = [];
    const offerElements = document.querySelectorAll('.loan-offer');
    
    offerElements.forEach((offer, index) => {
        const name = offer.querySelector('.offer-name').value || `Offer ${index + 1}`;
        const principal = parseFloat(offer.querySelector('.offer-principal').value) || 100000;
        const rate = parseFloat(offer.querySelector('.offer-rate').value) || 5;
        const years = parseInt(offer.querySelector('.offer-years').value) || 30;
        const fees = parseFloat(offer.querySelector('.offer-fees').value) || 0;
        
        loanOffers.push({
            name: name,
            principal: principal,
            rate: rate,
            years: years,
            fees: fees
        });
    });
    
    if (loanOffers.length === 0) {
        alert("Please add at least one loan offer");
        return;
    }
    
    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({offers: loanOffers})
        });
        
        if (!response.ok) throw new Error('Comparison failed');
        
        const data = await response.json();
        let html = '<h4>Loan Comparison Results</h4>';
        
        if (data.length === 0) {
            html += '<p class="warning">No valid loan offers to compare.</p>';
        } else {
            html += '<table class="comparison-table"><tr><th>Rank</th><th>Loan</th><th>Monthly Payment</th><th>Total Interest</th><th>Total Cost</th><th>APR</th><th>Term</th></tr>';
            
            data.forEach(loan => {
                if (loan.error) {
                    html += `<tr>
                        <td colspan="7" class="error">${loan.name}: ${loan.error}</td>
                    </tr>`;
                } else {
                    const rankBadge = loan.rank === 1 ? '🥇' : loan.rank === 2 ? '🥈' : loan.rank === 3 ? '🥉' : '';
                    html += `<tr>
                        <td><strong>${loan.rank}</strong> ${rankBadge}</td>
                        <td><strong>${loan.name}</strong></td>
                        <td>$${loan.monthly_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td>$${loan.total_interest.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td>$${loan.total_cost.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td>${loan.apr}%</td>
                        <td>${loan.term_years} years</td>
                    </tr>`;
                }
            });
            
            html += '</table>';
            
            // Add recommendation
            const bestLoan = data.find(loan => loan.rank === 1 && !loan.error);
            if (bestLoan) {
                html += `
                    <div class="metric-card success" style="margin-top: 20px;">
                        <div class="metric-title">Recommendation</div>
                        <div class="metric-value">${bestLoan.name}</div>
                        <div class="metric-description">
                            Lowest total cost: $${bestLoan.total_cost.toLocaleString()} | 
                            Monthly payment: $${bestLoan.monthly_payment.toLocaleString()}
                        </div>
                    </div>
                `;
            }
        }
        
        document.getElementById('compareResult').innerHTML = html;
        
    } catch (error) {
        document.getElementById('compareResult').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

async function sensitivityAnalysis() {
    const payload = {
        principal: parseFloat(document.getElementById('sensPrincipal').value),
        rate: parseFloat(document.getElementById('sensRate').value),
        years: parseFloat(document.getElementById('sensYears').value)
    };
    
    try {
        const response = await fetch('/sensitivity', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error('Analysis failed');
        
        const data = await response.json();
        let html = '<h4>Sensitivity to Interest Rate Changes</h4>';
        
        if (data.length === 0) {
            html += '<p>No sensitivity data available.</p>';
        } else {
            html += '<table class="sensitivity-table"><tr><th>Rate</th><th>Monthly Payment</th><th>Change</th><th>Total Interest</th><th>Total Cost</th></tr>';
            
            data.forEach(item => {
                const changeClass = item.payment_change_pct > 0 ? 'positive' : item.payment_change_pct < 0 ? 'negative' : '';
                const changeSign = item.payment_change_pct > 0 ? '+' : '';
                const isBaseRate = item.rate === payload.rate;
                const rowClass = isBaseRate ? 'highlight' : '';
                
                html += `<tr class="${rowClass}">
                    <td><strong>${item.rate}%</strong>${isBaseRate ? ' (Base)' : ''}</td>
                    <td>$${item.monthly_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td class="${changeClass}">${changeSign}${item.payment_change_pct}%</td>
                    <td>$${item.total_interest.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>$${item.total_cost.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                </tr>`;
            });
            
            html += '</table>';
            
            // Add insights
            const baseItem = data.find(item => item.rate === payload.rate);
            const worstItem = data.reduce((worst, current) => 
                current.payment_change_pct > worst.payment_change_pct ? current : worst
            );
            
            if (baseItem && worstItem) {
                html += `
                    <div class="metric-card" style="margin-top: 20px;">
                        <div class="metric-title">Key Insight</div>
                        <div class="metric-value">Rate increase of 2% increases payment by $${worstItem.payment_change.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                        <div class="metric-description">
                            That's a ${worstItem.payment_change_pct.toFixed(1)}% increase in monthly payment
                        </div>
                    </div>
                `;
            }
        }
        
        document.getElementById('sensitivityResult').innerHTML = html;
        
    } catch (error) {
        document.getElementById('sensitivityResult').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

async function affordabilityAnalysis() {
    const payload = {
        income: parseFloat(document.getElementById('income').value),
        debts: parseFloat(document.getElementById('debts').value),
        payment: parseFloat(document.getElementById('payment').value),
        housing_ratio: parseFloat(document.getElementById('housingRatio').value),
        total_ratio: parseFloat(document.getElementById('totalRatio').value)
    };
    
    try {
        const response = await fetch('/affordability', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error('Affordability check failed');
        
        const data = await response.json();
        
        let html = `
            <h4>Affordability Analysis</h4>
            <div class="affordability-result">
                <div class="metric-card ${data.affordable ? 'success' : 'warning'}">
                    <div class="metric-title">Front-end Ratio (Housing)</div>
                    <div class="metric-value">${data.front_end_ratio}%</div>
                    <div class="metric-description">
                        ${data.affordable_front ? '✓ Within limits' : '✗ Exceeds limit of ' + payload.housing_ratio + '%'}
                    </div>
                </div>
                
                <div class="metric-card ${data.affordable ? 'success' : 'warning'}">
                    <div class="metric-title">Back-end Ratio (Total Debt)</div>
                    <div class="metric-value">${data.back_end_ratio}%</div>
                    <div class="metric-description">
                        ${data.affordable_back ? '✓ Within limits' : '✗ Exceeds limit of ' + payload.total_ratio + '%'}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Maximum Affordable Payment</div>
                    <div class="metric-value">$${data.max_affordable_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">
                        Based on your income and existing debts
                    </div>
                </div>
                
                <div class="${data.affordable ? 'success' : 'warning'}" style="padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <h5>Recommendation:</h5>
                    <p>${data.recommendation}</p>
                    ${!data.affordable ? `<p><strong>Suggested action:</strong> Reduce loan amount to keep payment under $${data.max_affordable_payment.toLocaleString(undefined, {minimumFractionDigits: 2})}</p>` : ''}
                </div>
            </div>
        `;
        
        document.getElementById('affordabilityResult').innerHTML = html;
        
    } catch (error) {
        document.getElementById('affordabilityResult').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

async function prepaymentAnalysis() {
    const payload = {
        principal: parseFloat(document.getElementById('prepayPrincipal').value),
        rate: parseFloat(document.getElementById('prepayRate').value),
        years: parseFloat(document.getElementById('prepayYears').value),
        prepayment_amount: parseFloat(document.getElementById('prepaymentAmount').value),
        prepayment_start: parseInt(document.getElementById('prepaymentStart').value),
        prepayment_frequency: document.getElementById('prepaymentFrequency').value
    };
    
    try {
        const response = await fetch('/prepayment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error('Prepayment analysis failed');
        
        const data = await response.json();
        
        let html = `<h4>Prepayment Analysis</h4>`;
        
        // Original loan info
        html += `
            <div class="metric-card">
                <div class="metric-title">Original Loan</div>
                <div class="metric-value">$${data.original.monthly_payment.toLocaleString()}/month</div>
                <div class="metric-description">
                    Total Interest: $${data.original.total_interest.toLocaleString()} | 
                    Term: ${data.original.total_months} months
                </div>
            </div>
        `;
        
        // Prepayment scenarios
        if (data.scenarios && data.scenarios.length > 0) {
            html += `<h5 style="margin-top: 20px;">Prepayment Scenarios</h5>`;
            html += '<table class="prepayment-table"><tr><th>Frequency</th><th>Interest Saved</th><th>Months Saved</th><th>New Term</th><th>Recommendation</th></tr>';
            
            data.scenarios.forEach(scenario => {
                html += `<tr>
                    <td>${scenario.frequency}</td>
                    <td>$${scenario.interest_savings.toLocaleString()}</td>
                    <td>${scenario.months_saved}</td>
                    <td>${scenario.total_months} months</td>
                    <td><span class="${scenario.recommendation === 'Good' ? 'positive' : ''}">${scenario.recommendation}</span></td>
                </tr>`;
            });
            
            html += '</table>';
        }
        
        // Optimal prepayment amounts
        if (data.optimal_prepayments && data.optimal_prepayments.length > 0) {
            html += `<h5 style="margin-top: 20px;">Optimal Prepayment Amounts</h5>`;
            html += '<table class="prepayment-table"><tr><th>Amount</th><th>Interest Saved</th><th>ROI</th><th>Efficiency</th></tr>';
            
            data.optimal_prepayments.forEach(prepay => {
                html += `<tr>
                    <td>$${prepay.prepayment_amount.toLocaleString()}</td>
                    <td>$${prepay.interest_savings.toLocaleString()}</td>
                    <td>${prepay.roi_percent}%</td>
                    <td><span class="${prepay.efficiency === 'High' ? 'positive' : prepay.efficiency === 'Low' ? 'negative' : ''}">${prepay.efficiency}</span></td>
                </tr>`;
            });
            
            html += '</table>';
        }
        
        // Best scenario
        if (data.summary && data.summary.best_scenario) {
            const best = data.summary.best_scenario;
            html += `
                <div class="metric-card success" style="margin-top: 20px;">
                    <div class="metric-title">Best Prepayment Strategy</div>
                    <div class="metric-value">${best.frequency} prepayments of $${payload.prepayment_amount}</div>
                    <div class="metric-description">
                        Save $${best.interest_savings.toLocaleString()} in interest | 
                        Pay off ${best.months_saved} months early
                    </div>
                </div>
            `;
        }
        
        document.getElementById('prepaymentResult').innerHTML = html;
        
    } catch (error) {
        document.getElementById('prepaymentResult').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

async function refinancingAnalysis() {
    const payload = {
        remaining_balance: parseFloat(document.getElementById('refinanceBalance').value),
        old_rate: parseFloat(document.getElementById('oldRate').value),
        new_rate: parseFloat(document.getElementById('newRate').value),
        remaining_years: parseFloat(document.getElementById('remainingYears').value),
        new_years: parseFloat(document.getElementById('newYears').value),
        closing_costs: parseFloat(document.getElementById('closingCosts').value),
        roll_costs: document.getElementById('rollCosts').checked
    };
    
    try {
        const response = await fetch('/refinance', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error('Refinance analysis failed');
        
        const data = await response.json();
        
        const isRecommended = data.recommendation.includes('Recommended');
        
        let html = `
            <h4>Refinancing Analysis</h4>
            <div class="refinance-result">
                <div class="metric-card">
                    <div class="metric-title">Current Loan</div>
                    <div class="metric-value">$${data.old_monthly.toLocaleString(undefined, {minimumFractionDigits: 2})}/month</div>
                    <div class="metric-description">${payload.remaining_years} years remaining</div>
                </div>
                
                <div class="metric-card ${isRecommended ? 'success' : 'warning'}">
                    <div class="metric-title">New Loan</div>
                    <div class="metric-value">$${data.new_monthly.toLocaleString(undefined, {minimumFractionDigits: 2})}/month</div>
                    <div class="metric-description">${payload.new_years} years term</div>
                </div>
                
                <div class="metric-card ${data.monthly_savings > 0 ? 'success' : 'warning'}">
                    <div class="metric-title">Monthly Savings</div>
                    <div class="metric-value">$${data.monthly_savings.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">
                        ${data.monthly_savings > 0 ? 'Positive cash flow' : 'No monthly savings'}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Break-even Point</div>
                    <div class="metric-value">${data.break_even_months === "Never" ? "Never" : data.break_even_months + " months"}</div>
                    <div class="metric-description">
                        Time to recover closing costs
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Total Interest Savings</div>
                    <div class="metric-value">$${data.total_interest_savings.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">
                        Lifetime savings on interest
                    </div>
                </div>
                
                ${data.net_present_value ? `
                <div class="metric-card">
                    <div class="metric-title">Net Present Value (5 years)</div>
                    <div class="metric-value">$${data.net_present_value.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">
                        Present value of savings
                    </div>
                </div>
                ` : ''}
                
                <div class="${isRecommended ? 'success' : 'warning'}" style="padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <h5>Recommendation:</h5>
                    <p><strong>${data.recommendation}</strong></p>
                    <p>${getRefinanceRecommendation(data)}</p>
                </div>
            </div>
        `;
        
        document.getElementById('refinanceResult').innerHTML = html;
        
    } catch (error) {
        document.getElementById('refinanceResult').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

function getRefinanceRecommendation(data) {
    if (data.monthly_savings > 0 && data.break_even_months !== "Never" && data.break_even_months < 24) {
        return "Excellent refinance opportunity with quick payback.";
    } else if (data.monthly_savings > 0 && data.break_even_months < 36) {
        return "Good refinance opportunity with reasonable payback period.";
    } else if (data.monthly_savings > 0) {
        return "Consider if you plan to stay in the home long-term.";
    } else {
        return "Not financially beneficial at this time.";
    }
}

async function taxAnalysis() {
    const payload = {
        annual_interest: parseFloat(document.getElementById('annualInterest').value),
        tax_rate: parseFloat(document.getElementById('taxRate').value),
        property_tax: parseFloat(document.getElementById('propertyTax').value),
        filing_status: document.getElementById('filingStatus').value,
    };
    
    try {
        const response = await fetch('/tax', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error('Tax analysis failed');
        
        const data = await response.json();
        
        let html = `
            <h4>Tax Implications Analysis</h4>
            <div class="tax-result">
                <div class="metric-card">
                    <div class="metric-title">Annual Mortgage Interest</div>
                    <div class="metric-value">$${data.annual_interest.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">Potentially tax deductible</div>
                </div>

                <div class="metric-card ${data.tax_savings > 0 ? 'success' : ''}">
                    <div class="metric-title">Estimated Tax Savings</div>
                    <div class="metric-value">$${data.tax_savings.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">Based on ${data.tax_rate}% tax rate</div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">Effective Interest Cost</div>
                    <div class="metric-value">$${data.effective_interest.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">After tax savings</div>
                </div>

                <div class="metric-card ${data.should_itemize ? 'success' : 'warning'}">
                    <div class="metric-title">Deduction Strategy</div>
                    <div class="metric-value">${data.should_itemize ? 'Itemize Deductions' : 'Take Standard Deduction'}</div>
                    <div class="metric-description">
                        ${data.should_itemize ?
                            `Itemized: $${data.itemized_deductions.toLocaleString()} > Standard: $${data.standard_deduction.toLocaleString()}` :
                            `Standard: $${data.standard_deduction.toLocaleString()} > Itemized: $${data.itemized_deductions.toLocaleString()}`
                        }
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">Net Interest Cost</div>
                    <div class="metric-value">$${data.net_interest_cost.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">Actual cost after tax benefits</div>
                </div>

                ${data.marginal_rate_savings ? `
                <div class="metric-card">
                    <div class="metric-title">Marginal Rate Savings</div>
                    <div class="metric-value">$${data.marginal_rate_savings.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                    <div class="metric-description">Savings at your marginal tax rate</div>
                </div>
                ` : ''}

                ${data.note ? `
                <div class="metric-card">
                    <div class="metric-title">Note</div>
                    <div class="metric-description">${data.note}</div>
                </div>
                ` : ''}
                
                <div class="warning" style="padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <h5>Disclaimer:</h5>
                    <p>This is an estimate only. Tax laws vary by jurisdiction and individual circumstances. Consult with a qualified tax professional for personalized advice.</p>
                </div>
            </div>
        `;
        
        document.getElementById('taxResult').innerHTML = html;
        
    } catch (error) {
        document.getElementById('taxResult').innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

// Helper function to format currency
function formatCurrency(amount) {
    return '$' + amount.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Helper function to format percentage
function formatPercentage(value) {
    return value.toFixed(2) + '%';
}

// Helper function to show loading state
function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div class="loading-spinner"></div>
            <p>Loading...</p>
        </div>
    `;
}

// Helper function to show error
function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `
        <div class="error" style="padding: 15px; background-color: #f8d7da; color: #721c24; border-radius: 5px; margin: 10px 0;">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

// Initialize tooltips
function initializeTooltips() {
    // Add tooltip functionality to elements with data-tooltip attribute
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.position = 'absolute';
            tooltip.style.background = '#333';
            tooltip.style.color = '#fff';
            tooltip.style.padding = '5px 10px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '12px';
            tooltip.style.zIndex = '1000';
            tooltip.style.maxWidth = '200px';
            tooltip.style.whiteSpace = 'nowrap';
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            
            this._tooltip = tooltip;
        });
        
        el.addEventListener('mouseleave', function(e) {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}

// Call initialize tooltips when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    
    // Add today's date to start date if not already set
    const startDateInput = document.getElementById('startDate');
    if (!startDateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        startDateInput.value = today;
    }
});