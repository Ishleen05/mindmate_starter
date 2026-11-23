
import os
import streamlit as st
from openai import OpenAI


def generate(system_prompt, user_prompt, simulated_prompt):
    """
    Generate a response using the OpenAI API when configured.
    Otherwise, return a clearly labelled simulated response.
    """

    # First check environment variables
    api_key = os.getenv("OPENAI_API_KEY", "")

    # Check Streamlit secrets only if available
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", "")
        except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
            api_key = ""

    # Use simulated functionality when no API key exists
    if not api_key:
        return simulated_prompt, "Simulated AI"

    # Use real AI when an API key is configured
    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            instructions=system_prompt,
            input=user_prompt
        )

        return response.output_text, "Real AI"

    except Exception as error:
        return (
            f"AI service is currently unavailable. "
            f"Simulated response: {simulated_prompt}",
            "Simulated AI (API fallback)"
        )

