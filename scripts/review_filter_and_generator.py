import json
import uuid
from random import choices, randint
from datetime import datetime, timedelta

desired_features = ["Private Chat", "Voice messages", "Voice chat", "stickers", "Video Calling"]
desired_sentiments = ["am happy about", "sad about", "am so angry regarding", "am surprised with", "fear so much the",
                      "am disgusted with"]
sentiment_probabilities = [0.57, 0.12, 0.21, 0.07, 0.01, 0.02]


def generate_random_review():
    sentiment1 = choices(desired_sentiments, weights=sentiment_probabilities)[0]
    feature1 = desired_features[randint(0, len(desired_features) - 1)]

    sentiment2 = choices(desired_sentiments, weights=sentiment_probabilities)[0]
    feature2 = desired_features[randint(0, len(desired_features) - 1)]

    sentence1 = f"I {sentiment1} the {feature1} feature!."
    sentence2 = f"Also I would love to say that I {sentiment2} the {feature2} feature"

    return sentence1 + (" " + sentence2 if randint(0, 1) == 0 else f" {sentence2}")


def process_reviews(app):
    new_reviews = []
    review_count = 0
    for review in app['reviews']:
        if review_count >= 20:
            break
        review_text = review['review']

        if any(feature.lower() in review_text.lower() for feature in desired_features):
            new_reviews.append(review)
            review_count += 1
        else:
            random_review = generate_random_review()
            original_date = datetime.strptime(review['at'], '%b %d, %Y')
            random_date = original_date + timedelta(days=randint(1, 30))
            if random_date.year > 2022:
                random_date = original_date
            namespace = uuid.UUID(int=0)
            random_review_id = str(uuid.uuid3(namespace, random_review))

            random_review_data = {
                "reviewId": random_review_id,
                "review": random_review,
                "reply": None,
                "userName": "Random User",
                "score": randint(1, 5),
                "at": random_date.strftime('%b %d, %Y')
            }
            new_reviews.append(random_review_data)
            review_count += 1

    app['reviews'] = new_reviews


def main():
    with open('../data/small_dataset.json', 'r', encoding='utf-8') as file:
        dataset = json.load(file)

    for application in dataset:
        process_reviews(application)

    with open('../data/meaningfull_small_dataset.json', 'w', encoding='utf-8') as output_file:
        json.dump(dataset, output_file, indent=2)


if __name__ == '__main__':
    main()
