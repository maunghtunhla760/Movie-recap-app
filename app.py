import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import VideoFileClip
import os
import time

# --- ၁။ Configuration (သင့်ရဲ့ API Key ကို ဒီမှာ အစားထိုးပါ) ---
GOOGLE_API_KEY = "AIzaSyDOnMNyttZ4qolabxOvO_WH2KaMlPDL0z4"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Movie Recap AI", layout="wide")

# --- ၂။ Video Resolution ပြောင်းလဲပေးသည့် Function ---
def resize_video(input_path, output_path, resolution_type):
    with VideoFileClip(input_path) as video:
        if resolution_type == "TikTok/Reels (9:16)":
            final_clip = video.resize(height=1280)
            final_clip = final_clip.crop(x_center=final_clip.w/2, width=720)
        elif resolution_type == "YouTube Standard (16:9)":
            final_clip = video.resize(width=1280)
        else:
            final_clip = video
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

# --- ၃။ UI Design ---
st.title("🎬 Movie Recap AI Builder")
st.markdown("YouTube Transcript (သို့) Video တင်ပြီး **မြန်မာလို** Recap ပြုလုပ်ပါ။")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input")
    input_mode = st.radio("နည်းလမ်း ရွေးချယ်ပါ:", ["Transcript ထည့်မယ်", "Video Upload တင်မယ်"])
    
    res_choice = st.selectbox(
        "Video Resolution ပြောင်းမလား?",
        ["Original", "YouTube Standard (16:9)", "TikTok/Reels (9:16)"]
    )

    if input_mode == "Transcript ထည့်မယ်":
        user_input = st.text_area("Transcript ကို Paste လုပ်ပါ:", height=200)
    else:
        user_input = st.file_uploader("Video ဖိုင် ရွေးပါ (Max 500MB):", type=['mp4', 'mov', 'avi', 'mkv'])

with col2:
    st.subheader("📤 Output")
    if st.button("Generate Now ✨"):
        if not user_input:
            st.error("ကျေးဇူးပြု၍ Input တစ်ခုခု အရင်ထည့်ပါ။")
        else:
            with st.spinner("AI က လုပ်ဆောင်နေပါသည်..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Video Processing
                    if input_mode == "Video Upload တင်မယ်":
                        with open("temp_video.mp4", "wb") as f:
                            f.write(user_input.getbuffer())
                        
                        video_file = genai.upload_file(path="temp_video.mp4")
                        while video_file.state.name == "PROCESSING":
                            time.sleep(2)
                            video_file = genai.get_file(video_file.name)
                        
                        prompt = "Analyze this movie clip and write an exciting storytelling movie recap script in Burmese language."
                        response = model.generate_content([video_file, prompt])
                        script_text = response.text
                        
                        if res_choice != "Original":
                            st.info("Video Resolution ပြောင်းလဲနေပါသည်...")
                            resize_video("temp_video.mp4", "final_res.mp4", res_choice)
                            st.video("final_res.mp4")
                            with open("final_res.mp4", "rb") as file:
                                st.download_button("Download Resized Video", file, file_name="resized_video.mp4")

                    # Transcript Processing
                    else:
                        prompt = f"Rewrite this transcript into an exciting Burmese movie recap story: {user_input}"
                        response = model.generate_content(prompt)
                        script_text = response.text

                    # Results Display
                    st.success("အောင်မြင်ပါသည်။")
                    st.write(script_text)
                    
                    # Audio Generation
                    tts = gTTS(text=script_text, lang='my')
                    tts.save("recap.mp3")
                    st.audio("recap.mp3")
                    with open("recap.mp3", "rb") as f:
                        st.download_button("Download Audio (MP3)", f, file_name="recap.mp3")

                except Exception as e:
                    st.error(f"Error: {e}")
