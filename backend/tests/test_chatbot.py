import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class ChatbotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_missing_message(self):
        response = self.client.post('/api/chat', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_spend_most_intent(self):
        response = self.client.post('/api/chat', json={
            "message": "Where did I spend most?",
            "user_id": 1,
            "month_year": "2026-03" # using month from seed data
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], "SPEND_MOST")
        self.assertIn("highest expense", data['response'].lower())

    def test_save_more_intent(self):
        response = self.client.post('/api/chat', json={
            "message": "How can I save more?",
            "user_id": 1,
            "month_year": "2026-03"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], "SAVE_MORE")
        
    def test_unknown_intent(self):
        response = self.client.post('/api/chat', json={
            "message": "What is the weather today?",
            "user_id": 1,
            "month_year": "2026-03"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], "UNKNOWN")
        self.assertIn("not sure", data['response'].lower())

if __name__ == '__main__':
    unittest.main()
