import os
import json
import jsonlines
import time
import csv
from dotenv import load_dotenv
from openai import OpenAI
from io import StringIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class FileHandler:
    def __init__(self, GenerativeSentimentAnalysisController):
        self.system_prompt = "Can you tell me what emotion is expressing the message above? It can be one of the following: happiness, sadness, anger, fear, surprise, disgust or not-relevant (if it doesn't express any relevant emotion)."
        self.training_dataset_with_prompt = GenerativeSentimentAnalysisController.training_dataset_with_prompt
        self.results_path = GenerativeSentimentAnalysisController.results_path
        self.training_metrics_file = GenerativeSentimentAnalysisController.training_metrics_file
        self.chat_completion_result_file = "chat_completion_result_"
        self.emotion_labels_path = GenerativeSentimentAnalysisController.emotion_labels_path
        
    def add_prompt_to_jsonl_file(self, input_file_path, output_file_path):
        print("\033[0m" + "Starting add_prompt_to_jsonl_file...")
        try:
            with jsonlines.open(input_file_path, 'r') as reader, jsonlines.open(output_file_path, 'w') as writer:
                for line in reader:
                    messages = line.get('messages', [])
                    if messages:
                        messages.insert(0, {'role': 'system', 'content': self.system_prompt})
                    line['messages'] = messages
                    writer.write(line)
        
        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None

        print("\033[92m\u2714 " + f"Jsonl dataset with prompt saved in {output_file_path}")
        return output_file_path

    def upload_file(self):
        print("\033[0m" + "Starting upload_file...")
        try:
            file_uploaded = client.files.create(file=open(self.training_dataset_with_prompt, "rb"), purpose='fine-tune')

            while True:
                print("Waiting for file to process...")
                file_handle = client.files.retrieve(file_uploaded.id)
                if file_handle and file_handle.status == "processed":
                    print("\033[92m\u2714 " + "File processed")
                    break
                time.sleep(120)

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None

        print("\033[92m\u2714 " + "File uploaded")
        return file_uploaded

    def refactor_id_jsonl(self):
        print("\033[0m" + "Starting refactor_id_jsonl...")
        try:
            id_count = {}
            updated_lines = []

            with open(self.emotion_labels_path, 'r') as reader:
                lines = reader.readlines()

            for line in lines:
                data = json.loads(line)
                current_id = data.get('id')

                if current_id in id_count:
                    id_count[current_id] += 1
                    data['id'] = f"{current_id}_{id_count[current_id]}"
                else:
                    id_count[current_id] = 0

                updated_lines.append(json.dumps(data))

            with open(self.emotion_labels_path, 'w') as writer:
                for updated_line in updated_lines:
                    writer.write(f"{updated_line}\n")

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None

        print("\033[92m\u2714 " + f'IDs processed in {self.emotion_labels_path}')

    def add_emotion_and_id_to_csv(self, csv_file):
        print("\033[0m" + "Starting add_emotion_and_id_to_csv...")
        try:
            emotions = {}
            ids = []

            with open(csv_file.name, 'r+', newline='', encoding='utf-8') as file:
                csv_data = StringIO(file.read())
                csv_data.seek(0)

                csv_reader = csv.reader(csv_data)
                csv_list = list(csv_reader)

                header = csv_list[0]
                header.insert(0, 'ID')
                header.append('Emotion label')

                csv_data.seek(0)

                with jsonlines.open(self.emotion_labels_path, 'r') as reader:
                    for line in reader:
                        ids.append(line["id"])
                        emotions[line["id"]] = line["emotion"]

                for i, row in enumerate(csv_list[1:], start=1):
                    row.insert(0, ids[i - 1])
                    emotion = emotions.get(ids[i - 1], '')
                    row.append(emotion)

                csv_data.seek(0)

                writer = csv.writer(csv_data)
                writer.writerows(csv_list)

                file.seek(0)
                file.write(csv_data.getvalue())
                file.truncate()

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None

        print("\033[92m\u2714 " + "IDs and emotions added")
        return csv_file