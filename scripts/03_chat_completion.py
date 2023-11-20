import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

#--------------------------CREATE CHAT COMPLETION----------------------------
model = "ft:gpt-3.5-turbo-0613:universitat-polit-cnica-de-catalunya::8DJxRmih" # same as: model = openai.FineTuningJob.retrieve("ftjob-u6afRdtflMKM5A8YkQdjlk5X")

generated_completion = []

# NOTE: You can change this to any dataset you want to test
with open("./data/test_dataset.jsonl", "r") as test_data:
    for line in test_data:
        data = json.loads(line)
        data_message = data.get("messages")
        user_review = data_message[1].get("content")
        print('User review: ', user_review)

        completion_low_temperature = openai.ChatCompletion.create(
            model=model,
            messages=data_message,
            temperature=0.2
        )
        print('Completion low temperature: ', completion_low_temperature.choices[0].message.content)

        completion_high_temperature = openai.ChatCompletion.create(
            model=model,
            messages=data_message,
            temperature=0.8
        )
        print('Completion high temperature: ', completion_high_temperature.choices[0].message.content)
        result = ['User review: ' + user_review, 'Chat completion with temperature 0.2: ' + completion_low_temperature.choices[0].message.content, 'Chat completion with temperature 0.8: ' + completion_high_temperature.choices[0].message.content]
        generated_completion.append(result)
    
generated_completion = [convert_to_serializable(item) for item in generated_completion]

path = "results/"
existing_files = [item_file for item_file in os.listdir(path) if item_file.startswith('chat_completion_result_') and item_file.endswith('.json')]
next_number = 0 if not existing_files else len(existing_files) + 1
file_name = f'chat_completion_result_{next_number}.json'

with open(path + file_name, 'w') as result_file:
    json.dump(generated_completion, result_file, indent=4)

print(f"Results saved in {path}{file_name}")
