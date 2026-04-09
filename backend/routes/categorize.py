from flask import Blueprint, request, jsonify
from ml.categorizer import CategoryEngine
from config import DB_CONFIG, get_db_connection
import mysql.connector

categorize_bp = Blueprint('categorize', __name__)

# Initialize engine globally
engine = CategoryEngine(DB_CONFIG)

@categorize_bp.route('/api/categorize', methods=['POST'])
def categorize():
    """
    POST /api/categorize
    Categorize one or multiple descriptions.
    Body:
        { "description": "Uber eats" }
        or
        { "descriptions": ["Uber eats", "Electricity bill"] }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON body"}), 400

    if 'descriptions' in data:
        results = []
        for desc in data['descriptions']:
            cat, conf, method = engine.predict(desc)
            results.append({
                "description": desc,
                "category": cat,
                "confidence": conf,
                "method": method
            })
        return jsonify({"success": True, "results": results}), 200

    elif 'description' in data:
        desc = data['description']
        cat, conf, method = engine.predict(desc)
        return jsonify({
            "success": True,
            "description": desc,
            "category": cat,
            "confidence": conf,
            "method": method
        }), 200

    return jsonify({"success": False, "error": "Must provide 'description' or 'descriptions'"}), 400

@categorize_bp.route('/api/categorize/train', methods=['POST'])
def train_model():
    """
    POST /api/categorize/train
    Force a retrain of the Naive Bayes model using all data.
    """
    try:
        engine.retrain_model()
        return jsonify({"success": True, "message": "Model retrained successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@categorize_bp.route('/api/categorize/feedback', methods=['POST'])
def submit_feedback():
    """
    POST /api/categorize/feedback
    Save user correction for an incorrectly categorized transaction.
    Body:
        {
            "user_id": 1,
            "original_description": "amazon",
            "predicted_category_id": 5,
            "corrected_category_id": 6
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON payload"}), 400

    user_id = data.get('user_id', 1)
    original_desc = data.get('original_description')
    predicted_cat_id = data.get('predicted_category_id')
    corrected_cat_id = data.get('corrected_category_id')

    if not original_desc or corrected_cat_id is None:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO user_corrections 
            (user_id, original_description, predicted_category_id, corrected_category_id)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, original_desc, predicted_cat_id, corrected_cat_id)
        )
        conn.commit()
        
        # Optional: Auto-retrain if we accumulated say, 10 new corrections:
        # For now, just store it. The user can hit /api/categorize/train or we retrain on restart.
        
        return jsonify({"success": True, "message": "Feedback saved successfully"}), 201
        
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
