from openai import OpenAI

def summarize_personality(personality_text: str, openai_api_key: str) -> str:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    prompt = f"""
You are a psychologist writing a brief personality evaluation for a client.

Below is a facet-level personality profile of the individual, based on the Big Five personality framework:

{{
{personality_text}
}}

Step1. Please write a concise summary (3–5 sentences) that integrates the major patterns in the person's personality traits.
Use professional, clinical, or psychotherapeutic language — as you would in a psychological report.
Avoid repeating the facet names. Focus on interpretation and synthesis.

Step2. Now write the same summary, but in natural everyday language for a general audience.
Use casual tone and accessible vocabulary.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes personality profiles."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
