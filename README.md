# LEADWISE — AI-Powered Sales Lead Scoring & Conversion Intelligence Platform

Use Case #7: Sales lead-scoring assistant.

## Core principle
Deterministic Python scoring calculates the lead score, rank, and Hot/Warm/Cold tier. Gemini is an optional explanation layer and cannot override the score.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data
10-lead demo, 250-lead scalability dataset, and invalid test dataset are included.

## AI
Set `GEMINI_API_KEY` in Streamlit Secrets/environment. The app remains functional when Gemini is unavailable.
