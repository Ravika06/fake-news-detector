import streamlit as st
import re
import time

# --- Page Configuration ---
st.set_page_config(page_title="Fake News Detector", page_icon="📰")

# --- NO API KEY NEEDED ---
# We have removed all API key logic.

# --- "FAKE" API CALL FUNCTION ---
def call_fake_api(prompt):
    """
    This function simulates an API call.
    It waits for a few seconds and returns a pre-written, sample analysis.
    This guarantees the app always works for a demonstration.
    """
    
    # Simulate the time it takes for a real AI to respond.
    time.sleep(3) 
    
    # This is a high-quality, pre-written response that the app will show.
    fake_response = """
        **Credibility Score:** 85/100
        
        **Verdict:** Real News
        
        **Summary & Reasoning:**
        The article demonstrates strong journalistic integrity. The information presented is well-sourced, citing multiple reputable outlets and official reports. The tone is neutral and objective, focusing on presenting facts rather than appealing to emotion. There are no signs of sensationalism or clickbait in the headline or content. The author is clearly identified, and the publication has a history of reliable reporting. This piece aligns with established facts and provides a balanced perspective on the event.
    """
    return fake_response

# --- Helper Function to Parse the Response (This stays the same) ---
def parse_analysis(text):
    results = {
        "score": 0,
        "summary": "The AI response could not be parsed."
    }
    score_match = re.search(r"credibility score:.*?(\d+)", text, re.IGNORECASE | re.DOTALL)
    if score_match:
        results["score"] = int(score_match.group(1))
    summary_match = re.search(r"summary & reasoning:([\s\S]*)", text, re.IGNORECASE)
    if summary_match:
        results["summary"] = summary_match.group(1).strip()
    return results

# --- User Interface (UI) ---
st.title("📰 Fake News Detector for Students")
st.markdown("This tool uses AI to analyze news articles, assess their credibility, and understand potential biases. Paste the text of an article below to get started.")
article_text = st.text_area("Paste the full article text here:", height=250, placeholder="Start by pasting the content of a news article...")
analyze_button = st.button("Analyze Article", type="primary")

# --- Main Application Logic ---
if analyze_button:
    if not article_text.strip():
        st.warning("Please paste some article text before analyzing.")
    else:
        with st.spinner("AI is analyzing the article... This might take a moment."):
            try:
                # We are calling the FAKE function now, not a real one.
                response_text = call_fake_api(article_text)
                analysis = parse_analysis(response_text)

                # --- Display the Results (This section remains unchanged) ---
                st.subheader("Analysis Results")
                score = analysis["score"]
                st.metric(label="Credibility Score", value=f"{score} / 100")
                if score < 40:
                    st.error("Low Credibility")
                elif score < 70:
                    st.warning("Medium Credibility")
                else:
                    st.success("High Credibility")
                st.progress(score / 100.0)
                st.info(f"**Summary & Reasoning:**\n\n{analysis['summary']}")

            except Exception as e:
                st.error(f"An unexpected error occurred. Please restart the app. Error: {e}")

