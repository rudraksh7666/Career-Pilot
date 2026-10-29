"""Shared helpers: settings, Gemini calls, PDF reading, error messages."""

import io
import os
from collections.abc import Iterator

import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

DEFAULT_MODEL = "gemini-3.5-flash"
MAX_PDF_CHARS = 60_000


def get_secret(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets, then environment variables."""
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:  # no secrets.toml present
        pass
    return os.environ.get(name, default)


def sidebar_settings() -> tuple[str, str]:
    """Render API key / model settings in the sidebar and return them."""
    st.sidebar.header("Settings")
    api_key = get_secret("GEMINI_API_KEY")
    if api_key:
        st.sidebar.success("API key loaded")
    else:
        api_key = st.sidebar.text_input(
            "Gemini API key",
            type="password",
            help="Get a free key at https://aistudio.google.com/apikey",
        )
    model = st.sidebar.text_input("Model", value=get_secret("GEMINI_MODEL", DEFAULT_MODEL))
    return api_key, model


@st.cache_resource(show_spinner=False)
def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def generate(api_key: str, model: str, prompt: str, system: str | None = None,
             temperature: float = 0.7) -> str:
    """Single-shot generation. Raises on API errors (callers show them)."""
    response = _client(api_key).models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system, temperature=temperature),
    )
    return response.text or "(The model returned an empty response.)"


def stream_chat(api_key: str, model: str, history: list[dict], system: str) -> Iterator[str]:
    """Stream a reply for a chat history of {"role": "user"|"assistant", "content": str}."""
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in history
    ]
    stream = _client(api_key).models.generate_content_stream(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.7),
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text


@st.cache_data(show_spinner=False)
def extract_pdf_text(data: bytes) -> tuple[str, int, bool]:
    """Return (text, page_count, was_truncated) for a PDF given as bytes."""
    reader = PdfReader(io.BytesIO(data))
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(pages).strip()
    return text[:MAX_PDF_CHARS], len(reader.pages), len(text) > MAX_PDF_CHARS


def friendly_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "404" in msg or "no longer available" in msg or "not found" in msg:
        return (
            "That model isn't available. Change the model name in the sidebar "
            "(see the Gemini API docs for current model names)."
        )
    if "api key" in msg or "401" in msg or "403" in msg or "permission" in msg:
        return "The API key was rejected. Check that it is correct and active."
    if "429" in msg or "quota" in msg or "rate" in msg:
        return "Rate limit or quota reached. Wait a minute and try again."
    return f"Something went wrong: {exc}"
