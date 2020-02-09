import pyrebase

# Load all ML dependencies
import numpy as np

from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec

w2vmodel = Word2Vec.load("word2vec.model")

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

response = "Hello World!"

def stream_handler(message):

    print(message["event"]) # put
    print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

    title = message["data"]["title"].lower()
    body = message["data"]["body"].lower()

    try:
        response = w2vmodel.wv.most_similar (positive=title, topn=1)
    except:
        print("An exception occurred")
        response = ""

    firebase_db.child("users").child(username).child("read").set(
        {
            "message": response
        }
    )  

# Get the datastream from the realtime database
data_stream = firebase_db.child("users").child(username).child("post").stream(stream_handler)