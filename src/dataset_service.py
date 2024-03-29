import json
from collections import defaultdict

class DatasetService:
    def __init__(self, GenerativeSentimentAnalysisController):
        self.training_dataset = GenerativeSentimentAnalysisController.training_dataset
        self.test_dataset = GenerativeSentimentAnalysisController.test_dataset

    def validate_datasets(self):
        return self.valid_data_jsonl(self.training_dataset, True) and self.valid_data_jsonl(self.test_dataset, False)

    def valid_data_jsonl(self, data_path, isTrainingData):
        print("\033[0m" + f"Starting valid_data_jsonl for '{data_path}'...")
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                dataset = [json.loads(line) for line in f]

            format_errors = defaultdict(int)

            for ex in dataset:
                if not isinstance(ex, dict):
                    format_errors["data_type"] += 1
                    continue

                messages = ex.get("messages", None)
                if not messages:
                    format_errors["missing_messages_list"] += 1
                    continue

                for message in messages:
                    if "role" not in message or "content" not in message:
                        format_errors["message_missing_key"] += 1

                    if any(k not in ("role", "content", "name", "function_call") for k in message):
                        format_errors["message_unrecognized_key"] += 1

                    if message.get("role", None) not in ("system", "user", "assistant", "function"):
                        format_errors["unrecognized_role"] += 1

                    content = message.get("content", None)
                    function_call = message.get("function_call", None)

                    if (not content and not function_call) or not isinstance(content, str):
                        format_errors["missing_content"] += 1

                if isTrainingData:
                    if not any(message.get("role", None) == "assistant" for message in messages):
                        format_errors["example_missing_assistant_message"] += 1

            if format_errors:
                print("Found errors:")
                for k, v in format_errors.items():
                    print(f"{k}: {v}")
                return False

        except FileNotFoundError:
            print("\033[91m\u2718 " + f"The file '{data_path}' was not found.")
            return False

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return False

        print("\033[92m\u2714 " + "No errors found")
        return True