import praw
import os
from dotenv import load_dotenv
import re
import time
from xkcd_handler import XKCDHandler
from response_formatter import ResponseFormatter

def run_bot():
    """
    Main bot function that handles Reddit interaction and XKCD comic responses.
    Monitors specified subreddits for '!xkcd' commands and responds with comic information.
    """
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
    xkcd_pattern = re.compile(r'!xkcd\s*(\d*)')
    
    print(f"🤖 Bot started, logged in as u/{reddit.user.me().name}")
    
    # Get subreddits from environment
    subreddits = os.getenv('SUBREDDITS', 'test').strip().split(',')
    
    # Join subreddits with '+' for multi-subreddit monitoring
    # Example: 'test+programming+python'
    subreddit_names = '+'.join(subreddits)
    print(f"👀 Monitoring subreddits: r/{subreddit_names}")
    
    processed_comments = set()
    # TODO: database integration
    while True:
        try:
            subreddit = reddit.subreddit(subreddit_names)
            
            for comment in subreddit.stream.comments(skip_existing=True):
                if comment.id in processed_comments:
                    continue
                
                match = xkcd_pattern.search(comment.body.lower())
                if match:
                    comic_number_str = match.group(1)
                    print(f"🎯 Found !xkcd command in r/{comment.subreddit.display_name}")
                    
                    comic_number = None
                    if comic_number_str:
                        comic_number = xkcd_handler.validate_comic_number(comic_number_str)
                        if comic_number is None:
                            # If number is invalid (e.g., negative, non-numeric),
                            # respond with an error and skip to next comment
                            response = response_formatter.format_error_response("invalid_number")
                            comment.reply(response)
                            processed_comments.add(comment.id)
                            continue
                    
                    # Fetch and respond with comic data
                    # comic_number=None will fetch the latest comic
                    comic_data = xkcd_handler.get_comic(comic_number)
                    response = response_formatter.format_comic_response(comic_data)
                    comment.reply(response)
                    
                    processed_comments.add(comment.id)
                    time.sleep(2)  # Reddit API rate limiting
        
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    run_bot() 