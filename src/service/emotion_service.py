
def map_emotion(emotion):
    mapped_emotion = ''
    if emotion == 'angry':
        mapped_emotion = 'anger'
    elif emotion == 'happy':
        mapped_emotion = 'happiness'
    elif emotion == 'sad':
        mapped_emotion = 'sadness'
    elif emotion == 'surprise':
        mapped_emotion = 'surprise'
    elif emotion == 'disgust':
        mapped_emotion = 'disgust'
    elif emotion == 'not-relevant':
        mapped_emotion = 'Not relevant'
    else:
        mapped_emotion = emotion
    return mapped_emotion