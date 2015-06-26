
###############################################################################
# Model application
###############################################################################

import os
import re
import numpy as np
from bs4 import BeautifulSoup

from app.vietseg.makevec import make_vec
import app.vietseg.network as network



# Replace this with your model's result
net_dir = os.path.abspath(os.path.dirname(__file__))
JSON = os.path.join(net_dir,
                    '30hidden-30epochs-10batch-0.5eta-5.0lambda-7window-100shape-3run.net')
net = network.load(JSON)


def _get_iob(arr):
    d = {0: 'i', 1: 'o', 2: 'b'}
    n = np.argmax(arr)
    return d[n]

def _classify(token_list):
    "Classify a list of token"
    result = []
    sen_vec = make_vec(token_list)
    for x in sen_vec:
        result.append(_get_iob(net.feedforward(x)))
    return result

def _make_words(token_list, iob_list):
    "Make segmented words from token list and corresponding iob list"
    if not iob_list: return
    t = token_list[0:1]
    tokens = []
    for i in range(1, len(iob_list)):
        if iob_list[i] == 'i':
            t.append(token_list[i])
            continue
        if iob_list[i] == 'b':
            if not t:
                t = token_list[i:i+1]
                tokens.append(t)
                t = []
            else:
                tokens.append(t)
                t = token_list[i:i+1]
            continue
        if iob_list[i] == 'o':
            if t:
                tokens.append(t)
                t = []
            tokens.append(token_list[i:i+1])
    if t: tokens.append(t)
    return ['_'.join(tok) for tok in tokens]

def _strip_tags(html):
    "Strip html tags"
    return BeautifulSoup(html).get_text(' ')

def _text_to_token(text):
    "Get list of token for training"
    # Strip HTML
    text = _strip_tags(text)
    # Keep only word
    text = re.sub("\W", " ", text)
    # Lower and split sentence
    token = text.lower().split()
    return token

def html2word(html):
    text = _strip_tags(html)
    token = _text_to_token(text)
    iob = _classify(token)
    return _make_words(token, iob)

if __name__ == '__main__':
    html = 'Nghiên cứu cho thấy những người khứu giác kém có nguy cơ chết sớm hơn người bình thường.'
    html2word(html)





