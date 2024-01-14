import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

class ModelEvaluatorHandler:
    def __init__(self, GenerativeSentimentAnalysisController, csv_file):
        self.csv_file = csv_file
        self.results_path = GenerativeSentimentAnalysisController.results_path

    def evaluate_model(self, true_column, predicted_column, temperature):
        print("\033[0m" + "Starting evaluate_model...")
        try:
            with open(self.csv_file.name, 'r', newline='', encoding='utf-8') as file:
                data = StringIO(file.read())
                data.seek(0)
                csv_reader = csv.DictReader(data)

                label_map = {
                    "happiness": 0,
                    "sadness": 1,
                    "anger": 2,
                    "surprise": 3,
                    "fear": 4,
                    "disgust": 5,
                    "not-relevant": 6
                }
                
                y_true, y_pred = [], []
                for row in csv_reader:
                    y_true.append(label_map[row[true_column]])
                    y_pred.append(label_map[row[predicted_column]])

            conf_matrix = confusion_matrix(y_true, y_pred)
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted')
            recall = recall_score(y_true, y_pred, average='weighted')
            f1 = f1_score(y_true, y_pred, average='weighted')

            existing_images = [image for image in os.listdir(self.results_path) if image.startswith(f'confusion_matrix_{temperature}') and image.endswith('.png')]
            next_number = 1 if not existing_images else len(existing_images) + 1
            image_name = f'results/confusion_matrix_{temperature}_{next_number}.png'

            plt.figure(figsize=(8, 6))
            sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
            plt.xlabel('Predicted labels')
            plt.ylabel('True labels')
            plt.title('Confusion Matrix')
            plt.savefig(image_name)
            plt.close()

            results = [[accuracy, precision, recall, f1]]

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None

        print("\033[92m\u2714 " + "Model evaluated successfully")
        return results