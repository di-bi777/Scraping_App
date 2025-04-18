import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from pathlib import Path
from io import BytesIO
import zipfile
import time
from janome.tokenizer import Tokenizer
import os

def get_links(url):
    """ブログの各ページのリンクを取得する"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # <header>タグを特定し、その範囲を除外
    header = soup.find('header', class_='p-header p-header--full-width')
    if header:
        header.extract() 
    links = []
    for a_tag in soup.find_all('a', href=True, class_=lambda x: x and 'notion-page-link' in x):
        links.append(a_tag['href'])
    return links


def get_content(url):
    """各ページのコンテンツを取得する"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    #いらない部分を除去
    header = soup.find('header', class_='p-header p-header--full-width')
    if header:
        header.extract() 
    contents = ''
    callout = soup.find('div', class_=lambda y: y and 'notion-callout' in y)
    if callout:
        callout.extract()
    
    for a_content in soup.find_all(class_=lambda z: z and 'notion-text' in z):
        contents += a_content.text
    return contents

def tokenize_text(text):
    """テキストを形態素解析してトークン化する"""
    t = Tokenizer()
    tokens = t.tokenize(text)
    words = ' '.join([token.base_form for token in tokens if token.part_of_speech.startswith('名詞')])
    return words

def font(number):
    """フォントを指定させる"""
    st.write(f"{number}. ワードクラウド作成のため、日本語のフォントパスを指定する必要があります")
    choice = st.selectbox("パス指定方法を選択してください", ["自分で入力して開始", "自動でダウンロードして開始"])

    if choice == "自分で入力して開始":
        font_path = st.text_input("フォントパスを入力し、Enter")
        if font_path:
            if not os.path.isfile(font_path):
                st.error("フォントパスが正しくありません。もう一度確認してください。")
        st.markdown("<br>", unsafe_allow_html=True)
        button2 = st.button("ワードクラウド作成開始")
        if button2:
            return font_path
        
        
    else:
        button1 = st.button("自動でGoogle Fontsからフォントをダウンロードして開始")
        st.write("※一度このボタンでフォントをダウンロードしている場合、ボタンを押すと2度目のダウンロードはせずにそのままワードクラウド作成に移行します")
        st.write("※ダウンロードリンク：https://noto-website-2.storage.googleapis.com/pkgs/NotoSansCJKjp-hinted.zip")
        if button1:
            font_url = 'https://noto-website-2.storage.googleapis.com/pkgs/NotoSansCJKjp-hinted.zip'
            font_path = Path('noto_fonts/NotoSansCJKjp-Regular.otf')
            placeholder1 = st.empty()
            
            if  font_path.exists():
                return font_path
                
            if not font_path.exists():
                # フォントファイルをダウンロード
                placeholder1.text("フォントダウンロード中...")
                response = requests.get(font_url)
                font_zip = BytesIO(response.content)

                # ZIPファイルを解凍してフォントファイルを取得
                with zipfile.ZipFile(font_zip, 'r') as zip_ref:
                    zip_ref.extractall('noto_fonts')
                placeholder1.empty()
                return font_path  

def reset():
    """ワードクラウドの図を消す"""
    st.session_state["wordcloud"] = None
        

def make_wordcloud(text, font, option):
    """ワードクラウド生成"""
    holder = st.empty()
    holder.text("ワードクラウド作成中...")
    
    #形態素解析
    tokenized_content = tokenize_text(text)
    
    #ストップワード設定
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update(["こと", "の", "よう", "私", "ここ", "ため", "もの", "これ", "それぞれ", "的", "方", "https", "検索", "結果", "さん", "たち", "ところ", "そこ", "それ", "こちら"])      
    
    #ワードクラウド生成
    try:
        wordcloud = WordCloud(stopwords= custom_stopwords, width=800, height=400, background_color='white', font_path = str(font)).generate(tokenized_content)
        st.session_state["wordcloud"] = wordcloud
    except OSError as e:
        if "unknown file format" in str(e):
            st.error("指定されたファイルはフォントファイルではない可能性があります。フォントファイルを確認してください。")
        else:
            st.error(f"ワードクラウドの生成中にエラーが発生しました: {e}")
    except ValueError as e:
        if "We need at least 1 word to plot a word cloud" in str(e) and option == option2:
            st.error("選ばれたCSVの列にテキストが含まれていないため、ワードクラウドが作成できません。")
        else:
            st.error(f"ワードクラウドの生成中にエラーが発生しました: {e}")
    except Exception as e:
        st.error(f"ワードクラウドの生成中にエラーが発生しました: {e}")
        
    reset_button = st.button("リセット")
    if reset_button:
            reset()
            st.write("リセットされました")
    
    # ワードクラウドを表示
    if "wordcloud" in st.session_state and st.session_state["wordcloud"] is not None:
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        holder.empty()
     


# タイトル
st.title("スクラムサイン　トピック分析")
st.write("スクラムサインのホームページから情報を取得してワードクラウドを作成します")
st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    #ワードクラウド作成方法の選択
    option1 = "スクレイピングでデータを取得し、ワードクラウドを生成"
    option2 = "CSVファイルからデータを取得し、ワードクラウドを生成"

    main_choice = st.radio(
        "1．どちらの方法で行いますか？", 
        [f"***{option1}***", f"***{option2}***"],
        captions=[
            "スクラムサインホームページにアクセスし、スクレイピングを行って情報を取得し、ワードクラウドを作成します",
            "CSVファイルからデータを取得し、ワードクラウドを作成します"])
    
#空白
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

font_path = False

#スクレイピングでデータ取得し、ワードクラウド生成
if main_choice == f"***{option1}***":
    
    sub_choice = st.selectbox("2．どちらを分析しますか？", ["ブログ記事", "お客様の声"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    font_path = font(3)
    
    if font_path:    
        
        main_url = 'https://scrumsign.com'
        
        if sub_choice == "ブログ記事":
            url = main_url + "/blog"
        else:
            url = main_url + "/voice"
        
        #全リンク取得
        links = get_links(url)
        
        all_content = ''
        
        #プログレスバー
        progress_placeholder = st.empty()
        bar_text = st.empty()
        bar = progress_placeholder.progress(0) 
        
        #各リンクにアクセスして内容取得
        for i, link in enumerate(links):
            full_link = "https://scrumsign.com" + link
            all_content += get_content(full_link)
            
            # プログレスバーの更新
            progress = (i + 1) / len(links)
            bar.progress(progress)
            bar_text.text(f"記事取得中・・・　{i + 1}/{len(links)}")
            
            time.sleep(3)
        
        st.write("記事取得完了")
        progress_placeholder.empty()
        bar_text.empty()
        
    
            #ワードクラウド作成
        make_wordcloud(all_content, font_path, option1)   
        
        
        
    


elif main_choice == f"***{option2}***":

    st.markdown("<br>", unsafe_allow_html=True)
    
    csv_file = st.file_uploader("2．CSVファイルをアップロードしてください", type="csv")
    
    if csv_file is not None:
        # CSVファイルをデータフレームに読み込む
        df = pd.read_csv(csv_file, header=None)
        st.markdown("<br>", unsafe_allow_html=True)
        
        #入力されたファイルを表示
        st.write("あなたが入力したファイル")
        st.write(df)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # テキストデータの列を選択
        text_column = st.selectbox("3．テキストデータの列を選択してください", df.columns)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        font_path = font(4)
           
        if font_path:
            # ワードクラウドの生成
            text = " ".join(df[text_column].dropna().astype(str).tolist())
            make_wordcloud(text, font_path, option2)
            
