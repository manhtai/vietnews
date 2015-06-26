
import os
from app import create_app, mongo
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('CONFIG_ENV') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, mongo=mongo)
manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def tomongo():
    "Import word2vec dict to mongodb"
    from app.vietseg.makevec import _to_mongo
    _to_mongo()

@manager.command
def get():
    "Get and save news to mongodb actively"
    from app.rss.get_news import save_news
    save_news()

if __name__ == '__main__':
    manager.run()
