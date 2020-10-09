import os
import io
from io import BytesIO, StringIO
import time
from push_blob import push_blob_f
import streamlit as st

basepath = '.'

st.set_option('deprecation.showfileUploaderEncoding', False)

st.header("stream app")

def clean_cache():
    with st.spinner("Cleaning....."):
        os.system(f'rm {basepath}/*mp4')


if st.button(label = "Clean cache"):
    clean_cache()

file = st.file_uploader("Upload file", type=["mp4"])

show_f = st.empty()

if not file:
    pass
    # show_f.info("Upload file")

else:
    if isinstance(file, BytesIO):
        show_f.video(file)
        
        # os.system(f'rm *mp4')
        file_name = time.strftime("%Y%m%d-%H%M%S")

        with open(f'{basepath}/{file_name}.mp4','wb') as f:
            f.write(file.read())
    if st.button(label="Upload BLOB"):
        push_blob_f(video_id= file_name, container='var', basepath= '.')
