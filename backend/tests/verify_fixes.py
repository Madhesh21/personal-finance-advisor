import requests
import io

BASE = 'http://127.0.0.1:5000'
UID  = 1

def test_income_detection_manual():
    print("Testing manual income detection...")
    # Get Salary category ID
    r = requests.get(f'{BASE}/api/categories')
    cats = r.json().get('data', [])
    salary_cat = next((c for c in cats if 'salary' in c['category_name'].lower()), None)
    
    if not salary_cat:
        print("FAIL: Salary category not found")
        return
        
    # POST transaction WITHOUT transaction_type
    r = requests.post(f'{BASE}/api/transactions', json={
        'user_id': UID,
        'category_id': salary_cat['category_id'],
        'amount': 5000,
        'description': 'Manual Salary Test'
    })
    
    res = r.json()
    if r.status_code == 201 and res.get('data', {}).get('transaction_type') == 'INCOME':
        print("PASS: Manual income detection successful")
        # Cleanup
        tx_id = res['data']['transaction_id']
        requests.delete(f'{BASE}/api/transactions/{tx_id}')
    else:
        print(f"FAIL: Manual income detection failed. Got: {res.get('data', {}).get('transaction_type')}")

def test_income_detection_csv():
    print("Testing CSV income detection...")
    unique_desc = "UNIQUE_CSV_SALARY_TEST_123"
    # CSV content without 'type' column
    csv_content = f"date,amount,category,description\n2026-04-01,5000,Salary,{unique_desc}\n".encode()
    r = requests.post(f'{BASE}/api/upload/csv',
                      files={'file': ('test_salary.csv', io.BytesIO(csv_content), 'text/csv')})
    
    res = r.json()
    if r.status_code == 201:
        # Check the inserted transaction by description
        r_tx = requests.get(f'{BASE}/api/transactions', params={'user_id': UID, 'limit': 100})
        txs = r_tx.json().get('data', [])
        tx = next((t for t in txs if t.get('description') == unique_desc), None)
        
        if tx and tx.get('category_name').lower() == 'salary' and tx.get('transaction_type') == 'INCOME':
            print("PASS: CSV income detection successful")
        elif not tx:
            print("FAIL: CSV transaction not found in database")
        else:
            print(f"FAIL: CSV income detection failed. Got: {tx.get('transaction_type')}")
    else:
        print(f"FAIL: CSV upload failed. Status: {r.status_code}, Error: {res.get('error')}")

def test_budget_id_presence():
    print("Testing budget_id presence in summary...")
    # Ensure there's a budget
    requests.post(f'{BASE}/api/budgets', json={
        'user_id': UID,
        'category_id': 4, # Food (EXPENSE)
        'monthly_limit': 500,
        'month_year': '2026-04'
    })
    
    r = requests.get(f'{BASE}/api/budgets/summary', params={'user_id': UID, 'month_year': '2026-04'})
    data = r.json().get('data', [])
    food_row = next((x for x in data if x['category_id'] == 4), None)
    
    if food_row and 'budget_id' in food_row:
        print(f"PASS: budget_id found in summary: {food_row['budget_id']}")
        # Test deletion
        bid = food_row['budget_id']
        if bid:
            rd = requests.delete(f'{BASE}/api/budgets/{bid}')
            if rd.status_code == 200:
                print("PASS: Budget deletion successful")
            else:
                print(f"FAIL: Budget deletion failed. Status: {rd.status_code}")
    else:
        print("FAIL: budget_id NOT found in summary rows")

if __name__ == '__main__':
    try:
        test_income_detection_manual()
        test_income_detection_csv()
        test_budget_id_presence()
    except Exception as e:
        print(f"ERROR during testing: {e}")
