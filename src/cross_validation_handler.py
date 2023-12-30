from sklearn import datasets
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score

class CrossValidation:
    def __init__(self):
        self.complete_dataset = "../data/complete_dataset.jsonl"

    def cross_validation(self):
        print("\033[0m" + "Starting cross_validation...")
        try:
            with open(self.complete_dataset, 'r', encoding='utf-8') as f:
                dataset = [json.loads(line) for line in f]

            X = [item['messages'][0]['content'] for item in dataset]
            y = [item['messages'][1]['content'] for item in dataset]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
            

        except Exception as e:
            print("\033[91m\u2718 " + f"An error occurred: {e}")
            return None
