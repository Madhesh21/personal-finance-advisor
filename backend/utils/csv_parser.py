import pandas as pd
from datetime import datetime


REQUIRED_COLUMNS = {'date', 'amount', 'category', 'description'}

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


def parse_csv(file_obj, category_map: dict) -> tuple[list[dict], list[str]]:
    """
    Parse a CSV file object for bulk transaction import.

    Args:
        file_obj    : File-like object (from Flask request.files)
        category_map: dict mapping category_name (lowercase) -> category_id

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
        cat_name = str(row['category']).strip().lower()
        category_id = category_map.get(cat_name)
        if category_id is None:
            errors.append(
                f"Row {row_num}: Unknown category '{row['category']}'. "
                f"Available: {', '.join(sorted(category_map.keys()))}"
            )
            continue

        # ── Transaction Type ───────────────────────────────────────────────────
        if has_type_col:
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
        })

    return records, errors
