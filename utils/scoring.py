
import pandas as pd
import numpy as np

WEIGHTS = {
    "Firmographic Fit": 0.30,
    "Engagement": 0.30,
    "Intent": 0.25,
    "Recency": 0.15,
}

SIZE_SCORE = {"Startup":55, "SME":70, "Mid-Market":85, "Enterprise":100}
BUDGET_SCORE = {"Low":45, "Medium":70, "High":100}
TIMELINE_SCORE = {"0-30 days":100, "31-90 days":80, "3-6 months":60, "6+ months":35}

def _clip(x):
    return float(max(0, min(100, x)))

def score_leads(df):
    d=df.copy()
    d["Firmographic_Score"] = (
        d["Company_Size"].map(SIZE_SCORE).fillna(50)*0.45
        + d["Annual_Revenue_USD_M"].clip(lower=0).apply(lambda x:min(100, x/50)).fillna(0)*0.30
        + d["Decision_Maker_Flag"].clip(0,1).fillna(0)*100*0.25
    ).round(2)
    d["Engagement_Score"] = (
        d["Website_Visits_30D"].clip(lower=0).fillna(0).apply(lambda x:min(100,x*4))*0.20
        + d["Email_Opens_30D"].clip(lower=0).fillna(0).apply(lambda x:min(100,x*5))*0.15
        + d["Email_Clicks_30D"].clip(lower=0).fillna(0).apply(lambda x:min(100,x*8))*0.20
        + d["Content_Downloads_30D"].clip(lower=0).fillna(0).apply(lambda x:min(100,x*12))*0.15
        + d["Demo_Requests_30D"].clip(lower=0).fillna(0).apply(lambda x:min(100,x*35))*0.20
        + d["LinkedIn_Engagement_30D"].clip(lower=0).fillna(0).apply(lambda x:min(100,x*10))*0.10
    ).round(2)
    d["Intent_Score"] = (
        d["Budget_Fit"].map(BUDGET_SCORE).fillna(40)*0.45
        + d["Purchase_Timeline"].map(TIMELINE_SCORE).fillna(35)*0.55
    ).round(2)
    d["Recency_Score"] = d["Days_Since_Last_Activity"].clip(lower=0).fillna(60).apply(lambda x:max(0,100-x*2.5)).round(2)
    d["Overall_Lead_Score"] = (
        d["Firmographic_Score"]*WEIGHTS["Firmographic Fit"]
        + d["Engagement_Score"]*WEIGHTS["Engagement"]
        + d["Intent_Score"]*WEIGHTS["Intent"]
        + d["Recency_Score"]*WEIGHTS["Recency"]
    ).round(2)
    d["Lead_Tier"] = pd.cut(
        d["Overall_Lead_Score"], bins=[-np.inf,59.99,79.99,np.inf],
        labels=["Cold","Warm","Hot"], right=True
    ).astype(str)
    d["Rank"] = d["Overall_Lead_Score"].rank(method="min",ascending=False).astype(int)
    return d.sort_values(["Overall_Lead_Score","Lead_ID"],ascending=[False,True]).reset_index(drop=True)

def scenario_weights(name):
    scenarios={
        "Balanced": {"Firmographic Fit":.30,"Engagement":.30,"Intent":.25,"Recency":.15},
        "Engagement First": {"Firmographic Fit":.20,"Engagement":.45,"Intent":.20,"Recency":.15},
        "Intent First": {"Firmographic Fit":.20,"Engagement":.20,"Intent":.45,"Recency":.15},
        "Fresh Activity": {"Firmographic Fit":.25,"Engagement":.30,"Intent":.20,"Recency":.25},
    }
    return scenarios[name]

def rescore_with_weights(d, weights):
    x=d.copy()
    x["Scenario_Score"]=(
        x["Firmographic_Score"]*weights["Firmographic Fit"]+
        x["Engagement_Score"]*weights["Engagement"]+
        x["Intent_Score"]*weights["Intent"]+
        x["Recency_Score"]*weights["Recency"]
    ).round(2)
    x["Scenario_Rank"]=x["Scenario_Score"].rank(method="min",ascending=False).astype(int)
    return x.sort_values(["Scenario_Score","Lead_ID"],ascending=[False,True])
