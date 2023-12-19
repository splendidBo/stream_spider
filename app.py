import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import altair as alt
from collections import Counter
from wordcloud import WordCloud
from streamlit_echarts import st_pyecharts
import jieba
from pyecharts.charts import WordCloud as PyWordCloud

#根据给定的URL爬取网页内容，并统计网页中出现的中文词汇的次数。
def crawl_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()#使用response.raise_for_status()检查响应状态码，如果状态码不是200，则会抛出异常。
    response.encoding = 'utf-8'#设置响应的编码格式为utf-8，以确保正确解析中文文本。

    text_content = response.text#使用response.text获取网页内容，将其赋值给变量text_content。
    # 使用正则表达式模式r"[\u4E00-\u9FA5]+"匹配中文字符，将匹配结果保存在列表matches中。
    pattern = r"[\u4E00-\u9FA5]+"
    #使用Counter(matches)
    #对列表matches进行计数，生成一个字典counts，其中键是中文词汇，值是它在网页中出现的次数。
    matches = re.findall(pattern, text_content)
    counts = Counter(matches)
    return counts

def generate_wordcloud(counts):
    #list(counts.keys())将计数结果字典的键（中文词汇）转换为列表words，用于后续生成词云图。
    words = list(counts.keys())
    #使用列表推导式[(word, counts[word]) for word in words]，遍历列表words，将每个词汇和对应的出现次数构成元组，并保存在列表word_counts中。
    word_counts = [(word, counts[word]) for word in words]
   #创建PyWordCloud对象wordcloud，用于生成词云图。
    wordcloud = PyWordCloud()

    # ，word_counts为词汇和出现次数的列表，word_size_range=[20, 100]设置词云图中词汇的大小范围。
    wordcloud.add("", word_counts, word_size_range=[20, 100])
   #将词云图对象传递给st_pyecharts函数，用于在Streamlit应用程序中显示词云图
    st_pyecharts(wordcloud)

def main():
    st.title("静态网页爬虫")
    url = st.text_input("请输入网址：")

    if url:
        try:
            #调用crawl_webpage(url)函数，将爬取网页并统计词汇次数的结果保存在变量word_count中。
            word_count = crawl_webpage(url)
            #将word_count字典的键转换为列表words，保存词汇

            words = list(word_count.keys())
            # 将word_count字典的值转换为列表counts，保存词汇出现的次数。
            counts = list(word_count.values())
            #使用Pandas库创建一个数据框df，其中word列保存词汇，count列保存词汇出现的次数。
            df = pd.DataFrame({'word': words, 'count': counts})
            #获取出现次数最多的前15个词汇，并更新数据框df。
            df = df.nlargest(15, 'count')
            #使用Streamlit库创建一个下拉选择框，让用户选择要展示的图表类型，并将用户选择的结果保存在变量chart_type中。
            chart_type = st.selectbox('请选择图表类型：', ['饼图', '条形图', '折线图', '词云'])

            if chart_type == '饼图':
                #创建一个使用Altair库绘制饼图的图表，并将其赋值给变量chart
                chart = alt.Chart(df).mark_arc().encode(
                    color=alt.Color('word:N', scale=alt.Scale(scheme='category20b')),
                    angle='count',#：设置饼图角度
                    tooltip=['word', 'count']#设置鼠标悬停在饼图上时显示的提示信息，使用Altair库的tooltip参数，并指定显示word和count列的值。
                ).properties(
                    width=600,
                    height=400,
                    title="页面关键字分布"
                )

            elif chart_type == '条形图':
                #创建一个使用Altair库绘制条形图的图表，并将其赋值给变量chart
                chart = alt.Chart(df).mark_bar().encode(
                    x='count:Q',#设置条形图的横轴，
                    y=alt.Y('word:N', sort='-x'),#设置条形图的纵轴，使用Altair库的y参数，以word列作为纵轴，并按照横轴倒序排列。
                    tooltip=['word', 'count']
                ).properties(
                    width=1200,
                    height=800,
                    title="页面关键字数量"
                )

            elif chart_type == '折线图':
                chart = alt.Chart(df).mark_line().encode(
                    x='word:N',
                    y='count:Q',
                    tooltip=['word', 'count']
                ).properties(
                    width=800,
                    height=600,
                    title="页面关键字趋势"
                )

            elif chart_type == '词云':
                generate_wordcloud(word_count)
                return

            st.altair_chart(chart)

        except requests.exceptions.RequestException as e:
            st.error(f"发生错误：{e}")

if __name__ == "__main__":
    main()
