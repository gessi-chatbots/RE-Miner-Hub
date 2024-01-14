import unittest
import json
from OpenAIController import create_app

class TestExtractFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True
        self.data = {
            "text": [
                {
                    "id": "1",
                    "text": "Widget not the way it used to be No more 5-day forecast, temp, and local temp."
                },
                {
                    "id": "2",
                    "text": "I originally downloaded the app for pomodoro timing, but I stayed for the project management features, with syncing."
                },
                {
                    "id": "3",
                    "text": "I'm my phone the notifications of group message are not at a time please check what was the reason behind it because due to this default I loose some opportunity"
                }
            ]
        }

    def test_extract_features_with_transfeatex_success(self):
        response = self.app.post('/extract-features?model_features=transfeatex', json=self.data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content_type, 'application/json')

        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 3)

    def test_extract_features_with_t_frex_bert_base_uncased_success(self):
        response = self.app.post('/extract-features?model_features=t-frex-bert-base-uncased', json=self.data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content_type, 'application/json')

        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 3)

    def test_extract_features_invalid_data(self):
        response = self.app.post('/extract-features')

        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

        self.assertEqual(response.data.decode('utf-8'), "Lacking model and textual data in proper tag.")

if __name__ == '__main__':
    unittest.main()