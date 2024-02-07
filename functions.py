from urlextract import URLExtract
from textblob import TextBlob
import pandas as pd
from datetime import datetime
from wordcloud import WordCloud
extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    # number of msgs
    num_msgs = df.shape[0]
    # number of media
    num_med = df[df['msg'] == '<Media omitted>\n'].shape[0]

    # number of links
    link = []
    for msg in df['msg']:
        link.extend(extract.find_urls(msg))

    # Sentiment Analysis
    sentiments = df['msg'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    avg_sentiment = sentiments.mean()

    # Sentiment Label
    if avg_sentiment > 0:
        sentiment_label = 'Positive'
    elif avg_sentiment < 0:
        sentiment_label = 'Negative'
    else:
        sentiment_label = 'Neutral'

    return num_msgs, num_med, link, sentiment_label, avg_sentiment, sentiments


def monthly_timeline(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month'])['msg'].count().reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

# weekly timeline
def weekly_timeline(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month', pd.Grouper(key='date', freq='W-Mon')])['msg'].count().reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]) + '-' + str(timeline['date'][i].day))

    timeline['time'] = time

    return timeline

# modified daily timeline
def daily_timeline(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    timeline = df.groupby('date')['msg'].count().reset_index()
    timeline['day'] = timeline['date'].dt.day_name()

    return timeline



def activity_map(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    active_month_df = df.groupby('month')['msg'].count().reset_index()
    month_list = active_month_df['month'].tolist()
    month_msg_list = active_month_df['msg'].tolist()

    active_day_df = df.groupby('day')['msg'].count().reset_index()
    day_list = active_day_df['day'].tolist()
    day_msg_list = active_day_df['msg'].tolist()

    return active_month_df, month_list, month_msg_list, active_day_df, day_list, day_msg_list


def most_chaty(df):
    x = df['user'].value_counts().head()

    percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2)
    return x, percent

# calc word frequecny   
def calculate_word_frequency(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    # Exclude messages with '<Media omitted>\n'
    df_no_media = df[df['msg'] != '<Media omitted>\n']

    # Calculate word frequency in percentage
    word_freq_percent = (df_no_media['msg'].value_counts() / len(df_no_media)) * 100

    return word_freq_percent.to_dict()

# Modify create_wordcloud function to exclude media omitted messages
def create_wordcloud(selected_user, df):
    if selected_user != 'OverAll':
        df = df[df['user'] == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    
    # Exclude messages with '<Media omitted>\n'
    df_no_media = df[df['msg'] != '<Media omitted>\n']
    
    # Concatenate words from messages
    all_msgs = ' '.join(df_no_media['msg'])
    
    df_wc = wc.generate(all_msgs)
    
    return df_wc

# Calculate chat growth for all users
def chat_growth_all(df):
    # Group by date and count cumulative messages
    growth_data_all = df.groupby('date')['msg'].count().cumsum().reset_index()

    return growth_data_all

# Calculate the reply time 
def calculate_reply_time_analyses(df):
    """Calculates reply time statistics and identifies the fastest replier.

    Args:
        df (pandas.DataFrame): The chat DataFrame containing timestamp information.

    Returns:
        tuple: A tuple containing:
            - overall_mean_reply_time (float): Overall mean reply time in seconds.
            - overall_median_reply_time (float): Overall median reply time in seconds.
            - reply_time_per_user (pandas.DataFrame): Reply time statistics per user.
            - fastest_replier (str): Name of the fastest replier.
            - fastest_reply_time (float): Reply time of the fastest replier in seconds.
            - replier_advantage (float): Percentage advantage of the fastest replier.
    """

    # Sort messages by timestamp
    df = df.sort_values(by='date')

    # Calculate reply time for each message (excluding the first one)
    df['reply_time'] = df['date'].diff().dt.total_seconds()

    # Calculate overall statistics
    overall_mean_reply_time = df['reply_time'].mean()
    overall_median_reply_time = df['reply_time'].median()

    # Calculate reply time statistics per user
    reply_time_per_user = df.groupby('user')['reply_time'].agg(['mean', 'median'])

    # Identify fastest replier and calculate advantage
    fastest_replier = reply_time_per_user['mean'].idxmin()
    fastest_reply_time = reply_time_per_user.loc[fastest_replier]['mean']
    replier_advantage = ((reply_time_per_user['mean'].mean() - fastest_reply_time) /
                         reply_time_per_user['mean'].mean()) * 100

    return (overall_mean_reply_time, overall_median_reply_time, reply_time_per_user,
            fastest_replier, fastest_reply_time, replier_advantage)

def format_time(seconds):
    """Formats time in seconds into a human-readable format (minutes:seconds)."""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:.0f}m:{seconds:.2f}s"


# Mood Swing Chart
def mood_swing(df):
    overall_timeline = df.groupby(['year', 'month'])['msg'].count().reset_index()
    overall_timeline['media'] = df[df['msg'] == '<Media omitted>\n'].groupby(['year', 'month'])['msg'].count().reset_index()['msg']

    overall_timeline['total'] = overall_timeline['msg'] + overall_timeline['media']

    return overall_timeline