import openai
import os
import json

# Set your API key
openai.api_key = "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"

#--------------------------CREATE CHAT COMPLETION----------------------------
model = "ft:gpt-3.5-turbo-0613:universitat-polit-cnica-de-catalunya::8DJxRmih" # same as: model = openai.FineTuningJob.retrieve("ftjob-u6afRdtflMKM5A8YkQdjlk5X")
# NOTE: You can change this to any dataset you want to test on
messages = [
    {"role": "system", "content": "You are a helpful assistant that can recognize emotions."},
    {"role": "user", "content": "People often overestimate/underestimate the amount of time they did a certain task this app helps you to have a record of the said task."}
]

completion_low_temperature = openai.ChatCompletion.create(
    model=model,
    messages=messages,
    temperature=0.2
)
print('Completion low temperature: ', completion_low_temperature.choices[0].message)

completion_high_temperature = openai.ChatCompletion.create(
    model=model,
    messages=messages,
    temperature=0.8
)
print('Completion high temperature: ', completion_high_temperature.choices[0].message)