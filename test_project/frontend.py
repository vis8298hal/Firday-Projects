import streamlit as st
from main import main as main

st.set_page_config(page_title="Sentiment Analyzer", page_icon="💬", layout="centered")
st.title("Text Sentiment Analyzer")
st.caption("Powered by LangChain and Google AI Studio")

@st.cache_resource
def load_chain():
    return main()

chain = load_chain()

user_text = st.text_area(
    "Enter text to analyze:",
    placeholder="e.g., The battery life is incredible, easily lasts two full days!",
    height=150,
)

if st.button("Analyze Sentiment", type="primary"):
    if not user_text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Analyzing..."):
            try:
                result = chain.invoke({"text": user_text})

                badge_map = {
                    "positive": "🟢 Positive",
                    "negative": "🔴 Negative",
                    "neutral": "⚪ Neutral",
                }

                col1, col2 = st.columns(2)
                col1.metric("Sentiment", badge_map[result.sentiment])
                col2.metric("Confidence", f"{result.confidence:.0%}")

                st.progress(min(max(result.confidence, 0.0), 1.0))
                st.info(f"**Reasoning:** {result.reasoning}")

            except Exception as e:
                st.error(f"Error analyzing text: {e}")