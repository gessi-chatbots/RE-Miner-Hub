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
