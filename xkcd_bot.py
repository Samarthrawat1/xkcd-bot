import praw
import os
from dotenv import load_dotenv
import re
import time
from xkcd_handler import XKCDHandler
from response_formatter import ResponseFormatter

def run_bot():
    print("\n=== XKCD Bot Starting Up ===\n")
   
    load_dotenv()
    print("📁 Loaded environment variables")
    
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'XKCD_Bot/1.0 by u/samarthrawat1')
    )
    
    xkcd_handler = XKCDHandler()
    response_formatter = ResponseFormatter()
    
    # Regular expression to match !xkcd [number] pattern
    xkcd_pattern = re.compile(r'!xkcd\s*(\d*)')
    
    print(f"🤖 Bot started, logged in as u/{reddit.user.me().name}")
    print("👀 Monitoring comments for '!xkcd' commands...")
    
    # Track processed comments to avoid duplicates
    processed_comments = set()
    # TODO 
    
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
                    comic_number_str = match.group(1)
                    print(f"🎯 Found !xkcd command in comment {comment.id}")
                    
                    # Validate comic number if provided
                    comic_number = None
                    if comic_number_str:
                        comic_number = xkcd_handler.validate_comic_number(comic_number_str)
                        if comic_number is None:
                            response = response_formatter.format_error_response("invalid_number")
                            comment.reply(response)
                            processed_comments.add(comment.id)
                            continue
                    
                    print(f"🔢 Requesting comic number: {comic_number if comic_number else 'latest'}")
                    
                    # Fetch comic data
                    comic_data = xkcd_handler.get_comic(comic_number)
                    
                    # Format and send response
                    response = response_formatter.format_comic_response(comic_data)
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