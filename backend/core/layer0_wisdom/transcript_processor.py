from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import os

def fetch_expert_transcript(video_url):
    """Extract transcript from expert's YouTube video"""
    # Simple video_id extraction
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    else:
        video_id = video_url.split("/")[-1]
    
    # Try to get manual transcript first, fall back to auto-generated
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"Manual transcript failed, trying auto-generated: {e}")
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_generated_transcript(['en', 'hi', 'kn']).fetch()
        except Exception as e2:
            print(f"Failed to fetch transcript: {e2}")
            return None
    
    # Format as plain text
    formatter = TextFormatter()
    return formatter.format_transcript(transcript)

if __name__ == "__main__":
    # Test with a placeholder video if needed
    pass
