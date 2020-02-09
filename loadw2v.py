
import numpy as np

from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec

model = Word2Vec.load("word2vec.model")

w1 = "angry"
print(model.wv.most_similar (positive=w1))