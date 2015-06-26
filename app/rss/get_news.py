
import os
from datetime import datetime
from time import sleep

import feedparser
import numpy as np
from nimfa import mf, mf_run

from app.main.views import index
from app.vietseg.makewords import html2word
from app import mongo, cache

rss_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(rss_dir, 'rss_edited.txt')) as f:
    "Read rss links from file, ready for parsing"
    feedlist = []
    for link in f:
        feedlist.append(link.strip())

stops = ['có_thể', 'đến_nỗi', 'một_cách', 'tương_đương', 'tiếp_tục', 'liên_quan',
         'bất_ngờ', 'diễn_ra', 'trong_đó', 'khoảnh_khắc', 'thú_vị', 'cho_biết',
         'đề_nghị', 'sau_khi', 'không_phải']

def _get_articles():
    "Get words from rss sources"
    all_words = {}
    article_words = []
    article_titles = []
    article_links = []
    count = 0
    # Loop over every feed
    for feed in feedlist:
        f = feedparser.parse(feed)
        sleep(0) # How much should I wait?
        limit = 0
        # Loop over every article
        for e in f.entries:
            # Ignore identical articles or more than 7 articles have been added
            if (not e.title) or (e.title in article_titles): continue
            if limit > 10: break
            limit += 1
            # Extract the words
            cont = e.title + ' ' + e.description
            words = html2word(cont)
            article_words.append({})
            article_titles.append(e.title)
            article_links.append(e.link)
            # Increase the counts for this word in all_words and in article_words
            for word in words:
                # Eliminate words
                if '_' not in word or word in stops: continue
                all_words.setdefault(word, 0)
                all_words[word] += 1
                article_words[count].setdefault(word, 0)
                article_words[count][word] += 1
            count += 1
    return all_words, article_words, article_titles, article_links

def _make_matrix(all_words, article_words):
    "Make words matrix from words"
    word_vec = []
    hot = {}
    # Only take words that are common but not too common
    for w, c in all_words.items():
        if 5 <= c <= 49:
            word_vec.append(w)
            hot[w] = c
    # Save to mongo
    mongo.db.hot.drop()
    mongo.db.hot.insert({'hot': hot})
    # Create the word matrix
    word_matrix = [[(word in f and f[word] or 0) for word in word_vec]
                   for f in article_words]
    return np.asarray(word_matrix), word_vec

def _factorize(matrix):
    "Factorize the matrix to get pc"
    # Build the model
    model = mf(matrix,
               seed="random_vcol",
               rank=15,
               method="nmf",
               max_iter=15,
               initialize_only=True,
               update='divergence',
               objective='div')
    # Then fit it
    fit = mf_run(model)
    return fit.basis(), fit.coef()

def _save_news(w,h,titles,links,wordvec): 
    "Save articles in each feature to MongoDB"
    mongo.db.news.drop() # TODO: Save news until out of memory
    pc, wc = np.shape(h)
    # Loop over all the features
    for i in range(pc):
        slist = []
        # Create a list of words and their weights
        for j in range(wc):
            slist.append((h[i,j], wordvec[j]))
        # Reverse sort the word list
        slist.sort()
        slist.reverse()
        # Create a list of articles for this feature
        flist = []
        for j in range(len(titles)):
            # Add the article with its weight
            flist.append((w[j,i], titles[j], links[j]))
        # Reverse sort the list
        flist.sort()
        flist.reverse()
        # Save to mongo
        mongo.db.news.insert({'id': i,
                              'keywords': slist[:4], 
                              'articles': flist[:4]})
    mongo.db.update.drop()
    mongo.db.update.insert({'time': datetime.now().strftime('%d/%m/%Y %Hg:%Mp')})
    cache.delete_memoized(index)

def save_news():
    "A wrapper for all"
    all_words, article_words, article_titles, article_links = _get_articles()
    word_matrix, word_vec = _make_matrix(all_words, article_words)
    weights, features = _factorize(word_matrix)
    _save_news(weights, features, article_titles, article_links, word_vec)




