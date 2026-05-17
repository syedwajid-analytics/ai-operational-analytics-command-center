import os
import re
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI

# ======================================================
# PAGE SETUP
# ======================================================
st.set_page_config(
    page_title="AI Operational Analytics Command Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ======================================================
# PLOTLY STYLE
# ======================================================
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [
    "#326295",
    "#78B7E8",
    "#6AA17F",
    "#F4A261",
    "#D64545",
    "#8E9AAF",
]

# ======================================================
# GLOBAL STYLE
# ======================================================
st.markdown(
    """
<style>
    :root {
        --brand: #326295;
        --brand-dark: #24496e;
        --bg: #eef3f8;
        --card: #ffffff;
        --line: #e2e8f0;
        --text: #172033;
        --muted: #64748b;
        --red: #d64545;
        --green: #3fa34d;
        --orange: #f59e0b;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, #f8fbff 0%, transparent 28%),
            linear-gradient(180deg, #eef3f8 0%, #f5f8fc 50%, #edf2f7 100%);
        color: var(--text);
    }

    .main .block-container,
    .block-container {
        max-width: 1600px;
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 1.25rem;
    }

    section.main > div {
        padding-top: 0.8rem;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    header[data-testid="stHeader"] {
        background: rgba(255,255,255,0.86);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #e5eaf0;
    }

    .app-topbar {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding-top: 30px;
        padding-bottom: 24px;
        padding-left: 28px;
        padding-right: 28px;
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
    }

    .app-title {
        font-size: 1.65rem;
        font-weight: 850;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }

    .app-subtitle {
        font-size: 0.86rem;
        color: #64748b;
        margin-top: 6px;
    }

    .top-actions {
        display: flex;
        gap: 8px;
        align-items: center;
        color: #64748b;
        font-size: 0.82rem;
        margin-top: 8px;
    }

    .mini-pill {
        border: 1px solid #dbe5ef;
        background: #f8fafc;
        border-radius: 999px;
        padding: 7px 11px;
        font-weight: 650;
        color: #334155;
        white-space: nowrap;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 850;
        color: #0f172a;
        margin: 10px 0 10px 0;
    }

    .panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 10px;
    }

    .panel-tight {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 10px 12px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        margin-bottom: 10px;
    }

    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.92rem;
        font-weight: 850;
        color: #0f172a;
    }

    .panel-small-text {
        color: #64748b;
        font-size: 0.78rem;
        line-height: 1.45;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
        border: 1px solid #dfe7ef;
        border-radius: 14px;
        padding: 15px 16px;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
        height: 112px;
        min-height: 112px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    [data-testid="stMetricLabel"] {
        color: #475569;
        font-size: 0.82rem;
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: -1px;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.78rem;
        font-weight: 700;
    }

    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[role="radiogroup"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 6px;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
        margin-top: 4px;
        margin-bottom: 8px;
    }

    div[role="radiogroup"] label {
        padding: 8px 10px !important;
        border-radius: 9px !important;
        font-weight: 750 !important;
        color: #334155 !important;
    }

    .ai-callout {
        border-left: 5px solid #326295;
        background: linear-gradient(90deg, #eef6ff 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 12px 14px;
        color: #1e3a5f;
        font-size: 0.9rem;
        line-height: 1.55;
        margin-bottom: 10px;
    }

    .risk-callout {
        border-left: 5px solid #d64545;
        background: linear-gradient(90deg, #fff5f5 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 12px 14px;
        color: #7f1d1d;
        font-size: 0.9rem;
        line-height: 1.55;
        margin-bottom: 10px;
    }

    .good-callout {
        border-left: 5px solid #3fa34d;
        background: linear-gradient(90deg, #f0fff4 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 12px 14px;
        color: #14532d;
        font-size: 0.9rem;
        line-height: 1.55;
        margin-bottom: 10px;
    }

    .small-caption {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: -6px;
        margin-bottom: 8px;
    }

    .stDataFrame {
        border-radius: 12px;
    }

    .chat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    }

    .footer-note {
        text-align: center;
        color: #94a3b8;
        font-size: 0.75rem;
        margin-top: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)
# ======================================================
# OPENAI CLIENT
# ======================================================
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# ======================================================
# DATA GENERATION / LOADING
# ======================================================
REQUIRED_COLUMNS = [
    "RequestID",
    "CustomerName",
    "Channel",
    "Region",
    "Location",
    "ServiceCategory",
    "StatusBucket",
    "PriorityCustomerFlag",
    "AssignedFlag",
    "ApprovedFlag",
    "RejectedFlag",
    "ClosedFlag",
    "ResolutionDays",
    "FirstResponseMinutes",
    "CustomerAge",
    "CustomerSegment",
    "MonthlyIncome",
    "SatisfactionRating",
    "CreatedDate",
    "CompletionDate",
]


def generate_demo_data(rows: int = 1800) -> pd.DataFrame:
    np.random.seed(42)

    now = pd.Timestamp.now().floor("h")

    channels = ["Web", "Email", "Phone", "WhatsApp", "Chat", "Branch"]
    regions = ["North", "South", "East", "West", "Central"]
    locations = ["Al Warqa", "Jumeirah", "Dubai South", "Al Aweer", "Nad Al Sheba", "Mirdif", "Al Barsha", "Business Bay"]
    categories = ["Permit Request", "Customer Support", "Service Approval", "Document Review", "Field Inspection"]
    segments = ["Individual", "Priority", "Corporate", "Standard"]

    # Create realistic created dates: stronger activity in the latest days + random hours.
    recent_rows = int(rows * 0.38)
    older_rows = rows - recent_rows

    recent_hours_back = np.random.randint(0, 24 * 14, size=recent_rows)
    older_days_back = np.random.randint(15, 420, size=older_rows)
    older_hours = np.random.randint(0, 24, size=older_rows)

    recent_dates = [now - pd.Timedelta(hours=int(h)) for h in recent_hours_back]
    older_dates = [now - pd.Timedelta(days=int(d), hours=int(h)) for d, h in zip(older_days_back, older_hours)]
    created_dates = np.array(recent_dates + older_dates)
    np.random.shuffle(created_dates)

    # Status logic: more operational variety, not flat.
    statuses = np.random.choice(
        ["Open", "On Hold", "Overdue", "Due Today", "Closed", "Rejected"],
        rows,
        p=[0.26, 0.12, 0.08, 0.05, 0.43, 0.06],
    )

    # Make last 24 hours more active and realistic.
    created_series = pd.to_datetime(created_dates)
    last_24_mask = created_series >= (now - pd.Timedelta(hours=24))
    statuses[last_24_mask] = np.random.choice(
        ["Open", "On Hold", "Overdue", "Due Today", "Closed", "Rejected"],
        last_24_mask.sum(),
        p=[0.36, 0.15, 0.10, 0.12, 0.22, 0.05],
    )

    resolution_days = np.random.gamma(shape=2.8, scale=5.5, size=rows).round(1)
    first_response_minutes = np.random.gamma(shape=2.1, scale=18, size=rows).round(0)

    completion_dates = []
    for created, status, res_days in zip(created_series, statuses, resolution_days):
        if status in ["Closed", "Rejected"]:
            completion_dates.append(created + pd.Timedelta(days=float(res_days)))
        else:
            completion_dates.append(pd.NaT)

    data = pd.DataFrame(
        {
            "RequestID": np.arange(100001, 100001 + rows),
            "CustomerName": [f"Customer {i:04d}" for i in range(1, rows + 1)],
            "Channel": np.random.choice(channels, rows, p=[0.32, 0.25, 0.16, 0.10, 0.12, 0.05]),
            "Region": np.random.choice(regions, rows, p=[0.20, 0.18, 0.22, 0.16, 0.24]),
            "Location": np.random.choice(locations, rows, p=[0.16, 0.13, 0.15, 0.11, 0.12, 0.13, 0.10, 0.10]),
            "ServiceCategory": np.random.choice(categories, rows, p=[0.26, 0.24, 0.22, 0.16, 0.12]),
            "StatusBucket": statuses,
            "PriorityCustomerFlag": np.random.choice([0, 1], rows, p=[0.78, 0.22]),
            "AssignedFlag": np.random.choice([0, 1], rows, p=[0.13, 0.87]),
            "CustomerAge": np.random.randint(24, 68, rows),
            "CustomerSegment": np.random.choice(segments, rows, p=[0.42, 0.20, 0.16, 0.22]),
            "MonthlyIncome": np.random.randint(7000, 42000, rows),
            "ResolutionDays": resolution_days,
            "FirstResponseMinutes": first_response_minutes,
            "SatisfactionRating": np.random.choice(["Good", "Okay", "Bad"], rows, p=[0.72, 0.18, 0.10]),
            "CreatedDate": created_series,
            "CompletionDate": pd.to_datetime(completion_dates),
        }
    )

    # Make some service categories visibly slower/riskier.
    inspection_mask = data["ServiceCategory"] == "Field Inspection"
    review_mask = data["ServiceCategory"] == "Document Review"
    data.loc[inspection_mask, "ResolutionDays"] = data.loc[inspection_mask, "ResolutionDays"] * 1.55
    data.loc[review_mask, "ResolutionDays"] = data.loc[review_mask, "ResolutionDays"] * 1.25

    data["ClosedFlag"] = (data["StatusBucket"] == "Closed").astype(int)
    data["ApprovedFlag"] = data["ClosedFlag"]
    data["RejectedFlag"] = (data["StatusBucket"] == "Rejected").astype(int)

    return data


@st.cache_data
def load_data() -> pd.DataFrame:
    # For public portfolio demo, use generated anonymized data by default.
    # This avoids old sample_data.csv files creating Unknown/0-heavy dashboards.
    use_local_csv = False
    file_path = "sample_data.csv"

    if use_local_csv and os.path.exists(file_path):
        data = pd.read_csv(file_path)
    else:
        data = generate_demo_data(1800)

    rename_map = {
        "ApplicationNo": "RequestID",
        "ApplicantName": "CustomerName",
        "ApplicantAge": "CustomerAge",
        "MaritalStatus": "CustomerSegment",
        "ServiceType": "ServiceCategory",
        "ProjectName": "InitiativeName",
        "WidowFlag": "PriorityCustomerFlag",
        "DaysToDecision": "ResolutionDays",
        "NetIncome": "MonthlyIncome",
        "CompletionDate": "CompletionDate",
    }
    data = data.rename(columns={k: v for k, v in rename_map.items() if k in data.columns})

    for col in REQUIRED_COLUMNS:
        if col not in data.columns:
            if col in ["PriorityCustomerFlag", "AssignedFlag", "ApprovedFlag", "RejectedFlag", "ClosedFlag"]:
                data[col] = 0
            elif col in ["ResolutionDays", "FirstResponseMinutes", "CustomerAge", "MonthlyIncome"]:
                data[col] = 0
            elif col in ["CreatedDate", "CompletionDate"]:
                data[col] = pd.NaT
            else:
                data[col] = "Unknown"

    for date_col in ["CreatedDate", "CompletionDate"]:
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")

    for num_col in [
        "PriorityCustomerFlag",
        "AssignedFlag",
        "ApprovedFlag",
        "RejectedFlag",
        "ClosedFlag",
        "ResolutionDays",
        "FirstResponseMinutes",
        "CustomerAge",
        "MonthlyIncome",
    ]:
        data[num_col] = pd.to_numeric(data[num_col], errors="coerce").fillna(0)

    return data


df = load_data()

# ======================================================
# HELPERS
# ======================================================

def safe_percent(numerator, denominator):
    return round((numerator / denominator) * 100, 1) if denominator else 0


def filter_last_period(data: pd.DataFrame, period_label: str) -> pd.DataFrame:
    if "CreatedDate" not in data.columns or data["CreatedDate"].isna().all():
        return data.copy()

    max_date = data["CreatedDate"].max()

    if period_label == "Last 24 Hours":
        cutoff = max_date - pd.Timedelta(days=1)
    elif period_label == "Last 7 Days":
        cutoff = max_date - pd.Timedelta(days=7)
    elif period_label == "Last 30 Days":
        cutoff = max_date - pd.Timedelta(days=30)
    elif period_label == "Last 90 Days":
        cutoff = max_date - pd.Timedelta(days=90)
    else:
        return data.copy()

    return data[data["CreatedDate"] >= cutoff].copy()


def build_hourly_stats(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    work = data.copy()
    work = work.dropna(subset=["CreatedDate"])

    work["Hour"] = work["CreatedDate"].dt.hour

    hourly = (
        work.groupby("Hour")
        .agg(
            Requests=("RequestID", "count"),
            Closed=("ClosedFlag", "sum"),
        )
        .reset_index()
    )

    full_hours = pd.DataFrame({"Hour": list(range(24))})
    hourly = full_hours.merge(hourly, on="Hour", how="left").fillna(0)

    hourly["HourLabel"] = hourly["Hour"].apply(
        lambda h: f"{h}:00"
    )

    return hourly


def build_monthly_trend(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    work = data.copy()
    work = work.dropna(subset=["CreatedDate"])

    work["Month"] = work["CreatedDate"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        work.groupby("Month")
        .agg(
            Requests=("RequestID", "count"),
            Closed=("ClosedFlag", "sum"),
        )
        .reset_index()
        .sort_values("Month")
    )

    return monthly


def build_forecast_frame(monthly: pd.DataFrame, periods=3):
    if monthly.empty:
        return pd.DataFrame()

    recent_avg = monthly["Requests"].tail(3).mean()

    future_months = pd.date_range(
        monthly["Month"].max() + pd.offsets.MonthBegin(1),
        periods=periods,
        freq="MS"
    )

    values = [round(recent_avg * (1 + (i * 0.03)), 1) for i in range(periods)]

    return pd.DataFrame(
        {
            "Month": future_months,
            "ForecastRequests": values,
        }
    )


def compute_risk_table(data: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if data.empty or group_col not in data.columns:
        return pd.DataFrame()

    work = data.copy()
    work["PendingFlag"] = work["StatusBucket"].isin(["Open", "On Hold", "Overdue", "Due Today"]).astype(int)

    table = (
        work.groupby(group_col)
        .agg(
            Requests=("RequestID", "count"),
            Closed=("ClosedFlag", "sum"),
            Rejected=("RejectedFlag", "sum"),
            Pending=("PendingFlag", "sum"),
            AvgResolutionDays=("ResolutionDays", "mean"),
            Unassigned=("AssignedFlag", lambda s: int((s == 0).sum())),
        )
        .reset_index()
    )

    table["ClosureRate"] = (table["Closed"] / table["Requests"] * 100).round(1)
    table["RejectionRate"] = (table["Rejected"] / table["Requests"] * 100).round(1)
    table["AvgResolutionDays"] = table["AvgResolutionDays"].round(1)

    max_days = table["AvgResolutionDays"].max() or 1
    max_pending = table["Pending"].max() or 1
    max_unassigned = table["Unassigned"].max() or 1

    table["RiskScore"] = (
        (100 - table["ClosureRate"]) * 0.35
        + (table["AvgResolutionDays"] / max_days * 100) * 0.30
        + (table["Pending"] / max_pending * 100) * 0.22
        + (table["Unassigned"] / max_unassigned * 100) * 0.13
    ).round(1)

    return table.sort_values("RiskScore", ascending=False).reset_index(drop=True)


def ask_ai(question: str, data: pd.DataFrame) -> str:
    total = len(data)
    open_count = int((data["StatusBucket"] == "Open").sum()) if "StatusBucket" in data.columns else 0
    overdue = int((data["StatusBucket"] == "Overdue").sum()) if "StatusBucket" in data.columns else 0
    on_hold = int((data["StatusBucket"] == "On Hold").sum()) if "StatusBucket" in data.columns else 0
    closed = int(data["ClosedFlag"].sum()) if "ClosedFlag" in data.columns else 0
    unassigned = int((data["AssignedFlag"] == 0).sum()) if "AssignedFlag" in data.columns else 0
    closure_rate = safe_percent(closed, total)
    avg_resolution = round(float(data["ResolutionDays"].mean()), 1) if total else 0

    loc_risk = compute_risk_table(data, "Location")
    cat_risk = compute_risk_table(data, "ServiceCategory")
    top_location = loc_risk.iloc[0]["Location"] if not loc_risk.empty else "N/A"
    top_category = cat_risk.iloc[0]["ServiceCategory"] if not cat_risk.empty else "N/A"

    if client is None:
        q = question.lower()
        if "location" in q or "area" in q:
            return f"Highest risk location is {top_location}. Current view has {total:,} requests, {overdue:,} overdue, {on_hold:,} on hold, and {unassigned:,} unassigned. Focus first on the queue with high pending and slower resolution."
        if "service" in q or "category" in q:
            return f"Highest risk service category is {top_category}. Average resolution time is {avg_resolution} days and closure rate is {closure_rate}%. Review workload distribution and aged requests in this category."
        if "overdue" in q or "risk" in q or "problem" in q or "delay" in q or "why" in q:
            return f"Main operational risk: {overdue:,} overdue requests, {on_hold:,} on-hold requests, and {unassigned:,} unassigned requests. The first review should focus on {top_location} and {top_category}."
        if "total" in q or "how many" in q or "count" in q:
            return f"Total requests under current filters: {total:,}. Closed: {closed:,}. Open: {open_count:,}. Overdue: {overdue:,}. Closure rate: {closure_rate}%."
        return f"Current filtered view has {total:,} requests, {closure_rate}% closure rate, {overdue:,} overdue requests, {unassigned:,} unassigned requests, and {avg_resolution} average resolution days."

    sample = data.head(20).to_dict(orient="records")
    prompt = f"""
You are an executive analytics assistant for a safe demo dashboard.
Answer in a concise business style. Do not mention private companies or real organizations.

Current KPI context:
- Total requests: {total}
- Open requests: {open_count}
- On-hold requests: {on_hold}
- Overdue requests: {overdue}
- Unassigned requests: {unassigned}
- Closed requests: {closed}
- Closure rate: {closure_rate}%
- Avg resolution days: {avg_resolution}
- Highest risk location: {top_location}
- Highest risk service category: {top_category}

Sample rows:
{json.dumps(sample, default=str)}

Question: {question}
"""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return response.output_text.strip()
    except Exception as e:
        return f"AI response could not be generated. Fallback insight: total requests {total:,}, closure rate {closure_rate}%, overdue {overdue:,}. Error: {e}"


def render_ai_panel(data: pd.DataFrame, title: str = "AI Analytics Assistant", key_prefix: str = "global"):
    if f"{key_prefix}_messages" not in st.session_state:
        st.session_state[f"{key_prefix}_messages"] = []

    st.markdown('<div class="panel"><div class="panel-header">🤖 ' + title + '</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="ai-callout">
Ask questions like: <b>What is the main risk?</b>, <b>Which location needs attention?</b>,
<b>Which service category is slow?</b>, or <b>Summarize this dashboard for management.</b>
</div>
""",
        unsafe_allow_html=True,
    )

    history = st.session_state[f"{key_prefix}_messages"]
    if history:
        with st.expander("Conversation history", expanded=True):
            for msg in history[-6:]:
                role = "You" if msg["role"] == "user" else "AI"
                st.markdown(f"**{role}:** {msg['content']}")

    with st.form(f"{key_prefix}_ai_form", clear_on_submit=True):
        question = st.text_input("Ask AI about this page", placeholder="Example: Which location has the highest risk?")
        submitted = st.form_submit_button("Ask AI")

    if submitted and question.strip():
        answer = ask_ai(question.strip(), data)
        history.append({"role": "user", "content": question.strip()})
        history.append({"role": "assistant", "content": answer})
        st.session_state[f"{key_prefix}_messages"] = history
        st.rerun()

    if st.button("Clear AI Chat", key=f"{key_prefix}_clear"):
        st.session_state[f"{key_prefix}_messages"] = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ======================================================
# TOP BAR
# ======================================================
st.markdown(
    """
<div class="app-topbar">
    <div>
        <div class="app-title">AI Operational Analytics Command Center</div>
        <div class="app-subtitle">Enterprise-style monitoring, forecasting, diagnostics, and conversational analytics</div>
    </div>
    <div class="top-actions">
        <span class="mini-pill">🤖 AI Enabled</span>
        <span class="mini-pill">Demo Data</span>
        <span class="mini-pill">Public Safe</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ======================================================
# FILTER BAR
# ======================================================
filter_cols = st.columns([1, 1, 1, 1, 1.2])
with filter_cols[0]:
    period = st.selectbox("Period", ["All Time", "Last 90 Days", "Last 30 Days", "Last 7 Days", "Last 24 Hours"], index=0)
with filter_cols[1]:
    region = st.selectbox("Region", ["All"] + sorted(df["Region"].dropna().astype(str).unique().tolist()))
with filter_cols[2]:
    location = st.selectbox("Location", ["All"] + sorted(df["Location"].dropna().astype(str).unique().tolist()))
with filter_cols[3]:
    category = st.selectbox("Service", ["All"] + sorted(df["ServiceCategory"].dropna().astype(str).unique().tolist()))
with filter_cols[4]:
    status = st.selectbox("Status", ["All"] + sorted(df["StatusBucket"].dropna().astype(str).unique().tolist()))

filtered = filter_last_period(df, period)
if region != "All":
    filtered = filtered[filtered["Region"].astype(str) == region]
if location != "All":
    filtered = filtered[filtered["Location"].astype(str) == location]
if category != "All":
    filtered = filtered[filtered["ServiceCategory"].astype(str) == category]
if status != "All":
    filtered = filtered[filtered["StatusBucket"].astype(str) == status]

# ======================================================
# NAVIGATION
# ======================================================
view = st.radio(
    "View",
    ["Overview Dashboard", "Operational Diagnostics", "Customer & Channel", "AI Assistant"],
    horizontal=True,
    label_visibility="collapsed",
)


# ======================================================
# KPI SUMMARY
# ======================================================

total_requests = len(filtered)
open_requests = int((filtered["StatusBucket"] == "Open").sum()) if total_requests else 0
on_hold = int((filtered["StatusBucket"] == "On Hold").sum()) if total_requests else 0
overdue = int((filtered["StatusBucket"] == "Overdue").sum()) if total_requests else 0
due_today = int((filtered["StatusBucket"] == "Due Today").sum()) if total_requests else 0
unassigned = int((filtered["AssignedFlag"] == 0).sum()) if total_requests else 0
closed = int(filtered["ClosedFlag"].sum()) if total_requests else 0
closure_rate = safe_percent(closed, total_requests)
backlog = int((filtered["StatusBucket"].isin(["Open", "On Hold", "Overdue", "Due Today"])).sum()) if total_requests else 0
avg_resolution = round(float(filtered["ResolutionDays"].mean()), 1) if total_requests else 0
avg_first_response = round(float(filtered["FirstResponseMinutes"].mean()), 1) if total_requests else 0

# First KPI Row
k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Open Requests",
        f"{open_requests:,}",
        delta=f"{safe_percent(open_requests, total_requests)}%"
    )

with k2:
    st.metric(
        "On Hold Requests",
        f"{on_hold:,}"
    )

with k3:
    st.metric(
        "Overdue Requests",
        f"{overdue:,}",
        delta="Needs review",
        delta_color="inverse"
    )

# Second KPI Row
k4, k5, k6 = st.columns(3)

with k4:
    st.metric(
        "Due Today",
        f"{due_today:,}"
    )

with k5:
    st.metric(
        "Unassigned",
        f"{unassigned:,}",
        delta="Check queue",
        delta_color="inverse"
    )

with k6:
    st.metric(
        "Closed Requests",
        f"{closed:,}",
        delta=f"{closure_rate}%")
# ======================================================
# OVERVIEW DASHBOARD
# ======================================================
if view == "Overview Dashboard":
    st.markdown('<div class="section-title">Request Stats</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("New Requests", f"{total_requests:,}", "Current filtered scope")
    with c2:
        st.metric("On Hold", f"{on_hold:,}")
    with c3:
        st.metric("Closed", f"{closed:,}", f"{closure_rate}% closure")
    with c4:
        st.metric("Backlog", f"{backlog:,}", "Open + hold + overdue")

    hourly = build_hourly_stats(filtered)
    with st.container():
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-header"><span>Hourly Request Movement</span><span class="panel-small-text">Bars = requests, line = closed</span></div>',
            unsafe_allow_html=True
        )
        if not hourly.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=hourly["HourLabel"],
                y=hourly["Requests"],
                name="Requests",
                text=hourly["Requests"],
                textposition="outside"
            ))
            fig.add_trace(go.Scatter(
                x=hourly["HourLabel"],
                y=hourly["Closed"],
                name="Closed",
                mode="lines+markers",
                yaxis="y2"
            ))
            fig.update_traces(textfont_size=11)
            fig.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=35, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                uniformtext_minsize=8,
                uniformtext_mode="hide",
                yaxis=dict(title="Requests"),
                yaxis2=dict(title="Closed", overlaying="y", side="right", showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    left, middle, right = st.columns([1, 1, 1])

    with left:
        st.markdown('<div class="panel"><div class="panel-header">Traffic Analysis</div>', unsafe_allow_html=True)
        channel = filtered.groupby("Channel").size().reset_index(name="Requests").sort_values("Requests", ascending=False)
        if not channel.empty:
            fig = px.pie(channel, names="Channel", values="Requests", hole=0.62)
            fig.update_traces(textposition="inside", textinfo="percent")
            fig.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with middle:
        st.markdown('<div class="panel"><div class="panel-header">Average Handling Time</div>', unsafe_allow_html=True)
        response_time = avg_first_response
        resolution_time = avg_resolution * 24
        holding_time = round(float(filtered[filtered["StatusBucket"] == "On Hold"]["ResolutionDays"].mean() * 24), 1) if on_hold else 0
        handling = pd.DataFrame(
            {
                "Metric": ["First Response", "Resolution Time", "Hold Queue Time"],
                "Hours": [round(response_time / 60, 1), round(resolution_time, 1), holding_time],
            }
        )
        fig = px.bar(handling, x="Hours", y="Metric", orientation="h", text="Hours")
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel"><div class="panel-header">Satisfaction Ratings</div>', unsafe_allow_html=True)
        rating = filtered.groupby("SatisfactionRating").size().reset_index(name="Requests")
        if not rating.empty:
            fig = px.pie(rating, names="SatisfactionRating", values="Requests", hole=0.62)
            fig.update_traces(textposition="inside", textinfo="percent")
            fig.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    monthly = build_monthly_trend(filtered)
    forecast = build_forecast_frame(monthly)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="panel"><div class="panel-header">Monthly Trend + Forecast</div>', unsafe_allow_html=True)
        if not monthly.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Requests"], mode="lines+markers", name="Actual Requests"))
            if not forecast.empty:
                fig.add_trace(go.Scatter(x=forecast["Month"], y=forecast["ForecastRequests"], mode="lines+markers", name="Forecast", line=dict(dash="dot")))
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-header">AI Executive Summary</div>', unsafe_allow_html=True)
        if overdue > 0 or backlog > total_requests * 0.35:
            st.markdown(f'<div class="risk-callout"><b>Risk:</b> {overdue:,} overdue requests and {backlog:,} backlog items require attention. Focus on highest-risk service categories first.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="good-callout"><b>Stable:</b> Closure rate is {closure_rate}% and overdue volume is currently controlled under the selected filters.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-callout"><b>AI note:</b> Average resolution is {avg_resolution} days. Unassigned workload is {unassigned:,}. Review resource allocation if unassigned volume increases.</div>', unsafe_allow_html=True)
        if not forecast.empty:
            st.dataframe(forecast, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# OPERATIONAL DIAGNOSTICS
# ======================================================
elif view == "Operational Diagnostics":
    loc_risk = compute_risk_table(filtered, "Location")
    cat_risk = compute_risk_table(filtered, "ServiceCategory")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="panel"><div class="panel-header">Location Risk Ranking</div>', unsafe_allow_html=True)
        if not loc_risk.empty:
            st.dataframe(loc_risk, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-header">Service Category Risk Ranking</div>', unsafe_allow_html=True)
        if not cat_risk.empty:
            st.dataframe(cat_risk, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="panel"><div class="panel-header">Risk Score by Location</div>', unsafe_allow_html=True)
        if not loc_risk.empty:
            fig = px.bar(loc_risk.head(10), x="RiskScore", y="Location", orientation="h", text="RiskScore")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="panel"><div class="panel-header">Pending by Category</div>', unsafe_allow_html=True)
        if not cat_risk.empty:
            fig = px.bar(cat_risk, x="ServiceCategory", y="Pending", text="Pending")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# CUSTOMER & CHANNEL
# ======================================================
elif view == "Customer & Channel":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="panel"><div class="panel-header">Customer Segments</div>', unsafe_allow_html=True)
        seg = filtered.groupby("CustomerSegment").size().reset_index(name="Requests").sort_values("Requests", ascending=False)
        fig = px.bar(seg, x="CustomerSegment", y="Requests", text="Requests")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-header">Channel Mix</div>', unsafe_allow_html=True)
        channel = filtered.groupby("Channel").size().reset_index(name="Requests")
        fig = px.pie(channel, names="Channel", values="Requests", hole=0.55)
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel"><div class="panel-header">Priority Customers</div>', unsafe_allow_html=True)
        priority = filtered.groupby("PriorityCustomerFlag").size().reset_index(name="Requests")
        priority["Type"] = priority["PriorityCustomerFlag"].map({0: "Standard", 1: "Priority"}).fillna("Unknown")
        fig = px.pie(priority, names="Type", values="Requests", hole=0.55)
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-header">Customer Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(filtered[["RequestID", "CustomerName", "CustomerSegment", "Channel", "Region", "Location", "ServiceCategory", "StatusBucket", "SatisfactionRating"]].head(200), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# AI ASSISTANT
# ======================================================
elif view == "AI Assistant":
    render_ai_panel(filtered, title="Conversational Analytics Assistant", key_prefix="main_ai")

# AI panel available on every non-AI page
if view != "AI Assistant":
    render_ai_panel(filtered, title=f"AI Assistant for {view}", key_prefix=view.lower().replace(" ", "_").replace("&", "and"))

# ======================================================
# FOOTER
# ======================================================
st.markdown('<div class="footer-note">Portfolio demo • anonymized sample data • built for AI-ready enterprise analytics</div>', unsafe_allow_html=True)
