import os
import json
import jsonlines
import time
import csv
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict
from pydantic import BaseModel
from io import StringIO

from src.GenerativeSentimentAnalysisController import GenerativeSentimentAnalysisController

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if __name__ == '__main__':
    GenerativeSentimentAnalysisController = GenerativeSentimentAnalysisController()
    GenerativeSentimentAnalysisController.start_generative_sentiment_analysis()