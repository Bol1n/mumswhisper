import streamlit as st
import subprocess
import os
import time
from openai import OpenAI
from opencc import OpenCC


# --- CONFIG ---
client = OpenAI(api_key="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")  # <-- Replace with your real key
OUTPUT_FILE = "clip.mp3"

# --- STREAMLIT 中文 UI ---
st.title("🎧 YouTube 语音转文字工具")
st.markdown("使用 OpenAI Whisper，将 YouTube 视频的**指定片段**转录为文字（支持多种语言）。")

youtube_url = st.text_input("YouTube 视频链接", placeholder="https://www.youtube.com/watch?v=...")
start_time = st.text_input("开始时间 (时:分:秒)", "00:00:00")
end_time = st.text_input("结束时间 (时:分:秒)", "00:00:00")

language_codes = {
    "中文（普通话）": "zh",
    "英文": "en",
    "日文": "ja",
    "韩文": "ko",
    "西班牙文": "es",
    "法文": "fr",
    "德文": "de",
    "印地语": "hi",
    "越南语": "vi",
    "阿拉伯语": "ar",
    "菲律宾语（塔加洛语）": "tl"
}
language_display = st.selectbox("请选择语音所使用的语言", list(language_codes.keys()))
lang_code = language_codes[language_display]

if st.button("🔍 开始转录"):
    if not youtube_url or not start_time or not end_time:
        st.error("请填写所有内容。")
    else:
        progress = st.progress(0, text="⏬ 正在下载音频...")

        try:
            # Step 1: 下载并剪辑音频
            command = [
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                "--download-sections", f"*{start_time}-{end_time}",
                "-o", OUTPUT_FILE,
                youtube_url
            ]
            subprocess.run(command, check=True)
            progress.progress(30, text="✅ 音频下载完成")
        except Exception as e:
            st.error(f"下载失败: {e}")
            st.stop()

        time.sleep(0.5)
        progress.progress(50, text="📤 正在上传音频到 Whisper...")

        try:
            with open(OUTPUT_FILE, "rb") as audio_file:
                progress.progress(70, text="🧠 正在进行语音识别...")
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=lang_code
                )
                cc = OpenCC('t2s')  # Traditional → Simplified
                simplified_text = cc.convert(transcript.text)
            progress.progress(100, text="✅ 转录完成！")
            st.text_area("📝 转录结果（简体中文）", simplified_text, height=250)
        except Exception as e:
            st.error(f"转录失败: {e}")
        finally:
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
