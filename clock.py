from rq import Queue
from worker import conn
from apscheduler.schedulers.blocking import BlockingScheduler

from app.rss.get_news import save_news

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour='6-22/2', timezone='Asia/Ho_Chi_Minh')
def get_and_save_news():
    print("Start collect news...")
    q = Queue(connection=conn)
    q.enqueue(save_news)
    print("Finish collect news...")

sched.start()
