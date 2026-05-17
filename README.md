# AI Operational Analytics Command Center

Enterprise-style AI analytics dashboard prototype built with Streamlit, Plotly, and OpenAI.

## Overview

This project demonstrates an AI-powered operational analytics platform designed for:

- executive monitoring
- operational diagnostics
- customer analytics
- forecasting
- conversational AI insights

The dashboard uses anonymized demo data and focuses on modern enterprise analytics concepts.

---

## Features

- Executive KPI dashboard
- Operational monitoring
- Risk diagnostics
- Forecast preview
- Customer & channel analytics
- AI assistant for dashboard questions
- Multi-page analytics experience
- Enterprise-style UI design

---

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- OpenAI API

---

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Set your OpenAI API key before running:

```bash
set OPENAI_API_KEY=your_api_key_here
```

---

## Architecture Direction

```text
Oracle Cloud / Enterprise Data
        ↓
Microsoft Fabric OneLake / Lakehouse
        ↓
Bronze, Silver, Gold Medallion Layers
        ↓
Power BI Semantic Model
        ↓
Dashboard + AI Assistant
        ↓
Executive Insights
```

---

## Governance & Security Thinking

- Use governed and approved data sources
- Keep sensitive data within approved enterprise boundaries
- Apply role-based access for relevant users
- Avoid exposing raw data unnecessarily
- Support trusted KPI definitions through semantic models

---

## Dashboard Preview

### Executive Overview

![Executive Overview](screenshots/dashboard-overview.png)

---

### Operational Diagnostics

![Operational Diagnostics](screenshots/operational-diagnostics.png)

---

### Customer & Channel Analytics

![Customer Analytics](screenshots/customer-channel-analytics.png)

---

### AI Analytics Assistant

![AI Assistant](screenshots/ai-analytics-assistant.png)

---

## Future Improvements

- Connect to live enterprise data sources
- Add Microsoft Fabric / Lakehouse integration
- Add role-based security
- Improve multilingual AI questions
- Add forecasting models
- Add Power BI semantic model integration
- Deploy as an internal analytics assistant