import json
import os
import requests as r
from base64 import b64encode
import sys
from google.cloud import language_v1
from google.cloud.language_v1 import enums

#Text must be at least 20 words long for an accurate classification.
text_content = 'the computer is one of the most wonderful inventions of modern technology. It is fairly a recent invention. It has now become a part and parcel of day-to-day life. The computer was invented by an English mathematician called Charles Babbage. Computers are two basic types: analog and digital. Analog: computers deal with physical qualities and digital computers deal with numbers. Computers have five major components; input, store, control, processing, and output.'

client = language_v1.LanguageServiceClient()
type_ = enums.Document.Type.PLAIN_TEXT
        
language = "en"
document = {"content": text_content, "type": type_, "language": language}

response = client.classify_text(document)

print(text_content)

for category in response.categories:
        print(u"Topic Prediction {}".format(category.name))
        print(u"Confidence Level: {}".format(category.confidence))

def read_google_api_key():
	key = 'AIzaSyAkuoqnoU1cPWV1vhvjSfe-0IxtmO7pBLg'
