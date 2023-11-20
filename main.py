import openai
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def valid_data_jsonl(data_path):
    try:
        # Load the dataset
        with open(data_path, 'r', encoding='utf-8') as f:
            dataset = [json.loads(line) for line in f]

        # Initial dataset stats
        print("Num examples:", len(dataset))
        print("First example:")
        for message in dataset[0]["messages"]:
            print(message)

        # Format error checks
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

            if not any(message.get("role", None) == "assistant" for message in messages):
                format_errors["example_missing_assistant_message"] += 1

        if format_errors:
            print("Found errors:")
            for k, v in format_errors.items():
                print(f"{k}: {v}")
            return False

    except FileNotFoundError:
        print(f"The file '{data_path}' was not found.")
        return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    print("No errors found")
    return True

def valid_data_txt(data_path):
    try:
        with open(data_path, 'r', encoding='utf-8') as txt_file:
            for linea in txt_file:
                if not (linea.startswith('"') and linea.endswith('"')):
                    return False

    except FileNotFoundError:
        print(f"The file '{data_path}' was not found.")
        return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    return True

def upload_file(file_path):
    try:
        file_uploaded = openai.File.create(file=open(file_path, "rb"), purpose='fine-tune')

        while True:
            print("Waiting for file to process...")
            file_handle = openai.File.retrieve(id=file_uploaded.id)
            if len(file_handle) and file_handle.status == "processed":
                print("File processed")
                break
            time.sleep(120)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return file_uploaded

def create_json_file(path, file_name, content):
    try:
        #path = "results/"
        existing_files = [item_file for item_file in os.listdir(path) if item_file.startswith(file_name) and item_file.endswith('.json')]
        next_number = 0 if not existing_files else len(existing_files) + 1
        file_name = f'{file_name}{next_number}.json'

        with open(path + file_name, 'w') as result_file:
            json.dump(content, result_file, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    print(f"Results saved in {path}{file_name}")

def create_fine_tuning_job(file_uploaded, model):
    try:
        fine_tuning_job = openai.FineTuningJob.create(training_file=file_uploaded.id, model=model)

        while True:
            print("Waiting for fine-tuning to complete...")
            if fine_tuning_job.status == "succeeded":
                print("Fine-tuning complete")
                print("Fine-tuned job info: ", fine_tuning_job)
                break
            time.sleep(120)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    create_json_file("results/", "fine_tuning_job_result_", fine_tuning_job)
    if create_json_file is None:
            print("Error in create_json_file")
            return None

    return fine_tuning_job

def chat_completion(model, messages, temperature):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    print(f'Completion with temperature {temperature}: ', completion.choices[0].message)

def convert_to_serializable(item):
    try:
        if isinstance(item, set):
            return list(item)
        else:
            return item
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_chat_completion_results(model, dataset_path):
    try:
        generated_completion = []
        with open(dataset_path, "r") as test_data:
            for line in test_data:
                data = json.loads(line)
                data_message = data.get("messages")
                user_review = data_message[1].get("content")
                print('User review: ', user_review)

                chat_completion(model, data_message, 0.2)
                if chat_completion is None:
                    print("Error in chat completion with temperature 0.2")
                    return None
                chat_completion(model, data_message, 0.8)
                if chat_completion is None:
                    print("Error in chat completion with temperature 0.8")
                    return None

                result = ['User review: ' + user_review, 'Chat completion with temperature 0.2: ' + completion_low_temperature.choices[0].message.content, 'Chat completion with temperature 0.8: ' + completion_high_temperature.choices[0].message.content]
                generated_completion.append(result)
        
        generated_completion = [convert_to_serializable(item) for item in generated_completion]
        if generated_completion is None:
            print("Error in convert_to_serializable")
            return None
        
        create_json_file("results/", "chat_completion_result_", generated_completion)
        if create_json_file is None:
            print("Error in create_json_file")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    # NOTE: You can change this to any dataset you want to fine-tune on
    training_dataset = "./data/training_dataset.jsonl"
    # NOTE: You can change this to any dataset you want to test
    test_dataset = "./data/test_dataset.jsonl"
    
    # !: In case of test_dataset = "../data/test_dataset_content.txt", call valid_data_txt(test_dataset)

    if not valid_data_jsonl(training_dataset) or not valid_data_jsonl(test_dataset):
        return

    # Upload training file
    file_uploaded = upload_file(training_dataset)
    if file_uploaded is None:
        return

    # Create fine-tuning job
    model = "gpt-3.5-turbo"
    fine_tuned_job = create_fine_tuning_job(file_uploaded, model)
    if fine_tuned_job is None:
        return

    # Get the metrics
    result_files_id = fine_tuned_job["result_files"][0]
    content = openai.File.download(result_files_id, "results/")
    # TODO: Save the metrics in a file

    # Create chat completion and generate result file
    # model = "ft:gpt-3.5-turbo-0613:universitat-polit-cnica-de-catalunya::8DJxRmih"
    model = fine_tuned_job["fine_tuned_model"]
    generate_chat_completion_results(model, test_dataset)
    if generate_chat_completion_results is None:
        return

if __name__ == '__main__':
    main()