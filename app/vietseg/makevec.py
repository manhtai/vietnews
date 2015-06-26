
###############################################################################
# Convert word to vector
###############################################################################

import os
import json
import numpy as np
from app import mongo, cache

WINDOW = 7
SHAPE = 100
model_dir = os.path.abspath(os.path.dirname(__file__))

def _to_json():
    "Convert gensim.models.Word2Vec to json file"
    from gensim.models import Word2Vec
    # Load Word2Vec model from file, use your model's result or use mine
    model = Word2Vec.load(os.path.join(model_dir, '100features_10context_7minwords.vec'))
    dic = {}
    for word in model.vocab:
        dic[word] = model(word).tolist()
    with open(os.path.join(model_dir,'word2vec.json'), 'w') as f:
        json.dump(dic, f)

def _from_json():
    "Read model from json file"
    with open(os.path.join(model_dir,'word2vec.json')) as f:
        model = json.load(f)
    return model

def _to_mongo():
    "Convert json file to mongodb"
    model = _from_json()
    for k, v in model.items():
        mongo.db.word2vec.insert({'word': k, 'vec': v})

def _random_return(word):
    "Random return word for unknown word"
    np.random.seed(len(word))
    return 0.2 * np.random.uniform(-1, 1, SHAPE)

def _model_json(word):
    "Use json file as converter, this is not the right way to do, but f* it"
    model = _from_json()
    try:
        result = np.array(model[word])
    except:
        result = _random_return(word)
    return result

def _model_mongo(word):
    "Use mongodb as converter"
    w = mongo.db.word2vec.find_one({'word': word})
    if w:
        return np.array(w['vec'])
    else:
        return _random_return(word)

@cache.memoize(60**5)
def _model(word):
    "Wrapper for a converter, you choose"
    return _model_mongo(word)

def _word2index(word):
    "Convert word to index using result from Word2Vec learning"
    if word == -1:
        return np.zeros((SHAPE,))
    else:
        return _model(word)

def _context_window(l):
    "Make context window for a given word, 'WINDOW' must be odd"
    l = list(l)
    lpadded = WINDOW//2 * [-1] + l + WINDOW//2 * [-1]
    out = [ lpadded[i:i+WINDOW] for i in range(len(l)) ]
    assert len(out) == len(l)
    return out

def _context_matrix(conwin):
    "Return a list contain map element for each context window of 1 word"
    return [map(lambda x: _word2index(x), win) for win in conwin]

def _context_vector(cm):
    "Convert context matrix to vector"
    return [np.squeeze(np.asarray(list(x))).reshape((WINDOW*SHAPE,1)) for x in cm]

def make_vec(sen):
    "Make vector from a sentence for feeding to neural net directly"
    cw = _context_window(sen)
    cm = _context_matrix(cw)
    return _context_vector(cm)

if __name__ == '__main__':
    # _to_mongo()
    sen = ['mobifone', 'đầu', 'tư', 'hơn', '2', 'tỉ', 'đồng', 'phát', 'triển', 'mạng']
    vec = make_vec(sen)



