import numpy as np
import random
import json
from datetime import datetime
from scipy.stats import truncnorm


def truncated_normal(mean, sd, lower, upper):
    return truncnorm((lower - mean) / sd, (upper - mean) / sd, loc=mean, scale=sd)


def update_reviews(app_data, exclusion_date):
    sentiments = ['happiness', 'sadness', 'anger', 'surprise', 'fear', 'disgust']
    sentiment_probabilities = [0.57, 0.12, 0.21, 0.07, 0.01, 0.02]
    features = [
        "Lightweight", "End-to-End Encryption", "Privacy focused", "Dark Mode", "Free Speech",
        "VoiP Calls","Multiple Account support", "IFTTT Integration", "Self Destructing Messages", "Portable",
        "Cloud Sync", "Two-factor Authentication", "Works Offline", "Support for Themes", "Encrypted Chat",
        "Stickers", "Chat Bot", "Large File Transfer", "Instant Messaging", "Multi Device Support",
        "Video Calling", "Bots", "Channels", "Secret chats", "Share Videos",
        "Cloud based", "Animated stickers", "Integrated File Sharing", "Security focused", "Folders",
        "Video Conferencing", "Private Chat", "Public groups chat", "Persistent History", "Custom themes",
        "Voice messages", "Encrypted calls", "Multiple languages", "Chat organizer", "Instant view",
        "Customizable Themes", "Chat history", "Auto-delete", "Custom Backgrounds", "Cross-Platform",
        "Voice Chat", "Contact Folders", "Based on phone number", "Built-in Photo editor", "Messages in cloud",
        "Sync Contacts", "Hide chat", "Search by tags", "Cloud platform", "Encrypted VoIP calls",
        "Private messaging", "GPS Location Tracking", "Text messaging", "Anonymous Secure Filesharing", "Push to talk",
        "Progressive Web App"
    ]
    feature_probabilities = [
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.1, 0.01, 0.01, 0.01, 0.01,
        0.1, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.1, 0.01, 0.01, 0.01,
        0.1, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.1, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.01
    ]

    assert len(features) == len(feature_probabilities), "Lengths of features and probabilities should be equal"

    for app in app_data["apps"]["L"]:
        half_reviews = len(app["M"]["reviews"]["L"]) // 1
        for review in app["M"]["reviews"]["L"][:half_reviews]:
            num_features = int(truncnorm((1 - 3) / 1, (5 - 3) / 1, loc=3, scale=1).rvs())
            selected_features = random.choices(features, weights=feature_probabilities,
                                               k=min(num_features, len(features)))

            review["M"]["sentiments"]["L"] = [
                {
                    "M": {
                        "sentence": {"S": review["M"]["review"]["S"]},
                        "sentiment": {"S": np.random.choice(sentiments, p=sentiment_probabilities)}
                    }
                }
            ]
            review["M"]["features"]["L"] = [{"S": feature} for feature in selected_features]

    return app_data


def main():
    exclusion_date = datetime.strptime("2022-09-19", "%Y-%m-%d").date()

    with open("./data/data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    updated_data = update_reviews(data, exclusion_date)

    with open("./data/result_data.json", "w", encoding="utf-8") as result_file:
        json.dump(updated_data, result_file, indent=2, ensure_ascii=False)

    print("Updated data saved to result_data.json.")


if __name__ == "__main__":
    main()
