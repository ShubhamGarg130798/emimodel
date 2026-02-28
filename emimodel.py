import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

# ── PASSWORD GATE ─────────────────────────────────────────────────────────────
PASSWORD = "nbfcsecure123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    password = st.text_input("Enter password to access dashboard:", type="password")
    if password == PASSWORD:
        st.session_state.authenticated = True
        st.success("Access granted. Welcome!")
        st.rerun()
    elif password:
        st.error("Incorrect password")
    st.stop()

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="NBFC Multi-Tranche EMI Calculator", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%); }
#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
.main .block-container { padding: 1.5rem 2.5rem; max-width: 1600px; }

.dashboard-header {
    background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
    padding: 2.5rem 3rem; border-radius: 16px;
    box-shadow: 0 8px 24px rgba(26,54,93,0.25);
    margin-bottom: 2.5rem; position: relative; overflow: hidden;
}
.dashboard-header::before { content:''; position:absolute; top:-50%; right:-10%;
    width:400px; height:400px;
    background:radial-gradient(circle,rgba(255,255,255,0.08) 0%,transparent 70%); border-radius:50%; }
.dashboard-title { font-size:2.25rem; font-weight:800; color:white; margin:0;
    text-align:center; letter-spacing:-0.5px; position:relative; z-index:1; }
.dashboard-subtitle { font-size:1.125rem; color:rgba(255,255,255,0.9);
    margin:0.75rem 0 0 0; font-weight:500; text-align:center; position:relative; z-index:1; }

.section-header { font-size:1.5rem; font-weight:800; color:#1a365d;
    margin:3rem 0 1.5rem 0; padding-bottom:1rem;
    border-bottom:3px solid #e2e8f0; position:relative; letter-spacing:-0.5px; }
.section-header::before { content:''; position:absolute; bottom:-3px; left:0;
    width:80px; height:3px; background:linear-gradient(90deg,#2b6cb0,#4299e1); }

.kpi-card { border-radius:14px; padding:1rem 1.25rem;
    box-shadow:0 4px 12px rgba(0,0,0,0.15); transition:all 0.3s ease;
    height:150px; display:flex; flex-direction:column; justify-content:space-between; }
.kpi-card:hover { transform:translateY(-5px); box-shadow:0 16px 32px rgba(0,0,0,0.2); }
.kpi-header { display:flex; justify-content:space-between; align-items:center; }
.kpi-icon { width:36px; height:36px; border-radius:10px; display:flex; align-items:center;
    justify-content:center; font-size:1.1rem; background:rgba(255,255,255,0.25); }
.kpi-label { font-size:0.75rem; font-weight:600; color:rgba(255,255,255,0.9);
    text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.25rem; }
.kpi-value { font-size:1.35rem; font-weight:800; color:#fff; margin:0; line-height:1.2; }
.kpi-trend { font-size:0.8rem; font-weight:600; color:rgba(255,255,255,0.9); line-height:1.3; }
.kpi-blue   { background:linear-gradient(135deg,#3182ce,#2c5282); }
.kpi-green  { background:linear-gradient(135deg,#38a169,#2f855a); }
.kpi-orange { background:linear-gradient(135deg,#dd6b20,#c05621); }
.kpi-purple { background:linear-gradient(135deg,#805ad5,#6b46c1); }
.kpi-teal   { background:linear-gradient(135deg,#319795,#2c7a7b); }
.kpi-red    { background:linear-gradient(135deg,#e53e3e,#c53030); }
.kpi-indigo { background:linear-gradient(135deg,#5a67d8,#4c51bf); }

.tranche-card { border-radius:14px; padding:1.25rem 1.5rem; margin-bottom:0.5rem;
    box-shadow:0 4px 14px rgba(0,0,0,0.15); }
.tranche-title { font-size:0.8rem; font-weight:700; color:rgba(255,255,255,0.85);
    text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem; }
.tranche-pct { font-size:2.2rem; font-weight:900; color:#fff; line-height:1; margin-bottom:0.3rem; }
.tranche-detail { font-size:0.78rem; color:rgba(255,255,255,0.85); margin-top:0.2rem; }
.t3m  { background:linear-gradient(135deg,#3182ce,#2c5282); }
.t6m  { background:linear-gradient(135deg,#38a169,#276749); }
.t9m  { background:linear-gradient(135deg,#dd6b20,#c05621); }
.t12m { background:linear-gradient(135deg,#805ad5,#6b46c1); }

[data-testid="stSidebar"] { background:linear-gradient(180deg,#1a365d 0%,#2a4365 100%); }
[data-testid="stSidebar"] > div:first-child { padding:1.5rem 1.25rem; }
[data-testid="stSidebar"] h1 { color:#fff !important; font-weight:700 !important;
    font-size:1.125rem !important; padding:1rem !important;
    background:rgba(255,255,255,0.1) !important; border-radius:10px !important;
    text-align:center !important; border:1px solid rgba(255,255,255,0.2) !important; }
[data-testid="stSidebar"] * { color:#fff !important; }
[data-testid="stSidebar"] details summary { background:rgba(255,255,255,0.12) !important;
    border-radius:10px !important; padding:0.875rem 1rem !important; margin:0.5rem 0 !important;
    border:1px solid rgba(255,255,255,0.15) !important; font-weight:600 !important; cursor:pointer !important; }
[data-testid="stSidebar"] details summary:hover { background:rgba(255,255,255,0.18) !important; }
[data-testid="stSidebar"] label { color:#e2e8f0 !important; font-weight:600 !important; }
[data-testid="stSidebar"] input[type="number"] { background:rgba(255,255,255,0.95) !important;
    color:#2d3748 !important; border-radius:8px !important; font-weight:600 !important; }
[data-testid="stDownloadButton"] button { background:linear-gradient(135deg,#2b6cb0,#2c5282) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    padding:0.75rem 1.5rem !important; font-weight:600 !important; }
[data-testid="stDataFrame"] { border-radius:14px !important; overflow:hidden !important;
    box-shadow:0 4px 12px rgba(0,0,0,0.1) !important; }
[data-testid="stDataFrame"] thead tr th { background:linear-gradient(135deg,#1e3a5f,#2c5282) !important;
    color:white !important; font-weight:700 !important; font-size:0.8rem !important;
    text-transform:uppercase !important; text-align:center !important; }
[data-testid="stDataFrame"] tbody tr:nth-child(odd):not(:last-child)  { background:#e0f2fe !important; }
[data-testid="stDataFrame"] tbody tr:nth-child(even):not(:last-child) { background:#fff !important; }
[data-testid="stDataFrame"] tbody td { color:#374151 !important; font-size:0.875rem !important;
    font-weight:500 !important; text-align:center !important; }
[data-testid="stDataFrame"] tbody tr:last-child { background:linear-gradient(90deg,#1e3a8a,#1e40af) !important; }
[data-testid="stDataFrame"] tbody tr:last-child td { font-weight:800 !important; color:white !important; }

.summary-card { border-radius:12px; padding:1rem 1.25rem; margin-bottom:0.75rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.1); display:flex; align-items:center; gap:0.875rem; }
.summary-card:hover { transform:translateX(4px); box-shadow:0 6px 16px rgba(0,0,0,0.15); }
.s-icon { width:42px; height:42px; border-radius:10px; display:flex; align-items:center;
    justify-content:center; font-size:1.25rem; background:rgba(255,255,255,0.3); flex-shrink:0; }
.s-label { font-size:0.72rem; font-weight:600; color:rgba(255,255,255,0.9); text-transform:uppercase; }
.s-value { font-size:1.2rem; font-weight:800; color:white; }
.sc-blue   { background:linear-gradient(135deg,#3182ce,#2c5282); }
.sc-green  { background:linear-gradient(135deg,#38a169,#2f855a); }
.sc-teal   { background:linear-gradient(135deg,#319795,#2c7a7b); }
.sc-red    { background:linear-gradient(135deg,#e53e3e,#c53030); }
.sc-orange { background:linear-gradient(135deg,#dd6b20,#c05621); }
.sc-purple { background:linear-gradient(135deg,#805ad5,#6b46c1); }
.sc-indigo { background:linear-gradient(135deg,#5a67d8,#4c51bf); }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">📊 NBFC Multi-Tranche EMI Calculator</div>
    <div class="dashboard-subtitle">Split each disbursement across 3M · 6M · 9M · 12M tenures — independent rolling windows 🏦</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("# 🎛️ Input Parameters")

with st.sidebar.expander("📅 Projection Period", expanded=True):
    num_months = st.number_input("Number of Months", min_value=1, max_value=120, value=12, step=1)

with st.sidebar.expander("💰 Capital Deployed (₹ Crores)", expanded=False):
    capital_values = []
    c1, c2 = st.columns(2) if num_months <= 12 else (None, None)
    for i in range(num_months):
        m = i + 1
        default = [10.0,10.0,10.0,10.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0][i] if i < 12 else 0.0
        if num_months <= 12:
            col = c1 if i % 2 == 0 else c2
            with col:
                val = st.number_input(f"M{m}", 0.0, 10000.0, default, 0.5, key=f"cap_{m}")
        else:
            val = st.number_input(f"Month {m}", 0.0, 10000.0, default, 0.5, key=f"cap_{m}")
        capital_values.append(val)

with st.sidebar.expander("🔄 Capital Withdrawal (₹ Crores)", expanded=False):
    withdrawal_values = []
    w1, w2 = st.columns(2) if num_months <= 12 else (None, None)
    for i in range(num_months):
        m = i + 1
        if num_months <= 12:
            col = w1 if i % 2 == 0 else w2
            with col:
                val = st.number_input(f"M{m}", 0.0, 10000.0, 0.0, 0.5, key=f"wdraw_{m}")
        else:
            val = st.number_input(f"Month {m}", 0.0, 10000.0, 0.0, 0.5, key=f"wdraw_{m}")
        withdrawal_values.append(val)

# ── TRANCHE SPLIT ─────────────────────────────────────────────────────────────
with st.sidebar.expander("📐 Tranche Split (%) — Same Every Month", expanded=True):
    st.markdown("**Splits how each month's disbursement is allocated across tenures.**")
    t3  = st.number_input("🔵 3-Month  Tranche (%)", 0.0, 100.0, 50.0, 5.0, key="ts3")
    t6  = st.number_input("🟢 6-Month  Tranche (%)", 0.0, 100.0, 25.0, 5.0, key="ts6")
    t9  = st.number_input("🟠 9-Month  Tranche (%)", 0.0, 100.0, 15.0, 5.0, key="ts9")
    t12 = st.number_input("🟣 12-Month Tranche (%)", 0.0, 100.0, 10.0, 5.0, key="ts12")
    tranche_total = t3 + t6 + t9 + t12
    if abs(tranche_total - 100.0) > 0.01:
        st.error(f"⚠️ Total = {tranche_total:.1f}% — must equal 100%")
    else:
        st.success(f"✅ Total = {tranche_total:.1f}%")

tranche_splits = {3: t3/100, 6: t6/100, 9: t9/100, 12: t12/100}
TENURES = [3, 6, 9, 12]

with st.sidebar.expander("📈 Revenue Parameters", expanded=False):
    processing_fees_pct        = st.number_input("Processing Fees (%)",        0.0,  30.0, 11.8, 0.1)
    monthly_interest_rate_pct  = st.number_input("Monthly Interest Rate (%)",  0.0,  50.0, 10.0, 0.5)
    marketing_rate_pct         = st.number_input("Marketing Expenses (%)",     0.0,  20.0,  3.0, 0.1)
    cost_of_funds_rate_pct     = st.number_input("Cost of Funds (% monthly)",  0.0,  30.0,  3.0, 0.1)
processing_fees       = processing_fees_pct       / 100
monthly_interest_rate = monthly_interest_rate_pct / 100
marketing_rate        = marketing_rate_pct        / 100
cost_of_funds_rate    = cost_of_funds_rate_pct    / 100

with st.sidebar.expander("🎯 Loan Parameters", expanded=False):
    avg_ticket_size = st.number_input("Average Loan Ticket (₹)", 1000, 5000000, 300000, 10000)

with st.sidebar.expander("🏢 Operational Expenses", expanded=False):
    opex_month1_value = st.number_input("Month 1 OpEx (₹)", 0, 50000000, 2500000, 50000)
    opex_values = [opex_month1_value / 1e7]
    opex_types  = ['fixed']
    for i in range(1, num_months):
        m = i + 1
        st.markdown(f"**Month {m}**")
        otype = st.radio(f"Type M{m}", ['% of Prev AUM', 'Fixed ₹'], key=f"ot_{m}", horizontal=True)
        if otype == '% of Prev AUM':
            opex_values.append(st.number_input(f"M{m} Rate (%)", 0.0, 30.0, 5.0, 0.5, key=f"opex_{m}") / 100)
            opex_types.append('percentage')
        else:
            opex_values.append(st.number_input(f"M{m} OpEx (₹)", 0, 50000000, 1500000, 50000, key=f"opex_{m}") / 1e7)
            opex_types.append('fixed')

with st.sidebar.expander("📊 Collection Parameters", expanded=False):
    t0_col  = st.number_input("T+0  Collection Rate (%)", 0, 100, 80, 1) / 100
    t30_col = st.number_input("T+30 Collection Rate (%)", 0, 100,  5, 1) / 100
    t60_col = st.number_input("T+60 Collection Rate (%)", 0, 100,  4, 1) / 100
    t90_col = st.number_input("T+90 Collection Rate (%)", 0, 100,  2, 1) / 100
    total_col_pct = (t0_col + t30_col + t60_col + t90_col) * 100
    st.error(f"⚠️ Total: {total_col_pct:.1f}% — exceeds 100%!") if total_col_pct > 100 else st.success(f"✅ Total collection: {total_col_pct:.1f}%")
    api_cost_80 = st.number_input("API Cost per Non-Converted Lead (₹)", 0, 500, 10,  5)
    api_cost_20 = st.number_input("API Cost per Converted Customer (₹)",  0, 500, 40, 5)

# ── EMI FACTORS ───────────────────────────────────────────────────────────────
def calc_emi_factor(rate, n):
    if rate == 0:
        return 1.0 / n if n > 0 else 1.0
    pwr = (1 + rate) ** n
    return (rate * pwr) / (pwr - 1)

emi_factors = {n: calc_emi_factor(monthly_interest_rate, n) for n in TENURES}

# AUM aging weights
w1 = 1.0 - t0_col
w2 = 1.0 - t0_col - t30_col
w3 = 1.0 - t0_col - t30_col - t60_col

# ── CALCULATION ───────────────────────────────────────────────────────────────
def calculate():
    months = num_months
    cap   = [capital_values[i] * 1e7    if i < len(capital_values)   else 0.0 for i in range(months)]
    wdraw = [withdrawal_values[i] * 1e7 if i < len(withdrawal_values) else 0.0 for i in range(months)]
    opex_r = [opex_values[i] if i < len(opex_values) else 0.05 for i in range(months)]
    opex_t = [opex_types[i]  if i < len(opex_types)  else 'percentage' for i in range(months)]

    # Per-tranche per-month batch arrays
    emi_batches  = {n: [] for n in TENURES}
    int_batches  = {n: [] for n in TENURES}
    disb_batches = {n: [] for n in TENURES}

    amount_available   = []
    amount_disbursed   = []
    customers_list     = []
    opex_list          = []
    api_list           = []
    marketing_list     = []
    cof_list           = []
    bad_debt_list      = []
    gst_list           = []
    pf_list            = []
    recovery_list      = []
    profit_loss        = []
    aum_list           = []

    emi_recv_by_tranche = {n: [] for n in TENURES}
    int_total_by_tranche = {n: [] for n in TENURES}
    emi_received_total  = []
    interest_total      = []

    for m in range(months):
        if m == 0:
            avail = cap[m]
        else:
            prev_int_per_batch = sum(int_batches[n][m-1] for n in TENURES)
            avail = profit_loss[m-1] + cap[m] + emi_received_total[m-1] - prev_int_per_batch - wdraw[m-1]
        amount_available.append(avail)

        # Disbursed (gross, inflated by PF)
        total_disb = avail / (1.0 - processing_fees)
        amount_disbursed.append(total_disb)

        # Split into tranches — each runs independently
        for n in TENURES:
            td = total_disb * tranche_splits[n]
            disb_batches[n].append(td)
            eb = td * emi_factors[n]
            emi_batches[n].append(eb)
            ib = ((eb * n) - td) / n
            int_batches[n].append(ib)

        # Customers
        customers_list.append(total_disb / avg_ticket_size)

        # OpEx
        if m == 0:
            op = opex_month1_value
        else:
            op = aum_list[m-1] * opex_r[m] if opex_t[m] == 'percentage' else opex_r[m] * 1e7
        opex_list.append(op)

        # API
        nc = total_disb / avg_ticket_size
        api_list.append((nc * 2 * api_cost_20) + (nc * 8 * api_cost_80))

        # Marketing
        marketing_list.append(total_disb * marketing_rate)

        # Cost of Funds (on cumulative capital)
        cof_list.append(sum(cap[:m+1]) * cost_of_funds_rate)

        # Rolling EMI & Interest per tranche (each has its own window)
        emi_total_m = 0.0
        int_total_m = 0.0
        for n in TENURES:
            start = max(0, m - n + 1)
            emi_n = sum(emi_batches[n][start:m+1])
            int_n = sum(int_batches[n][start:m+1])
            emi_recv_by_tranche[n].append(emi_n)
            int_total_by_tranche[n].append(int_n)
            emi_total_m += emi_n
            int_total_m += int_n

        emi_received_total.append(emi_total_m)
        interest_total.append(int_total_m)

        # PF & GST
        pf = total_disb * processing_fees
        pf_list.append(pf)
        gst_list.append(pf * 18.0 / 118.0)

        # Bad Debt
        bad_debt_list.append((total_disb + int_total_m) * (1.0 - t0_col))

        # Recovery
        rec = 0.0
        if m >= 1: rec += (amount_disbursed[m-1] + interest_total[m-1]) * t30_col
        if m >= 2: rec += (amount_disbursed[m-2] + interest_total[m-2]) * t60_col
        if m >= 3: rec += (amount_disbursed[m-3] + interest_total[m-3]) * t90_col
        recovery_list.append(rec)

        # Profit
        revenue = int_total_m + rec + pf
        costs   = op + api_list[m] + marketing_list[m] + cof_list[m] + bad_debt_list[m] + gst_list[m] + wdraw[m]
        profit_loss.append(revenue - costs)

        # AUM
        curr  = total_disb + int_total_m
        prev1 = (amount_disbursed[m-1] + interest_total[m-1]) if m >= 1 else 0.0
        prev2 = (amount_disbursed[m-2] + interest_total[m-2]) if m >= 2 else 0.0
        prev3 = (amount_disbursed[m-3] + interest_total[m-3]) if m >= 3 else 0.0
        aum_list.append(curr + prev1*w1 + prev2*w2 + prev3*w3)

    df = pd.DataFrame({
        'month':             range(1, months+1),
        'amount_invested':   [cap[i]/1e7 for i in range(months)],
        'withdrawal':        [wdraw[i]/1e7 for i in range(months)],
        'amount_available':  [x/1e7 for x in amount_available],
        'amount_disbursed':  [x/1e7 for x in amount_disbursed],
        'disb_3m':           [disb_batches[3][i]/1e7  for i in range(months)],
        'disb_6m':           [disb_batches[6][i]/1e7  for i in range(months)],
        'disb_9m':           [disb_batches[9][i]/1e7  for i in range(months)],
        'disb_12m':          [disb_batches[12][i]/1e7 for i in range(months)],
        'emi_3m':            [emi_recv_by_tranche[3][i]/1e7  for i in range(months)],
        'emi_6m':            [emi_recv_by_tranche[6][i]/1e7  for i in range(months)],
        'emi_9m':            [emi_recv_by_tranche[9][i]/1e7  for i in range(months)],
        'emi_12m':           [emi_recv_by_tranche[12][i]/1e7 for i in range(months)],
        'int_3m':            [int_total_by_tranche[3][i]/1e7  for i in range(months)],
        'int_6m':            [int_total_by_tranche[6][i]/1e7  for i in range(months)],
        'int_9m':            [int_total_by_tranche[9][i]/1e7  for i in range(months)],
        'int_12m':           [int_total_by_tranche[12][i]/1e7 for i in range(months)],
        'customers':         [round(x) for x in customers_list],
        'emi_received_total':[x/1e7 for x in emi_received_total],
        'interest_total':    [x/1e7 for x in interest_total],
        'pf':                [x/1e7 for x in pf_list],
        'recovery':          [x/1e7 for x in recovery_list],
        'opex':              [x/1e7 for x in opex_list],
        'api':               [x/1e7 for x in api_list],
        'marketing':         [x/1e7 for x in marketing_list],
        'cost_of_funds':     [x/1e7 for x in cof_list],
        'bad_debt':          [x/1e7 for x in bad_debt_list],
        'gst':               [x/1e7 for x in gst_list],
        'profit_loss':       [x/1e7 for x in profit_loss],
        'aum':               [x/1e7 for x in aum_list],
    })
    return df

# Guard
if abs(tranche_total - 100.0) > 0.01:
    st.error("⚠️ Tranche splits must sum to exactly 100%. Please fix in the sidebar.")
    st.stop()

df = calculate()
total_capital = sum(capital_values)
final_aum     = df['aum'].iloc[-1]
total_profit  = df['profit_loss'].sum()

# ── TRANCHE OVERVIEW CARDS ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Tranche Configuration</div>', unsafe_allow_html=True)

tc1, tc2, tc3, tc4 = st.columns(4, gap="small")
tranche_meta = [
    (3,  t3,  "t3m",  "🔵 3-Month",  "tc1"),
    (6,  t6,  "t6m",  "🟢 6-Month",  "tc2"),
    (9,  t9,  "t9m",  "🟠 9-Month",  "tc3"),
    (12, t12, "t12m", "🟣 12-Month", "tc4"),
]
sample_disb = (capital_values[0] / (1 - processing_fees)) if capital_values[0] > 0 else 0

for n, pct, css, label, col_var in tranche_meta:
    ef = emi_factors[n]
    td = sample_disb * tranche_splits[n]
    with eval(col_var):
        st.markdown(f"""
        <div class="tranche-card {css}">
            <div class="tranche-title">{label} Tranche</div>
            <div class="tranche-pct">{pct:.0f}%</div>
            <div class="tranche-detail">📐 EMI Factor: <strong>{ef:.6f}</strong></div>
            <div class="tranche-detail">💰 M1 Allocation: <strong>₹{td:.2f} Cr</strong></div>
            <div class="tranche-detail">📅 Rollover Window: <strong>{n} months</strong></div>
        </div>""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

def kpi(color, label, value, trend, icon):
    return f"""<div class="kpi-card kpi-{color}">
        <div class="kpi-header"><div><div class="kpi-label">{label}</div></div><div class="kpi-icon">{icon}</div></div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-trend">{trend}</div></div>"""

# ── ROW 1: 4 cards — Capital, Final AUM, Total Customers, Total Interest ──────
c1, c2, c3, c4 = st.columns(4, gap="small")
with c1: st.markdown(kpi("blue",   "Capital Deployed",     f"₹{total_capital:.1f} Cr",            f"Over {num_months} months",      "💰"), unsafe_allow_html=True)
with c2: st.markdown(kpi("green",  "Final Month AUM",      f"₹{final_aum:.2f} Cr",                f"Month {num_months}",             "🏆"), unsafe_allow_html=True)
with c3: st.markdown(kpi("indigo", "Total Customers",      f"{df['customers'].sum():,}",           "Loans originated",               "👥"), unsafe_allow_html=True)
with c4: st.markdown(kpi("purple", "Total Interest",       f"₹{df['interest_total'].sum():.2f} Cr","All tranches combined",          "💵"), unsafe_allow_html=True)

st.markdown('<div style="margin-top:1.5rem;"></div>', unsafe_allow_html=True)

# ── ROW 2: 3 cards — Processing Fees, Cost of Funds, Total Disbursed ──────────
c5, c6, c7 = st.columns(3, gap="small")
with c5: st.markdown(kpi("blue",   "Total Processing Fees",f"₹{df['pf'].sum():.2f} Cr",           "PF revenue",                     "📄"), unsafe_allow_html=True)
with c6: st.markdown(kpi("orange", "Total Cost of Funds",  f"₹{df['cost_of_funds'].sum():.2f} Cr","Cumulative CoF",                 "💼"), unsafe_allow_html=True)
with c7: st.markdown(kpi("teal",   "Total Disbursed",      f"₹{df['amount_disbursed'].sum():.2f} Cr","All months combined",         "📤"), unsafe_allow_html=True)

# ── CHARTS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Portfolio Insights</div>', unsafe_allow_html=True)

TCOLORS = {3:'#3182ce', 6:'#38a169', 9:'#dd6b20', 12:'#805ad5'}

col1, col2 = st.columns(2)
with col1:
    fig1 = go.Figure()
    for n in TENURES:
        fig1.add_trace(go.Bar(x=df['month'], y=df[f'disb_{n}m'], name=f'{n}M',
            marker_color=TCOLORS[n], opacity=0.88))
    fig1.update_layout(title='Monthly Disbursement by Tranche (Stacked)',
        xaxis=dict(title='Month', dtick=1), yaxis=dict(title='₹ Crores'),
        barmode='stack', height=380, template='plotly_white',
        legend=dict(orientation='h', y=-0.3, x=0.5, xanchor='center'))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    for n in TENURES:
        fig2.add_trace(go.Scatter(x=df['month'], y=df[f'emi_{n}m'], name=f'{n}M EMI',
            mode='lines+markers', line=dict(color=TCOLORS[n], width=2.5), marker=dict(size=6)))
    fig2.add_trace(go.Scatter(x=df['month'], y=df['emi_received_total'], name='Total EMI',
        mode='lines+markers', line=dict(color='#1a365d', width=4, dash='dash'), marker=dict(size=9)))
    fig2.update_layout(title='Rolling EMI Received by Tranche',
        xaxis=dict(title='Month', dtick=1), yaxis=dict(title='₹ Crores'),
        height=380, template='plotly_white',
        legend=dict(orientation='h', y=-0.3, x=0.5, xanchor='center'))
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    fig3 = go.Figure()
    for n in TENURES:
        fig3.add_trace(go.Scatter(x=df['month'], y=df[f'int_{n}m'], name=f'{n}M Interest',
            mode='lines+markers', line=dict(color=TCOLORS[n], width=2.5), marker=dict(size=6)))
    fig3.add_trace(go.Scatter(x=df['month'], y=df['interest_total'], name='Total Interest',
        mode='lines+markers', line=dict(color='#1a365d', width=4, dash='dash'), marker=dict(size=9)))
    fig3.update_layout(title='Rolling Interest Revenue by Tranche',
        xaxis=dict(title='Month', dtick=1), yaxis=dict(title='₹ Crores'),
        height=380, template='plotly_white',
        legend=dict(orientation='h', y=-0.3, x=0.5, xanchor='center'))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df['month'], y=df['aum'], name='AUM',
        fill='tozeroy', fillcolor='rgba(66,153,225,0.15)', line=dict(color='#2b6cb0', width=3)))
    fig4.add_trace(go.Scatter(x=df['month'], y=df['profit_loss'], name='Monthly Profit',
        mode='lines+markers', line=dict(color='#38a169', width=2.5, dash='dot'), marker=dict(size=7), yaxis='y2'))
    fig4.update_layout(title='AUM Growth & Monthly Profit',
        xaxis=dict(title='Month', dtick=1),
        yaxis=dict(title='AUM (₹ Crores)'),
        yaxis2=dict(title='Profit (₹ Crores)', overlaying='y', side='right'),
        height=380, template='plotly_white',
        legend=dict(orientation='h', y=-0.3, x=0.5, xanchor='center'))
    st.plotly_chart(fig4, use_container_width=True)

# ── MONTHLY REGISTER ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Monthly Register</div>', unsafe_allow_html=True)

display_df = df.copy().round(4)
display_df = display_df.rename(columns={
    'month':'Month', 'amount_invested':'Invested (₹Cr)', 'withdrawal':'Withdrawal (₹Cr)',
    'amount_available':'Available (₹Cr)', 'amount_disbursed':'Total Disbursed (₹Cr)',
    'disb_3m':'Disb 3M', 'disb_6m':'Disb 6M', 'disb_9m':'Disb 9M', 'disb_12m':'Disb 12M',
    'emi_3m':'EMI 3M', 'emi_6m':'EMI 6M', 'emi_9m':'EMI 9M', 'emi_12m':'EMI 12M',
    'int_3m':'Int 3M', 'int_6m':'Int 6M', 'int_9m':'Int 9M', 'int_12m':'Int 12M',
    'customers':'Customers', 'emi_received_total':'EMI Total (₹Cr)',
    'interest_total':'Interest Total (₹Cr)', 'pf':'PF (₹Cr)', 'recovery':'Recovery (₹Cr)',
    'opex':'OpEx (₹Cr)', 'api':'API (₹Cr)', 'marketing':'Marketing (₹Cr)',
    'cost_of_funds':'CoF (₹Cr)', 'bad_debt':'Bad Debt (₹Cr)', 'gst':'GST (₹Cr)',
    'profit_loss':'Profit (₹Cr)', 'aum':'AUM (₹Cr)',
})

SUM_COLS = ['Invested (₹Cr)','Withdrawal (₹Cr)','Total Disbursed (₹Cr)',
            'Disb 3M','Disb 6M','Disb 9M','Disb 12M',
            'EMI 3M','EMI 6M','EMI 9M','EMI 12M',
            'Int 3M','Int 6M','Int 9M','Int 12M',
            'Customers','EMI Total (₹Cr)','Interest Total (₹Cr)','PF (₹Cr)',
            'Recovery (₹Cr)','OpEx (₹Cr)','API (₹Cr)','Marketing (₹Cr)',
            'CoF (₹Cr)','GST (₹Cr)','Profit (₹Cr)']
totals_row = {col: '' for col in display_df.columns}
totals_row['Month'] = 'TOTAL'
for col in SUM_COLS:
    totals_row[col] = round(display_df[col].sum(), 4)
display_df = pd.concat([display_df, pd.DataFrame([totals_row])], ignore_index=True)


def to_excel(dataframe):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Multi-Tranche')
        ws = writer.sheets['Multi-Tranche']
        for idx in range(len(dataframe.columns)):
            col_letter = chr(65 + idx) if idx < 26 else chr(64 + idx // 26) + chr(65 + idx % 26)
            max_len = max(dataframe.iloc[:, idx].astype(str).map(len).max(),
                          len(str(dataframe.columns[idx])))
            ws.column_dimensions[col_letter].width = min(max_len + 2, 20)
    buf.seek(0)
    return buf

dl_col, _ = st.columns([1, 3])
with dl_col:
    st.download_button("📥 Download Excel", data=to_excel(display_df),
        file_name=f"NBFC_MultiTranche_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

st.dataframe(display_df, use_container_width=True, hide_index=True, height=450)

# ── FINANCIAL SUMMARY ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Financial Summary</div>', unsafe_allow_html=True)

total_rev  = df['interest_total'].sum() + df['pf'].sum() + df['recovery'].sum()
total_cost = (df['opex'].sum() + df['api'].sum() + df['marketing'].sum() +
              df['cost_of_funds'].sum() + df['bad_debt'].sum() + df['gst'].sum() + df['withdrawal'].sum())

def scard(icon, label, value, css):
    return f"""<div class="summary-card {css}">
        <div class="s-icon">{icon}</div>
        <div><div class="s-label">{label}</div><div class="s-value">{value}</div></div></div>"""

in_col, out_col = st.columns(2, gap="large")
with in_col:
    st.markdown('<h3 style="color:#1a365d;font-weight:700;margin-bottom:1.5rem;">Input Parameters</h3>', unsafe_allow_html=True)
    i1, i2 = st.columns(2)
    with i1:
        st.markdown(scard("📅","Projection Period",    f"{num_months} Months",              "sc-blue"),   unsafe_allow_html=True)
        st.markdown(scard("💳","Avg Ticket Size",      f"₹{avg_ticket_size:,}",             "sc-teal"),   unsafe_allow_html=True)
        st.markdown(scard("💵","Monthly Interest",     f"{monthly_interest_rate_pct:.1f}%", "sc-purple"), unsafe_allow_html=True)
        st.markdown(scard("📄","Processing Fees",      f"{processing_fees_pct:.1f}%",       "sc-indigo"), unsafe_allow_html=True)
        st.markdown(scard("🔵🟢","3M / 6M Split",     f"{t3:.0f}% / {t6:.0f}%",           "sc-blue"),   unsafe_allow_html=True)
    with i2:
        st.markdown(scard("💰","Total Capital",        f"₹{total_capital:.2f} Cr",          "sc-green"),  unsafe_allow_html=True)
        st.markdown(scard("💼","Cost of Funds",        f"{cost_of_funds_rate_pct:.1f}%/mo", "sc-red"),    unsafe_allow_html=True)
        st.markdown(scard("📢","Marketing Rate",       f"{marketing_rate_pct:.1f}%",        "sc-teal"),   unsafe_allow_html=True)
        st.markdown(scard("📊","Total Collection",     f"{total_col_pct:.1f}%",             "sc-orange"), unsafe_allow_html=True)
        st.markdown(scard("🟠🟣","9M / 12M Split",    f"{t9:.0f}% / {t12:.0f}%",          "sc-purple"), unsafe_allow_html=True)

with out_col:
    st.markdown('<h3 style="color:#1a365d;font-weight:700;margin-bottom:1.5rem;">Output Results</h3>', unsafe_allow_html=True)
    o1, o2 = st.columns(2)
    with o1:
        st.markdown(scard("🏆","Final Month AUM",      f"₹{final_aum:.2f} Cr",                         "sc-teal"),   unsafe_allow_html=True)
        st.markdown(scard("📈","Total Revenue",        f"₹{total_rev:.2f} Cr",                         "sc-green"),  unsafe_allow_html=True)
        st.markdown(scard("💵","Total Interest",       f"₹{df['interest_total'].sum():.2f} Cr",        "sc-blue"),   unsafe_allow_html=True)
        st.markdown(scard("📄","Total PF Revenue",     f"₹{df['pf'].sum():.2f} Cr",                   "sc-indigo"), unsafe_allow_html=True)
        st.markdown(scard("👥","Total Customers",      f"{df['customers'].sum():,}",                   "sc-purple"), unsafe_allow_html=True)
    with o2:
        pcss = "sc-orange" if total_profit >= 0 else "sc-red"
        st.markdown(scard("🎯","Net Profit/Loss",      f"₹{total_profit:.2f} Cr",                      pcss),        unsafe_allow_html=True)
        st.markdown(scard("💳","Total Costs",          f"₹{total_cost:.2f} Cr",                        "sc-red"),    unsafe_allow_html=True)
        st.markdown(scard("🔄","Total Recovery",       f"₹{df['recovery'].sum():.2f} Cr",              "sc-green"),  unsafe_allow_html=True)
        st.markdown(scard("📢","Total Marketing",      f"₹{df['marketing'].sum():.2f} Cr",             "sc-teal"),   unsafe_allow_html=True)
        st.markdown(scard("💼","Total CoF",            f"₹{df['cost_of_funds'].sum():.2f} Cr",         "sc-orange"), unsafe_allow_html=True)
