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

from src.emotion_analysis import EmotionAnalysis

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if __name__ == '__main__':
    emotion_analysis = EmotionAnalysis()
    emotion_analysis.start_emotion_analysis()