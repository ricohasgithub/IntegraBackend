import json
import os
import requests as r
from base64 import b64encode
import sys
from google.cloud import language_v1
from google.cloud.language_v1 import enums

import random

import pyrebase

# Load all ML dependencies
import numpy as np

from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec

import spacy

w2vmodel = Word2Vec.load("word2vec.model")
# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

client = language_v1.LanguageServiceClient()
type_ = enums.Document.Type.PLAIN_TEXT

def read_google_api_key():
	key = 'AIzaSyAkuoqnoU1cPWV1vhvjSfe-0IxtmO7pBLg'

# Configuration key for realtime database with all permission (read + write) to true
config = {
    "apiKey": "AIzaSyDUNr8QUe_7DJq_kkQojAO1cMz_BQHP6dM",
    "authDomain": "integra-e5643.firebaseapp.com",
    "databaseURL": "https://integra-e5643.firebaseio.com",
    "storageBucket": "integra-e5643.appspot.com",
}

# Initialize the "pyrebase" and retrieve the realtime database
firebase = pyrebase.initialize_app(config)
firebase_db = firebase.database()

# This will be set to some user account
username = "ricozhuthegreat"

w2vresponse = "Hello World!"

# This function takes in the body paragraphs and a list of overall essay topics and identifies the most key (aka topic) sentence in the pararaphs
def fetch_topic(body, str_response_gc_list):

    # Get every sentence from the body paragraphs
    sentences = body.split('.')

    max_sim_score = -10.0
    max_sim_sent = ""

    # Iterate thorugh every sentence and get its w2v spaces
    for sentence in sentences:

        # This variable stores the current similarity score for the current sentence
        c_sim_score = 0.0

        sentence_arr = sentence.split(' ')

        # Iterate through every word in the sentence and find its cosine differences from the topics
        for word in sentence_arr:

            # Iterate through every topic predicted by GC for the overall composition
            for topic in str_response_gc_list:

                topic = str(topic)

                try:
                    c_sim_score = c_sim_score + w2vmodel.similarity(word, topic)
                except:
                    print("Topic word not found; uncompatible with w2v")

        # At the end of every sentence, update if its the most similar

        print("SCORE", max_sim_score)
        if c_sim_score > max_sim_score:
            max_sim_score = c_sim_score
            max_sim_sent = sentence

    # Return the most relevant topic sentence
    print(max_sim_score)
    print("MAX SENTENCE", max_sim_sent)
    return max_sim_sent

# Rephrase nouns into question (no verbs)
def sendMessage(num, word):
    if num == 0:
        return "What is your stance or belief about " + word + "?"
    elif num == 1: 
        return "What are some common misconceptions about " + word + "?"
    elif num == 2: 
        return "What's an example of " + word + " done properly?"
    elif num == 3:
        return "How is " + word + " changing over time?"
    elif num == 4:
        return "Why is "+ word + " so important?"
    elif num == 5:
        return "What are the pros and cons about " + word + "?"
    elif num == 6: 
        return "Elaborate on " + word
    elif num == 7: 
        return "What is the importance of " + word + "?"
    elif num == 8:
        return "How does " + word + " affect you?"
    else:
        return ""

def stream_handler(message):

    print(message["event"]) # put
    print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

    title = message["data"]["title"].lower()
    body = message["data"]["body"].lower()

    text_content = body

    language = "en"
    document = {"content": text_content, "type": type_, "language": language}

    response = client.classify_text(document)

    print(text_content)

    str_response = ""

    for category in response.categories:
        print(u"Topic Prediction {}".format(category.name))
        print(u"Confidence Level: {}".format(category.confidence))
        str_response = str_response + category.name

    try:
        w2vresponse = w2vmodel.wv.most_similar (positive=title, topn=1)
    except:
        print("An exception occurred")
        w2vresponse = ""

    str_response_gc_list1 = str_response.split('/')

    str_response_gc_list = []

    # Some words have a & seperating it
    for topic in str_response_gc_list1:

        topic = topic.lower()

        if " & " in topic:
            new_list = topic.split(" & ")
            for itm in new_list:
                str_response_gc_list.append(itm)
        else:
            str_response_gc_list.append(topic)

    print("LIST: ", str_response_gc_list)

    # Identify critical topic sentence (one sentence that best summarizes the currently discussed topics)
    topic_sentence = fetch_topic(body, str_response_gc_list)

    print(topic_sentence)

    doc = nlp(topic_sentence)

    nouns = [chunk.text for chunk in doc.noun_chunks]
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

    print(nouns)
    print(verbs)

    message = ""

    if len(verbs) > 0:

        noun_to_sort = []
        ave_confs_to_sort = []

        # Find noun with highest confidence/relation to the main topic from word2vec
        for word in nouns:

            tot_conf = 0.0

            # Iterate through every topic predicted by GC for the overall composition
            for topic in str_response_gc_list:

                topic = str(topic)

                try:
                    tot_conf = tot_conf + w2vmodel.similarity(word, topic)
                except:
                    print("Topic word not found; uncompatible with w2v")

            noun_to_sort.append(word)
            # "Hash" the confidence level to the noun
            ave_confs_to_sort.append(tot_conf/len(str_response_gc_list))

        # Max index
        max_index = ave_confs_to_sort.index(max(ave_confs_to_sort))

        conf_noun = noun_to_sort[max_index]

        message = sendMessage(random.randint(0, 8), conf_noun)

    print(message)

    firebase_db.child("users").child(username).child("read").set(
        {
            "message": message,
            "topics": str_response
        }
    )  

# Get the datastream from the realtime database
data_stream = firebase_db.child("users").child(username).child("post").stream(stream_handler)