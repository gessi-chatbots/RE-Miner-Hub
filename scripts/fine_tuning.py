import openai
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def valid_data_jsonl(data_path):
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

    else:
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
    file_uploaded = openai.File.create(file=open(file_path, "rb"), purpose='fine-tune')

    while True:
        print("Waiting for file to process...")
        file_handle = openai.File.retrieve(id=file_uploaded.id)
        if len(file_handle) and file_handle.status == "processed":
            print("File processed")
            break
        time.sleep(120)

    return file_uploaded

def create_fine_tuning_job(file_uploaded):
    fine_tuning_job = openai.FineTuningJob.create(training_file=file_uploaded.id, model="gpt-3.5-turbo")

    while True:
        print("Waiting for fine-tuning to complete...")
        if fine_tuning_job.status == "succeeded":
            print("Fine-tuning complete")
            print("Fine-tuned job info: ", fine_tuning_job)
            break
        time.sleep(120)

    return fine_tuning_job

def chat_completion(model, messages, temperature):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    print(f'Completion with temperature {temperature}: ', completion.choices[0].message)

def convert_to_serializable(item):
    if isinstance(item, set):
        return list(item)
    else:
        return item

def create_file(content):
    existing_files = [item_file for item_file in os.listdir() if item_file.startswith('completion_result') and item_file.endswith('.json')]
    next_number = 0 if not existing_files else len(existing_files) + 1
    file_name = f'completion_result{next_number}.json'

    with open("../results/" + file_name, 'w') as result_file:
        json.dump(content, result_file, indent=4)

    print("Results saved in ../results/" + file_name)

def generate_chat_completion_results(model, dataset_path):
    generated_completion = []
    with open(dataset_path, "r") as test_data:
        for line in test_data:
            print('Message: ', line)
            line_obj = {line.strip()}
            generated_completion.append('Message: ' + line_obj)
            messages=[{"role": "system", "content": "Can you tell me what emotion is expressing the message above? It can be one of the following: happiness, sadness, anger, fear, surprise or disgust."}, {"role": "user", "content": line}]
            chat_completion(model, messages, 0.2)
            generated_completion.append('Completion with low temperature: ' + {completion_low_temperature.choices[0].message["content"].strip()})
            chat_completion(model, messages, 0.8)
            generated_completion.append('Completion with high temperature: ' + {completion_high_temperature.choices[0].message["content"].strip()})
    
    generated_completion = [convert_to_serializable(item) for item in generated_completion]
    
    create_file(generated_completion)

    """ with open("../results/completion_result.json", "w") as result_file:
        json.dump(generated_completion, result_file, indent=4)

    print("Results saved in ../results/completion_result.json") """

def main():
    # NOTE: You can change this to any dataset you want to fine-tune on
    training_dataset = "../data/training_dataset.jsonl"
    # NOTE: You can change this to any dataset you want to test
    test_dataset = "../data/test_dataset.jsonl"
    
    # !: In case of test_dataset = "../data/test_dataset_content.txt", call valid_data_txt(test_dataset)

    if not valid_data_jsonl(training_dataset) or not valid_data_jsonl(test_dataset):
        return

    # Upload training file
    file_uploaded = upload_file(training_dataset)

    # Create fine-tuning job
    fine_tuned_job = create_fine_tuning_job(file_uploaded)

    # Get the metrics
    result_files_id = fine_tuned_job["result_files"][0]
    content = openai.File.download(result_files_id)

    # Create chat completion and generate result file
    # model = "ft:gpt-3.5-turbo-0613:universitat-polit-cnica-de-catalunya::8DJxRmih"
    model = fine_tuned_job["fine_tuned_model"]
    generate_chat_completion_results(model, test_dataset)

if __name__ == '__main__':
    main()