"""
financial_context.py
---------------------
Fetches the user's financial summary from MySQL and formats it
as a structured plain-text context block to inject into the LLM prompt.

This is the "retrieval" step of the context-injection architecture.
"""

from config import get_db_connection
from datetime import datetime


def get_financial_context(user_id: int = 1, month_year: str = None) -> str:
    """
    Fetches and formats a comprehensive financial snapshot for `user_id`
    covering the given `month_year` (YYYY-MM).  Returns a plain-text
    block ready to be embedded inside the LLM system prompt.
    """
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')

    try:
        year, month = map(int, month_year.split('-'))
    except ValueError:
        year, month = datetime.now().year, datetime.now().month
        month_year = f"{year}-{month:02d}"

    lines = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        month_label = datetime(year, month, 1).strftime('%B %Y')
        lines.append(f"=== Financial Summary for {month_label} ===\n")

        # ── 1. Monthly Income & Expense Totals ──────────────────────────────
        cursor.execute("""
            SELECT transaction_type, SUM(amount) AS total
            FROM transactions
            WHERE user_id = %s
              AND YEAR(transaction_date) = %s
              AND MONTH(transaction_date) = %s
            GROUP BY transaction_type
        """, (user_id, year, month))

        totals = {"INCOME": 0.0, "EXPENSE": 0.0}
        for row in cursor.fetchall():
            totals[row['transaction_type']] = float(row['total'])

        income  = totals['INCOME']
        expense = totals['EXPENSE']
        net     = income - expense
        savings_rate = round((net / income * 100), 1) if income > 0 else 0.0

        lines.append("## Monthly Overview")
        lines.append(f"- Total Income:   ${income:,.2f}")
        lines.append(f"- Total Expenses: ${expense:,.2f}")
        lines.append(f"- Net Balance:    ${net:,.2f}  ({'surplus' if net >= 0 else 'deficit'})")
        lines.append(f"- Savings Rate:   {savings_rate}%")
        lines.append("")

        # ── 2. Top Expense Categories ────────────────────────────────────────
        cursor.execute("""
            SELECT c.category_name, SUM(t.amount) AS spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
              AND t.transaction_type = 'EXPENSE'
              AND YEAR(t.transaction_date) = %s
              AND MONTH(t.transaction_date) = %s
            GROUP BY c.category_name
            ORDER BY spent DESC
            LIMIT 7
        """, (user_id, year, month))

        top_cats = cursor.fetchall()
        if top_cats:
            lines.append("## Top Expense Categories")
            for i, row in enumerate(top_cats, 1):
                pct = round(float(row['spent']) / expense * 100, 1) if expense > 0 else 0
                lines.append(f"  {i}. {row['category_name']}: ${float(row['spent']):,.2f} ({pct}% of expenses)")
            lines.append("")

        # ── 3. Budget Status ─────────────────────────────────────────────────
        cursor.execute("""
            SELECT
                c.category_name,
                COALESCE(b.monthly_limit, 0) AS budget_limit,
                COALESCE(SUM(t.amount), 0)   AS actual_spent
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
            HAVING budget_limit > 0 OR actual_spent > 0
        """, (user_id, month_year, user_id, year, month))

        budget_rows = cursor.fetchall()
        if budget_rows:
            lines.append("## Budget Status")
            over_budget  = []
            under_budget = []
            no_budget    = []

            for row in budget_rows:
                cat    = row['category_name']
                limit  = float(row['budget_limit'])
                spent  = float(row['actual_spent'])

                if limit > 0:
                    remaining = limit - spent
                    status = "OVER" if remaining < 0 else "under"
                    if remaining < 0:
                        over_budget.append(f"  ⚠ {cat}: spent ${spent:,.2f} / budget ${limit:,.2f} (OVER by ${abs(remaining):,.2f})")
                    else:
                        under_budget.append(f"  ✓ {cat}: spent ${spent:,.2f} / budget ${limit:,.2f} (${remaining:,.2f} remaining)")
                elif spent > 0:
                    no_budget.append(f"  • {cat}: ${spent:,.2f} (no budget set)")

            for l in over_budget:  lines.append(l)
            for l in under_budget: lines.append(l)
            for l in no_budget:    lines.append(l)
            lines.append("")

        # ── 4. Last 3 Months Trend ───────────────────────────────────────────
        cursor.execute("""
            SELECT
                YEAR(transaction_date)  AS yr,
                MONTH(transaction_date) AS mo,
                transaction_type,
                SUM(amount) AS total
            FROM transactions
            WHERE user_id = %s
            GROUP BY yr, mo, transaction_type
            ORDER BY yr DESC, mo DESC
            LIMIT 18
        """, (user_id,))

        trend_raw = cursor.fetchall()
        months_map = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        trend_map  = {}
        for row in trend_raw:
            key   = f"{row['yr']}-{row['mo']:02d}"
            label = f"{months_map[row['mo']-1]} {row['yr']}"
            if key not in trend_map:
                trend_map[key] = {"label": label, "income": 0.0, "expense": 0.0}
            if row['transaction_type'] == 'INCOME':
                trend_map[key]['income']  += float(row['total'])
            elif row['transaction_type'] == 'EXPENSE':
                trend_map[key]['expense'] += float(row['total'])

        sorted_months = sorted(trend_map.items(), key=lambda x: x[0])[-4:]
        if sorted_months:
            lines.append("## Recent Monthly Trend (last months)")
            for _, data in sorted_months:
                n = data['income'] - data['expense']
                lines.append(f"  • {data['label']}: Income ${data['income']:,.2f} | Expenses ${data['expense']:,.2f} | Net ${n:,.2f}")
            lines.append("")

        # ── 5. Last 10 Transactions ──────────────────────────────────────────
        cursor.execute("""
            SELECT t.transaction_date, t.amount, t.transaction_type,
                   t.description, c.category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC
            LIMIT 10
        """, (user_id,))

        recent = cursor.fetchall()
        if recent:
            lines.append("## Recent Transactions (last 10)")
            for row in recent:
                date  = str(row['transaction_date'])[:10]
                ttype = row['transaction_type']
                cat   = row['category_name'] or 'Uncategorized'
                desc  = row['description'] or cat
                amt   = float(row['amount'])
                sign  = "+" if ttype == "INCOME" else "-"
                lines.append(f"  • {date} | {cat} | {desc[:40]} | {sign}${amt:,.2f}")
            lines.append("")

        cursor.close()
        conn.close()

    except Exception as e:
        lines.append(f"[Note: Could not fully load financial data: {str(e)}]")

    lines.append("=== End of Financial Context ===")
    return "\n".join(lines)
