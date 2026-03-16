import streamlit as st
import requests

st.set_page_config(
    page_title="AI Requirements Engine",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS (Design aligned with application layout)
# -------------------------------------------------

st.markdown("""
<style>

/* Slider background */
.stSlider div[data-baseweb="slider"] {
    background: transparent !important;
}

/* Slider track */
.stSlider div[data-baseweb="slider"] > div {
    background-color: rgba(255,255,255,0.25) !important;
    height: 6px;
    border-radius: 10px;
}

/* Active slider area */
.stSlider div[data-baseweb="slider"] div div {
    background-color: #D1DBFF !important;
}

/* Slider handle */
.stSlider [role="slider"] {
    background-color: #000B31 !important;
    border: 2px solid white !important;
    width: 18px;
    height: 18px;
}

/* App background */
.stApp {
    background-color: #ECEDFB;
}

/* Global text color */
body, p, span, div, label {
    color: #000B31 !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #000B31 !important;
}

/* Streamlit widgets */
.stMarkdown, .stText, .stTextInput, .stSlider {
    color: #000B31 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #000B31;
    color: white;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Result cards */
.card {
    background-color: white;
    padding: 22px;
    border-radius: 10px;
    border-left: 6px solid #000B31;
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* LLM explanation box */
.llm-box {
    background-color: #F4F5FD;
    padding: 20px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("AI Requirements Engine")

st.markdown(
"""
Semantic search over requirements using embeddings, vector similarity, and LLM-based explanations.
"""
)

# -------------------------------------------------
# SIDEBAR (Query / Settings)
# -------------------------------------------------

with st.sidebar:

    st.header("Search")

    query = st.text_input("Requirement")

    top_k = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5
    )

    analyze_button = st.button("Analyze")

# -------------------------------------------------
# MAIN AREA
# -------------------------------------------------

if analyze_button and query:

    with st.spinner("Analyzing requirements..."):

        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "query": query,
                "top_k": top_k
            }
        )

        if response.status_code != 200:
            st.error("API error")
            st.write(response.text)
            st.stop()

        data = response.json()

    # -------------------------------------------------
    # SIMILAR REQUIREMENTS
    # -------------------------------------------------

    st.subheader("Similar Requirements")

    for r in data["results"]:

        similarity_percent = r["similarity"] * 100

        st.markdown(f"""
        <div class="card">
        <b>{r['id']}</b>
        <span class="similarity"> — {similarity_percent:.1f}% similarity</span>
        <br><br>
        {r["text"]}
        </div>
        """, unsafe_allow_html=True)

        st.progress(r["similarity"])

    # -------------------------------------------------
    # LLM EXPLANATION
    # -------------------------------------------------

    st.subheader("LLM Explanation")

    st.markdown(f"""
    <div class="llm-box">
    {data["llm_explanation"]}
    </div>
    """, unsafe_allow_html=True)

else:

    st.info("Enter a requirement and click **Analyze**.")