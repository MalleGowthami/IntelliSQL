"""
app.py
Streamlit web application for Intelligent SQL Querying with Gemini Pro.
Provides a chat-like interface for users to ask questions in natural language
and get SQL-powered answers from the database.
"""

import streamlit as st
import pandas as pd
import os
from database_setup import create_database, get_schema_info, DB_PATH
from sql_agent import ask_question

# ── Page configuration ──
st.set_page_config(
    page_title="Intelligent SQL Query with Gemini Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #5f6368;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sql-box {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1a73e8;
    }
</style>
""", unsafe_allow_html=True)


def initialize_database():
    """Ensure the database exists; create if missing."""
    if not os.path.exists(DB_PATH):
        with st.spinner("Setting up the sample database..."):
            create_database()
        st.success("Sample database created successfully!")


def display_sidebar():
    """Render the sidebar with schema info and sample questions."""
    with st.sidebar:
        st.header("📊 Database Schema")
        st.markdown("---")

        schema = get_schema_info()
        for table_block in schema.split("\n\n"):
            lines = table_block.strip().split("\n")
            if lines:
                table_name = lines[0].replace("Table: ", "")
                with st.expander(f"📋 {table_name}", expanded=False):
                    for col_line in lines[1:]:
                        st.text(col_line.strip())

        st.markdown("---")
        st.header("💡 Sample Questions")
        sample_questions = [
            "Show all employees in Engineering department",
            "What is the average salary by department?",
            "List all active projects with their budgets",
            "Who is assigned to the AI Chatbot project?",
            "Which employee earns the highest salary?",
            "How many employees were hired in 2023?",
            "What is the total budget of completed projects?",
            "Show employees and their project assignments",
        ]
        for q in sample_questions:
            if st.button(f"🔹 {q}", key=q, use_container_width=True):
                st.session_state["selected_question"] = q

        st.markdown("---")
        st.caption("Powered by Google Gemini Pro & Streamlit")


def main():
    """Main application entry point."""

    # Initialize database
    initialize_database()

    # Sidebar
    display_sidebar()

    # ── Main content ──
    st.markdown('<p class="main-header">🤖 Intelligent SQL Querying</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Ask questions in plain English — '
        'Gemini Pro converts them to SQL and fetches results from the database</p>',
        unsafe_allow_html=True,
    )

    # ── Chat history ──
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Input area ──
    col1, col2 = st.columns([5, 1])
    with col1:
        default_q = st.session_state.pop("selected_question", "")
        user_question = st.text_input(
            "🔍 Ask a question about the database:",
            value=default_q,
            placeholder="e.g., Show me all employees in the Engineering department",
            key="question_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button("Ask  🚀", use_container_width=True, type="primary")

    # ── Process question ──
    if ask_button and user_question.strip():
        with st.spinner("🔄 Gemini Pro is thinking..."):
            result = ask_question(user_question.strip())

        # Store in history
        st.session_state.chat_history.append(result)

        # Display result
        if result["error"]:
            st.error(f"❌ Error: {result['error']}")
        else:
            # SQL Query
            st.markdown("### 📝 Generated SQL Query")
            st.code(result["sql_query"], language="sql")

            # Results table
            if result["rows"]:
                st.markdown(f"### 📊 Query Results ({len(result['rows'])} rows)")
                df = pd.DataFrame(result["rows"], columns=result["columns"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("The query returned no results.")

            # Natural language answer
            st.markdown("### 💬 Answer")
            st.markdown(
                f'<div class="result-card">{result["answer"]}</div>',
                unsafe_allow_html=True,
            )

    elif ask_button:
        st.warning("Please enter a question first.")

    # ── Chat history ──
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 📜 Query History")

        for i, entry in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(
                f"{'✅' if not entry['error'] else '❌'} {entry['question']}",
                expanded=False,
            ):
                if entry["error"]:
                    st.error(entry["error"])
                else:
                    st.code(entry["sql_query"], language="sql")
                    if entry["rows"]:
                        df = pd.DataFrame(entry["rows"], columns=entry["columns"])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    st.markdown(entry["answer"])

        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()

    # ── Footer ──
    st.markdown("---")
    st.markdown(
        "<center><small>Built with ❤️ using Google Gemini Pro | "
        "Intelligent SQL Querying with LLMs</small></center>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
