import streamlit as st
from google import genai
import os
import re

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="QuizCraft AI",
    page_icon="📝",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666666;
    margin-bottom: 30px;
}

.question-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    background-color: Black;
    margin-bottom: 15px;
}

.answer {
    padding: 10px;
    border-radius: 8px;
    background-color: #f1f5f9;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown(
    '<div class="title">📝 QuizCraft AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Interactive AI-Powered Question Generator</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# API KEY
# --------------------------------------------------

api_key = None

# First try Streamlit secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

# If not available, try environment variable
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Quiz Settings")

    topic = st.text_input(
        "📚 Topic",
        placeholder="Example: Python, DBMS, HTML"
    )

    difficulty = st.selectbox(
        "🎯 Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    question_type = st.selectbox(
        "❓ Question Type",
        [
            "Multiple Choice Questions",
            "True / False",
            "Short Answer Questions",
            "Mixed Questions"
        ]
    )

    number_of_questions = st.slider(
        "🔢 Number of Questions",
        min_value=1,
        max_value=20,
        value=5
    )

    include_answers = st.checkbox(
        "Show Answers",
        value=True
    )

    generate_button = st.button(
        "🚀 Generate Questions",
        use_container_width=True
    )

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "questions" not in st.session_state:
    st.session_state.questions = []

# --------------------------------------------------
# GENERATE QUESTIONS
# --------------------------------------------------

if generate_button:

    if not api_key:
        st.error(
            "Google API key not found. Please add GOOGLE_API_KEY "
            "to Streamlit Secrets or enter it as an environment variable."
        )
        st.stop()

    if not topic.strip():
        st.warning("Please enter a topic first.")
        st.stop()

    try:

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an expert educational question generator.

Generate {number_of_questions} questions about:
{topic}

Difficulty level:
{difficulty}

Question type:
{question_type}

Follow these rules:

1. Questions must be clear and educational.
2. Avoid duplicate questions.
3. Match the requested difficulty.
4. For multiple-choice questions, provide exactly four options.
5. Clearly identify the correct answer.
6. Provide a short explanation for every answer.
7. Format the response in a structured way.

Use this format:

QUESTION 1:
Question: <question>

Options:\n
A. <option>\n
B. <option>\n
C. <option>\n
D. <option>

Answer: <correct answer>

Explanation: <short explanation>

QUESTION 2:
...
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        st.session_state.questions = response.text

    except Exception as e:
        st.error(f"Error generating questions: {e}")

# --------------------------------------------------
# DISPLAY QUESTIONS
# --------------------------------------------------

if st.session_state.questions:

    st.subheader("📖 Generated Questions")

    raw_questions = st.session_state.questions

    # Split questions
    questions = re.split(
        r"QUESTION\s+\d+\s*:",
        raw_questions,
        flags=re.IGNORECASE
    )

    question_number = 1

    for question in questions:

        question = question.strip()

        if not question:
            continue

        # Remove answer and explanation if user doesn't want them
        display_question = question

        if not include_answers:

            display_question = re.split(
                r"Answer\s*:",
                display_question,
                flags=re.IGNORECASE
            )[0]

        st.markdown(
            f"""
            <div class="question-card">
                <h3>Question {question_number}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(display_question)

        question_number += 1

    # --------------------------------------------------
    # DOWNLOAD QUESTIONS
    # --------------------------------------------------

    st.divider()

    st.subheader("📥 Download")

    st.download_button(
        label="⬇️ Download Questions",
        data=raw_questions,
        file_name="generated_questions.txt",
        mime="text/plain"
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <center>
    <small>Built with Python, Streamlit and Google Gemini AI 🚀</small>
    </center>
    """,
    unsafe_allow_html=True
)
