import json

def limit_reviews(app_data, max_reviews=200):
    for app in app_data:
        if "reviews" in app:
            app["reviews"] = app["reviews"][:max_reviews]

    return app_data

def main():
    with open('data/big_dataset.jsonl', 'r', encoding='utf-8') as file:
        app_data = json.load(file)

    # Limit reviews for each app to 200
    app_data_with_limited_reviews = limit_reviews(app_data)

    # Save the modified app data to small_dataset.jsonl
    with open('data/small_dataset.jsonl', 'w', encoding='utf-8') as output_file:
        json.dump(app_data_with_limited_reviews, output_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
