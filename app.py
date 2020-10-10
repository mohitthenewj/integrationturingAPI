# handling data
import numpy as np
import pandas as pd
from collections import Counter

import os
import io
import copy
from io import BytesIO, StringIO
import time
from push_blob import push_blob_f
import requests
from oddf import odasdf
from ast import literal_eval


# MY-SQL connection
import mysql.connector
from mysql.connector import Error
# import pymysql

# Date-Time
import  datetime
from datetime import datetime, date, timedelta

# model deployment
import streamlit as st

# utils
import os
import joblib

# hide streamlit style
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# connect with Azure-db
cnx = mysql.connector.connect(host = 'mysqlservernewjprod.mysql.database.azure.com', user = 'phantom@mysqlservernewjprod', password = 'Zurich$1', db = 'fb', port = 3306)
cursor = cnx.cursor(buffered=True)

# Find the value From Dictionary
def get_value(val,my_dict):
	for key ,value in my_dict.items():
		if val == key:
			return value

# Find the Key From Dictionary
def get_key(val,my_dict):
	for key ,value in my_dict.items():
		if val == value:
			return key

# Load Models
def load_model_n_predict(model_file):
	loaded_model = joblib.load(open(os.path.join(model_file),"rb"))
	return loaded_model

# Load Models
def load_transformer(model_file):
	transformed_data = joblib.load(open(os.path.join(model_file),"rb"))
	return transformed_data

def od_feature(od_df = None):
        # Replace labels by super class labels
    if od_df is not None:
        super_class_df = pd.read_csv('data/super_class_final.csv')
        for i in range(od_df.shape[0]):
            for j in range(super_class_df.shape[0]):
                if od_df['label'][i] == super_class_df['person'][j]:
                    od_df['label'][i] = super_class_df['person.3'][j]

        # number_of_label_first_3_frame
        # max area percent
        count = 0
        max_area = []
        for num in range(od_df.shape[0]):
            if od_df['frame'][num] == 1 or od_df['frame'][num] == 2 or od_df['frame'][num] == 3:
                count = count + od_df['count'][num]

            max_area.append(od_df['area_percentage'][num])

        number_of_label_first_3_frame = count
        max_area_percentage = max(max_area)

        # most_occured_label_first_3_frame_number
        temp_df = od_df[od_df['frame']<4]
        temp_df_label = Counter(temp_df['label'])
        most_occured_label_first_3_frame_number = max(list(temp_df_label.values()))

        # most_occured_label_number
        most_occured_label_number = max(list(Counter(od_df['label']).values()))

        return (max_area_percentage, \
        most_occured_label_number, number_of_label_first_3_frame, \
        most_occured_label_first_3_frame_number)
    else:
         return (None, \
        None, None, \
        None)

def main():
    """ NEWJPLUS: FACEBOOK VIEWS PREDICTION MODEL"""
    st.title('TURING: NEWJ PREDICTION MODEL')
    menu = ["About", "How To Use Turing","Prediction", "Feedback"]
    choice = st.sidebar.selectbox('MENU', menu)
    golden = pd.read_csv("data/turing_data.csv")

    # Basic information about the project
    if choice == 'About':
        st.subheader("1. ABOUT:")
        st.text('Turing is views prediction model for NewjPlus Facebook page')
        st.image("images/newj_fb_page.png", width= 600)
        st.subheader("2. OBJECTIVE:")
        st.text('The objective is to predict views, the video can get over seven days from the date,\nthe video got published.')
        st.image("images/newj_fb_views.png", width=600)
        st.subheader("3. HOW TURING WORKS:")
        st.text('The prediction model is trained on 861 videos. The model predicts views based on several\n'
                'parameters. Each parameter is important to predict views, so giving correct input\n'
                'is very important to get an accurate prediction. Model try to predict views for the\n'
                'given combinations from user based on data on which it is trained.')

    elif choice == 'How To Use Turing':
        st.subheader("**1. Primary Category**")
        st.markdown("**Government:** All about Government's rules, announcements, policies, decisions, economy, budget and any such news")
        st.markdown("**Global news:** Any news/ info about the world is a part of this category. ")
        st.markdown("**Technology & Innovations:** This includes Science, Technology and Innovation related news, information, updates and anything that has science in it.")
        st.markdown("**Sports & Games:** All about the news, updates awards, achievements,  national/international tournaments or players in any sport or game. Life journey of a well known or budding sportsmen or player. Any information about rules/decisions in sports/games.")
        st.markdown("**Politics:** Everything that has info about a political party/individual and elections")
        st.markdown("**Entertainment:** All about Entertainment industry, bollywood, regional, television, digital. Also includes the videos of common people who are entertaining us through some dance or song")
        st.markdown("**Environment/Ecosystem:** All about flora-fauna, conservation, crisis,pollution, cleaning the surroundings and waste management. Any news or updates or stories about social/volunteer work for environment or wildlife/pets/street animals")
        st.markdown("**Lifestyle:** All about the way of living, religion, culture, sexuality,economy, philisophy,beliefs etc")
        st.markdown("**Places:** All the stories/ info about any place like city, country, or village. It also includes anything related to a religious/historical place.")
        st.markdown("**Judiciary & Crime:** All about judicial system, laws, policies, rules, norms, crime, violations, violence, court ruling, cases etc or any information about anyone or anything that's a part of judicial system or crime")
        st.markdown("**Rare:** Any other categories will fall into rare")

        st.subheader("**2. Video Type**")
        st.markdown("**Emotions:** 'funny', 'emotional', 'shocking/surprising', and 'scary' type of videos will fall into emotions")
        st.markdown("**Rare:** All other categories than 'informative', 'inspiring', 'explainers', 'day-specific' and 'emotions' will fall into Rare")

        st.subheader("**3. Background Music In First 3 Seconds**")
        st.markdown("**No Music:** If the background music is not starting in first 3 seconds then we call it as 'no music")
        st.markdown("**Relevant:** If the background music is matching with video then call it as relevant")
        st.markdown("**Low, Loud and Neutral:** If the background music is not relevant to the video then it can fall into 'Low', 'Loud' and 'Neutral' based on the loudness of the music")

        st.subheader("**4. Voice In First 3 Seconds**")
        st.markdown("**Text Only:** If the video do not have any voice in first 3 seconds but it consist of text then we call it as 'text only'")
        st.markdown("**Common Voice:** If the video consist of human voice in first 3 seconds and voice is not of the famous personality then it is a 'common voice'")
        st.markdown("**Voice Of Famous Personality:** If the video have voice of famous personality in first 3 seconds.")
        st.markdown("**Other:** If the video start with voice of 'crowd', 'animals', 'nature' then it falls into 'other' category")
        st.markdown("**Rare:** Anything else than above mentioned categories will fall into 'rare'")

        st.subheader("**5. Thumbnail**")
        st.markdown("**Rare:** If the thumbnail does not contain 'Object', 'Crowd', 'Famous Personality', or 'Commoner' then it is thumbnail.")


    # Prediction
    elif choice == 'Prediction':
        # dictionary of encoded variables
        d_primary = {'sports & games': 0,
                       'government': 1,
                       'global news': 2,
                       'technology & innovations': 3,
                       'politics': 4,
                       'places': 5,
                       'environment/ecosystem': 6,
                       'rare': 7,
                       'entertainment': 8,
                       'lifestyle': 9,
                       'judiciary & crime': 10}


        # OD
        basepath = '.'

        st.set_option('deprecation.showfileUploaderEncoding', False)

        st.header("stream app")

        def clean_cache():
            with st.spinner("Cleaning....."):
                os.system(f'rm {basepath}/*mp4')

########################################################################################
        if st.button(label="Clean cache"):
            clean_cache()
        
        file = st.file_uploader("Upload file", type=["mp4"])
        
        show_f = st.empty()

        global od_df
        od_df = None

        if not file:
            pass
            # show_f.info("Upload file")
        
        else:
            if isinstance(file, BytesIO):
                show_f.video(file)
        
                # os.system(f'rm *mp4')
                # file_name = time.strftime("%Y%m%d-%H%M%S")
                # file_name_static = copy.deepcopy(file_name)
        
                with open(f'{basepath}/file_tmp.mp4', 'wb') as f:
                    f.write(file.read())
            if st.button(label="Upload BLOB"):
                push_blob_f(video_id='file_tmp', container='var', basepath='.')

            if st.button(label="Get OD results"):
                # st.text(f'{file_name}')
                r = requests.post("http://52.226.46.64:5000",
                                json={'ID': 'file_tmp', 'FPS': '1', 'duration': '5', 'lang': '',
                                        'container': 'var'})
                
                od_df = odasdf(literal_eval(r.text))
                od_df

########################################################################################
        res = od_feature(od_df)
        max_area_percentage, most_occured_label_number, number_of_label_first_3_frame,most_occured_label_first_3_frame_number = res
        
        st.text(f'{max_area_percentage, most_occured_label_number, number_of_label_first_3_frame,most_occured_label_first_3_frame_number}')
        # Take user input GOLDEN DATA
        primary = st.selectbox('Primary Category', tuple(d_primary.keys()))

        # Retreive data from FB API
        published_date = st.date_input('Video Publishing Date')
        # st.text(type(published_date))
        # Any production date after today will be consider as today only
        def correct_date(date_):
            if date_ > (datetime.now()).date():
                return (datetime.now()).date()
            elif date_ < date(2019, 3, 18):
                return date(2019, 3, 18)
            else:
                return date_

        published_date = correct_date(published_date)
        #st.write(published_date)

        last_day_features = ['last_day_page_fan_adds_by_paid_non_paid_unique_paid',
                             'last_day_page_impressions_unique',
                             'last_day_page_posts_impressions_nonviral',
                             'last_day_page_posts_impressions_nonviral_unique',
                             'last_day_page_actions_post_reactions_like_total',
                             'last_day_page_actions_post_reactions_wow_total',
                             'last_day_page_actions_post_reactions_anger_total',
                             'last_day_page_fan_removes_unique',
                             'last_day_page_video_repeat_views',
                             'last_day_page_video_complete_views_30s_autoplayed']

        # last_seven_day_features = ['last_7_days_page_fan_adds_by_paid_non_paid_unique_unpaid', 'last_7_days_page_impressions_nonviral',
        # 'last_7_days_page_impressions_nonviral_unique', 'last_7_days_page_posts_impressions_nonviral_unique',
        # 'last_7_days_page_actions_post_reactions_wow_total', 'last_7_days_page_actions_post_reactions_sorry_total',
        # 'last_7_days_page_fans', 'last_7_days_page_fan_removes_unique', 'last_7_days_page_video_complete_views_30s_repeat_views']

        last_day_features_values = []
        last_seven_day_features_values = []

        # read the page data from database
        page_sql = 'SELECT * FROM fb.pageinsightsdaily where pageName = "NEWJPLUS"'
        ld_df = pd.read_sql(page_sql, cnx)

        # last day features extraction
        for feature in last_day_features:
            last_day_features_values.append(
                (ld_df[ld_df['consolidated_end_time'] == published_date - timedelta(days=1)][feature[9:]]).reset_index(
                    drop=True)[0])
            cursor.close()

        # last seven days features extraction
        # for feature in last_seven_day_features:
        #     value = 0
        #     for i in range(1,8):
        #         value = value + (ld_df[ld_df['consolidated_end_time'] == published_date - timedelta(days=i)][feature[12:]]).reset_index(
        #             drop=True)[0]
        #     last_seven_day_features_values.append(value)
        #     cursor.close()

        # GET VALUES FOR EACH INPUT
        k_primary = get_value(primary, d_primary)

        # RESULT OF USER INPUT

        vectorized_result = [max_area_percentage,
                            most_occured_label_number, number_of_label_first_3_frame,
                            most_occured_label_first_3_frame_number, k_primary] + last_day_features_values
        st.text(vectorized_result)
        # st.text(vectorized_result)
        # global sample_data 
        sample_data = np.array(vectorized_result).reshape(1, -1)
        sample_data_cp = sample_data.copy()
        st.text(sample_data)
        # st.write(sample_data)


        # from sklearn.preprocessing import MinMaxScaler

        #tr = load_transformer("models/pkl_transform_1.pkl")
       #  transformed_sample_data = tr.transform(pd.DataFrame(data = sample_data, columns= ['visual_first_3_seconds', 'background_music_type_first_3_seconds',
       # 'Primary_Category_1_grouped', 'voice_first_3_seconds_grouped',
       # 'thumbnail_1_grouped', 'time_distribution',
       # 'last_day_page_fan_adds_by_paid_non_paid_unique_total',
       # 'last_day_page_fan_adds_by_paid_non_paid_unique_unpaid',
       # 'last_day_page_impressions_paid',
       # 'last_day_page_impressions_paid_unique',
       # 'last_day_page_posts_impressions_paid',
       # 'last_day_page_posts_impressions_viral',
       # 'last_day_page_posts_impressions_nonviral_unique',
       # 'last_day_page_actions_post_reactions_haha_total', 'last_day_page_fans',
       # 'last_day_page_video_complete_views_30s_repeat_views',
       # 'last_7_days_page_negative_feedback_by_type_hide_clicks',
       # 'last_7_days_page_impressions_nonviral_unique',
       # 'last_7_days_page_posts_impressions_nonviral_unique',
       # 'last_7_days_page_fans', 'last_7_days_page_fan_removes',
       # 'last_7_days_page_fan_removes_unique',
       # 'last_7_days_page_video_complete_views_30s_repeat_views']))


        # print(transformed_sample_data)
        # st.write(transformed_sample_data)

        if st.button("Make Prediction"):
            st.text(sample_data_cp)
            #prediction_label = {"low": 0, "average": 1, 'high': 2}
            model_predictor = load_model_n_predict("models/classification_ada_15_newjplus.pkl")
            prediction = model_predictor.predict(sample_data_cp)
            # st.text(prediction)
            #final_result = get_key(prediction, prediction_label)
            st.success("Predicted video category is --> {}".format(prediction[0].upper()))
            st.write('Low: 0-12800')
            st.write('Average: 12801-39000')
            st.write('High: Any number of views above 39000')

    else:
        feedback = st.subheader('For any feedback/suggestion,\nkindly email to [Yogeshwar Thosare] (mailto:yogeshwar.thosare@thenewj.com) or slack [@yogeshwar] (https://app.slack.com/client/TEERTFU84/DRPJGCL81)')



if __name__ == '__main__':
    main()