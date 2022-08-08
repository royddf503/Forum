import pandas as pd
from sqlalchemy import create_engine
from web import User
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax
import seaborn as sns
import matplotlib.pyplot as plt

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


def convert_tableSQL_df(name_table):
    """
    Convert sql table to pandas dataframe
    :param name_table: name of sql table
    :return: pandas data frame
    """
    cnx = create_engine('sqlite:///posts.db').connect()
    df = pd.read_sql_table(name_table, cnx)
    return df


def get_user_avg_sentiment(user_id):
    """
    Returns the avg sentiment of user by scanning all of his posts
    """
    user_posts = User.query.get(user_id).posts
    if len(user_posts) == 0:
        return pd.Series([None] * 3)
    total_scores = [0] * 3
    for post in user_posts:
        encoded_text = tokenizer(post.content, return_tensors='pt')
        output = model(**encoded_text)
        scores = output[0][0].detach().numpy()
        total_scores += softmax(scores)

    return pd.Series([x / len(user_posts) for x in total_scores])


def get_users_mood_data():
    df1 = convert_tableSQL_df('user')
    df2 = df1.apply(lambda row: get_user_avg_sentiment(row['id']), axis=1)
    df2.rename(columns={0: 'neg_avg', 1: 'neu_avg', 2: 'pos_avg'}, inplace=True)
    df3 = df1.join(df2).sort_values(by=['neg_avg'])
    return df3


def plot_gender_mood():
    df = get_users_mood_data()
    fig, axs = plt.subplots(1, 3, figsize=(12, 3))
    sns.barplot(data=df, x='gender', y='pos_avg', ax=axs[0])
    sns.barplot(data=df, x='gender', y='neu_avg', ax=axs[1])
    sns.barplot(data=df, x='gender', y='neg_avg', ax=axs[2])
    axs[0].set_title('Positive')
    axs[1].set_title('Neutral')
    axs[2].set_title('Negative')
    plt.tight_layout()
    plt.show()


get_users_mood_data()
plot_gender_mood()
