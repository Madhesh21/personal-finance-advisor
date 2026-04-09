import requests
import json

BASE  = 'http://127.0.0.1:5000'
MONTH = '2026-04'
UID   = 1
PASS  = True

def show(label, r):
    print(f'\n=== {label} ===')
    d = r.json()
    print(json.dumps(d, indent=2, default=str)[:800])

def check(label, condition):
    global PASS
    status = '✅' if condition else '❌'
    print(f'{status}  {label}')
    if not condition:
        PASS = False

# 1. Find Food category id
cats = requests.get(f'{BASE}/api/categories').json()['data']
food_id = next(c['category_id'] for c in cats if 'food' in c['category_name'].lower())
print(f'Food category_id = {food_id}')

# ─── Test 1: Set budget BELOW current spend → DANGER ───
requests.post(f'{BASE}/api/budgets', json={
    'user_id': UID, 'category_id': food_id,
    'monthly_limit': 30,   # actual_spent=50 → 166% → DANGER
    'month_year': MONTH
})
print('\nBudget set: Food limit=30, actual spend=50 → expect DANGER')

summary = requests.get(f'{BASE}/api/budgets/summary', params={'user_id': UID, 'month_year': MONTH}).json()
food_row = next((r for r in summary['data'] if r['category_id'] == food_id), None)
show('Budget summary (Food row)', type('R', (), {'json': lambda s: food_row, 'status_code': 200})())

check('percent_used present', food_row and 'percent_used' in food_row)
check('percent_used > 100', food_row and food_row['percent_used'] > 100)
check('alert field present', food_row and 'alert' in food_row)
check('alert contains "exceeded"', food_row and food_row['alert'] and 'exceeded' in food_row['alert'].lower())

alerts = requests.get(f'{BASE}/api/budgets/alerts', params={'user_id': UID, 'month_year': MONTH}).json()
show('GET /api/budgets/alerts', type('R', (), {'json': lambda s: alerts, 'status_code': 200})())
check('alerts endpoint returns success', alerts['success'])
check('alert_count > 0', alerts['alert_count'] > 0)
check('alert message correct', alerts['alerts'][0]['alert'] and 'exceeded' in alerts['alerts'][0]['alert'].lower())

# ─── Test 2: Update budget → WARNING range (80-99%) ───
requests.post(f'{BASE}/api/budgets', json={
    'user_id': UID, 'category_id': food_id,
    'monthly_limit': 60,   # actual_spent=50 → 83% → WARNING
    'month_year': MONTH
})
print('\nBudget updated: Food limit=60, actual spend=50 → expect WARNING')
alerts2 = requests.get(f'{BASE}/api/budgets/alerts', params={'user_id': UID, 'month_year': MONTH}).json()
check('alert_count still 1', alerts2['alert_count'] == 1)
check('warning alert (close to limit)', alerts2['alerts'][0]['alert'] and 'close' in alerts2['alerts'][0]['alert'].lower())

# ─── Test 3: Update budget → SAFE range (<80%) ───
requests.post(f'{BASE}/api/budgets', json={
    'user_id': UID, 'category_id': food_id,
    'monthly_limit': 100,   # actual_spent=50 → 50% → SAFE
    'month_year': MONTH
})
print('\nBudget updated: Food limit=100, actual spend=50 → expect SAFE')
alerts3 = requests.get(f'{BASE}/api/budgets/alerts', params={'user_id': UID, 'month_year': MONTH}).json()
check('alert_count = 0 (safe)', alerts3['alert_count'] == 0)

# ─── Test 4: DELETE budget ───
budgets = requests.get(f'{BASE}/api/budgets', params={'user_id': UID, 'month_year': MONTH}).json()['data']
for b in budgets:
    bid = b['budget_id']
    r = requests.delete(f'{BASE}/api/budgets/{bid}')
    check(f'DELETE budget_id={bid} returns success', r.json()['success'])

remaining = requests.get(f'{BASE}/api/budgets', params={'user_id': UID, 'month_year': MONTH}).json()['data']
check('All budgets removed', len(remaining) == 0)

print(f'\n{"=" * 40}')
print(f'Phase 4 Tests: {"ALL PASSED ✅" if PASS else "SOME FAILED ❌"}')
print(f'{"=" * 40}')
