"""
sql_agent.py
Core engine that uses Google Gemini Pro to convert natural language questions
into SQL queries, execute them, and return human-readable answers.
"""

import os
import sys
import time
import socket
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
from database_setup import DB_PATH, get_schema_info

# Force IPv4 to avoid IPv6 connectivity issues
original_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(*args, **kwargs):
    responses = original_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET] or responses

socket.getaddrinfo = _ipv4_only_getaddrinfo

# Load environment variables
load_dotenv()


def configure_gemini():
    """Configure the Gemini API with the user's API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        raise ValueError(
            "Please set a valid GOOGLE_API_KEY in your .env file.\n"
            "Get one at: https://makersuite.google.com/app/apikey"
        )
    genai.configure(api_key=api_key)


def get_gemini_model():
    """Return the Gemini Pro model instance."""
    configure_gemini()
    return genai.GenerativeModel("gemini-2.5-flash")


def call_gemini_with_retry(model, prompt, max_retries=3):
    """Call Gemini API with retry logic for transient network errors."""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1 and ("503" in error_msg or "timeout" in error_msg.lower() or "connect" in error_msg.lower()):
                wait_time = 2 ** (attempt + 1)  # 2s, 4s, 8s
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise


# ── Prompt template for SQL generation ──
SQL_GENERATION_PROMPT = """
You are an expert SQL query generator. You are given a SQLite database schema
and a natural language question. Your job is to generate a valid SQLite SQL query
that answers the question.

DATABASE SCHEMA:
{schema}

RULES:
1. Generate ONLY a valid SQLite SELECT query — no INSERT, UPDATE, DELETE, DROP, or ALTER.
2. Use only the tables and columns listed in the schema above.
3. Return ONLY the raw SQL query — no explanations, no markdown, no code fences.
4. Use proper JOINs when data spans multiple tables.
5. Use aliases for readability when joining tables.
6. If the question is ambiguous, make a reasonable assumption and proceed.
7. Always end the query with a semicolon.

QUESTION: {question}

SQL QUERY:
"""

# ── Prompt template for answer generation ──
ANSWER_GENERATION_PROMPT = """
You are a helpful data assistant. Given a user's question, the SQL query that was
executed, and the results from the database, provide a clear, concise, and
human-friendly answer.

QUESTION: {question}

SQL QUERY EXECUTED:
{sql_query}

QUERY RESULTS:
{results}

COLUMN NAMES: {columns}

Instructions:
- Provide a natural language answer summarizing the results.
- If the results are tabular, present them in a well-formatted way.
- If no results were returned, say so politely and suggest possible reasons.
- Keep the answer concise but informative.

ANSWER:
"""


def generate_sql_query(question: str) -> str:
    """
    Use Gemini Pro to convert a natural language question into a SQL query.

    Args:
        question: The user's natural language question.

    Returns:
        A SQL query string.
    """
    model = get_gemini_model()
    schema = get_schema_info()

    prompt = SQL_GENERATION_PROMPT.format(schema=schema, question=question)
    response = call_gemini_with_retry(model, prompt)

    sql_query = response.text.strip()

    # Clean up: remove markdown code fences if the model accidentally adds them
    if sql_query.startswith("```"):
        lines = sql_query.split("\n")
        sql_query = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        ).strip()

    return sql_query


def execute_sql_query(sql_query: str) -> tuple:
    """
    Execute a SQL query against the SQLite database.

    Args:
        sql_query: The SQL query to execute.

    Returns:
        A tuple of (column_names, rows).

    Raises:
        ValueError: If the query is not a SELECT statement (safety check).
    """
    # Safety check — only allow SELECT queries
    normalized = sql_query.strip().upper()
    if not normalized.startswith("SELECT"):
        raise ValueError(
            "Only SELECT queries are allowed. "
            "The generated query was not a SELECT statement."
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(sql_query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return columns, rows
    except sqlite3.Error as e:
        raise RuntimeError(f"SQL execution error: {e}")
    finally:
        conn.close()


def generate_natural_answer(question: str, sql_query: str, columns: list, rows: list) -> str:
    """
    Use Gemini Pro to generate a natural language answer from query results.

    Args:
        question: The original user question.
        sql_query: The SQL query that was executed.
        columns: Column names from the result.
        rows: Result rows.

    Returns:
        A human-friendly answer string.
    """
    model = get_gemini_model()

    # Format results for readability
    if rows:
        results_str = "\n".join(str(row) for row in rows[:50])  # Limit to 50 rows
        if len(rows) > 50:
            results_str += f"\n... and {len(rows) - 50} more rows"
    else:
        results_str = "No results found."

    prompt = ANSWER_GENERATION_PROMPT.format(
        question=question,
        sql_query=sql_query,
        results=results_str,
        columns=columns,
    )

    response = call_gemini_with_retry(model, prompt)
    return response.text.strip()


def ask_question(question: str) -> dict:
    """
    End-to-end pipeline: question → SQL → execute → natural answer.

    Args:
        question: The user's natural language question.

    Returns:
        A dict with keys: sql_query, columns, rows, answer, error (if any).
    """
    result = {
        "question": question,
        "sql_query": None,
        "columns": None,
        "rows": None,
        "answer": None,
        "error": None,
    }

    try:
        # Step 1 — Generate SQL
        sql_query = generate_sql_query(question)
        result["sql_query"] = sql_query

        # Step 2 — Execute SQL
        columns, rows = execute_sql_query(sql_query)
        result["columns"] = columns
        result["rows"] = rows

        # Step 3 — Generate natural language answer
        answer = generate_natural_answer(question, sql_query, columns, rows)
        result["answer"] = answer

    except Exception as e:
        result["error"] = str(e)

    return result


# ── Quick CLI test ──
if __name__ == "__main__":
    test_questions = [
        "Show me all employees in the Engineering department",
        "What is the total budget of all active projects?",
        "Who earns the highest salary?",
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {q}")
        res = ask_question(q)
        if res["error"]:
            print(f"Error: {res['error']}")
        else:
            print(f"SQL: {res['sql_query']}")
            print(f"Answer: {res['answer']}")
