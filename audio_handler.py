import time
from faster_whisper import WhisperModel

# Initialize the model once when the module is imported.
# We use the "base" model size and "int8" compute type for maximum compatibility on CPU/GPU.
MODEL_SIZE = "base"
_model = None


def _get_model() -> WhisperModel:
    """Lazy-load the Whisper model to avoid blocking import time."""
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes the given audio file using Faster-Whisper.
    Returns a dict with transcription text, language info, and timing metadata.
    On failure, returns a dict with an 'error' key.
    """
    start_time = time.time()

    try:
        model = _get_model()
        segments, info = model.transcribe(file_path, beam_size=5)

        # Combine all segments into a single transcription string
        transcription_parts = []
        for segment in segments:
            transcription_parts.append(segment.text)

        transcription = " ".join(transcription_parts).strip()
        elapsed = round(time.time() - start_time, 2)

        return {
            "text": transcription,
            "language": getattr(info, "language", "unknown"),
            "language_probability": round(getattr(info, "language_probability", 0.0), 2),
            "duration_seconds": elapsed,
            "model_size": MODEL_SIZE,
            "error": None,
        }

    except RuntimeError as e:
        return {
            "text": "",
            "error": f"Audio decoding failed — the file may be corrupt or in an unsupported format. Details: {e}",
            "duration_seconds": round(time.time() - start_time, 2),
        }
    except FileNotFoundError:
        return {
            "text": "",
            "error": "Audio file not found. It may have been deleted before processing.",
            "duration_seconds": 0.0,
        }
    except Exception as e:
        return {
            "text": "",
            "error": f"Unexpected transcription error: {e}",
            "duration_seconds": round(time.time() - start_time, 2),
        }
