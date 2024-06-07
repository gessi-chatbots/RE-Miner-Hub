import nltk
from dto import SentenceDTO

def add_sentences_to_review(review):
    sentences = split_review(review.review)
    try:
        if len(review.sentences) > 0:
            for index, sentence in enumerate(sentences):
                review.sentences[index].text = sentence
    except IndexError: # TODO check this bug
            sentence_id = f"{review.reviewId}_{index + 1}"
            review.sentences.append(SentenceDTO(id=sentence_id, featureData=None, sentimentData=None, text=sentence))
    
def is_review_splitted(review):
    return review.sentences is not None and len(review.sentences) > 0

def check_review_splitting(review):
    if not is_review_splitted(review):
        extend_and_split_review(review)  
    else:
        add_sentences_to_review(review)

def extend_and_split_review(review):
    sentences = split_review(review.review)
    for index, sentence in enumerate(sentences):
        sentence_id = f"{review.reviewId}_{index}"
        text = sentence
        review.sentences.append(SentenceDTO(id=sentence_id, featureData=None, sentimentData=None, text=text))

def split_review(review_text):
    return nltk.sent_tokenize(review_text)
