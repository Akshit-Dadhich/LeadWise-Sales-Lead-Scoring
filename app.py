
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.scoring import score_leads, scenario_weights, rescore_with_weights, WEIGHTS
from utils.validation import validate_dataframe
from utils.ai_analysis import get_ai_response

st.set_page_config(page_title="LeadWise",page_icon="🎯",layout="wide")
ROOT=Path(__file__).parent
st.title("LEADWISE")
st.caption("AI-Powered Sales Lead Scoring & Conversion Intelligence Platform")
st.info("Decision-support only: deterministic scoring ranks leads; AI provides optional explanations and recommendations.")

@st.cache_data
def load_data():
    return pd.read_csv(ROOT/"sample_leads_10.csv")

raw=load_data()
validation=validate_dataframe(raw)
if not validation["valid"]:
    st.error("Demo dataset failed validation.")
    st.dataframe(pd.DataFrame(validation["errors"]))
    st.stop()
scored=score_leads(raw)

pages=["Home","Executive Dashboard","Lead Ranking","Lead Analysis","Lead Profile","Prioritization Simulator","What-If Analysis","AI Sales Assistant","Data Validation"]
page=st.sidebar.radio("Navigation",pages)
st.sidebar.caption("LeadWise v1.0 | Synthetic demo data")
st.sidebar.download_button("Download 10-lead CSV",raw.to_csv(index=False),file_name="leadwise_sample.csv",mime="text/csv")

if page=="Home":
    st.header("Smarter lead prioritization. Better sales focus.")
    a,b,c,d=st.columns(4)
    a.metric("Demo Leads",len(scored)); b.metric("Hot Leads",int((scored.Lead_Tier=="Hot").sum()))
    c.metric("Warm Leads",int((scored.Lead_Tier=="Warm").sum())); d.metric("Cold Leads",int((scored.Lead_Tier=="Cold").sum()))
    st.subheader("How it works")
    st.write("1. Validate lead data → 2. Calculate deterministic component scores → 3. Rank leads → 4. Classify Hot/Warm/Cold → 5. Explain results with optional AI.")
    st.subheader("Scoring weights")
    st.dataframe(pd.DataFrame({"Criterion":list(WEIGHTS),"Weight":[f"{v:.0%}" for v in WEIGHTS.values()]}),hide_index=True,use_container_width=True)
elif page=="Executive Dashboard":
    st.header("Executive Sales Dashboard")
    a,b,c,d=st.columns(4)
    a.metric("Leads",len(scored)); b.metric("Avg Score",f"{scored.Overall_Lead_Score.mean():.1f}")
    c.metric("Top Score",f"{scored.Overall_Lead_Score.max():.1f}"); d.metric("Hot Share",f"{(scored.Lead_Tier.eq('Hot').mean()*100):.0f}%")
    st.plotly_chart(px.bar(scored.sort_values("Overall_Lead_Score",ascending=True),x="Overall_Lead_Score",y="Company_Name",color="Lead_Tier",orientation="h",title="Lead Score Ranking"),use_container_width=True)
    st.plotly_chart(px.pie(scored,names="Lead_Tier",title="Lead Tier Mix"),use_container_width=True)
elif page=="Lead Ranking":
    st.header("Lead Ranking")
    st.dataframe(scored[["Rank","Lead_ID","Company_Name","Industry","Company_Size","Engagement_Score","Intent_Score","Overall_Lead_Score","Lead_Tier"]],hide_index=True,use_container_width=True)
    export=scored.to_csv(index=False)
    st.download_button("Export CRM-style ranked leads",export,file_name="leadwise_ranked_leads.csv",mime="text/csv")
elif page=="Lead Analysis":
    st.header("Lead Analysis")
    name=st.selectbox("Select lead",scored.Company_Name)
    v=scored[scored.Company_Name==name].iloc[0]
    a,b,c,d=st.columns(4); a.metric("Rank",int(v.Rank)); b.metric("Score",f"{v.Overall_Lead_Score:.1f}"); c.metric("Tier",v.Lead_Tier); d.metric("Recency",f"{v.Recency_Score:.1f}")
    x=pd.DataFrame({"Criterion":["Firmographic","Engagement","Intent","Recency"],"Score":[v.Firmographic_Score,v.Engagement_Score,v.Intent_Score,v.Recency_Score]})
    st.plotly_chart(px.bar(x,x="Criterion",y="Score",title="Lead Score Drivers"),use_container_width=True)
    st.write(f"**Company:** {v.Company_Name} | **Industry:** {v.Industry} | **Country:** {v.Country} | **Job title:** {v.Job_Title}")
    st.write(f"**Budget fit:** {v.Budget_Fit} | **Timeline:** {v.Purchase_Timeline} | **Decision maker:** {'Yes' if v.Decision_Maker_Flag else 'No'}")
elif page=="Lead Profile":
    st.header("Lead Profile")
    name=st.selectbox("Lead",scored.Company_Name)
    v=scored[scored.Company_Name==name].iloc[0]
    st.json(v.to_dict())
elif page=="Prioritization Simulator":
    st.header("Lead Prioritization Simulator")
    s=st.selectbox("Scenario",["Balanced","Engagement First","Intent First","Fresh Activity"])
    w=scenario_weights(s); alt=rescore_with_weights(scored,w)
    st.write("Scenario weights:",w)
    st.dataframe(alt[["Scenario_Rank","Lead_ID","Company_Name","Scenario_Score","Lead_Tier"]].rename(columns={"Scenario_Rank":"Rank","Scenario_Score":"Scenario Score"}),hide_index=True,use_container_width=True)
elif page=="What-If Analysis":
    st.header("What-If Analysis")
    st.write("Adjust the importance of each driver. Weights are normalized automatically.")
    fw=st.slider("Firmographic Fit",0,100,30); ew=st.slider("Engagement",0,100,30); iw=st.slider("Intent",0,100,25); rw=st.slider("Recency",0,100,15)
    total=fw+ew+iw+rw
    if total==0: st.warning("Set at least one weight above zero.")
    else:
        w={"Firmographic Fit":fw/total,"Engagement":ew/total,"Intent":iw/total,"Recency":rw/total}
        alt=rescore_with_weights(scored,w)
        st.dataframe(alt[["Scenario_Rank","Lead_ID","Company_Name","Scenario_Score"]].rename(columns={"Scenario_Rank":"Rank","Scenario_Score":"Score"}),hide_index=True,use_container_width=True)
elif page=="AI Sales Assistant":
    st.header("AI Sales Assistant")
    name=st.selectbox("Focus lead",scored.Company_Name)
    q=st.text_area("Question",f"Why is {name} prioritized where it is, and what should the sales team consider next?")
    v=scored[scored.Company_Name==name].iloc[0]
    if st.button("Analyze with AI",type="primary"):
        ans,err=get_ai_response({"selected_lead":v.to_dict(),"top_leads":scored.head(3).to_dict("records"),"weights":WEIGHTS},q)
        _=st.warning(err) if err else st.markdown(ans)
    st.caption("AI explains structured analytics; it cannot change deterministic lead scores or tiers.")
else:
    st.header("Data Validation")
    st.metric("Demo dataset status","PASS" if validation["valid"] else "FAIL")
    if validation["errors"]: st.dataframe(pd.DataFrame(validation["errors"]),hide_index=True,use_container_width=True)
    if st.button("Validate invalid test dataset"):
        r=validate_dataframe(pd.read_csv(ROOT/"test_leads_invalid.csv"))
        st.write(f"Errors detected: {len(r['errors'])}")
        st.dataframe(pd.DataFrame(r["errors"]),hide_index=True,use_container_width=True)
