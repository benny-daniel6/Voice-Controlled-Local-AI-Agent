import json
import time
import ollama

MODEL_NAME = "gemma4:e2b"

SYSTEM_PROMPT = """You are a strict, highly capable Intent Classification AI.
Your job is to analyze the user's text and output a structured JSON object reflecting ALL of their intents and parameters.

IMPORTANT: The user may issue COMPOUND COMMANDS containing multiple actions in a single sentence.
You MUST identify every distinct action and return them all.

You must choose from the following intents for each action:
- "create_file": When the user asks to create, save, or write text into a new file.
- "write_code": When the user asks to write, generate, or create code/scripts.
- "summarize": When the user explicitly asks to summarize some text or concept.
- "general_chat": For any other request, question, or general conversation.

You MUST respond strictly in the following JSON schema:
{
  "intents": [
    {
      "intent": "create_file" | "write_code" | "summarize" | "general_chat",
      "filename": "string or null",
      "content": "string"
    }
  ]
}

Instructions for parameters:
- For "create_file" or "write_code": If the user implies a filename (e.g. "create a python script named basic.py"), set `filename` to that value. Otherwise, generate a sensible default name with the correct extension. The `content` should be the actual file content or the generated code (complete, runnable code — not pseudocode).
- For "summarize": The `content` should be the summary of the text the user refers to.
- For "general_chat": The `content` should be a helpful response to the user's question.

Examples of compound commands:
- "Summarize this text and save it to summary.txt" → two intents: summarize + create_file
- "Write a hello world script in Python and also explain what recursion is" → two intents: write_code + general_chat

DO NOT include any markdown formatting, explanations, or extra text outside the JSON block. Your entire response must be valid parseable JSON.
"""


def get_intent_and_params(user_text: str) -> dict:
    """
    Calls the local Ollama model to classify intent and extract parameters.
    Supports compound commands — always returns a dict with an 'intents' list.
    """
    start_time = time.time()

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            format="json",
            options={"num_ctx": 4096},
            think=False,
        )

        response_text = response["message"]["content"]
        elapsed = round(time.time() - start_time, 2)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            # Retry once on malformed JSON
            retry_response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Your previous response was not valid JSON. Please try again for this input:\n\n{user_text}",
                    },
                ],
                format="json",
                options={"num_ctx": 4096},
                think=False,
            )
            try:
                parsed = json.loads(retry_response["message"]["content"])
                elapsed = round(time.time() - start_time, 2)
            except json.JSONDecodeError:
                return {
                    "intents": [
                        {
                            "intent": "general_chat",
                            "filename": None,
                            "content": user_text,
                        }
                    ],
                    "model": MODEL_NAME,
                    "duration_seconds": elapsed,
                    "error": "LLM returned invalid JSON after retry. Falling back to general_chat.",
                }

        # Normalize: handle both old single-intent and new multi-intent formats
        if "intents" in parsed and isinstance(parsed["intents"], list):
            intents_list = parsed["intents"]
        elif "intent" in parsed:
            # Backward compat: single-intent response
            intents_list = [parsed]
        else:
            intents_list = [
                {"intent": "general_chat", "filename": None, "content": user_text}
            ]

        return {
            "intents": intents_list,
            "model": MODEL_NAME,
            "duration_seconds": elapsed,
            "error": None,
        }

    except Exception as e:
        error_type = type(e).__name__
        if "ConnectionError" in error_type or "ConnectError" in error_type:
            error_msg = (
                "Cannot connect to Ollama. Please make sure Ollama is running "
                "(run `ollama serve` in a terminal)."
            )
        else:
            error_msg = f"LLM processing failed: {e}"

        return {
            "intents": [
                {"intent": "general_chat", "filename": None, "content": user_text}
            ],
            "model": MODEL_NAME,
            "duration_seconds": round(time.time() - start_time, 2),
            "error": error_msg,
        }
