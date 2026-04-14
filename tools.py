import os
import re
import ollama

MODEL_NAME = "gemma4:e2b"

# Strict Sandboxing: ensure output directory is relative to this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Characters not allowed in filenames (Windows + Unix safe)
UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def init_output_dir():
    """Ensure the sandboxed output directory exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and invalid characters.
    Returns a safe, flat filename.
    """
    if not filename or filename.strip() == "":
        return "default_output.txt"

    # Strip path components — defense against ../../etc/passwd
    safe = os.path.basename(filename.strip())

    # Remove any remaining unsafe characters
    safe = UNSAFE_FILENAME_CHARS.sub("_", safe)

    # Collapse multiple underscores
    safe = re.sub(r"_+", "_", safe).strip("_")

    if not safe:
        return "default_output.txt"

    return safe


def create_file(filename: str, content: str) -> dict:
    """
    Creates a file in the restricted ./output/ directory.
    Returns a structured result dict.
    """
    init_output_dir()
    safe_filename = _sanitize_filename(filename)
    file_path = os.path.join(OUTPUT_DIR, safe_filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {
            "success": True,
            "message": f"File `{safe_filename}` created successfully in `./output/`",
            "filename": safe_filename,
            "path": file_path,
            "size_bytes": os.path.getsize(file_path),
        }
    except PermissionError:
        return {
            "success": False,
            "message": f"Permission denied: cannot write to `{safe_filename}`. Check folder permissions.",
            "filename": safe_filename,
        }
    except OSError as e:
        return {
            "success": False,
            "message": f"OS error creating `{safe_filename}`: {e}",
            "filename": safe_filename,
        }


def summarize_text(text: str) -> dict:
    """
    Summarizes the given text using local LLM.
    """
    prompt = f"Please provide a concise, well-structured summary of the following text:\n\n{text}"
    result = general_chat(prompt)
    result["action"] = "summarize"
    return result


def general_chat(prompt: str) -> dict:
    """
    Answers a general conversational query using Ollama.
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            think=False,
        )
        return {
            "success": True,
            "message": response["message"]["content"],
            "action": "general_chat",
        }
    except Exception as e:
        error_type = type(e).__name__
        if "ConnectionError" in error_type or "ConnectError" in error_type:
            msg = "Cannot connect to Ollama. Is it running? (`ollama serve`)"
        else:
            msg = f"LLM execution error: {e}"
        return {"success": False, "message": msg, "action": "general_chat"}


def execute_tool(intent_dict: dict) -> dict:
    """
    Orchestration router: triggers the correct function based on a single intent dict.
    Returns a structured result dict.
    """
    intent = intent_dict.get("intent", "general_chat")
    filename = intent_dict.get("filename")
    content = intent_dict.get("content", "")

    if intent in ["create_file", "write_code"]:
        result = create_file(filename, content)
        result["action"] = intent
        return result

    elif intent == "summarize":
        return summarize_text(content)

    elif intent == "general_chat":
        return general_chat(content)

    else:
        return {
            "success": False,
            "message": f"Unknown intent: '{intent}'",
            "action": intent,
        }
