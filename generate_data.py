import os
import re
import json
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# -------------------------------------------------------
# Page setup
# -------------------------------------------------------
st.set_page_config(
    page_title="Housing Applications Intelligence Hub",
    page_icon="🏠",
    layout="wide"
)

# -------------------------------------------------------
# Styling
# -------------------------------------------------------
st.markdown("""
<style>
    :root {
        --brand-primary: #2f6bff;
        --brand-primary-dark: #1f4ed8;
        --brand-soft: #eef4ff;
        --brand-bg: #f6f8fc;
        --brand-surface: #ffffff;
        --brand-border: #dce6f5;
        --brand-text: #142033;
        --brand-muted: #6b7a90;
        --brand-shadow: 0 12px 28px rgba(20, 32, 51, 0.08);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(47, 107, 255, 0.08), transparent 28%),
            linear-gradient(135deg, #fbfcff 0%, var(--brand-bg) 50%, #eef3fb 100%);
    }

    .block-container {
        max-width: 1420px;
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
    }

    .top-banner {
        background: linear-gradient(90deg, #173166 0%, #2557cc 60%, #2f6bff 100%);
        color: white;
        padding: 24px 26px;
        border-radius: 22px;
        margin-bottom: 16px;
        box-shadow: 0 14px 34px rgba(23, 49, 102, 0.20);
        border: 1px solid rgba(255,255,255,0.10);
    }

    .top-banner-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .top-banner-subtitle {
        font-size: 0.98rem;
        opacity: 0.94;
        line-height: 1.6;
        max-width: 960px;
    }

    .panel {
        background: var(--brand-surface);
        border-radius: 20px;
        border: 1px solid var(--brand-border);
        box-shadow: var(--brand-shadow);
        padding: 18px;
        margin-bottom: 16px;
    }

    .panel-title {
        font-size: 1.02rem;
        font-weight: 800;
        color: var(--brand-text);
        margin-bottom: 14px;
    }

    .filter-wrap {
        background: rgba(255,255,255,0.84);
        border: 1px solid var(--brand-border);
        border-radius: 18px;
        box-shadow: 0 8px 20px rgba(20, 32, 51, 0.04);
        padding: 14px 14px 6px 14px;
        margin-bottom: 16px;
    }

    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 18px;
    }

    .kpi-card {
        background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
        border-radius: 18px;
        min-height: 126px;
        padding: 16px 18px;
        border: 1px solid var(--brand-border);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 8px;
    }

    .kpi-topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .kpi-icon {
        width: 36px;
        height: 36px;
        border-radius: 12px;
        background: var(--brand-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }

    .kpi-label {
        font-size: 0.82rem;
        color: var(--brand-muted);
        font-weight: 700;
        letter-spacing: 0.2px;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--brand-text);
        line-height: 1.1;
    }

    .mini-note {
        color: var(--brand-muted);
        font-size: 0.82rem;
        line-height: 1.5;
    }

    .chart-title {
        font-size: 1rem;
        font-weight: 800;
        color: var(--brand-text);
        margin-bottom: 8px;
    }

    .svc-card {
        background: #ffffff;
        border: 1px solid var(--brand-border);
        border-radius: 22px;
        padding: 18px 18px 16px 18px;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
        min-height: 300px;
        direction: rtl;
        text-align: center;
    }

    .svc-title {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        color: white;
        font-size: 1rem;
        font-weight: 800;
        text-align: center;
        padding: 11px 12px;
        border-radius: 14px;
        margin-bottom: 16px;
        width: 100%;
        display: block;
    }

    .svc-title.green {
        background: linear-gradient(135deg, #15803d 0%, #22c55e 100%);
    }

    .svc-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px 14px;
        align-items: stretch;
        justify-items: stretch;
    }

    .svc-grid > div {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        min-height: 76px;
        padding: 4px 4px;
        background: #fbfdff;
        border-radius: 14px;
        border: 1px solid #edf2fa;
    }

    .svc-metric-label {
        color: #425466;
        font-size: 0.84rem;
        margin-bottom: 6px;
        text-align: center;
        width: 100%;
        line-height: 1.4;
    }

    .svc-metric-value {
        color: var(--brand-text);
        font-size: 1.45rem;
        font-weight: 800;
        text-align: center;
        width: 100%;
        line-height: 1.15;
    }

    .svc-note {
        color: var(--brand-muted);
        font-size: 0.78rem;
        line-height: 1.7;
        margin-top: 12px;
        text-align: center;
    }

    .dash-note {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
        padding: 12px 14px;
        border-radius: 14px;
        margin-top: 10px;
        font-size: 0.92rem;
        text-align: center;
        line-height: 1.7;
    }

    .rich-answer-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border-left: 6px solid var(--brand-primary);
        border-radius: 18px;
        border: 1px solid var(--brand-border);
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 8px 18px rgba(39, 73, 109, 0.08);
    }

    .rich-answer-title {
        font-size: 1rem;
        font-weight: 800;
        color: var(--brand-text);
        margin-bottom: 8px;
    }

    .rich-answer-main {
        font-size: 1.18rem;
        font-weight: 800;
        color: var(--brand-primary-dark);
        line-height: 1.4;
        margin-bottom: 8px;
    }

    .rich-answer-detail {
        font-size: 0.94rem;
        color: #425466;
        line-height: 1.65;
        margin-bottom: 10px;
    }

    .rich-answer-meta {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 10px;
    }

    .rich-answer-chip {
        background: var(--brand-soft);
        color: var(--brand-primary-dark);
        border: 1px solid #cfe0ff;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.76rem;
        font-weight: 700;
    }

    div[data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--brand-border);
        border-radius: 16px;
        padding: 8px 10px;
        margin-bottom: 10px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--brand-border);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f9fbfd 0%, #eef3f8 100%);
        border-right: 1px solid var(--brand-border);
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# OpenAI client
# -------------------------------------------------------
api_key = os.environ.get("OPENAI_API_KEY")
client = None
if api_key and OpenAI is not None:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None


# -------------------------------------------------------
# Demo data generation
# -------------------------------------------------------
def make_demo_data(rows=1800, seed=42):
    random.seed(seed)

    names = [
        "Ahmed Ali", "Fatima Hassan", "Mohammed Saeed", "Aisha Khalid", "Omar Nasser",
        "Mariam Rashid", "Yousef Salem", "Noor Abdullah", "Huda Mahmood", "Ali Ibrahim",
        "Sara Hamad", "Khalid Majid", "Zainab Abbas", "Hamad Jassim", "Reem Tariq"
    ]
    locations = ["Abu Dhabi", "Al Ain", "Dubai", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
    region_map = {
        "Abu Dhabi": "Central",
        "Al Ain": "East",
        "Dubai": "West",
        "Sharjah": "North",
        "Ajman": "North",
        "Ras Al Khaimah": "North",
        "Fujairah": "East",
        "Umm Al Quwain": "North"
    }
    projects = [
        "Palm Residences", "Desert Homes", "Community Towers", "Oasis Villas",
        "Skyline Residences", "Lagoon Homes", "Pearl Community", "Al Noor Villas"
    ]
    service_types = ["Grant", "Loan"]
    marital_statuses = ["Single", "Married", "Widowed", "Divorced"]
    genders = ["Male", "Female"]
    statuses = ["Approved", "Rejected", "In Progress", "On Hold"]
    status_weights = [0.52, 0.16, 0.22, 0.10]

    coords = {
        "Abu Dhabi": (24.4539, 54.3773),
        "Al Ain": (24.1917, 55.7606),
        "Dubai": (25.2048, 55.2708),
        "Sharjah": (25.3463, 55.4209),
        "Ajman": (25.4052, 55.5136),
        "Ras Al Khaimah": (25.8007, 55.9762),
        "Fujairah": (25.1288, 56.3265),
        "Umm Al Quwain": (25.5647, 55.5552),
    }

    start_date = datetime(2023, 1, 1)
    rows_out = []

    for i in range(rows):
        app_no = 1000 + i
        location = random.choice(locations)
        region = region_map[location]
        project = random.choice(projects)
        service_type = random.choices(service_types, weights=[0.48, 0.52], k=1)[0]
        marital = random.choices(marital_statuses, weights=[0.20, 0.58, 0.12, 0.10], k=1)[0]
        gender = random.choice(genders)
        status = random.choices(statuses, weights=status_weights, k=1)[0]

        approved = 1 if status == "Approved" else 0
        rejected = 1 if status == "Rejected" else 0
        widow_flag = 1 if marital == "Widowed" else 0

        age = random.randint(24, 58)
        income = random.randint(7000, 42000)

        if service_type == "Grant":
            allowed_loan_value = random.randint(850000, 1250000)
        else:
            allowed_loan_value = random.randint(250000, 950000)

        if status in ["Approved", "Rejected"]:
            days_to_decision = random.randint(8, 120)
        elif status == "In Progress":
            days_to_decision = random.randint(15, 180)
        else:
            days_to_decision = random.randint(20, 220)

        no_units = random.randint(1, 4)
        base_lat, base_lon = coords[location]
        lat = base_lat + random.uniform(-0.06, 0.06)
        lon = base_lon + random.uniform(-0.06, 0.06)

        completion_date = start_date + timedelta(days=random.randint(0, 1100))

        rows_out.append({
            "ApplicationNo": app_no,
            "CustomerName": random.choice(names),
            "Gender": gender,
            "ApplicantAge": age,
            "NetIncome": income,
            "Location": location,
            "Region": region,
            "ProjectName": project,
            "MaritalStatus": marital,
            "WidowFlag": widow_flag,
            "ServiceType": service_type,
            "StatusBucket": status,
            "ApprovedFlag": approved,
            "RejectedFlag": rejected,
            "DaysToDecision": days_to_decision,
            "AllowedLoanValue": allowed_loan_value,
            "NoUnits": no_units,
            "Latitude": round(lat, 6),
            "Longitude": round(lon, 6),
            "CompletionDate": completion_date.strftime("%Y-%m-%d")
        })

    return pd.DataFrame(rows_out)


@st.cache_data
def load_data():
    if os.path.exists("sample_data.csv"):
        return pd.read_csv("sample_data.csv")
    return make_demo_data(rows=1800, seed=42)


df = load_data()


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def is_arabic_text(text):
    return any('\u0600' <= ch <= '\u06FF' for ch in str(text))


def safe_sum(series):
    if series is None:
        return 0
    return pd.to_numeric(series, errors="coerce").fillna(0).sum()


def to_numeric_if_possible(value):
    try:
        if isinstance(value, str) and value.strip() == "":
            return value
        num = pd.to_numeric(value)
        return num.item() if hasattr(num, "item") else num
    except Exception:
        return value


def normalize_plan(plan):
    default_plan = {
        "filters": [],
        "group_by": [],
        "metrics": [{"name": "applications", "type": "count"}],
        "sort_by": None,
        "limit": None,
        "answer_style": "auto"
    }

    if not isinstance(plan, dict):
        return default_plan

    merged = default_plan.copy()
    merged.update(plan)

    if not isinstance(merged.get("filters"), list):
        merged["filters"] = []

    if not isinstance(merged.get("group_by"), list):
        merged["group_by"] = []

    if not isinstance(merged.get("metrics"), list) or not merged["metrics"]:
        merged["metrics"] = [{"name": "applications", "type": "count"}]

    return merged


def extract_json_object(text):
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None
    return None


def detect_text_filters_from_question(user_question, data):
    q = str(user_question).strip().casefold()
    detected_filters = []
    text_columns = ["Location", "Region", "ProjectName", "MaritalStatus", "ServiceType", "StatusBucket"]

    for col in text_columns:
        if col not in data.columns:
            continue
        unique_values = data[col].dropna().astype(str).unique().tolist()
        for value in unique_values:
            value_norm = str(value).strip().casefold()
            if value_norm and value_norm in q:
                detected_filters.append({"column": col, "operator": "=", "value": value})
                break

    return detected_filters


def extract_application_number(question):
    match = re.search(r"\b(\d{3,})\b", str(question))
    return int(match.group(1)) if match else None


def detect_requested_field(question):
    q = str(question).strip().lower()
    field_map = [
        (["marital status", "الحالة الاجتماعية"], "MaritalStatus", "Marital Status"),
        (["service type", "نوع الخدمة", "الخدمة"], "ServiceType", "Service Type"),
        (["status", "الحالة"], "StatusBucket", "Status"),
        (["age", "العمر"], "ApplicantAge", "Age"),
        (["location", "الموقع"], "Location", "Location"),
        (["region", "المنطقة"], "Region", "Region"),
        (["project", "المشروع"], "ProjectName", "Project"),
        (["income", "salary", "net income", "الدخل", "الراتب"], "NetIncome", "Net Income"),
        (["days to decision", "decision days", "أيام القرار"], "DaysToDecision", "Days To Decision"),
    ]

    for terms, column, label in field_map:
        if any(term in q for term in terms):
            return {"column": column, "label": label}

    return None


def extract_customer_name_from_question(question, data):
    if "CustomerName" not in data.columns:
        return None
    q = str(question).strip().casefold()
    candidates = []
    for name in data["CustomerName"].dropna().astype(str).unique().tolist():
        name_norm = name.strip().casefold()
        if name_norm and name_norm in q:
            candidates.append(name)
    if not candidates:
        return None
    return max(candidates, key=len)


def find_single_record(question, data):
    if data is None or data.empty:
        return None, None

    app_no = extract_application_number(question)
    if app_no is not None and "ApplicationNo" in data.columns:
        app_series = pd.to_numeric(data["ApplicationNo"], errors="coerce")
        matched = data[app_series == app_no].copy()
        if not matched.empty:
            return matched.iloc[[0]].copy(), f"application {app_no}"

    customer_name = extract_customer_name_from_question(question, data)
    if customer_name and "CustomerName" in data.columns:
        name_series = data["CustomerName"].astype(str).str.strip().str.casefold()
        matched = data[name_series == str(customer_name).strip().casefold()].copy()
        if not matched.empty:
            return matched.iloc[[0]].copy(), f"applicant {customer_name}"

    return None, None


def question_requests_application_details(question, data=None):
    q = str(question).strip().lower()
    detail_terms = [
        "full details", "all details", "complete details",
        "full information", "all information", "complete information",
        "application details", "application information", "full record",
        "تفاصيل", "كل التفاصيل", "كامل التفاصيل",
        "معلومات كاملة", "كل المعلومات", "بيانات الطلب", "تفاصيل الطلب"
    ]
    has_number = extract_application_number(question) is not None
    has_name = False
    if data is not None:
        has_name = extract_customer_name_from_question(question, data) is not None

    return any(term in q for term in detail_terms) and (has_number or has_name or "application" in q or "الطلب" in q)


def get_application_detail_result(question, filtered_df):
    record_df, target_label = find_single_record(question, filtered_df)

    if record_df is None or record_df.empty:
        title = "Application Details"
        result = pd.DataFrame({"Field": ["Status"], "Value": ["No matching record"]})
        summary = "No matching record was found under the current filters."
        insight = "Try clearing filters or check the application number/name."
        return title, result, summary, insight

    detail_df = record_df.iloc[0].reset_index()
    detail_df.columns = ["Field", "Value"]
    title = f"Full details for {target_label}"
    summary = f"Showing the full record for {target_label}."
    insight = "The table lists every available column and its value."
    return title, detail_df, summary, insight


def get_record_field_result(question, filtered_df):
    requested_field = detect_requested_field(question)
    if not requested_field:
        return None, None, None, None

    record_df, target_label = find_single_record(question, filtered_df)
    if record_df is None or record_df.empty:
        return None, None, None, None

    column = requested_field["column"]
    label = requested_field["label"]

    if column not in record_df.columns:
        title = f"{label} Lookup"
        result = pd.DataFrame({label: ["Field not available"]})
        summary = f"{label} is not available for the selected record."
        insight = "The record was found, but the requested field does not exist in the dataset."
        return title, result, summary, insight

    value = record_df.iloc[0][column]
    if pd.isna(value):
        value = "Not available"

    title = f"{label} for {target_label}"
    result = pd.DataFrame({label: [value]})
    summary = f"{label} for {target_label} is {value}."
    insight = "Returned only the requested field instead of the full application record."
    return title, result, summary, insight

def heuristic_plan(user_question, data):
    q = str(user_question).lower().strip()
    columns = set(data.columns.tolist())
    has_record_target = (
        extract_application_number(user_question) is not None
        or extract_customer_name_from_question(user_question, data) is not None
    )

    plan = {
        "filters": [],
        "group_by": [],
        "metrics": [{"name": "applications", "type": "count"}],
        "sort_by": None,
        "limit": None,
        "answer_style": "auto"
    }

    if ("location" in q or "الموقع" in q) and "Location" in columns and not has_record_target:
        plan["group_by"] = ["Location"]
    elif ("region" in q or "المنطقة" in q) and "Region" in columns and not has_record_target:
        plan["group_by"] = ["Region"]
    elif ("project" in q or "المشروع" in q) and "ProjectName" in columns and not has_record_target:
        plan["group_by"] = ["ProjectName"]
    elif ("marital" in q or "الحالة الاجتماعية" in q) and "MaritalStatus" in columns and not has_record_target:
        plan["group_by"] = ["MaritalStatus"]
    elif ("status" in q or "الحالة" in q) and "StatusBucket" in columns and not has_record_target:
        plan["group_by"] = ["StatusBucket"]

    if ("widow" in q or "الأرامل" in q or "ارامل" in q or "أرامل" in q) and "WidowFlag" in columns:
        plan["filters"].append({"column": "WidowFlag", "operator": "=", "value": 1})

    if ("approved" in q or "المعتمد" in q or "المعتمدة" in q or "اعتماد" in q) and "approval rate" not in q and "نسبة" not in q:
        if "ApprovedFlag" in columns:
            plan["filters"].append({"column": "ApprovedFlag", "operator": "=", "value": 1})

    if ("rejected" in q or "مرفوض" in q or "المرفوض" in q or "رفض" in q) and "RejectedFlag" in columns:
        plan["filters"].append({"column": "RejectedFlag", "operator": "=", "value": 1})

    if "approval rate" in q or "نسبة الاعتماد" in q:
        plan["metrics"] = [{"name": "approval_rate", "type": "rate", "numerator": "ApprovedFlag", "denominator": "rows"}]
    elif "average age" in q or "avg age" in q or "متوسط العمر" in q:
        if "ApplicantAge" in columns:
            plan["metrics"] = [{"name": "avg_age", "type": "mean", "column": "ApplicantAge"}]
    elif "average days" in q or "avg days" in q or "days to decision" in q or "متوسط الأيام" in q:
        if "DaysToDecision" in columns:
            plan["metrics"] = [{"name": "avg_days_to_decision", "type": "mean", "column": "DaysToDecision"}]

    if any(word in q for word in ["highest", "top", "most", "maximum", "max", "أعلى", "اعلى", "الأعلى", "الاكثر", "الأكثر"]):
        metric_name = plan["metrics"][0]["name"]
        plan["sort_by"] = {"column": metric_name, "order": "desc"}
        plan["limit"] = 1

    if any(word in q for word in ["lowest", "least", "minimum", "min", "أقل", "اقل", "الأقل", "الاقل"]):
        metric_name = plan["metrics"][0]["name"]
        plan["sort_by"] = {"column": metric_name, "order": "asc"}
        plan["limit"] = 1

    top_match = re.search(r"top\s+(\d+)", q)
    if top_match:
        metric_name = plan["metrics"][0]["name"]
        plan["sort_by"] = {"column": metric_name, "order": "desc"}
        plan["limit"] = int(top_match.group(1))

    detected_filters = detect_text_filters_from_question(user_question, data)
    existing_filter_cols = {f["column"] for f in plan["filters"]}

    for f in detected_filters:
        if f["column"] not in existing_filter_cols:
            plan["filters"].append(f)

    return plan


def parse_question(user_question, data):
    if client is None:
        return heuristic_plan(user_question, data)

    schema_info = {
        "columns": data.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()}
    }

    prompt = f"""
You are a BI query planner.

Convert the user's question into a JSON execution plan for pandas.

Available dataframe schema:
{json.dumps(schema_info, ensure_ascii=False)}

Return only valid JSON in this exact format:
{{
  "filters": [{{"column": "column_name", "operator": "=", "value": "value"}}],
  "group_by": ["column1"],
  "metrics": [
    {{"name": "applications", "type": "count"}},
    {{"name": "approval_rate", "type": "rate", "numerator": "ApprovedFlag", "denominator": "rows"}},
    {{"name": "avg_age", "type": "mean", "column": "ApplicantAge"}},
    {{"name": "avg_days_to_decision", "type": "mean", "column": "DaysToDecision"}}
  ],
  "sort_by": {{"column": "applications", "order": "desc"}},
  "limit": 10,
  "answer_style": "auto"
}}

Understand both English and Arabic.
Use only available columns.
If the user asks about one application number or one applicant name with a field like status or age, do not group by anything.
"""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt + "\nUser question:\n" + user_question)
        parsed = extract_json_object(response.output_text.strip())
        if parsed:
            return normalize_plan(parsed)
    except Exception:
        pass

    return heuristic_plan(user_question, data)


def apply_filters(data, filters):
    result = data.copy()
    for f in filters:
        col = f.get("column")
        op = f.get("operator", "=")
        val = f.get("value")

        if col not in result.columns:
            continue

        if pd.api.types.is_numeric_dtype(result[col]):
            val = to_numeric_if_possible(val)
            try:
                if op == "=":
                    result = result[result[col] == val]
                elif op == "!=":
                    result = result[result[col] != val]
                elif op == ">":
                    result = result[result[col] > val]
                elif op == "<":
                    result = result[result[col] < val]
                elif op == ">=":
                    result = result[result[col] >= val]
                elif op == "<=":
                    result = result[result[col] <= val]
            except Exception:
                continue
        else:
            series = result[col].astype(str).str.strip().str.casefold()
            value_norm = str(val).strip().casefold()
            try:
                if op == "=":
                    result = result[series == value_norm]
                elif op == "!=":
                    result = result[series != value_norm]
                elif op == "contains":
                    result = result[series.str.contains(value_norm, na=False)]
            except Exception:
                continue

    return result


def run_query(plan, data):
    plan = normalize_plan(plan)
    working_data = apply_filters(data, plan.get("filters", []))

    group_by = [col for col in plan.get("group_by", []) if col in working_data.columns]
    metrics = plan.get("metrics", [])
    sort_by = plan.get("sort_by")
    limit = plan.get("limit")

    if not group_by:
        row = {}
        for metric in metrics:
            mtype = metric.get("type")
            mname = metric.get("name", "metric")
            if mtype == "count":
                row[mname] = len(working_data)
            elif mtype == "mean":
                col = metric.get("column")
                row[mname] = round(pd.to_numeric(working_data[col], errors="coerce").dropna().mean(), 2) if col in working_data.columns else None
            elif mtype == "rate":
                numerator_col = metric.get("numerator")
                denominator = len(working_data)
                numerator = safe_sum(working_data[numerator_col]) if numerator_col in working_data.columns else 0
                row[mname] = round((numerator / denominator) * 100, 2) if denominator else 0
        return "Result", pd.DataFrame([row])

    grouped = working_data.groupby(group_by, dropna=False)
    result = pd.DataFrame(index=grouped.size().index).reset_index()

    for metric in metrics:
        mname = metric.get("name", "metric")
        mtype = metric.get("type")

        if mtype == "count":
            metric_df = grouped.size().reset_index(name=mname)
            result = result.merge(metric_df, on=group_by, how="left")
        elif mtype == "mean":
            col = metric.get("column")
            if col in working_data.columns:
                metric_df = grouped[col].apply(lambda s: pd.to_numeric(s, errors="coerce").mean()).reset_index(name=mname)
                metric_df[mname] = metric_df[mname].round(2)
                result = result.merge(metric_df, on=group_by, how="left")
        elif mtype == "rate":
            numerator_col = metric.get("numerator")
            if numerator_col in working_data.columns:
                metric_df = grouped[numerator_col].sum().reset_index(name="_num")
                count_df = grouped.size().reset_index(name="_den")
                metric_df = metric_df.merge(count_df, on=group_by, how="left")
                metric_df[mname] = ((metric_df["_num"] / metric_df["_den"]) * 100).round(2)
                metric_df = metric_df[group_by + [mname]]
                result = result.merge(metric_df, on=group_by, how="left")

    if sort_by:
        sort_col = sort_by.get("column")
        ascending = sort_by.get("order") == "asc"
        if sort_col in result.columns:
            result = result.sort_values(sort_col, ascending=ascending)

    if limit is not None:
        try:
            result = result.head(int(limit))
        except Exception:
            pass

    return "Query Result", result.reset_index(drop=True)


def build_executive_summary(question, result):
    arabic = is_arabic_text(question)
    if result is None or result.empty:
        return "لم يتم العثور على نتائج مطابقة لهذا السؤال." if arabic else "I could not find a matching result for that question."

    if len(result) == 1 and len(result.columns) == 1:
        col = result.columns[0]
        return f"نتيجة السؤال هي {result.iloc[0][col]}." if arabic else f"The result is {result.iloc[0][col]}."

    if len(result) == 1 and len(result.columns) >= 2:
        first_col = result.columns[0]
        second_col = result.columns[1]
        return f"أعلى نتيجة هي {result.iloc[0][first_col]} بقيمة {result.iloc[0][second_col]}." if arabic else f"The leading result is {result.iloc[0][first_col]} with {result.iloc[0][second_col]}."

    first_col = result.columns[0]
    return f"تم العثور على {len(result)} صفوف، وتبدأ النتائج بـ {result.iloc[0][first_col]}." if arabic else f"I found {len(result)} rows. The table starts with {result.iloc[0][first_col]}."


def build_insight_text(plan, result, question=""):
    arabic = is_arabic_text(question)
    if result is None or result.empty:
        return "لا توجد سجلات مطابقة بعد تطبيق عوامل التصفية." if arabic else "No matching records were found after applying the filters."
    return "تم حساب النتيجة بنجاح." if arabic else "Result calculated successfully."


def build_rich_answer_html(dashboard_name, title, question, result, insight):
    if result is None or result.empty:
        main_text = "No matching result found."
        detail_text = "Try changing the filters or rephrasing the question."
        rows_text = "0 rows"
    elif list(result.columns) == ["Field", "Value"]:
        rows_text = f"{len(result)} fields"
        main_text = "Detailed record view"
        detail_text = f"For the question '{question}', the application record has been returned field by field."
    else:
        rows_text = f"{len(result)} row{'s' if len(result) != 1 else ''}"
        if len(result) == 1 and len(result.columns) == 1:
            value = result.iloc[0, 0]
            main_text = f"{value}"
            detail_text = f"For the question '{question}', the current filtered dataset returns {value}."
        elif len(result) == 1 and len(result.columns) >= 2:
            first_col = result.columns[0]
            second_col = result.columns[1]
            first_val = result.iloc[0][first_col]
            second_val = result.iloc[0][second_col]
            main_text = f"{first_val} — {second_val}"
            detail_text = f"The leading result for '{question}' is {first_val} with a value of {second_val}."
        else:
            first_col = result.columns[0]
            first_val = result.iloc[0][first_col]
            main_text = f"Top result starts with {first_val}"
            detail_text = f"The query returned {len(result)} rows for '{question}', ranked from the strongest matching result."

    return f"""
    <div class="rich-answer-card">
        <div class="rich-answer-title">{title}</div>
        <div class="rich-answer-main">{main_text}</div>
        <div class="rich-answer-detail">{detail_text}</div>
        <div class="rich-answer-detail"><strong>Insight:</strong> {insight}</div>
        <div class="rich-answer-meta">
            <span class="rich-answer-chip">{dashboard_name}</span>
            <span class="rich-answer-chip">{rows_text}</span>
            <span class="rich-answer-chip">Current filters applied</span>
        </div>
    </div>
    """


def resolve_chat_response(user_question, filtered_df):
    try:
        if question_requests_application_details(user_question, filtered_df):
            return get_application_detail_result(user_question, filtered_df)

        field_response = get_record_field_result(user_question, filtered_df)
        if field_response is not None:
            return field_response

        parsed = parse_question(user_question, filtered_df)
        title, result = run_query(parsed, filtered_df)
        summary = build_executive_summary(user_question, result)
        insight = build_insight_text(parsed, result, user_question)
        return title, result, summary, insight

    except Exception as e:
        return (
            "Error",
            pd.DataFrame({"Error": [str(e)]}),
            f"Error while processing question: {e}",
            "The assistant hit an exception while building the answer."
        )


def resolve_chat_response(user_question, filtered_df):
    if question_requests_application_details(user_question):
        return get_application_detail_result(user_question, filtered_df)

    title, result, summary, insight = get_record_field_result(user_question, filtered_df)
    if result is not None:
        return title, result, summary, insight

    parsed = parse_question(user_question, filtered_df)
    title, result = run_query(parsed, filtered_df)
    summary = build_executive_summary(user_question, result)
    insight = build_insight_text(parsed, result, user_question)
    return title, result, summary, insight


def render_dashboard_chat(dashboard_name, filtered_df):
    cfg = DASHBOARD_CONFIG[dashboard_name]
    chat_key = cfg["chat_key"]

    st.markdown(f"### {dashboard_name} Assistant")
    st.caption(f"Scope: {cfg['scope']}")

    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and msg.get("html"):
                st.markdown(msg["html"], unsafe_allow_html=True)
            else:
                st.write(msg["content"])

            if msg.get("table") is not None:
                st.dataframe(pd.DataFrame(msg["table"]), use_container_width=True)

    user_question = st.chat_input(f"Ask about {dashboard_name.lower()}...", key=f"chat_input_{chat_key}")

    if not user_question:
        return

    st.session_state[chat_key].append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.write(user_question)

    try:
        title, result, summary, insight = resolve_chat_response(user_question, filtered_df)

        rich_html = build_rich_answer_html(
            dashboard_name=dashboard_name,
            title=title,
            question=user_question,
            result=result,
            insight=insight
        )

        st.session_state[chat_key].append({
            "role": "assistant",
            "content": summary,
            "table": result.to_dict(orient="records") if result is not None else None,
            "html": rich_html
        })

        with st.chat_message("assistant"):
            st.markdown(rich_html, unsafe_allow_html=True)
            if result is not None and not result.empty:
                st.dataframe(result, use_container_width=True)
            else:
                st.info("No matching records found.")

    except Exception as e:
        error_text = f"Error while processing question: {e}"

        st.session_state[chat_key].append({
            "role": "assistant",
            "content": error_text,
            "table": None,
            "html": None
        })

        with st.chat_message("assistant"):
            st.error(error_text)

# -------------------------------------------------------
# Dashboard config
# -------------------------------------------------------
DASHBOARD_CONFIG = {
    "Executive Overview": {
        "chat_key": "chat_exec",
        "scope": "executive overview, KPIs, top locations, approval performance",
        "prompt_examples": [
            "What is the approval rate?",
            "Which location has the highest applications?",
            "status of application 1001",
            "show full details of application 1001",
            "كم عدد الطلبات المعتمدة؟"
        ]
    },
    "Customer Analytics": {
        "chat_key": "chat_customer",
        "scope": "customer demographics, age, marital status, widow cases, income",
        "prompt_examples": [
            "What is the average age?",
            "Show marital status breakdown",
            "age of application 1015",
            "كم عدد الأرامل حسب الموقع؟"
        ]
    },
    "Application Performance": {
        "chat_key": "chat_perf",
        "scope": "project performance, service type, approvals, rejections",
        "prompt_examples": [
            "Which project has the most applications?",
            "Show approval rate by project",
            "status breakdown"
        ]
    },
    "Geographic Analysis": {
        "chat_key": "chat_geo",
        "scope": "region, location, map distribution, area comparison",
        "prompt_examples": [
            "Count applications by location",
            "Which region has the most applications?",
            "Show top 10 locations"
        ]
    }
}

for dashboard_name, cfg in DASHBOARD_CONFIG.items():
    if cfg["chat_key"] not in st.session_state:
        st.session_state[cfg["chat_key"]] = []


# -------------------------------------------------------
# Sidebar navigation
# -------------------------------------------------------
with st.sidebar:
    st.markdown("## Navigation")
    dashboard = st.radio(
        "Select dashboard",
        ["Executive Overview", "Customer Analytics", "Application Performance", "Geographic Analysis"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### Dataset")
    st.write(f"Rows: **{len(df):,}**")
    st.write(f"Columns: **{len(df.columns):,}**")

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download current CSV", data=csv_bytes, file_name="sample_data.csv", mime="text/csv", use_container_width=True)

    with st.expander("Preview data", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)


# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.markdown(f"""
<div class="top-banner">
    <div class="top-banner-title">{dashboard}</div>
    <div class="top-banner-subtitle">
        Customer-facing applications analytics and company performance monitoring in a cleaner single-file dashboard.
    </div>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# Shared filters
# -------------------------------------------------------
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">Global Filters</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    selected_location = st.selectbox("Location", ["All"] + sorted(df["Location"].dropna().unique().tolist()))
with f2:
    selected_status = st.selectbox("Status", ["All"] + sorted(df["StatusBucket"].dropna().unique().tolist()))
with f3:
    selected_service = st.selectbox("Service Type", ["All"] + sorted(df["ServiceType"].dropna().unique().tolist()))
with f4:
    selected_marital = st.selectbox("Marital Status", ["All"] + sorted(df["MaritalStatus"].dropna().unique().tolist()))

st.markdown("</div>", unsafe_allow_html=True)

filtered_df = df.copy()
if selected_location != "All":
    filtered_df = filtered_df[filtered_df["Location"] == selected_location]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["StatusBucket"] == selected_status]
if selected_service != "All":
    filtered_df = filtered_df[filtered_df["ServiceType"] == selected_service]
if selected_marital != "All":
    filtered_df = filtered_df[filtered_df["MaritalStatus"] == selected_marital]


# -------------------------------------------------------
# Dashboard pages
# -------------------------------------------------------
if dashboard == "Executive Overview":
    local_df = filtered_df.copy()
    local_df["CompletionDate"] = pd.to_datetime(local_df["CompletionDate"], errors="coerce")
    local_df["CompletionYear"] = local_df["CompletionDate"].dt.year.astype("Int64")

    available_years = sorted([str(int(y)) for y in local_df["CompletionYear"].dropna().unique().tolist()], reverse=True)
    year_options = ["All"] + available_years

    top_filter_col1, gap_col, top_filter_col2 = st.columns([4.2, 0.15, 1])
    with top_filter_col1:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">لوحة القيادة - الخدمات الإسكانية</div>
            <div class="dash-note">
                هذا العرض تجريبي ويستخدم بيانات محاكاة لتمثيل مؤشرات الطلبات، المنح، القروض، والخدمات السكنية بشكل قريب من لوحة تنفيذية حقيقية.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with top_filter_col2:
        selected_exec_year = st.radio("السنة", year_options, index=0)

    if selected_exec_year != "All":
        local_df = local_df[local_df["CompletionYear"] == int(selected_exec_year)]

    local_df["ApprovedFlag"] = pd.to_numeric(local_df["ApprovedFlag"], errors="coerce").fillna(0)
    local_df["RejectedFlag"] = pd.to_numeric(local_df["RejectedFlag"], errors="coerce").fillna(0)
    local_df["DaysToDecision"] = pd.to_numeric(local_df["DaysToDecision"], errors="coerce")
    local_df["AllowedLoanValue"] = pd.to_numeric(local_df["AllowedLoanValue"], errors="coerce")
    local_df["NoUnits"] = pd.to_numeric(local_df["NoUnits"], errors="coerce")

    total_applications = len(local_df)
    approved_cases = int(local_df["ApprovedFlag"].sum())
    rejected_cases = int(local_df["RejectedFlag"].sum())
    approval_rate = round((approved_cases / total_applications) * 100, 1) if total_applications else 0

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-topline"><div class="kpi-label">إجمالي الطلبات</div><div class="kpi-icon">📄</div></div>
            <div class="kpi-value">{total_applications:,}</div>
            <div class="mini-note">All filtered applications</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-topline"><div class="kpi-label">الحالات المعتمدة</div><div class="kpi-icon">✅</div></div>
            <div class="kpi-value">{approved_cases:,}</div>
            <div class="mini-note">Approved cases</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-topline"><div class="kpi-label">الحالات المرفوضة</div><div class="kpi-icon">⛔</div></div>
            <div class="kpi-value">{rejected_cases:,}</div>
            <div class="mini-note">Rejected cases</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-topline"><div class="kpi-label">نسبة الاعتماد</div><div class="kpi-icon">📈</div></div>
            <div class="kpi-value">{approval_rate}%</div>
            <div class="mini-note">Approval rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    grant_df = local_df[local_df["ServiceType"].astype(str).str.casefold() == "grant"]
    loan_df = local_df[local_df["ServiceType"].astype(str).str.casefold() == "loan"]

    name_series = local_df["ProjectName"].fillna("").astype(str).str.lower()
    apartment_mask = name_series.str.contains("residences|community|towers", regex=True)
    house_mask = name_series.str.contains("villas|homes", regex=True)
    maintenance_mask = ((local_df["AllowedLoanValue"] < 650000) & (local_df["ServiceType"].astype(str).str.casefold() == "loan"))
    land_mask = ((local_df["AllowedLoanValue"] >= 950000) & (local_df["ServiceType"].astype(str).str.casefold() == "grant"))

    apartment_grant_df = local_df[apartment_mask & (local_df["ServiceType"].astype(str).str.casefold() == "grant")]
    ready_grant_df = local_df[house_mask & (local_df["ServiceType"].astype(str).str.casefold() == "grant")]
    ready_loan_df = local_df[house_mask & (local_df["ServiceType"].astype(str).str.casefold() == "loan")]
    maintenance_df = local_df[maintenance_mask]
    land_grant_df = local_df[land_mask]
    unit_df = local_df.copy()

    c1, gap1, c2, gap2, c3 = st.columns([1, 0.06, 1, 0.06, 1])
    with c1:
        st.markdown('<div class="chart-title">منح</div>', unsafe_allow_html=True)
        grant_breakdown = pd.DataFrame({
            "الخدمة": ["منحة أرض سكنية", "أعمال صيانة وإضافة", "منحة شقة سكنية", "منحة المسكن الجاهز"],
            "العدد": [len(land_grant_df), len(maintenance_df), len(apartment_grant_df), len(ready_grant_df)]
        }).sort_values("العدد", ascending=True)
        fig_grants = px.bar(grant_breakdown, x="العدد", y="الخدمة", orientation="h", text="العدد")
        fig_grants.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_grants, use_container_width=True)
    with c2:
        st.markdown('<div class="chart-title">مؤشر عدد طلبات الخدمات الإسكانية</div>', unsafe_allow_html=True)
        mix_df = pd.DataFrame({"الفئة": ["منح", "قروض"], "القيمة": [len(grant_df), len(loan_df)]})
        fig_mix = px.pie(mix_df, names="الفئة", values="القيمة", hole=0.56)
        fig_mix.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
        st.plotly_chart(fig_mix, use_container_width=True)
    with c3:
        st.markdown('<div class="chart-title">قروض</div>', unsafe_allow_html=True)
        loan_breakdown = pd.DataFrame({
            "الخدمة": ["قرض مسكن جاهز", "أعمال صيانة وإضافة", "قرض شراء مسكن جاهز", "استئجار وحدة سكنية"],
            "العدد": [len(ready_loan_df), len(maintenance_df), max(0, round(len(loan_df) * 0.55)), max(0, round(len(loan_df) * 0.10))]
        }).sort_values("العدد", ascending=True)
        fig_loans = px.bar(loan_breakdown, x="العدد", y="الخدمة", orientation="h", text="العدد")
        fig_loans.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_loans, use_container_width=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    def card_metrics(data_slice):
        total = len(data_slice)
        approved = int(pd.to_numeric(data_slice["ApprovedFlag"], errors="coerce").fillna(0).sum()) if not data_slice.empty else 0
        pending = int(data_slice["StatusBucket"].isin(["In Progress", "On Hold"]).sum()) if not data_slice.empty else 0
        avg_days_series = pd.to_numeric(data_slice["DaysToDecision"], errors="coerce").dropna()
        avg_days = round(avg_days_series.mean(), 1) if not avg_days_series.empty else 0
        units = int(pd.to_numeric(data_slice["NoUnits"], errors="coerce").fillna(0).sum()) if not data_slice.empty else 0
        return total, approved, pending, avg_days, units

    def render_service_card(title, data_slice, green=False):
        total, approved, pending, avg_days, units = card_metrics(data_slice)
        title_class = "svc-title green" if green else "svc-title"
        st.markdown(f"""
        <div class="svc-card">
            <div class="{title_class}">{title}</div>
            <div class="svc-grid">
                <div><div class="svc-metric-label">عدد الطلبات</div><div class="svc-metric-value">{total:,}</div></div>
                <div><div class="svc-metric-label">الحالات المعتمدة</div><div class="svc-metric-value">{approved:,}</div></div>
                <div><div class="svc-metric-label">قيد المعالجة</div><div class="svc-metric-value">{pending:,}</div></div>
                <div><div class="svc-metric-label">متوسط أيام القرار</div><div class="svc-metric-value">{avg_days}</div></div>
                <div><div class="svc-metric-label">الوحدات المرتبطة</div><div class="svc-metric-value">{units:,}</div></div>
                <div><div class="svc-metric-label">نسبة الاعتماد</div><div class="svc-metric-value">{round((approved / total) * 100, 1) if total else 0}%</div></div>
            </div>
            <div class="svc-note">مؤشرات تقديرية لأغراض العرض التجريبي وتعتمد على تجميع منطقي للبيانات الحالية.</div>
        </div>
        """, unsafe_allow_html=True)

    r1c1, r1g1, r1c2, r1g2, r1c3, r1g3, r1c4 = st.columns([1, 0.05, 1, 0.05, 1, 0.05, 1])
    with r1c1:
        render_service_card("الوحدات السكنية", unit_df)
    with r1c2:
        render_service_card("منحة شقة سكنية", apartment_grant_df)
    with r1c3:
        render_service_card("منحة المسكن الجاهز", ready_grant_df)
    with r1c4:
        render_service_card("قرض شراء مسكن جاهز", ready_loan_df, green=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    r2c1, r2g1, r2c2, r2g2, r2c3 = st.columns([1, 0.05, 1, 0.05, 1])
    with r2c1:
        render_service_card("الصيانة", maintenance_df)
    with r2c2:
        render_service_card("خدمات المبادرات السكنية", local_df[local_df["StatusBucket"].isin(["In Progress", "On Hold"])])
    with r2c3:
        render_service_card("منحة الأرض السكنية", land_grant_df)

    render_dashboard_chat("Executive Overview", local_df)

elif dashboard == "Customer Analytics":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Customer Demographics & Segmentation</div>', unsafe_allow_html=True)
    top_col1, top_col2 = st.columns([1, 2])
    with top_col1:
        st.subheader("Gender Distribution")
        gender_counts = filtered_df["Gender"].fillna("Unknown").value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig_gender = px.pie(gender_counts, names="Gender", values="Count", hole=0.55)
        fig_gender.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
        st.plotly_chart(fig_gender, use_container_width=True)
    with top_col2:
        st.subheader("Age vs Net Income")
        scatter_df = filtered_df.copy()
        scatter_df["ApplicantAge"] = pd.to_numeric(scatter_df["ApplicantAge"], errors="coerce")
        scatter_df["NetIncome"] = pd.to_numeric(scatter_df["NetIncome"], errors="coerce")
        scatter_df["ApprovalLabel"] = scatter_df["ApprovedFlag"].map({1: "Approved", 0: "Not Approved"}).fillna("Unknown")
        scatter_df = scatter_df.dropna(subset=["ApplicantAge", "NetIncome"])
        fig_scatter = px.scatter(scatter_df, x="ApplicantAge", y="NetIncome", color="ApprovalLabel", hover_data=["CustomerName", "Location", "MaritalStatus", "ServiceType"], title="")
        fig_scatter.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
        st.plotly_chart(fig_scatter, use_container_width=True)
    bottom_col1, bottom_col2 = st.columns(2)
    with bottom_col1:
        st.subheader("Marital Status Mix")
        marital_counts = filtered_df["MaritalStatus"].fillna("Unknown").value_counts().reset_index()
        marital_counts.columns = ["MaritalStatus", "Count"]
        fig_marital = px.bar(marital_counts, x="MaritalStatus", y="Count", text="Count")
        fig_marital.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
        st.plotly_chart(fig_marital, use_container_width=True)
    with bottom_col2:
        st.subheader("Widow Cases by Location")
        widow_df = filtered_df.copy()
        widow_df["WidowFlag"] = pd.to_numeric(widow_df["WidowFlag"], errors="coerce").fillna(0)
        widow_by_location = widow_df.groupby("Location")["WidowFlag"].sum().reset_index(name="WidowCases").sort_values("WidowCases", ascending=False).head(10)
        fig_widow = px.bar(widow_by_location, x="WidowCases", y="Location", orientation="h", text="WidowCases")
        fig_widow.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_widow, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    render_dashboard_chat("Customer Analytics", filtered_df)

elif dashboard == "Application Performance":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Company Performance Against Applications</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        status_counts = filtered_df["StatusBucket"].value_counts(dropna=False).reset_index()
        status_counts.columns = ["StatusBucket", "Count"]
        fig_status = px.bar(status_counts, x="StatusBucket", y="Count", text="Count")
        fig_status.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_status, use_container_width=True)
    with c2:
        project_perf = filtered_df.groupby("ProjectName").agg(Applications=("ApplicationNo", "count"), Approved=("ApprovedFlag", "sum")).reset_index().sort_values("Applications", ascending=False).head(10)
        st.subheader("Top Projects")
        st.dataframe(project_perf, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    render_dashboard_chat("Application Performance", filtered_df)

elif dashboard == "Geographic Analysis":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Geographic Analysis</div>', unsafe_allow_html=True)
    map_df = filtered_df.copy()
    map_df["Latitude"] = pd.to_numeric(map_df["Latitude"], errors="coerce")
    map_df["Longitude"] = pd.to_numeric(map_df["Longitude"], errors="coerce")
    map_points = map_df.dropna(subset=["Latitude", "Longitude"])[["Latitude", "Longitude"]].rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.subheader("Application Locations")
    st.map(map_points)
    location_counts = filtered_df.groupby("Location").size().reset_index(name="Applications").sort_values("Applications", ascending=False)
    st.dataframe(location_counts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    render_dashboard_chat("Geographic Analysis", filtered_df)
