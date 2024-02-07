import streamlit as st
import preprocessor
import functions
from functions import format_time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

st.sidebar.title('WhatsApp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader("Choose a File")

if uploaded_file is None:
    st.markdown('''Please export your WhatsApp chat (without media), whether it be a group chat or an individual/private chat, then click on "Browse Files" and upload it to this platform.''')
    st.markdown('''Afterward, kindly proceed to click on the "Analyse" button. This action will generate a variety of insights concerning your conversation.''')
    st.markdown(''' You will have the option to select the type of analysis, whether it is an overall analysis or one that specifically focuses on particular participants' analysis.''')
    st.markdown('Thank You!')
    st.markdown('Devanshu Prajapati')

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # st.write(bytes_data)

    # converting bytes into text
    data = bytes_data.decode('utf-8')

    # show text data
    # st.text(data)

    # DataFrame
    df = preprocessor.preprocess(data)

    # show dataframe
    # st.dataframe(df)

    # fetch unique user
    user_details = df['user'].unique().tolist()
    # remove Group Notifications
    if 'Group Notification' in user_details:
        user_details.remove('Group Notification')
    # sorting list
    user_details.sort()
    # insert overall option
    user_details.insert(0, 'OverAll')

    # drop down to select user
    selected_user = st.sidebar.selectbox('Show Analysis as:', user_details)

    if st.sidebar.button('Analyse'):

        num_msgs, num_med, links, sentiment_label, avg_sentiment, sentiments = functions.fetch_stats(selected_user, df)

        # overall statistics
        st.title('OverAll Basic Statistics')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header('Messages')
            st.subheader(num_msgs)
        with col2:
            st.header('Media Shared')
            st.subheader(num_med)
        with col3:
            st.header('Link Shared')
            st.subheader(len(links))
            
        with col4:
            st.header('Avg Sentiment')
            st.subheader(f'{sentiment_label} ({avg_sentiment:.2f})')
        
        # Display Links Separately
        st.subheader('Links Shared:')
        num_links_to_display = len(links)

        links_display = "\n".join([f"{i}. {link}" for i, link in enumerate(links[:num_links_to_display], start=1)])
        links_text_area = st.text_area(label='', value=links_display, height=100)

        # monthly timeline
        timeline = functions.monthly_timeline(selected_user, df)
        st.title('Monthly Timeline')

        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['msg'], color='maroon')
        plt.xticks(rotation=90)
        st.pyplot(fig)

        # weekly timeline
        timeline_weekly = functions.weekly_timeline(selected_user, df)
        st.title('Weekly Timeline')

        fig, ax = plt.subplots(figsize=(15, 5))  # Adjust the figure size
        ax.plot(timeline_weekly['time'], timeline_weekly['msg'], color='blue')
        plt.xticks(rotation=45, ha='right')  # Adjust rotation and horizontal alignment
        plt.tight_layout()  # Ensure tight layout for better visibility
        st.pyplot(fig)

        # modified daily timeline
        timeline_daily = functions.daily_timeline(selected_user, df)
        st.title('Daily Timeline')

        fig, ax = plt.subplots()
        ax.plot(timeline_daily['date'], timeline_daily['msg'], color='purple')
        plt.xticks(rotation=90)
        st.pyplot(fig)


        # active map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        active_month_df, month_list, month_msg_list, active_day_df, day_list, day_msg_list = functions.activity_map(selected_user, df)
        with col1:
            # active month
            st.header('Most Active Month')
            fig, ax = plt.subplots()
            ax.bar(active_month_df['month'], active_month_df['msg'])
            ax.bar(month_list[month_msg_list.index(max(month_msg_list))], max(month_msg_list), color='green', label = 'Highest')
            ax.bar(month_list[month_msg_list.index(min(month_msg_list))], min(month_msg_list), color='red', label = 'Lowest')
            plt.xticks(rotation=90)
            st.pyplot(fig)

        with col2:
            # active day
            st.header('Most Active Day')
            fig, ax = plt.subplots()
            ax.bar(active_day_df['day'], active_day_df['msg'])
            ax.bar(day_list[day_msg_list.index(max(day_msg_list))], max(day_msg_list), color='green', label='Highest')
            ax.bar(day_list[day_msg_list.index(min(day_msg_list))], min(day_msg_list), color='red', label='Lowest')
            plt.xticks(rotation=90)
            st.pyplot(fig)


        # most chatiest user
        # if selected_user == 'OverAll':
        st.title('Most Active Users')

        x, percent = functions.most_chaty(df)
        fig, ax = plt.subplots()

        col1, col2 = st.columns(2)
        with col1:
            ax.bar(x.index, x, color='cyan')

            st.pyplot(fig)
        with col2:
            st.dataframe(percent)

        # WordCloud
        df_wc = functions.create_wordcloud(selected_user, df)
        st.title('Most Common Words')
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Word Frequency in Percentage
        st.title('Word Frequency in Percentage')
        word_freq_percent = functions.calculate_word_frequency(selected_user, df)
        st.dataframe(pd.DataFrame(list(word_freq_percent.items()), columns=['Word', 'Frequency (%)']).sort_values(by='Frequency (%)', ascending=False))

        # Sentiment Analysis Chart
        st.title('Sentiment Analysis')
        fig, ax = plt.subplots()
        sns.histplot(sentiments, bins=20, kde=True, color='skyblue')
        ax.set_xlabel('Sentiment Polarity')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)

        # Chat Growth for All Users
        st.title('Chat Growth Over Time (All Users)')
        growth_data_all = functions.chat_growth_all(df)

        fig, ax = plt.subplots()
        ax.plot(growth_data_all['date'], growth_data_all['msg'], color='orange')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

        # Reply time 
        reply_time_analyses = functions.calculate_reply_time_analyses(df)
        st.title('Reply Time Analyses')

        st.subheader('Reply Time Per User')
        st.dataframe(reply_time_analyses[2])

        # Highlight the fastest replier
        fastest_replier = reply_time_analyses[3]
        fastest_reply_time = format_time(reply_time_analyses[4])
        replier_advantage = str(round(reply_time_analyses[5], 2)) + '%'
        st.success(f"Fastest Replier: **{fastest_replier}** (Replies faster on average, {replier_advantage} advantage)")
        
        # Mood Swing Chart
        mood_swing_data = functions.mood_swing(df)
        st.title('Mood Swing Over Time')

        fig, ax1 = plt.subplots(figsize=(10, 5))

        color = 'tab:red'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Total Messages', color=color)
        ax1.plot(mood_swing_data['year'].astype(str) + '-' + mood_swing_data['month'], mood_swing_data['total'], color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:blue'
        ax2.set_ylabel('Media Shared', color=color)  # we already handled the x-label with ax1
        ax2.plot(mood_swing_data['year'].astype(str) + '-' + mood_swing_data['month'], mood_swing_data['media'], color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        # Rotate x-axis labels by 90 degrees
        ax1.set_xticks(ax1.get_xticks())
        ax1.set_xticklabels(mood_swing_data['year'].astype(str) + '-' + mood_swing_data['month'], rotation=90)

        fig.tight_layout()  # otherwise, the right y-label is slightly clipped
        st.pyplot(fig)

        st.text(' ')
        st.text(' ')
