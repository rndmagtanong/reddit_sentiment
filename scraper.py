import praw
import pandas as pd
from praw.models import MoreComments
# import urllib.request
# import os

def get_relevant_posts_and_comments(my_client_id, my_secret, my_user_agent, target_sub, keyword):
    # Read-only instance
    reddit_read_only = praw.Reddit(client_id = my_client_id,         # your client id
        client_secret = my_secret,                                   # your client secret
        user_agent = my_user_agent)                                  # your user agent

    target_sub = target_sub # enter target subreddit here
    subreddit = reddit_read_only.subreddit(target_sub)

    # Scraping posts from certain time
    # Options: "all", "day", "hour", "week", "month", "year"
    posts = subreddit.top(time_filter = "year")

    posts_dict = {"Title": [], "Post Text": [],
                "ID": [], "Score": [],
                "Total Comments": [], "Post URL": [],
                }

    for post in posts:
        # Title of each post
        posts_dict["Title"].append(post.title)
        
        # Text inside a post
        posts_dict["Post Text"].append(post.selftext)
        
        # Unique ID of each post
        posts_dict["ID"].append(post.id)
        
        # The score of a post
        posts_dict["Score"].append(post.score)
        
        # Total number of comments inside the post
        posts_dict["Total Comments"].append(post.num_comments)
        
        # URL of each post
        posts_dict["Post URL"].append(post.url)
        
    top_posts = pd.DataFrame(posts_dict)

    # get only relevant posts
    keyword = keyword
    relevant_posts = top_posts[top_posts['Title'].str.contains(keyword, case = False)]

    # get comments of relevant posts
    comments_df = pd.DataFrame()

    for id in relevant_posts['ID']:

        submission = reddit_read_only.submission(id=id)
        post_comments = []

        for comment in submission.comments:
            if type(comment) == MoreComments:
                continue

            post_comments.append(comment.body)
        
        # creating a dataframe
        comments_df[id] = pd.DataFrame(post_comments)

    return relevant_posts, comments_df.astype("string")

if __name__ == "__main__":
    my_client_id = ''
    my_secret = ''
    my_user_agent = ''
    relevant_posts, comments_df = get_relevant_posts_and_comments(my_client_id, my_secret, my_user_agent, 'inearfidelity', 'Moondrop')