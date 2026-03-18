from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

# Key rotation logic
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4")
]
current_key_index = 0

def get_gemini_model():
    global current_key_index
    # Filter out None values
    valid_keys = [k for k in API_KEYS if k]
    if not valid_keys:
        raise ValueError("No Gemini API keys found in environment.")
    
    key = valid_keys[current_key_index]
    genai.configure(api_key=key)
    current_key_index = (current_key_index + 1) % len(valid_keys)
    return genai.GenerativeModel('gemini-2.5-flash')

PROMPT_TEMPLATE = """
You are an expert geopolitical analyst tasked with extracting structured intelligence from video transcripts.

EXPERT: {expert_name}
VIDEO_TITLE: {video_title}
DATE: {video_date}
TRANSCRIPT:
{transcript_text}

Extract ALL geopolitical predictions, warnings, or analyses that could impact:
1. Energy prices (crude oil, natural gas, LPG)
2. Shipping routes (Strait of Hormuz, Red Sea, Suez Canal)
3. India-specific economic impacts
4. Karnataka/Bengaluru specifically (if mentioned)

For each prediction, output a JSON object with:
- event_type: (strait_blockage, sanction, conflict_escalation, diplomatic_breakdown, etc.)
- region: (Middle East, Europe, Indo-Pacific, etc.)
- confidence: (low/medium/high based on expert's language)
- time_horizon: (immediate/1-7 days/1-4 weeks/long-term)
- affected_commodities: [list]
- reasoning: (2-3 sentence summary of expert's logic)
- exact_quote: (the sentence from transcript containing the prediction)

If multiple predictions, output a JSON array.

Also extract any disagreements with other experts or mainstream narratives.

Return ONLY valid JSON, no other text.
"""
