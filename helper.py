import pandas as pd
import numpy as np
import re
import emoji
from collections import Counter
from urlextract import URLExtract
import circlify
import seaborn as sns
sns.set_palette('Set1')
import matplotlib.pyplot as plt
from plotly import express as px
import plotly.graph_objects as go
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import streamlit as st



def preprocessor(data):

    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    #pass the pattern and data to split it to get the list of messages
    messages = re.split(pattern, data)[1:]

    #extract all dates
    dates = re.findall(pattern, data)

    #create dataframe
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df.message = df.message.apply(lambda x:x.rstrip('\n'))
    df['message_date'] = df.message_date.apply(lambda x: x.rstrip(' - ')).str.replace(',','')
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y %H:%M')    
    df['only_date'] = df.message_date.dt.date
    df['year'] = df.message_date.dt.year
    df['month'] = df.message_date.dt.month
    df['day'] = df.message_date.dt.day
    df['hour'] = df.message_date.dt.hour
    df['minute'] = df.message_date.dt.minute
    df['month_name'] = df.message_date.dt.month_name()
    df['day_name'] = df.message_date.dt.day_name()
    df['is_weekend'] = np.where(df.day_name.isin(['Saturday','Sunday']),1,0)
    df['period'] = df.message_date.dt.strftime('%Y%m')
    df = df[df.user != 'group_notification']

    return df

def get_users(data):
    return data.user.unique().tolist()

def words_counter(data):
   
    
    data = data.loc[~(data.message.str.lower().isin(['<media omitted>','null']))]
    words = []
    for message in data['message']:
            words.extend(message.lower().split())
    words_count = len(words)
    df_word_count = pd.DataFrame(Counter(words).most_common(),columns = ['Word','Count'])
   

    

    
    return words_count, df_word_count

def emoji_counter(data):
    try:
        emojis = []
        for message in data['message']:
            emojis.extend(( [ c for c in message if c in emoji.EMOJI_DATA]))
        df_emoji = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))[0]
        
        most_used_emojis = df_emoji[0] +  df_emoji[1] + df_emoji[2] + df_emoji[3]  + df_emoji[4]
        return df_emoji,most_used_emojis
    except:
        return 0,0

def link_counter(data):

    links = []
    extractor = URLExtract()
    for message in data['message']:
        links.extend(extractor.find_urls(message))
    link_count = len(links)
    return link_count

def user_counter(data):
    return data.user.nunique()

def message_counter(data):
    return data.message.shape[0]

def media_message_counter(data):
    return data.loc[(data['message'] == '<Media omitted>') | (data['message'] is None)].shape[0]

def most_talkative_finder(data):
    return data.user.value_counts().sort_values(ascending=False).index[0]

def message_counter_by_user(data):

    count_df = data.user.value_counts().to_frame().reset_index().rename({'index':'user','user':'count'},axis = 1)
    count_df['rate'] = round((count_df['count'] / len(data))*100)
    fig = px.pie(count_df, 
                 values='count', 
                 names='user',
                 hole=.3
                )
    
    fig.update_layout(legend=dict(
                orientation="h",
                entrywidth=70,
                yanchor="bottom",
                y=0.2,
                xanchor="right"))
   
                    
    return fig

def plot_count_bar_chart(data):
    count_df = data.user.value_counts().to_frame().reset_index().rename({'index':'user','user':'count'},axis = 1)
    fig = px.bar(count_df, 
                 x='count', 
                 y='user',
                 text_auto=True,
                 color_discrete_sequence = ['#25D366']
                
                 )
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_xaxes(title='Messages', visible=False, showticklabels=False)
    fig.update_traces(textfont_size=15)
   
                
    return fig


def most_talked_day(data):

    most_talked_day = data.groupby(['only_date'])['message'].count().sort_values(ascending = False).to_frame().reset_index().loc[0][0]

    shared_number =  data.groupby(['only_date'])['message'].count().sort_values(ascending = False).to_frame().reset_index().loc[0][1]

    return most_talked_day,shared_number 

def chatted_days_finder(data):

    return (data.message_date.max() - data.message_date.min()).days

def get_colordict(palette,number,start):

    pal = list(sns.color_palette(palette=palette, n_colors=number).as_hex())
    color_d = dict(enumerate(pal, start=start))
    return color_d


def plot_chat_timeline(data):

    df_to_plot = data.groupby(['only_date'])['message'].count().to_frame().reset_index()
    fig = px.line(x = 'only_date', 
                y='message', 
                data_frame=df_to_plot,
                labels={'only_date':'Date','message':'Messages'},
                color_discrete_sequence=["#DC0A00"]
                )
    return fig

def plot_words_by_circle(data):
   
    n = data['Count'][0:30].max()
    circles = circlify.circlify(data['Count'][0:30].tolist(), 
                                show_enclosure=False, 
                                target_enclosure=circlify.Circle(x=0, y=0)
                            )
    fig, ax = plt.subplots(figsize=(9,9), facecolor='white')
    ax.axis('off')
    lim = max(max(abs(circle.x)+circle.r, abs(circle.y)+circle.r,) for circle in circles)
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # list of labels
    labels = list(data['Word'][0:30])
    counts = list(data['Count'][0:30])
    labels.reverse()
    counts.reverse()
    color_dict = get_colordict('light:#5A9',n , 1)
    # print circles
    for circle, label, count in zip(circles, labels, counts):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.9, color = color_dict.get(count)))
        plt.annotate(label +'\n'+ str(count), (x,y), size=12, va='center', ha='center')
    plt.xticks([])
    plt.yticks([])

    return fig


def plot_monthly_message_rates(data):
 
    df_user_message_cnt = pd.pivot_table(index = 'period',
                                         values = 'message',
                                         aggfunc = 'count',
                                         columns = 'user',
                                         data = data).reset_index(drop = False)
    
    cols_number = len(df_user_message_cnt.columns)
    df_user_message_cnt['Sum'] =  df_user_message_cnt.sum(axis = 1,numeric_only = True)
    df_user_message_rate = df_user_message_cnt.iloc[:,1:cols_number].apply(lambda x:x/df_user_message_cnt['Sum']*100)
    df_user_message_rate.index = df_user_message_cnt.period
    df_user_message_rate = df_user_message_rate.reset_index()

   

    ax = df_user_message_rate.plot(x= 'period',
                              stacked = True,
                              kind = 'bar',
                              figsize = (40,17),
                              fontsize = 35,
                              legend = False,
                              width = 0.9
                              #color = ['#FF423D','#78C0FA','#F5FA5F']
                             

                              )
    ax.get_yaxis().set_visible(False)
    ax.set(xlabel = None)
    ax.legend(loc = 'upper center',bbox_to_anchor=(0.5, -0.18), fancybox=True, shadow=True, ncol=5,fontsize = 35)
    ax.title.set_size(35)

    for i,c in enumerate(ax.containers):
        labels = [v.get_height() if v.get_height()>0 else ''for v in c]
        labels =['%.0f' % elem + '%' for elem in labels ]
        ax.bar_label(c,labels = labels, label_type = 'center',color = 'black',fontsize = 35)

    for index,value in enumerate(df_user_message_cnt.Sum):
        plt.text(x = index -0.35,
                y = 101,
                s = str(value),
                fontsize = 30)
        
    return ax.figure


def plot_hourly_message_cnt(data):

    df_hourly_message_cnt = data.pivot_table(index = 'hour', values = 'message',columns = 'user', aggfunc = 'count').reset_index()
    df_hourly_message_cnt['Sum'] =  df_hourly_message_cnt.sum(axis = 1,numeric_only = True)
    fig = px.histogram(df_hourly_message_cnt, x='hour',
                       y = df_hourly_message_cnt.columns[1:len(df_hourly_message_cnt.columns)-1].tolist(),
                        nbins = 24,
                        template="simple_white",
                        labels = {'variable':''},
                        color_discrete_sequence=px.colors.qualitative.Set1,
                        text_auto = True
                    )
    
    fig.update_yaxes(title='Messages', visible=True, showticklabels=True)
    fig.update_xaxes(title='Hours', visible=True, showticklabels=True)

    fig.add_hline(y = df_hourly_message_cnt.Sum.mean().round() ,
                                    line_width=3,
                                    line_dash="dash",
                                    line_color="black",
                                    annotation_text = 'Avg',
                                    annotation_position="right",
                                    annotation_font_size=15,
                                    annotation_font_color="black")

    return fig

def plot_daily_message_cnt(data):

    df_daily_message_cnt = data.pivot_table(index = 'day_name', values = 'message',columns = 'user', aggfunc = 'count').reset_index()
    df_daily_message_cnt['Sum'] =  df_daily_message_cnt.sum(axis = 1,numeric_only = True)
    df_daily_message_cnt = df_daily_message_cnt.sort_values(by ='Sum',ascending = False)
    fig = px.histogram(df_daily_message_cnt, x='day_name',
                       y = df_daily_message_cnt.columns[1:len(df_daily_message_cnt.columns)-1].tolist(),
                        nbins = 7,
                        template="simple_white",
                        labels = {'variable':''},
                        color_discrete_sequence=px.colors.qualitative.Set1,
                        text_auto = True

                    )
    fig.add_hline(y = df_daily_message_cnt.Sum.mean().round() ,
                                    line_width=3,
                                    line_dash="dash",
                                    line_color="black",
                                    annotation_text = 'Avg',
                                    annotation_position="bottom right",
                                    annotation_font_size=15,
                                    annotation_font_color="black")
    
    fig.update_yaxes(title='Messages', visible=True, showticklabels=True)
    fig.update_xaxes(title='Days', visible=True, showticklabels=True)

    return fig

def create_wordcloud(data):
   
    wordcloud = WordCloud( width = 600,height = 400,
                          background_color='white',
                          max_font_size = 50,
                          colormap='Paired',
                          collocations=True).generate(str(data))
    return wordcloud 

def create_space(number_of_row):
        for i in range(number_of_row):

            st.sidebar.markdown("&nbsp;")   
    









