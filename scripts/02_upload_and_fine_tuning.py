import openai
import os
import json

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# NOTE: You can change this to any dataset you want to fine-tune on
data_path = "../data/training_dataset.jsonl"

#--------------------------UPLOAD FILE-------------------------------------
file_uploaded = openai.File.create(file=open(data_path, "rb"), purpose='fine-tune')
while True:
    print("Waiting for file to process...")
    file_handle = openai.File.retrieve(id=file_uploaded.id)
    if len(file_handle) and file_handle.status == "processed":
        print("File processed")
        break
    time.sleep(120)

#--------------------------FINE TUNING--------------------------------------
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