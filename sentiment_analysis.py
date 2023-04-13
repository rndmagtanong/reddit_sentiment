import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scraper

plt.style.use('ggplot')

import nltk

## Step 1. VADER Sentiment Scoring
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm

sia = SentimentIntensityAnalyzer()

## Roberta Pretrained Model
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Run for Roberta Model
def polarity_scores_roberta(example):
    encoded_text = tokenizer(example, return_tensors = 'pt')
    output = model(**encoded_text)
    output
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'roberta_neg' : scores[0],
        'roberta_neu' : scores[1],
        'roberta_pos' : scores[2],
    }
    return scores_dict

## Using own dataset

my_client_id = ''
my_secret = ''
my_user_agent = ''

def get_sentiment(subreddit, keyword):
    relevant_posts, comments_df = scraper.get_relevant_posts_and_comments(
        my_client_id, my_secret, my_user_agent, subreddit, keyword
    )

    sentiment_df = pd.DataFrame()

    for id in relevant_posts['ID']:
        comment_number = 0
        for comment in comments_df[id]:
            try:
                vader_result = sia.polarity_scores(str(comment))
                vader_result_rename = {}
                for key, value in vader_result.items():
                    vader_result_rename[f"vader_{key}"] = value
                roberta_result = polarity_scores_roberta(str(comment))
                both = {**vader_result_rename, **roberta_result}
                sentiment_df = pd.concat((sentiment_df, (pd.DataFrame(both, index=[id])).T), axis = 1)
            except RuntimeError:
                print(f'Broke for id {id} comment number {comment_number}')
            
            comment_number += 1

    overall_score = pd.DataFrame()

    for id in relevant_posts['ID']:
        post_sentiment = sentiment_df.filter(like = id)
        overall_score[id] = post_sentiment.T.mean()

    overall_score.plot(kind = 'bar')

    return relevant_posts, comments_df

if __name__ == "__main__":
    get_sentiment('inearfidelity', 'Moondrop')
    