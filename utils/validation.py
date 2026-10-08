
import pandas as pd

REQUIRED = [
"Lead_ID","Company_Name","Industry","Company_Size","Country","Annual_Revenue_USD_M",
"Job_Title","Decision_Maker_Flag","Lead_Source","Product_Interest","Website_Visits_30D",
"Email_Opens_30D","Email_Clicks_30D","Content_Downloads_30D","Demo_Requests_30D",
"LinkedIn_Engagement_30D","Previous_Interactions","Days_Since_Last_Activity",
"Budget_Fit","Purchase_Timeline","Competitor_Usage"
]
NUMERIC_NONNEG = ["Annual_Revenue_USD_M","Website_Visits_30D","Email_Opens_30D","Email_Clicks_30D",
"Content_Downloads_30D","Demo_Requests_30D","LinkedIn_Engagement_30D","Previous_Interactions",
"Days_Since_Last_Activity"]
ALLOWED_BUDGET={"Low","Medium","High"}
ALLOWED_TIMELINE={"0-30 days","31-90 days","3-6 months","6+ months"}

def validate_dataframe(df):
    errors=[]; warnings=[]
    missing=[c for c in REQUIRED if c not in df.columns]
    for c in missing: errors.append({"field":c,"issue":"Missing required column"})
    if "Lead_ID" in df.columns:
        dup=df["Lead_ID"][df["Lead_ID"].duplicated(keep=False)].dropna().unique().tolist()
        if dup: errors.append({"field":"Lead_ID","issue":f"Duplicate IDs: {dup}"})
    for c in REQUIRED:
        if c in df.columns:
            n=int(df[c].isna().sum())
            if n: errors.append({"field":c,"issue":f"{n} missing values"})
    for c in NUMERIC_NONNEG:
        if c in df.columns:
            vals=pd.to_numeric(df[c],errors="coerce")
            bad=int((vals.isna() & df[c].notna()).sum())
            neg=int((vals<0).sum())
            if bad: errors.append({"field":c,"issue":f"{bad} non-numeric values"})
            if neg: errors.append({"field":c,"issue":f"{neg} negative values"})
    if "Decision_Maker_Flag" in df.columns:
        vals=pd.to_numeric(df["Decision_Maker_Flag"],errors="coerce")
        if ((~vals.isin([0,1])) | vals.isna()).any():
            errors.append({"field":"Decision_Maker_Flag","issue":"Must be 0 or 1"})
    if "Budget_Fit" in df.columns:
        bad=set(df["Budget_Fit"].dropna())-ALLOWED_BUDGET
        if bad: errors.append({"field":"Budget_Fit","issue":f"Invalid values: {sorted(bad)}"})
    if "Purchase_Timeline" in df.columns:
        bad=set(df["Purchase_Timeline"].dropna())-ALLOWED_TIMELINE
        if bad: errors.append({"field":"Purchase_Timeline","issue":f"Invalid values: {sorted(bad)}"})
    return {"valid":len(errors)==0,"errors":errors,"warnings":warnings}
