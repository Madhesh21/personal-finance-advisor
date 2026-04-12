import requests
import json
import io
import sys

BASE = 'http://127.0.0.1:5000'
UID  = 1
ALL_PASS = True

def check(label, condition):
    global ALL_PASS
    icon = 'PASS' if condition else 'FAIL'
    print(f'  [{icon}] {label}')
    if not condition:
        ALL_PASS = False

# ── Phase 1 & 2: Core API + Data Ingestion ──────────────────────────────────
print('== PHASE 1 & 2: Core API + Data Ingestion ==')

r = requests.get(f'{BASE}/api/health')
check('GET /api/health', r.status_code == 200 and r.json().get('status') == 'ok')

r = requests.get(f'{BASE}/api/categories')
cats = r.json().get('data', [])
check('GET /api/categories (>=11 categories)', r.status_code == 200 and len(cats) >= 11)

r = requests.get(f'{BASE}/api/transactions', params={'user_id': UID})
check('GET /api/transactions returns data', r.status_code == 200)

r = requests.get(f'{BASE}/api/transactions/summary', params={'user_id': UID})
s = r.json()
check('GET /api/transactions/summary has income/expense/net', all(k in s for k in ['total_income','total_expense','net_balance']))

food_id = next(c['category_id'] for c in cats if 'food' in c['category_name'].lower())

r = requests.post(f'{BASE}/api/transactions', json={
    'user_id': UID, 'category_id': food_id, 'amount': 9.99,
    'transaction_type': 'EXPENSE', 'transaction_date': '2026-04-01',
    'description': 'Walkthrough test tx'
})
check('POST /api/transactions', r.status_code == 201)
new_id = r.json().get('data', {}).get('transaction_id')

r = requests.delete(f'{BASE}/api/transactions/{new_id}')
check('DELETE /api/transactions/<id>', r.status_code == 200)

# CSV Upload
csv_content = b'date,amount,category,description,type\n2026-04-05,200,Food,CSV test,EXPENSE\n'
r = requests.post(f'{BASE}/api/upload/csv',
                  files={'file': ('test.csv', io.BytesIO(csv_content), 'text/csv')})
check('POST /api/upload/csv', r.status_code in (200, 201) and r.json().get('success'))

r = requests.get(f'{BASE}/api/upload/template')
check('GET /api/upload/template', r.status_code == 200)

# ── Phase 3: Categorization Engine ──────────────────────────────────────────
print()
print('== PHASE 3: Expense Categorization Engine ==')

r = requests.post(f'{BASE}/api/categorize',
                  json={'descriptions': ['Uber to airport', 'Netflix subscription']})
check('POST /api/categorize', r.status_code == 200 and r.json().get('success'))
results = r.json().get('results', [])
check('Uber -> Transport (rule-based)', any('Transport' in res.get('category','') for res in results))

r = requests.post(f'{BASE}/api/categorize', json={'descriptions': ['Medical consultation fee']})
check('POST /api/categorize ML fallback', r.status_code == 200 and r.json().get('success'))

# ── Phase 4: Budgeting Module ────────────────────────────────────────────────
print()
print('== PHASE 4: Budgeting Module ==')

r = requests.get(f'{BASE}/api/budgets', params={'user_id': UID, 'month_year': '2026-04'})
check('GET /api/budgets', r.status_code == 200 and r.json().get('success'))

r = requests.post(f'{BASE}/api/budgets', json={
    'user_id': UID, 'category_id': food_id,
    'monthly_limit': 30, 'month_year': '2026-04'
})
check('POST /api/budgets (Food limit=30)', r.json().get('success'))
bid = r.json()['data']['budget_id']

r = requests.get(f'{BASE}/api/budgets/summary', params={'user_id': UID, 'month_year': '2026-04'})
data = r.json().get('data', [])
food_row = next((x for x in data if x['category_id'] == food_id), None)
check('GET /api/budgets/summary has percent_used', food_row and 'percent_used' in food_row)
check('GET /api/budgets/summary has alert field', food_row and 'alert' in food_row)
check('Danger alert triggered (Food exceeded)', food_row and food_row.get('alert') is not None)

r = requests.get(f'{BASE}/api/budgets/alerts', params={'user_id': UID, 'month_year': '2026-04'})
check('GET /api/budgets/alerts returns active alerts', r.status_code == 200 and r.json().get('alert_count', 0) > 0)
if r.json().get('alerts'):
    print(f'       Alert: {r.json()["alerts"][0]["alert"]}')

r = requests.delete(f'{BASE}/api/budgets/{bid}')
check('DELETE /api/budgets/<id>', r.json().get('success'))

# ── Phase 5: Recommendation Engine (Core AI) ──────────────────────────────────
print()
print('== PHASE 5: Recommendation Engine ==')

r = requests.get(f'{BASE}/api/recommendations', params={'user_id': UID, 'month_year': '2026-03'})
check('GET /api/recommendations', r.status_code == 200 and r.json().get('success'))
recs = r.json().get('data', [])
if recs:
    print(f'       Example Rec: {recs[0]["title"]}')

# Final verdict
print()
print('=' * 48)
if ALL_PASS:
    print('OVERALL: ALL SYSTEMS GREEN -- Phases 1-5 OK')
else:
    print('OVERALL: SOME CHECKS FAILED -- review above')
print('=' * 48)
