import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

#--------------------------VALIDATE DATA-------------------------------------

# NOTE: You can change this to any dataset you want to fine-tune on
data_path = "../data/training_dataset.jsonl"

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

else:
    print("No errors found")

    #--------------------------UPLOAD FILE-------------------------------------
    # Upload file
    file_uploaded = openai.File.create(file=open(data_path, "rb"), purpose='fine-tune')
    while True:
        print("Waiting for file to process...")
        file_handle = openai.File.retrieve(id=file_uploaded.id)
        if len(file_handle) and file_handle.status == "processed":
            print("File processed")
            break
        time.sleep(120)

    #--------------------------FINE TUNING--------------------------------------
    # Create fine-tuning job
    fine_tuned_job = openai.FineTuningJob.create(training_file=file_uploaded.id, model="gpt-3.5-turbo")
    while True:
        print("Waiting for fine-tuning to complete...")
        if fine_tuned_job.status == "succeeded":
            print("Fine-tuning complete")
            print("Fine-tuned job info: ", fine_tuned_job)
            break
        time.sleep(120)

    #--------------------------GET THE METRICS----------------------------------
    result_files_id = fine_tuned_job["result_files"][0]
    content = openai.File.download(result_files_id)

    #--------------------------CREATE CHAT COMPLETION AND RESULT FILE----------------------------
    model = fine_tuned_job["fine_tuned_model"]
    generated_completion = []

    with open("../data/test_dataset_content.txt", "r") as test_data:
        for line in test_data:
            print('Message: ', line)
            line_obj = {line.strip()}
            generated_completion.append(line_obj)

            completion_low_temperature = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": line}],
                temperature=0.2
            )
            print('Completion low temperature: ', completion_low_temperature.choices[0].message)
            generated_completion.append({completion_low_temperature.choices[0].message["content"].strip()})

            completion_high_temperature = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": line}],
                temperature=0.8
            )
            print('Completion high temperature: ', completion_high_temperature.choices[0].message)
            generated_completion.append({completion_high_temperature.choices[0].message["content"].strip()})

    def convert_to_serializable(item):
        if isinstance(item, set):
            return list(item)
        else:
            return item

    generated_completion = [convert_to_serializable(item) for item in generated_completion]

    with open("../results/completion_result.json", "w") as result_file:
        json.dump(generated_completion, result_file, indent=4)

    print("Results saved in ../results/completion_result.json")