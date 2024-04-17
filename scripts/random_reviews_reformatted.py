import json
import random

def generate_random_reviews(input_file, output_file, total_reviews=100):
    # Load the JSON data from file
    with open(input_file, 'r') as file:
        data = json.load(file)
    all_reviews = []
    for app in data:
        if app.get('reviews', None) is not None:
            for review in app['reviews']:
                all_reviews.append(review)
    random.shuffle(all_reviews)
    selected_reviews = all_reviews[:total_reviews]
    simplified_reviews = []
    for rev in selected_reviews:
        print(f"review: {rev} \n")
        simplified_review = {'reviewId': rev['reviewId'], 'review': rev['review']}
        simplified_reviews.append(simplified_review)
    with open(output_file, 'w') as file:
        json.dump(simplified_reviews, file, indent=4)

def main():
    input_file = '../data/big_dataset.json'
    output_file = '../data/result_random_reviews.json'
    total_reviews = 100
    generate_random_reviews(input_file, output_file, total_reviews)

if __name__ == "__main__":
    main()
