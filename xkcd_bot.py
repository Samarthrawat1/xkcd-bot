import praw
import requests
import os
from dotenv import load_dotenv
import re
import time

def get_xkcd_comic(comic_number=None):
    """Fetch XKCD comic data from the API"""
    if comic_number:
        url = f'https://xkcd.com/{comic_number}/info.0.json'
    else:
        url = 'https://xkcd.com/info.0.json'  # Gets the latest comic
    
    print(f"🔍 Fetching XKCD comic from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        comic_data = response.json()
        print(f"✅ Successfully fetched comic #{comic_data['num']}: {comic_data['title']}")
        return comic_data
    except requests.RequestException as e:
        print(f"❌ Error fetching XKCD comic: {e}")
        return None

def create_comment_response(comic_data):
    """Create a formatted Reddit comment with the comic information"""
    if not comic_data:
        return "Sorry, I couldn't fetch that XKCD comic. Please try again!"
    
    return f"""**[{comic_data['title']}](https://xkcd.com/{comic_data['num']})**

{comic_data['alt']}

Direct image link: {comic_data['img']}

^(I am a bot | [Source](https://github.com/your-username/xkcd-bot))"""

def run_bot():
    print("\n=== XKCD Bot Starting Up ===\n")
    
    # Load environment variables
    load_dotenv()
    print("📁 Loaded environment variables")
    
    # Initialize Reddit instance
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent='xkcd_bot by /u/samarthrawat1'
    )
    
    # Regular expression to match !xkcd [number] pattern
    xkcd_pattern = re.compile(r'!xkcd\s*(\d*)')
    
    print(f"🤖 Bot started, logged in as u/{reddit.user.me().name}")
    print("👀 Monitoring comments for '!xkcd' commands...")
    
    # Track processed comments to avoid duplicates
    processed_comments = set()
    
    while True:
        try:
            # Monitor comments in specified subreddits
            subreddit = reddit.subreddit('test')  # Add more subreddits with '+': 'test+python+etc'
            print(f"📡 Watching subreddit: r/{subreddit}")
            
            for comment in subreddit.stream.comments(skip_existing=True):
                print(f"💭 New comment detected: {comment.id}")
                
                # Skip if we've already processed this comment
                if comment.id in processed_comments:
                    print(f"⏭️ Skipping already processed comment: {comment.id}")
                    continue
                
                # Look for !xkcd command in comment
                match = xkcd_pattern.search(comment.body.lower())
                if match:
                    comic_number = match.group(1)
                    print(f"🎯 Found !xkcd command in comment {comment.id}")
                    print(f"🔢 Requested comic number: {comic_number if comic_number else 'latest'}")
                    
                    # If no number specified, get the latest comic
                    if not comic_number:
                        comic_data = get_xkcd_comic()
                    else:
                        comic_data = get_xkcd_comic(comic_number)
                    
                    # Reply to the comment
                    response = create_comment_response(comic_data)
                    comment.reply(response)
                    print(f"✅ Successfully replied to comment {comment.id} with XKCD #{comic_data['num'] if comic_data else 'unknown'}")
                    
                    # Add to processed comments
                    processed_comments.add(comment.id)
                    print(f"💾 Added comment {comment.id} to processed comments")
                    
                    # Sleep to avoid rate limits
                    print("⏳ Waiting 2 seconds before next action...")
                    time.sleep(2)
        
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("⏳ Waiting 60 seconds before retrying...")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    run_bot() 