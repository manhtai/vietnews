
from flask import render_template
from app.main import main
from app import mongo, cache
import re


@main.route('/')
@cache.memoize(60*60*2)
def index():
    news = []
    for n in mongo.db.news.find():
        x = lambda *x: n['id']
        x.keywords = ', '.join([re.sub('_', ' ', b) for _, b in n['keywords']])
        x.articles = [(a, b) for _, a, b in n['articles']]
        news.append(x)
    update = mongo.db.update.find()[0]['time']
    hot = mongo.db.hot.find()[0]['hot']
    mean = sum(hot.values())/len(hot)
    hot = [(c, w) for w, c in hot.items() if c > mean]
    hot.sort()
    hot = ', '.join([re.sub('_', ' ', w) for _, w in hot])
    return render_template('index.html', news=news, update=update, hot=hot)

