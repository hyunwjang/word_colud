import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageFont


   
st.subheader("뉴스기사 제목 워드클라우드")     
news_num =  st.number_input('페이지수', 100)
query  = st.text_input('네이버 검색어','')
# news_num  = 100
#news_num =  st.number_input(뉴스기사 수, value)

date = str(datetime.now())
date = date[:date.rfind(':')].replace(' ', '_')
date = date.replace(':','시') + '분'


# query = input('검색 키워드를 입력하세요 : ')
# news_num = int(input('총 필요한 뉴스기사 수를 입력해주세요(숫자만 입력) : '))
query = query.replace(' ', '+')


news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}'

req = requests.get(news_url.format(query))
soup = BeautifulSoup(req.text, 'html.parser')


news_dict = {}
idx = 0
cur_page = 1

while idx < news_num:
### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###
    
    table = soup.find('ul',{'class' : 'list_news'})
    li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
    area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
    a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
    
    for n in a_list[:min(len(a_list), news_num-idx)]:
        news_dict[idx] = {'title' : n.get('title'),
                          'url' : n.get('href') }
        idx += 1

    cur_page += 1

    pages = soup.find('div', {'class' : 'sc_page_inner'})
    next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')
    
    req = requests.get('https://search.naver.com/search.naver' + next_page_url)
    soup = BeautifulSoup(req.text, 'html.parser')
df = pd.DataFrame(news_dict).T

st.write(query,"  ", str(news_num)+ "개" )

#st.dataframe(df.style.highlight_max(axis=0))

# st.write("st.table api")
# st.table(df)
from wordcloud import WordCloud

df_2 = df.drop(['url'], axis = 1)
from sklearn.feature_extraction.text import CountVectorizer

cvect = CountVectorizer()
dtm = cvect.fit_transform(df["title"])

feature_names = cvect.get_feature_names_out()
df_4 = pd.DataFrame(dtm.toarray(), columns=feature_names)
df8 = pd.DataFrame(df_4.sum())
df8.reset_index(inplace=True)
# print(df8)
df8.columns = ['title', 'count']
df_1 = df8
# print(df_1)
wc = df_1.set_index('title').to_dict()['count']

font = 'MALGUN.TTF'
#font = ImageFont.load("arial.pil")
#font = 'C:\Windows\Fonts\HMFMPYUN.ttf'
wordCloud = WordCloud(font_path=font,
                      width=400, height=400, 
                      scale=2.0,
                      max_font_size=250).generate_from_frequencies(wc)
fig = plt.figure()
plt.imshow(wordCloud)
plt.axis("off")
plt.show()
st.pyplot(fig)

