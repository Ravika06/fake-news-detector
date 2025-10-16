import streamlit as st
import openai
import re
import time

# --- UI Configuration ---
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="wide"
)

# --- Function to call the OpenAI API ---
def call_openai_api(api_key, article_text):
    """
    Calls the OpenAI API with a specific prompt to analyze the article.
    """
    try:
        # Initialize the OpenAI client with the API key
        client = openai.OpenAI(api_key=api_key)

        # The prompt is engineered to ask for a structured response
        system_prompt = "You are an expert fact-checker and media analyst. Your role is to analyze a news article and provide a structured, unbiased assessment of its credibility."
        user_prompt = f"""
        Please analyze the following news article and provide your analysis in the exact format below, with each item on a new line:

        1.  **Credibility Score:** [A numerical score from 0 (completely false) to 100 (highly credible)]
        2.  **Verdict:** [A one-sentence conclusion, e.g., "This article appears credible," or "This article shows signs of being misinformation."]
        3.  **Summary & Reasoning:** [A detailed, neutral summary explaining your verdict. Mention specific elements like sourcing, tone, and potential biases.]

        --- ARTICLE TEXT ---
        {article_text}
        """

        # Make the API call to the GPT-3.5-Turbo model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5, # Keep the response focused and consistent
        )

        # Extract the text content from the response
        return response.choices[0].message.content

    except openai.APIError as e:
        # Handle specific API errors (e.g., rate limits, invalid key)
        st.error(f"An OpenAI API error occurred: {e}. This might be an issue with your API key or account.")
        return None
    except Exception as e:
        # Handle other potential errors (e.g., network issues)
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Function to parse the AI response and update the UI ---
def update_ui_with_results(response_text):
    """
    Parses the structured text from the AI and updates the Streamlit UI elements.
    """
    # Use regular expressions to find the score, verdict, and summary
    score_match = re.search(r"Credibility Score:\s*(\d+)", response_text, re.IGNORECASE)
    verdict_match = re.search(r"Verdict:\s*(.*)", response_text, re.IGNORECASE)
    summary_match = re.search(r"Summary & Reasoning:\s*([\s\S]*)", response_text, re.IGNORECASE)

    if score_match and verdict_match and summary_match:
        score = int(score_match.group(1))
        verdict = verdict_match.group(1).strip()
        summary = summary_match.group(1).strip()

        # Display the results in styled containers
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
        # If parsing fails, show the raw response for debugging
        st.warning("Could not parse the AI's response. Displaying raw output:")
        st.text(response_text)

# --- Main App Interface ---
st.title("📰 AI-Powered Fake News Detector")
st.markdown("This tool uses the GPT-3.5-Turbo model to analyze news articles. Paste the text of an article below to get started.")

article_text = st.text_area("Paste the full article text here:", height=250, placeholder="Enter the article content...")

analyze_button = st.button("Analyze Article", type="primary")

if analyze_button:
    if not article_text.strip():
        st.warning("Please paste some article text to analyze.")
    else:
        with st.spinner('Analyzing the article... This may take a moment.'):
            # Retrieve the API key from Streamlit's secret management
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                analysis_result = call_openai_api(api_key, article_text)
                if analysis_result:
                    update_ui_with_results(analysis_result)
            except KeyError:
                st.error("OpenAI API key not found. Please add it to your Streamlit secrets.")

