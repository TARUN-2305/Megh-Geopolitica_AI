"""
Expert Monitor Agent
Runs periodically to:
- Check YouTube RSS for new videos from tracked experts
- Fetch transcripts
- Extract geopolitical insights using Gemini
- Save to /backend/data/expert_insights/
"""

import sys
import os
import feedparser
import json
import sqlite3
import time
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Add base directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from agents.expert_monitor.config import EXPERT_CHANNELS
from backend.core.layer0_wisdom.transcript_processor import fetch_expert_transcript
from backend.core.layer0_wisdom.insight_extractor import get_gemini_model, PROMPT_TEMPLATE

# Setup paths
INSIGHTS_DIR = os.path.join(BASE_DIR, "backend", "data", "expert_insights")
os.makedirs(INSIGHTS_DIR, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "raw", "events.db")

def run_expert_monitor():
    print(f"[{datetime.now()}] Expert Monitor started...")
    model = None
    try:
        model = get_gemini_model()
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return

    for expert in EXPERT_CHANNELS:
        name = expert['name']
        channel_id = expert['channel_id']
        print(f"Checking {name} ({channel_id})...")
        
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print(f"  No videos found for {name}.")
            continue
            
        # Process the most recent 3 videos
        for entry in feed.entries[:3]:
            video_id = entry.yt_videoid
            video_title = entry.title
            video_url = entry.link
            video_date = entry.published
            
            insight_file = os.path.join(INSIGHTS_DIR, f"{video_id}.json")
            if os.path.exists(insight_file):
                # print(f"  Already processed: {video_title}")
                continue
                
            print(f"  Processing: {video_title}")
            
            # 1. Fetch transcript
            transcript = fetch_expert_transcript(video_url)
            if not transcript:
                print(f"    Could not get transcript for {video_id}")
                continue
                
            # 2. Extract insights with Gemini
            prompt = PROMPT_TEMPLATE.format(
                expert_name=name,
                video_title=video_title,
                video_date=video_date,
                transcript_text=transcript[:15000] # Limit to ~15k chars for safety
            )
            
            try:
                response = model.generate_content(prompt)
                # Clean up response text if it contains markdown markers
                response_text = response.text.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                insights = json.loads(response_text)
                
                # 3. Save insight
                result = {
                    "expert": name,
                    "video_id": video_id,
                    "title": video_title,
                    "date": video_date,
                    "url": video_url,
                    "insights": insights,
                    "processed_at": datetime.now().isoformat()
                }
                
                with open(insight_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)
                    
                print(f"    Successfully extracted {len(insights) if isinstance(insights, list) else 1} insights.")
                
            except Exception as e:
                print(f"    Error processing {video_id} with Gemini: {e}")
                continue

if __name__ == "__main__":
    run_expert_monitor()
