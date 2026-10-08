
import os, json
SYSTEM_PROMPT="""You are LeadWise's sales decision-support assistant.
Interpret only structured lead analytics supplied by the application.
Never invent lead facts. Never change or override deterministic scores or tiers.
Clearly distinguish facts from recommendations. Identify uncertainty.
Do not claim a lead will definitely convert. Do not make autonomous outreach decisions."""
def get_ai_response(context, question):
    key=os.getenv("GEMINI_API_KEY")
    if not key:
        return None,"AI explanation is currently unavailable. Deterministic lead scoring remains available."
    try:
        from google import genai
        from google.genai import types
        client=genai.Client(api_key=key)
        model=os.getenv("GEMINI_MODEL","gemini-3.8-flash")
        prompt=SYSTEM_PROMPT+"\n\nSTRUCTURED DATA:\n"+json.dumps(context,default=str)+"\n\nQUESTION:\n"+question
        r=client.models.generate_content(model=model,contents=prompt,
            config=types.GenerateContentConfig(temperature=.2,max_output_tokens=800))
        return r.text,None
    except Exception:
        return None,"AI explanation is currently unavailable. Deterministic lead scoring remains available."
