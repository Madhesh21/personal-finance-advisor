from flask import Blueprint, request, jsonify
from config import get_db_connection
import mysql.connector
from datetime import datetime
import spacy

chatbot_bp = Blueprint('chatbot', __name__)

# Load SpaCy model lazily or at module level
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    nlp = None
    print(f"Failed to load spacy model: {e}")

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    POST /api/chat
    Payload:
      - message: string
      - user_id: int (default 1)
      - month_year: YYYY-MM (default: current month)
    """
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    user_id = data.get('user_id', 1)
    month_year = data.get('month_year', datetime.now().strftime('%Y-%m'))
    
    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400
        
    try:
        year, month = month_year.split('-')
    except ValueError:
        return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM"}), 400

    if not nlp:
        return jsonify({"success": False, "error": "NLP model not loaded. Please ensure spacy and en_core_web_sm are installed."}), 500

    # Parse message with spaCy
    doc = nlp(message.lower())
    
    # Extract lemmas to determine intent
    lemmas = [token.lemma_ for token in doc]
    
    # Intent 1: "Where did I spend most?" (spend + most / highest / top)
    # Intent 2: "How can I save more?" (save / reduce / cut)
    
    intent = "UNKNOWN"
    
    spend_keywords = {"spend", "spent", "spending", "expense", "cost"}
    most_keywords = {"most", "highest", "top", "biggest", "majority"}
    
    save_keywords = {"save", "saving", "savings", "reduce", "cut", "decrease", "less"}
    
    # Rule-based check combined with NLP lemmas
    has_spend = any(k in lemmas for k in spend_keywords) or any(k in message.lower() for k in spend_keywords)
    has_most = any(k in lemmas for k in most_keywords) or any(k in message.lower() for k in most_keywords)
    has_save = any(k in lemmas for k in save_keywords) or any(k in message.lower() for k in save_keywords)
    
    if has_save:
        intent = "SAVE_MORE"
    elif has_spend and has_most:
        intent = "SPEND_MOST"
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        reply = "I'm not sure how to answer that yet. Try asking me 'Where did I spend most?' or 'How can I save more?'"
        
        if intent == "SPEND_MOST":
            cursor.execute('''
                SELECT c.category_name, SUM(t.amount) as actual_spent
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE t.user_id = %s 
                  AND t.transaction_type = 'EXPENSE'
                  AND YEAR(t.transaction_date) = %s 
                  AND MONTH(t.transaction_date) = %s
                GROUP BY c.category_name
                ORDER BY actual_spent DESC
                LIMIT 1
            ''', (user_id, int(year), int(month)))
            
            row = cursor.fetchone()
            if row:
                cat = row['category_name']
                amt = float(row['actual_spent'])
                reply = f"In {month_year}, your highest expense was on {cat}, totaling ${amt:,.2f}."
            else:
                reply = f"I couldn't find any expenses for {month_year}."
                
        elif intent == "SAVE_MORE":
            # 1. Check for budget exceptions
            cursor.execute("""
                SELECT
                    c.category_name,
                    COALESCE(b.monthly_limit, 0) AS budget_limit,
                    COALESCE(SUM(t.amount), 0) AS actual_spent
                FROM categories c
                LEFT JOIN budgets b 
                    ON b.category_id = c.category_id 
                   AND b.user_id = %s AND b.month_year = %s
                LEFT JOIN transactions t 
                    ON t.category_id = c.category_id 
                   AND t.user_id = %s 
                   AND t.transaction_type = 'EXPENSE'
                   AND YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s
                WHERE c.category_type = 'EXPENSE'
                GROUP BY c.category_name, b.monthly_limit
            """, (user_id, month_year, user_id, int(year), int(month)))
            
            rows = cursor.fetchall()
            exceeded = []
            highest_cat = None
            highest_amt = 0.0
            
            for r in rows:
                cat = r['category_name']
                limit = float(r['budget_limit'])
                spent = float(r['actual_spent'])
                
                if cat.lower() not in ('rent', 'mortgage', 'utilities', 'insurance'):
                    if spent > highest_amt:
                        highest_amt = spent
                        highest_cat = cat
                        
                if limit > 0 and spent > limit:
                    exceeded.append((cat, spent - limit))
                    
            if exceeded:
                exceeded.sort(key=lambda x: x[1], reverse=True)
                top_exceed = exceeded[0]
                reply = f"To save more, start by cutting back on {top_exceed[0]}. You are over budget by ${top_exceed[1]:,.2f} this month."
            elif highest_cat and highest_amt > 0:
                reply = f"You are staying within your budgets! To save even more, consider reducing your spending on {highest_cat}, which is your highest discretionary expense right now (${highest_amt:,.2f})."
            else:
                reply = "Your core expenses look well-managed and you don't have high discretionary spending. Consider automating transfers to a high-yield savings account as your next step."

        return jsonify({
            "success": True,
            "intent": intent,
            "response": reply
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
