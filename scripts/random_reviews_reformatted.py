import json
import random

def generate_random_reviews(input_file, 
                            output_simplfied_file, 
                            output_complete_file, 
                            total_reviews=100):
    with open(input_file, 'r') as dataset:
        data = json.load(dataset)

    all_reviews = []
    for app in data:
        if app.get('reviews', None) is not None:
            for review in app['reviews']:
                all_reviews.append(review)

    random.shuffle(all_reviews)

    selected_reviews = all_reviews[:total_reviews]
    simplified_reviews = []
    complete_reviews = []

    for rev in selected_reviews:
        simplified_review = {'reviewId': rev['reviewId'], 'review': rev['review']}
        simplified_reviews.append(simplified_review)
        complete_reviews.append(rev)

    with open(output_simplfied_file, 'w') as file:
        json.dump(simplified_reviews, file, indent=4)
    with open(output_complete_file, 'w') as file:
        json.dump(complete_reviews, file, indent=4)

def main():
    input_file = '../data/big_dataset.json'
    simplified_random_reviews_file = '../data/result_simplified_random_reviews.json'
    random_reviews_file = '../data/random_reviews.json'

    total_reviews = 100
    generate_random_reviews(input_file, simplified_random_reviews_file, random_reviews_file, total_reviews)

if __name__ == "__main__":
    main()
