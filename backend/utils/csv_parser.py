import pandas as pd
from datetime import datetime


REQUIRED_COLUMNS = {'date', 'amount', 'description'}

# Accepted date formats to try when parsing
DATE_FORMATS = [
    '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y',
    '%d/%m/%Y', '%Y/%m/%d', '%d-%b-%Y',
]


def _parse_date(date_str: str) -> str:
    """Try multiple date formats and return ISO 'YYYY-MM-DD' string."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(str(date_str).strip(), fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: '{date_str}'")


def parse_csv(file_obj, category_map: dict, category_engine=None) -> tuple[list[dict], list[str]]:
    """
    Parse a CSV file object for bulk transaction import.

    Args:
        file_obj    : File-like object (from Flask request.files)
        category_map: dict mapping category_name (lowercase) -> category_id
        category_engine: CategoryEngine instance to use for missing/unknown categories

    Returns:
        (records, errors)
        records : list of dicts ready for DB insert
        errors  : list of human-readable error strings for bad rows
    """
    # ── Read CSV ───────────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {e}")

    # Normalise column names: lowercase, strip whitespace
    df.columns = [c.strip().lower() for c in df.columns]

    # Check required columns exist
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    # Optional: 'type' column (INCOME / EXPENSE). Default to EXPENSE if absent.
    has_type_col = 'type' in df.columns

    records = []
    errors  = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed, +1 for header row

        # ── Validate Date ──────────────────────────────────────────────────────
        try:
            parsed_date = _parse_date(row['date'])
        except ValueError as e:
            errors.append(f"Row {row_num}: {e}")
            continue

        # ── Validate Amount ────────────────────────────────────────────────────
        try:
            amount = float(str(row['amount']).replace(',', '').strip())
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            errors.append(f"Row {row_num}: Invalid amount '{row['amount']}'")
            continue

        # ── Validate Category ──────────────────────────────────────────────────
        auto_categorized = 0
        cat_name = str(row.get('category', '')).strip().lower()
        cat_info = category_map.get(cat_name)
        category_id = cat_info['id'] if cat_info else None
        
        if category_id is None and category_engine is not None:
            # Predict
            description = str(row.get('description', '')).strip()[:255]
            predicted_cat, conf, _ = category_engine.predict(description)
            if predicted_cat:
                cat_info = category_map.get(predicted_cat.lower())
                category_id = cat_info['id'] if cat_info else None
                auto_categorized = 1

        if category_id is None:
            errors.append(
                f"Row {row_num}: Unknown category '{row.get('category', '')}' and auto-categorization failed."
            )
            continue

        # ── Transaction Type ───────────────────────────────────────────────────
        # Priority: Category's own type (if known) > CSV 'type' column > Default 'EXPENSE'
        if cat_info:
            tx_type = cat_info['type']
        elif has_type_col and str(row['type']).strip():
            tx_type = str(row['type']).strip().upper()
            if tx_type not in ('INCOME', 'EXPENSE'):
                errors.append(f"Row {row_num}: type must be INCOME or EXPENSE, got '{row['type']}'")
                continue
        else:
            tx_type = 'EXPENSE'

        # ── Description ────────────────────────────────────────────────────────
        description = str(row.get('description', '')).strip()[:255]

        records.append({
            "transaction_date": parsed_date,
            "amount":           amount,
            "category_id":      category_id,
            "transaction_type": tx_type,
            "description":      description,
            "auto_categorized": auto_categorized,
        })

    return records, errors
