from flask import Blueprint, request, jsonify
from datetime import datetime

from utils.financial_context import get_financial_context
from utils.llm_service import call_llm

chatbot_bp = Blueprint('chatbot', __name__)

# ── System prompt template ────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """\
You are FinVerde — a smart, friendly, and concise personal finance advisor chatbot.

You have access to the user's real financial data shown below. Always ground your
answers in that data. When the data is insufficient or the question is general,
give practical, evidence-based financial advice.

Guidelines:
- Be concise but complete (aim for 3-6 lines max unless a detailed breakdown is asked).
- Use bullet points (•) for lists.
- Use dollar amounts and percentages from the data when relevant.
- Speak in first-person about the user ("Your top expense is…", "You spent…").
- If the user asks a follow-up like "what about last month?" or "which one?",
  use the conversation history to understand what they mean.
- Never make up numbers. If data is missing, say so clearly.
- For general finance questions (emergency funds, 50/30/20, investing, etc.)
  give helpful advice even without personal data.

{financial_context}
"""

# ── Chat endpoint ─────────────────────────────────────────────────────────────

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    POST /api/chat
    Payload:
      - message:    string  (required) — the user's latest message
      - user_id:    int     (default 1)
      - month_year: YYYY-MM (default: current month)
      - history:    list of {role: "user"|"bot", text: "..."} (last 10 turns)
    """
    data       = request.get_json() or {}
    message    = data.get('message', '').strip()
    user_id    = data.get('user_id', 1)
    month_year = data.get('month_year', datetime.now().strftime('%Y-%m'))
    raw_history = data.get('history', [])

    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400

    # ── 1. Fetch financial context from DB ────────────────────────────────────
    try:
        financial_context = get_financial_context(user_id=user_id, month_year=month_year)
    except Exception as e:
        financial_context = f"[Financial data unavailable: {str(e)}]"

    # ── 2. Build system prompt ────────────────────────────────────────────────
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(financial_context=financial_context)

    # ── 3. Convert frontend history to LLM format (last 10 turns max) ────────
    # Frontend sends: [{role: "user"|"bot", text: "..."}]
    # LLM expects:   [{role: "user"|"assistant", content: "..."}]
    llm_history = []
    for turn in raw_history[-10:]:          # cap at 10 turns for token efficiency
        role    = "user" if turn.get("role") == "user" else "assistant"
        content = turn.get("text", "").strip()
        if content:
            llm_history.append({"role": role, "content": content})

    # ── 4. Call LLM ───────────────────────────────────────────────────────────
    try:
        reply = call_llm(
            system_prompt=system_prompt,
            history=llm_history,
            user_message=message,
        )
    except Exception as e:
        error_msg = str(e)
        # Surface a friendly message but also log the real error
        print(f"[chatbot] LLM call failed: {error_msg}")

        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
            friendly = (
                "⚠️ I can't connect to the AI service right now — the API key "
                "may be missing or invalid. Please set LLM_API_KEY in your database/.env file."
            )
        elif "rate" in error_msg.lower() or "429" in error_msg:
            friendly = "⚠️ I've hit the rate limit for the AI service. Please wait a moment and try again."
        else:
            friendly = f"⚠️ Something went wrong with the AI service: {error_msg}"

        return jsonify({"success": False, "error": friendly}), 500

    return jsonify({
        "success":    True,
        "response":   reply,
        "month_year": month_year,
    }), 200
