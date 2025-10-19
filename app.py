import streamlit as st
import requests
import re
import time

# --- UI Configuration ---
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="wide"
)

# --- Function to call the Hugging Face Inference API ---
def call_huggingface_api(api_key, model_id, article_text):
    """
    Calls the Hugging Face Inference API for a specific model.
    Handles model loading with retries.
    """
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    # The prompt structure is specific to the Phi-3 Instruct model
    prompt = f"""<|user|>
You are an expert fact-checker and media analyst. Your role is to analyze a news article and provide a structured, unbiased assessment of its credibility in the exact format requested.

Please analyze the following news article and provide your analysis in the exact format below, with each item on a new line:

1.  **Credibility Score:** [A numerical score from 0 (completely false) to 100 (highly credible)]
2.  **Verdict:** [A one-sentence conclusion, e.g., "This article appears credible," or "This article shows signs of being misinformation."]
3.  **Summary & Reasoning:** [A detailed, neutral summary explaining your verdict. Mention specific elements like sourcing, tone, and potential biases.]

--- ARTICLE TEXT ---
{article_text}<|end|>
<|assistant|>
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "return_full_text": False,
            "temperature": 0.6,
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 503:
            st.info("The AI model is waking up, this might take up to a minute...")
            time.sleep(25)
            response = requests.post(api_url, headers=headers, json=payload)

        response.raise_for_status()
        
        data = response.json()
        return data[0]['generated_text']

    except requests.exceptions.HTTPError as e:
        st.error(f"A web error occurred: {e}. This might be your API key or the model name.")
        st.error(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Function to parse the AI response and update the UI ---
def update_ui_with_results(response_text):
    """
    Parses the structured text from the AI and updates the Streamlit UI elements.
    """
    score_match = re.search(r"Credibility Score:\s*(\d+)", response_text, re.IGNORECASE)
    verdict_match = re.search(r"Verdict:\s*(.*)", response_text, re.IGNORECASE)
    summary_match = re.search(r"Summary & Reasoning:\s*([\s\S]*)", response_text, re.IGNORECASE)

    if score_match and verdict_match and summary_match:
        score = int(score_match.group(1))
        verdict = verdict_match.group(1).strip()
        summary = summary_match.group(1).strip()

        st.subheader("Analysis Results")
        st.progress(score, text=f"Credibility Score: {score}/100")

        if score < 40:
            st.error(f"**Verdict:** {verdict}")
        elif score < 70:
            st.warning(f"**Verdict:** {verdict}")
        else:
            st.success(f"**Verdict:** {verdict}")

        st.info(f"**Summary & Reasoning:**\n\n{summary}")
    else:
        st.warning("Could not parse the AI's response. Displaying raw output:")
        st.text(response_text)

# --- Main App Interface ---
st.title("📰 AI-Powered Fake News Detector")
st.markdown("This tool uses AI to analyze news articles.")

article_text = st.text_area("Paste the full article text here:", height=250, placeholder="Enter the article content...")

analyze_button = st.button("Analyze Article", type="primary")

if analyze_button:
    if not article_text.strip():
        st.warning("Please paste some article text to analyze.")
    else:
        with st.spinner('Analyzing the article... This may take a moment.'):
            try:
                api_key = st.secrets["HUGGINGFACE_API_KEY"]
                # This is a non-gated model that works without pre-approval.
                model_to_use = "microsoft/Phi-3-mini-4k-instruct"
                analysis_result = call_huggingface_api(api_key, model_to_use, article_text)
                if analysis_result:
                    update_ui_with_results(analysis_result)
            except KeyError:
                st.error("Hugging Face API key not found. Please add it to your Streamlit secrets.")

