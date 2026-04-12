import requests
import json
from datetime import datetime

BASE  = 'http://127.0.0.1:5000'
MONTH = datetime.now().strftime('%Y-%m') # E.g., '2026-04'
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

# 1. Fetch recommendations (assuming data setup in previous phases will trigger some logic)
r = requests.get(f'{BASE}/api/recommendations', params={'user_id': UID, 'month_year': '2026-03'})
show('GET /api/recommendations for 2026-03', r)

check('Recommendations endpoint returns 200', r.status_code == 200)
check('Response has success=True', r.json().get('success') == True)
check('Response data is a list', isinstance(r.json().get('data'), list))

print(f'\n{"=" * 40}')
print(f'Phase 5 Tests: {"ALL PASSED ✅" if PASS else "SOME FAILED ❌"}')
print(f'{"=" * 40}')
