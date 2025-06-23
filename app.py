import streamlit as st
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

st.set_page_config(page_title="YouTube Channel Transcripts", layout="wide")

st.title("📄 YouTube Channel Transcript Viewer")

# Input field for channel URL
channel_url = st.text_input("Enter YouTube Channel URL (e.g. https://www.youtube.com/@andybiggs2257):")

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

def get_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([line['text'] for line in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        return f"[Error fetching transcript: {e}]"

if st.button("Get Transcripts") and channel_url:
    with st.spinner("Fetching video list and transcripts..."):
        video_ids = get_url_list(channel_url)
        if not video_ids:
            st.warning("No videos found or failed to retrieve playlist.")
        else:
            for idx, video_id in enumerate(video_ids, start=1):
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.markdown(f"### 🎬 Transcript for Video {idx}: [{video_url}]({video_url})")
                transcript_text = get_transcript_text(video_id)
                if transcript_text:
                    st.text_area("Transcript", transcript_text, height=300)
                else:
                    st.warning("Transcript not available.")
