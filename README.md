# ⚡ VoiceForge — Voice-Controlled Local AI Agent

A fully local, privacy-preserving AI orchestration pipeline.

---

## 🏗️ High-Level Architecture & Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                        VoiceForge Pipeline                       │
├────────┬──────────────┬───────────┬────────────┬────────────────┤
│  🎤    │    🗣️        │   🧠      │    ⚙️      │      ✅        │
│ Audio  │ Transcription│  Intent   │  Execute   │    Output      │
│ Input  │   (STT)      │  (LLM)   │  (Tools)   │   (Results)    │
├────────┼──────────────┼───────────┼────────────┼────────────────┤
│Mic /   │Faster-Whisper│gemma3:4b │create_file │Styled result   │
│Upload  │(base, int8)  │via Ollama │write_code  │   cards with   │
│.wav    │              │JSON mode  │summarize   │   metadata     │
│.mp3    │              │           │general_chat│                │
└────────┴──────────────┴───────────┴────────────┴────────────────┘
```

1. **Input Layer:** Streamlit UI handles web-based microphone recording and `.wav`/`.mp3` file uploads.
2. **Transcription Layer (STT):** `audio_handler.py` runs [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) (base model, int8 CPU compute) to turn your voice into a text transcript.
3. **Reasoning Layer (LLM):** `agent.py` connects to local Ollama via the Python SDK. Using strict system prompting and JSON enforcement, it parses the transcribed text into one or more actionable intent structures (supports compound commands).
4. **Execution Layer (Tools):** `tools.py` receives the intent payloads, routes them to the correct sub-modules, enforces strict sandboxing to prevent path traversal, and executes the local logic.
5. **Output Layer:** Streamlit dynamically renders a pipeline tracker, styled result cards, and metadata for the entire session.

---

## 🚀 Setup and Installation

### Prerequisites

1. **Python 3.10+**: Ensure Python is installed.
2. **Ollama**: You must have [Ollama installed](https://ollama.com/download) on your system to run local LLMs.
3. **Pull the LLM model**: Once Ollama is installed, pull `gemma3:4b`:
   ```bash
   ollama pull gemma3:4b
   ```
4. **FFmpeg** *(optional but recommended)*: Faster-Whisper needs FFmpeg to decode audio formats.
   - **Windows**: `choco install ffmpeg` (via Chocolatey) or download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

### Installation Steps

1. **Clone or navigate** to this directory.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```
5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## ⚡ Hardware Workarounds & Scaling

| Configuration | Setting | Notes |
|---|---|---|
| **CPU (default)** | `device="cpu"`, `compute_type="int8"` | Works everywhere, ~3-8s per transcription |
| **NVIDIA GPU** | `device="cuda"`, `compute_type="float16"` | Change in `audio_handler.py` for near-instant STT |
| **Low-end fallback** | Groq/OpenAI API | Replace `transcribe_audio()` in `audio_handler.py` with an API call |

> **Note on API-based STT**: If your machine cannot run Faster-Whisper locally, you can swap the STT layer to use the [Groq Python Client](https://github.com/groq/groq-python) or OpenAI Whisper API. This breaks the "fully local" paradigm but enables ultra-fast STT on older hardware.
