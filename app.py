import streamlit as st
import subprocess
import time
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    TooManyRequests
)

st.set_page_config(page_title="YouTube Channel Transcripts", layout="wide")
st.title("YouTube Channel Transcripts")

channel_url = st.text_input("Enter YouTube Channel URL (e.g. https://www.youtube.com/@andybiggs2257):")
max_videos = st.number_input("Maximum videos to fetch transcripts for", min_value=1, max_value=500, value=20)

def get_url_list(channel_url):
    command = f"yt-dlp --flat-playlist --print id {channel_url}"
    try:
        output_bytes = subprocess.check_output(command, shell=True)
        command_output = output_bytes.decode("utf-8")
        video_ids = command_output.strip().split('\n')
        return video_ids
    except subprocess.CalledProcessError as e:
        st.error(f"Error fetching video IDs: {e}")
        return []

def get_transcript_text(video_id, retries=3):
    for attempt in range(retries):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return "\n".join([line['text'] for line in transcript])
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except TooManyRequests:
            wait_time = 5 * (attempt + 1)
            st.warning(f"Rate limited. Waiting {wait_time} seconds before retrying (attempt {attempt + 1})...")
            time.sleep(wait_time)
        except Exception as e:
            return f"[Error fetching transcript: {e}]"
    return None

if st.button("Get Transcripts") and channel_url:
    with st.spinner("Fetching video list and transcripts..."):
        video_ids = get_url_list(channel_url)[:max_videos]
        if not video_ids:
            st.warning("No videos found or failed to retrieve playlist.")
        else:
            combined_output = ""
            for idx, video_id in enumerate(video_ids, start=1):
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.info(f"Fetching transcript for video {idx}: {video_url}")
                transcript_text = get_transcript_text(video_id)
                if transcript_text:
                    combined_output += f"\n\n=== Video {idx}: {video_url} ===\n{transcript_text}"
                else:
                    combined_output += f"\n\n=== Video {idx}: {video_url} ===\n[Transcript not available]"
                time.sleep(1.5)  # Delay between requests to avoid rate-limiting

            # Display all transcripts in a single, copyable text area
            st.markdown("## All Transcripts")
            st.text_area("All Transcripts", combined_output.strip(), height=600)

