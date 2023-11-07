import openai
import os
import json

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

#--------------------------CREATE CHAT COMPLETION----------------------------
model = "ft:gpt-3.5-turbo-0613:universitat-polit-cnica-de-catalunya::8DJxRmih" # same as: model = openai.FineTuningJob.retrieve("ftjob-u6afRdtflMKM5A8YkQdjlk5X")

generated_completion = []

with open("../data/test_dataset.jsonl", "r") as file_jsonl:
    for line in file_jsonl:
        obj_json = json.loads(line)
        print('Message: ', obj_json)
        generated_completion.append(obj_json)
        
        completion_low_temperature = openai.ChatCompletion.create(
            model=model,
            messages=obj_json,
            temperature=0.2
        )
        print('Completion low temperature: ', completion_low_temperature.choices[0].message)
        generated_completion.append(completion_low_temperature.choices[0].message)

        completion_high_temperature = openai.ChatCompletion.create(
            model=model,
            messages=obj_json,
            temperature=0.8
        )
        print('Completion high temperature: ', completion_high_temperature.choices[0].message)
        generated_completion.append(completion_high_temperature.choices[0].message)

with open("results/completion_result.json", "w") as result_file:
    json.dump(generated_completion, result_file)


""" 
for m in messages:
    print('Message: ', messages[m])
    completion_low_temperature = openai.ChatCompletion.create(
        model=model,
        messages=messages[m],
        temperature=0.2
    )
    print('Completion low temperature: ', completion_low_temperature.choices[0].message)

    completion_high_temperature = openai.ChatCompletion.create(
        model=model,
        messages=messages[m],
        temperature=0.8
    )
    print('Completion high temperature: ', completion_high_temperature.choices[0].message)
"""
