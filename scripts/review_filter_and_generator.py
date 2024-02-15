import json

desired_app_names = ["WhatsApp Messenger", "Facebook Lite", "Strava: Run, Ride, Hike", "Telegram"]
desired_feature_ids = ["f_34", "f_32", "f_47", "f_51", "f_60", "f_62", "f_36", "f_35", "f_85"]


def extract_desired_apps(app_dataset):
    return [app for app in app_dataset if app['app_name'] in desired_app_names]


def main():
    with open('../data/full_dataset.json', 'r', encoding='utf-8') as full_dataset_file:
        dataset = json.load(full_dataset_file)
    with open('../data/feature_review-sentence_dictionary.json', 'r', encoding='utf-8') as feature_filter_file:
        feature_filters = json.load(feature_filter_file)

    applications_data = extract_desired_apps(dataset)

    for desired_feature_id in desired_feature_ids:
        desired_feature_reviews = feature_filters.get(desired_feature_id, [])
        for application in applications_data:
            desired_reviews = []
            for review in application['reviews']:
                for desired_feature_review in desired_feature_reviews:
                    if review['reviewId'] in desired_feature_review:
                        desired_reviews.append(review)
            if desired_reviews:
                if 'filtered_reviews' not in application:
                    application['filtered_reviews'] = []
                for desired_review in desired_reviews:
                    found = False
                    for filtered_review in application['filtered_reviews']:
                        if desired_review['reviewId'] != filtered_review['reviewId']:
                            found = False
                        else:
                            found = True
                            break
                    if not found:
                        application['filtered_reviews'].append(desired_review)


    for application in dataset:
        application['reviews'] = application.get('filtered_reviews', [])

    with open('../data/meaningful_small_dataset.json', 'w', encoding='utf-8') as output_file:
        json.dump(applications_data, output_file, indent=2)


if __name__ == '__main__':
    main()
