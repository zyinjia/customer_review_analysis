from nltk.corpus import stopwords # Import the stop word list
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
import re
import random


stopwords = stopwords.words("english")
stopwds = set(stopwords)
stopwds.discard('no')
stopwds.discard('not')
stopwds.discard('nor')


def get_data(path='./data_bagofwords/data.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    df = df.drop('Unnamed: 0', 1)
    df = df[df.Reviews.notnull()]
    return df


def clean_text(text):
    text = text.decode('utf-8').lower()
    text_letter_only = re.sub("[^a-zA-Z0-9]", " ", text)
    words = text_letter_only.split()
    meaningful_words = [w for w in words if not w in stopwds]
    return " ".join(meaningful_words)


def split_df(df, train_size=20000, test_size=2000, predict_size=2000):
    '''
    randomly select the training dataset, test dataset and predict dataset
    df: the complete pandas.dataframe
    '''
    indices = random.sample(df.index, 
                            train_size + test_size + predict_size)
    df_select = df.ix[indices]
    df_train = df_select[:train_size]
    df_test = df_select[train_size:train_size+test_size]
    df_predict = df_select[train_size+test_size+predict_size:]
    return df_train, df_test, df_predict


def get_train_features_bw(reviews_train, vectorizer):
    '''
    - reviews: a list of reviews text
    - sample vectorizer (sklearn):
        vectorizer = CountVectorizer(analyzer = "word",\
                                 tokenizer = None,    \
                                 preprocessor = None, \
                                 stop_words = None,   \
                                 max_features = 5000)
        - vectorizer is fitted in this function
    '''
    train_features = vectorizer.fit_transform(reviews_train)
    train_features = train_features.toarray()
    #vocab = vectorizer.get_feature_names() #get vocabulary
    return train_features


def get_test_features_bw(reviews_test, vectorizer):
    test_features = vectorizer.transform(reviews_test)
    test_features = test_data_features.toarray()
    return test_features

def get_similarity_matrix(train_features_normalized):
    n = train_features_normalized.shape[1]
    sim_matrix = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            if j >= i:
                sim_matrix[i, j] = np.dot(train_features_normalized[i], train_features_normalized[j])
            else:
                sim_matrix[i, j] = sim_matrix[j, i]
    return sim_matrix