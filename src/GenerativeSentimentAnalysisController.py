import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from .dataset_handler import DatasetHandler
from .file_handler import FileHandler
from .fine_tuning_job_handler import FineTuningJobHandler
from .csv_file_creator_handler import CSVFileCreatorHandler
from .chat_completion_handler import ChatCompletionHandler
from .model_evaluator_handler import ModelEvaluatorHandler

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenerativeSentimentAnalysisController:
    def __init__(self):
        self.training_dataset = "./data/training_dataset.jsonl"
        self.test_dataset = "./data/test_dataset.jsonl"
        self.training_dataset_with_prompt = "./data/training_dataset_with_prompt.jsonl"
        self.test_dataset_with_prompt = "./data/test_dataset_with_prompt.jsonl"
        self.model = "gpt-3.5-turbo"
        self.results_path = "results/"
        self.training_metrics_file = "training_metrics_"
        self.chat_completion_file = "chat_completion_result_"
        self.emotion_labels_path = "./data/emotion_labels_test_dataset.jsonl"
        self.model_evaluation_file_low_temperature = "model_evaluation_result_low_temperature"
        self.model_evaluation_file_high_temperature = "model_evaluation_result_high_temperature"

    def start_generative_sentiment_analysis(self):
        print("Starting generative sentiment analysis...")

        dataset_handler = DatasetHandler(self)
        # Validate datasets
        if not dataset_handler.validate_datasets():
            return

        file_handler = FileHandler(self)
        # Add prompt to training dataset
        self.training_dataset_with_prompt = file_handler.add_prompt_to_jsonl_file(self.training_dataset, self.training_dataset_with_prompt)
        if self.training_dataset_with_prompt is None:
            return

        # Validate training dataset with prompt
        if not dataset_handler.valid_data_jsonl(self.training_dataset_with_prompt, True):
            return

        # Upload training file
        file_uploaded = file_handler.upload_file()
        if file_uploaded is None:
            return

        # Create fine-tuning job
        fine_tuning_job_handler = FineTuningJobHandler(self)
        fine_tuned_job = fine_tuning_job_handler.create_fine_tuning_job(file_uploaded)
        if fine_tuned_job is None:
            return
        
        # Generate fine-tuning job result file
        fine_tuned_job_serializable = fine_tuned_job.model_dump()
        fine_tuned_job_result_file = fine_tuning_job_handler.generate_fine_tuning_results(fine_tuned_job_serializable)

        # Get the fine-tuning job metrics
        result_files_id = fine_tuned_job.result_files[0]
        content = client.files.retrieve_content(result_files_id)
        csv_file_creator_handler = CSVFileCreatorHandler(self)
        fine_tuning_job_metrics_file = csv_file_creator_handler.create_csv_file_processing_content(content, self.training_metrics_file)
        if fine_tuning_job_metrics_file is None:
            return

        # Add prompt to test file
        self.test_dataset_with_prompt = file_handler.add_prompt_to_jsonl_file(self.test_dataset, self.test_dataset_with_prompt)
        if self.test_dataset_with_prompt is None:
            return

        # Validate test dataset with prompt
        if not dataset_handler.valid_data_jsonl(self.test_dataset_with_prompt, False):
            return
        
        # Create chat completion
        fine_tuned_model = fine_tuned_job.fine_tuned_model
        chat_completion_handler = ChatCompletionHandler(self)
        generated_chat_completion = chat_completion_handler.generate_chat_completion(fine_tuned_model, self.test_dataset_with_prompt)
        if generated_chat_completion is None:
            return
        
        # Generate chat completion result file
        header = ['User review', 'Emotion for chat completion with temperature 0.2', 'Emotion for chat completion with temperature 0.8']
        chat_completion_result_file = csv_file_creator_handler.create_csv_file(generated_chat_completion, self.chat_completion_file, header)
        if chat_completion_result_file is None:
            return

        # Add ID & emotion to CSV file
        file_handler.refactor_id_jsonl()
        chat_completion_result_file = file_handler.add_emotion_and_id_to_csv(chat_completion_result_file)
        if chat_completion_result_file is None:
            return

        # Evaluate the results
        model_evaluator_handler = ModelEvaluatorHandler(self, chat_completion_result_file)
        model_evaluation_results_low_temperature = model_evaluator_handler.evaluate_model('Emotion label', 'Emotion for chat completion with temperature 0.2', 'low_temperature')
        model_evaluation_results_high_temperature = model_evaluator_handler.evaluate_model('Emotion label', 'Emotion for chat completion with temperature 0.8', 'high_temperature')
        if (model_evaluation_results_low_temperature or model_evaluation_results_high_temperature) is None:
            return
        
        # Generate evaluation result file
        header = ['Accuracy', 'Precision', 'Recall', 'F1-score']
        model_evaluation_result_file = csv_file_creator_handler.create_csv_file(model_evaluation_results_low_temperature, self.model_evaluation_file_low_temperature, header)
        model_evaluation_result_file2 = csv_file_creator_handler.create_csv_file(model_evaluation_results_high_temperature, self.model_evaluation_file_high_temperature, header)
        if model_evaluation_result_file is None:
            return
        
        print("\033[92m\u2714 " + "The program has finished successfully")