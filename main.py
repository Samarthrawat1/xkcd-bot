import praw
import requests
import re
import time
from dotenv import load_dotenv
import os
from flask import Flask, render_template, jsonify
from threading import Thread
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///bot_stats.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Stats(Base):
    __tablename__ = 'stats'
    
    id = Column(Integer, primary_key=True)
    comments_processed = Column(Integer, default=0)
    successful_replies = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def get_or_create(cls, session):
        stats = session.query(cls).first()
        if not stats:
            stats = cls()
            session.add(stats)
            session.commit()
        return stats

# Create tables
Base.metadata.create_all(engine)

# Reddit API credentials
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent='xkcd_bot by /u/' + os.getenv('REDDIT_USERNAME')
)

def update_stats(stat_name):
    with Session() as session:
        stats = Stats.get_or_create(session)
        setattr(stats, stat_name, getattr(stats, stat_name) + 1)
        stats.last_updated = datetime.utcnow()
        session.commit()

def get_stats():
    with Session() as session:
        stats = Stats.get_or_create(session)
        return {
            'comments_processed': stats.comments_processed,
            'successful_replies': stats.successful_replies,
            'errors': stats.errors,
            'last_updated': stats.last_updated.isoformat()
        }

def fetch_xkcd(comic_number=None):
    url = f'https://xkcd.com/{comic_number}/info.0.json' if comic_number else 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['img'], data['title']
    return None, None

def process_comment(comment):
    pattern = re.compile(r'!xkcd(\s+\d+)?')
    match = pattern.search(comment.body)
    if match:
        comic_number = match.group(1)
        comic_number = int(comic_number.strip()) if comic_number else None
        img_url, title = fetch_xkcd(comic_number)
        if img_url:
            reply = f"**{title}**\n{img_url}"
            comment.reply(reply)
            print(f"Replied to comment {comment.id}")
            return True
    return False

def run_bot():
    subreddit = reddit.subreddit('all')
    
    for comment in subreddit.stream.comments(skip_existing=True):
        try:
            process_comment(comment)
            update_stats('comments_processed')
            if process_comment(comment):  # Modified to return True if reply was made
                update_stats('successful_replies')
        except Exception as e:
            print(f"Error: {e}")
            update_stats('errors')
            time.sleep(10)

# Web routes
@app.route('/')
def home():
    return render_template('index.html', stats=get_stats())

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

if __name__ == '__main__':
    # Start the bot in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
