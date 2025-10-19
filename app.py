import streamlit as st
import google.generativeai as genai
import re
import time

# --- UI Configuration ---
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="wide"
)

# --- Function to call the Google Gemini API ---
def call_gemini_api(api_key, article_text):
    """
    Calls the Google Gemini API with a specific prompt to analyze the article.
    """
    try:
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # We will use  gemini-1.0-pro model
        model = genai.GenerativeModel('gemini-1.0-pro')
        
        # The prompt is engineered to ask for a response
        prompt = f"""
        As an expert fact-checker and media analyst, your role is to analyze a news article and provide a structured, unbiased assessment of its credibility.

        Please analyze the following news article and provide your analysis in the exact format below, with each item on a new line:

        1.  **Credibility Score:** [A numerical score from 0 (completely false) to 100 (highly credible)]
        2.  **Verdict:** [A one-sentence conclusion, e.g., "This article appears credible," or "This article shows signs of being misinformation."]
        3.  **Summary & Reasoning:** [A detailed, neutral summary explaining your verdict. Mention specific elements like sourcing, tone, and potential biases.]

        --- ARTICLE TEXT ---
        {article_text}
        """

        # Make the API call
        response = model.generate_content(prompt)
        
        # Extract the text content from the response
        return response.text

    except Exception as e:
        # Handle potential errors 
        st.error(f"An error occurred with the Google Gemini API: {e}")
        return None


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
st.markdown("This tool uses the Google Gemini model to analyze news articles.")

article_text = st.text_area("Paste the full article text here:", height=250, placeholder="Enter the article content...")

analyze_button = st.button("Analyze Article", type="primary")

if analyze_button:
    if not article_text.strip():
        st.warning("Please paste some article text to analyze.")
    else:
        with st.spinner('Analyzing the article with Google Gemini... This may take a moment.'):
            try:
                # Retrieve the API key from Streamlit's secret management
                api_key = st.secrets["GEMINI_API_KEY"]
                analysis_result = call_gemini_api(api_key, article_text)
                if analysis_result:
                    update_ui_with_results(analysis_result)
            except KeyError:
                st.error("Google Gemini API key not found. Please add it to your Streamlit secrets.")

