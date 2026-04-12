import requests
import json
from datetime import datetime

BASE  = 'http://127.0.0.1:5000'
MONTH = datetime.now().strftime('%Y-%m')
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

# 1. Test Trends
r_trends = requests.get(f'{BASE}/api/analytics/trends', params={'user_id': UID, 'months': 6})
show('GET /api/analytics/trends (6 months)', r_trends)

check('Trends endpoint returns 200', r_trends.status_code == 200)
check('Trends response has success=True', r_trends.json().get('success') == True)
check('Trends data is a list', isinstance(r_trends.json().get('data'), list))

# 2. Test Distribution
r_dist = requests.get(f'{BASE}/api/analytics/distribution', params={'user_id': UID, 'month_year': '2026-03'})
show('GET /api/analytics/distribution for 2026-03', r_dist)

check('Distribution endpoint returns 200', r_dist.status_code == 200)
check('Distribution data is a list', isinstance(r_dist.json().get('data'), list))
check('Distribution has total_expense', 'total_expense' in r_dist.json())

# 3. Test Metrics
r_metrics = requests.get(f'{BASE}/api/analytics/metrics', params={'user_id': UID, 'month_year': '2026-03'})
show('GET /api/analytics/metrics for 2026-03', r_metrics)

check('Metrics endpoint returns 200', r_metrics.status_code == 200)
data = r_metrics.json().get('data', {})
check('Metrics has savings_rate_pct', 'savings_rate_pct' in data)
check('Metrics has top_expenses', isinstance(data.get('top_expenses'), list))

print(f'\n{"=" * 40}')
print(f'Phase 6 Tests: {"ALL PASSED ✅" if PASS else "SOME FAILED ❌"}')
print(f'{"=" * 40}')
