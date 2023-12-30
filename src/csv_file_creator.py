import os
import csv

class CSVFileCreator:
    def __init__(self, emotion_analysis):
        self.results_path = emotion_analysis.results_path
        self.training_metrics_file = emotion_analysis.training_metrics_file
        self.chat_completion_result_file = "chat_completion_result_"

    def create_csv_file(self, content, file_name, header=None):
        print("\033[0m" + f"Starting create_csv_file for {file_name}...")
        try:
            directory = os.path.join(self.results_path, os.path.dirname(file_name))
            if not os.path.exists(directory):
                os.makedirs(directory)

            existing_files = [item_file for item_file in os.listdir(self.results_path) if item_file.startswith(file_name) and item_file.endswith('.csv')]
            next_number = 0 if not existing_files else len(existing_files) + 1
            file_name = f'{file_name}{next_number}.csv'

            with open(os.path.join(self.results_path, file_name), 'w', newline='') as result_file:
                writer = csv.writer(result_file)
                if header:
                    writer.writerow(header)
                writer.writerows(content)
        
        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None

        print("\033[92m\u2714 " + f"Results saved in {self.results_path}{file_name}")
        return result_file

    def create_csv_file_without_header(self, content):
        processed_content = self.process_content(content)
        return self.create_csv_file(processed_content, self.training_metrics_file)

    def create_csv_file_with_header(self, content):
        header = ['User review', 'Emotion for chat completion with temperature 0.2', 'Emotion for chat completion with temperature 0.8']
        return self.create_csv_file(content, self.chat_completion_result_file, header)

    def process_content(self, content):
        processed_content = content.split('\n')
        data = [line.split(',') for line in processed_content]
        return data