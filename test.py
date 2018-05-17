import os

import anago
from anago.reader import load_data_and_labels, load_glove

from gensim.models.keyedvectors import KeyedVectors

import numpy as np

DATA_ROOT = os.path.join(os.path.dirname(__file__), '/home/mercue/data/ch')
EMBEDDING_PATH = '/opt/nfs/nlu_system_data/data/vectors.txt.word2vec'

train_path = os.path.join(DATA_ROOT, 'train.txt')
valid_path = os.path.join(DATA_ROOT, 'train.txt')

print('Loading data...')
x_train, y_train = load_data_and_labels(train_path)
x_valid, y_valid = load_data_and_labels(valid_path)
print(len(x_train), 'train sequences')
print(len(x_valid), 'valid sequences')

embedding = KeyedVectors.load_word2vec_format(EMBEDDING_PATH,binary=False)

model = {}
for word in embedding.vocab:
    wv = embedding.word_vec(word)
    vector = np.array(wv)
    model[word] = vector

# Use pre-trained word embeddings
model = anago.Sequence(batch_size=1, word_emb_size=150, embeddings=model)
model.train(x_train, y_train, x_valid, y_valid)
token_list = "唐納·川普 的 父親 佛瑞德·川普 在 美國 紐約 市 出生 ， 是 一個 美國 房地產 開發 者 ， 而 母親 瑪麗·安妮·麥唐納·川普 是 來自 英國 蘇格蘭 的 移民 ， 她 在 蘇格蘭 路易斯島 出生 ， 是 一名 家庭主婦 。".split()
matches = model.analyze(token_list)
print(matches)