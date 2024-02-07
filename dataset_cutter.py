import json
from datetime import datetime, timedelta


def limit_reviews(app_data, max_reviews_per_app=200, reviews_per_day_increment=10):
    for app in app_data:
        if "reviews" in app:
            current_date = datetime.strptime(app["current_version_release_date"], "%b %d, %Y")
            for index, review in enumerate(app["reviews"]):
                if index % reviews_per_day_increment == 0 and index > 0:
                    current_date += timedelta(days=1)
                review["at"] = current_date.strftime("%b %d, %Y")
            app["reviews"] = app["reviews"][:max_reviews_per_app]

    return app_data


def main():
    with open('./data/big_dataset.json', 'r', encoding='utf-8') as file:
        app_data = json.load(file)
    app_data_with_limited_reviews = limit_reviews(app_data, max_reviews_per_app=200, reviews_per_day_increment=10)
    with open('./data/small_dataset.json', 'w', encoding='utf-8') as output_file:
        json.dump(app_data_with_limited_reviews, output_file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
