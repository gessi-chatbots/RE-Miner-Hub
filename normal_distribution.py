import numpy as np
import random
import json


def update_reviews(app_data):
    sentiments = ['happiness', 'sadness', 'anger', 'surprise', 'fear', 'disgust']
    features = [
        "Lightweight", "End-to-End Encryption", "Privacy focused", "Dark Mode", "VoiP Calls",
        "Multiple Account support", "IFTTT Integration", "Self Destructing Messages", "Portable",
        "Cloud Sync", "Two-factor Authentication", "Works Offline", "Support for Themes",
        "Encrypted Chat", "Stickers", "Chat Bot", "Large File Transfer", "Instant Messaging",
        "Multi Device Support", "Video Calling", "Bots", "Channels", "Secret chats", "Share Videos",
        "Cloud based", "Animated stickers", "Integrated File Sharing", "Security focused", "Folders",
        "Video Conferencing", "Private Chat", "Public groups chat", "Persistent History",
        "Custom themes", "Voice messages", "Encrypted calls", "Multiple languages", "Chat organizer",
        "Instant view", "Customizable Themes", "Chat history", "Auto-delete", "Custom Backgrounds",
        "Cross-Platform", "Voice Chat", "Contact Folders", "Based on phone number",
        "Built-in Photo editor", "Messages in cloud", "Sync Contacts", "Hide chat", "Search by tags",
        "Cloud platform", "Encrypted VoIP calls", "Private messaging", "GPS Location Tracking",
        "Text messaging", "Anonymous Secure Filesharing", "Push to talk", "Progressive Web App",
        "Free Speech"
    ]

    for app in app_data["apps"]["L"]:
        half_reviews = len(app["M"]["reviews"]["L"]) // 3
        for review in app["M"]["reviews"]["L"][:half_reviews]:
            review["M"]["sentiments"]["L"] = [
                {
                    "M": {
                        "sentence": {"S": review["M"]["review"]["S"]},
                        "sentiment": {"S": np.random.choice(sentiments, p=[0.1, 0.2, 0.2, 0.2, 0.2, 0.1])}
                    }
                }
            ]
            review["M"]["features"]["L"] = [{"S": feature} for feature in
                                            random.sample(features, random.randint(1, len(features)))]

    return app_data


def main():
    with open("./data/data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    updated_data = update_reviews(data)

    with open("./data/result_data.json", "w", encoding="utf-8") as result_file:
        json.dump(updated_data, result_file, indent=2, ensure_ascii=False)

    print("Updated data saved to result_data.json.")


if __name__ == "__main__":
    main()
