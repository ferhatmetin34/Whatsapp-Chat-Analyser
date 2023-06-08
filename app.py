import streamlit as st
import os
import re
import regex
import helper
import streamlit.components.v1 as components
from plotly import express as px
import warnings
warnings.filterwarnings("ignore")
st.set_option('deprecation.showPyplotGlobalUse', False)


html_temp = """
            <div style="background-color:#25D366;padding:10px;border-radius:10px">
            <h1 style="color:white;text-align:center;">Whatsapp Chat Analyser</h1>
            </div>
            """

st.markdown(html_temp, unsafe_allow_html = True) 
uploaded_file = st.sidebar.file_uploader("Choose a Text File to Analyse:")

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    #regular expression to find the dates
    data = helper.preprocessor(data)
    user_list = helper.get_users(data)
    
    
    st.title("Top Statistics")

    col1, col2, col3, col4 = st.columns(4)
    
    user_count = helper.user_counter(data)
    message_count = helper.message_counter(data)
    num_media_msgs = helper.media_message_counter(data)
    words_count,df_word_count,df_filtered_word = helper.words_counter(data)
    df_emoji,most_used_emoji = helper.emoji_counter(data)
    link_count = helper.link_counter(data)
    most_talkative = helper.most_talkative_finder(data)
    chatted_days = helper.chatted_days_finder(data)

    col5, col6,col7,col8 = st.columns(4)
   

    with col1:
            st.header("User Number")
            st.title(user_count)
    with col2:
            st.header("Total Messages")
            st.title(message_count)
    with col3:
            st.header("Media Shared")
            st.title(num_media_msgs)
    with col4:
            st.header("Total Words")
            st.title(words_count)

    with col5:
            st.header('Most Used Emojis')
            st.title(most_used_emoji)
    with col6:
           st.header('Links Shared')
           st.title(link_count)
    with col7:
           st.header('Most Talkative')
           st.title(most_talkative)       
    with col8:
            st.header('Chatted Days')
            st.title(chatted_days)


    st.title('Chat Timeline')
    fig = helper.plot_chat_timeline(data)
    st.plotly_chart(fig)
    most_talked_day,shared_number = helper.most_talked_day(data)

    with st.expander("**See explanation**"):
        st.write(f"""  
                 The chart above shows daily message counts.\n The day with the most messages is on **{most_talked_day}** and \nnumber of messages shared is **{shared_number}**.
            
        """)
    st.title('Message Rates by Users')
    col9,col10 = st.columns(2)
    fig = helper.message_counter_by_user(data)
    fig_bar = helper.plot_count_bar_chart(data)
   
    with col9:
          
           col9.plotly_chart(fig, use_container_width=True)       
    with col10:
           
            col10.plotly_chart(fig_bar, use_container_width=True)

    st.title('Top 5 Emojis by Users')
    for user in user_list:
           try:
                df_dummy,emojis = helper.emoji_counter(data.loc[data.user == user])
               
                st.markdown(f'<p style="background-color:#25D366;color:#000000;font-size:24px;border-radius:2%;">{f"{user} :  {emojis} "}</p>', unsafe_allow_html=True)
           except:
                  pass
    
    st.title('Most 30 Used Words by Users')
    
    selected_user = st.selectbox('**Select a User**',user_list+['All'])
    for user in user_list:
           if user ==selected_user:
                words_count, df_word_count,df_filtered_word = helper.words_counter(data.loc[data.user == user])

    selected_viz_type = st.radio(label = '**Select a visualisation type**' ,
             options = ['Circle','WordCloud'])
    if selected_viz_type == 'Circle':
        try:        
                fig = helper.plot_words_by_circle(df_word_count)
                st.pyplot(fig)
                fig = helper.plot_monthly_message_rates(data)
                st.title('Message Rates by Months')
                st.pyplot(fig)

                with st.expander("**See explanation**"):
                        st.write(f""" 
                                        The numbers above the chart show total messages in the related month.
                                        """)
        except:
                pass
    else:
         try:        
                st.image(helper.create_wordcloud(df_word_count['Word'].head(30).to_string()).to_array())
               
                fig = helper.plot_monthly_message_rates(data)
                st.title('Message Rates by Months')
                st.pyplot(fig)

                with st.expander("**See explanation**"):
                        st.write(f""" 
                                        The numbers above the chart show total messages in the related month.
                                        """)
         except:
                pass
        
           
    st.title('Messages by Hours')
    fig = helper.plot_hourly_message_cnt(data)
    st.plotly_chart(fig)
    st.title(' Messages by Days')
    fig = helper.plot_daily_message_cnt(data)
    st.plotly_chart(fig) 

st.sidebar.info('To analyse your Whatsapp chat, you need to export chat without media!',icon = 'ℹ️')
helper.create_space(2)
st.sidebar.markdown('**Made by Ferhat Metin**')
st.sidebar.markdown("**ferhatmetin34@gmail.com**")

st.sidebar.markdown(""" 
                        <a href="https://linkedin.com/in/ferhat-metin" target="blank"><img align="center" 
                        src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/linkedin.svg" alt="ferhat-metin" height="30" width="30" /></a><a
                        href="https://kaggle.com/ferhatmetin34" target="blank"><img align="center"
                        src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/kaggle.svg" alt="ferhatmetin34" height="30" width="30" /></a><a
                        href="https://github.com/ferhatmetin34" target="blank"><img align="center"
                        src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/github.svg" alt="ferhatmetin34" height="30" width="30" /></a></p>
                        
                """, unsafe_allow_html = True)


    
      
   
   

    
    

   
   
    
    
    
    
   


