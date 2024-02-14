import os
from openai import OpenAI
from dotenv import load_dotenv

from src.generative_sentiment_analysis_service import GenerativeSentimentAnalysisService

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if __name__ == '__main__':
    GenerativeSentimentAnalysisController = GenerativeSentimentAnalysisService()
    GenerativeSentimentAnalysisController.start_generative_sentiment_analysis()
