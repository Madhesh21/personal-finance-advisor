from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.csv_parser import parse_csv
from utils.db_helper import get_category_map, bulk_insert_transactions
import mysql.connector
from routes.categorize import engine as category_engine

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv'}


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/api/upload/csv', methods=['POST'])
@jwt_required()
def upload_csv():
    """
    POST /api/upload/csv
    Accepts a multipart/form-data CSV file and bulk-inserts transactions.

    Form fields:
      - file    : the CSV file (required)
      - user_id : int (optional, default 1)

    Expected CSV columns:
      - date        (required)  → various formats accepted
      - amount      (required)  → positive number
      - category    (required)  → must match an existing category name
      - description (required)  → free text
      - type        (optional)  → INCOME | EXPENSE (defaults to EXPENSE)

    Returns a JSON summary: inserted, skipped rows, and any row-level errors.
    """
    # ── Validate file presence ──────────────────────────────────────────────
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request. Use key 'file'"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"success": False, "error": "Only .csv files are accepted"}), 400

    user_id = get_jwt_identity()

    # ── Parse CSV ───────────────────────────────────────────────────────────
    try:
        category_map = get_category_map()     # {name_lower: id}
        records, errors = parse_csv(file, category_map, category_engine=category_engine)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 422

    if not records:
        return jsonify({
            "success":  False,
            "error":    "No valid rows found in CSV",
            "row_errors": errors
        }), 422

    # ── Bulk Insert ─────────────────────────────────────────────────────────
    try:
        inserted = bulk_insert_transactions(records, user_id)
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": f"Database error: {err}"}), 500

    return jsonify({
        "success":    True,
        "message":    f"Successfully imported {inserted} transactions",
        "inserted":   inserted,
        "skipped":    len(errors),
        "row_errors": errors   # list of skipped row descriptions
    }), 201


@upload_bp.route('/api/upload/template', methods=['GET'])
def download_template():
    """
    GET /api/upload/template
    Returns a sample CSV template as plain text so users know the expected format.
    """
    template = (
        "date,amount,category,description,type\n"
        "2026-03-01,5000,salary,Monthly salary,INCOME\n"
        "2026-03-05,1500,rent,Apartment rent,EXPENSE\n"
        "2026-03-10,450,food,Groceries,EXPENSE\n"
        "2026-03-15,120,transport,Uber rides,EXPENSE\n"
    )
    return (
        template,
        200,
        {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="transactions_template.csv"'
        }
    )
