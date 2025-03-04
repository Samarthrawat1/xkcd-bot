import praw
import os
from dotenv import load_dotenv
import re
import time
from xkcd_handler import XKCDHandler
from response_formatter import ResponseFormatter
from logger_config import setup_logger

def run_bot():
    """
    Main bot function that handles Reddit interaction and XKCD comic responses.
    Monitors specified subreddits for '!xkcd' commands and responds with comic information.
    """
    logger = setup_logger()
    logger.info("=== XKCD Bot Starting Up ===")
   
    load_dotenv()
    logger.info("📁 Loaded environment variables")
    
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'XKCD_Bot/1.0')
    )
    
    xkcd_handler = XKCDHandler()
    response_formatter = ResponseFormatter()
    
    # Matches both !xkcd and !xkcd 123
    xkcd_pattern = re.compile(r'!xkcd\s*(\d*)')
    
    logger.info(f"🤖 Bot started, logged in as u/{reddit.user.me().name}")
    
    subreddits = os.getenv('SUBREDDITS', 'test').strip().split(',')
    subreddit_names = '+'.join(subreddits)
    logger.info(f"👀 Monitoring subreddits: r/{subreddit_names}")
    
    processed_comments = set()
    
    while True:
        try:
            subreddit = reddit.subreddit(subreddit_names)
            
            for comment in subreddit.stream.comments(skip_existing=True):
                if comment.id in processed_comments:
                    logger.debug(f"Skipping already processed comment: {comment.id}")
                    continue
                
                match = xkcd_pattern.search(comment.body.lower())
                if match:
                    comic_number_str = match.group(1)
                    logger.info(f"🎯 Found !xkcd command in r/{comment.subreddit.display_name}")
                    
                    comic_number = None
                    if comic_number_str:
                        comic_number = xkcd_handler.validate_comic_number(comic_number_str)
                        if comic_number is None:
                            logger.warning(f"Invalid comic number received: {comic_number_str}")
                            response = response_formatter.format_error_response("invalid_number")
                            comment.reply(response)
                            processed_comments.add(comment.id)
                            continue
                    
                    logger.debug(f"Fetching {'latest' if comic_number is None else f'comic #{comic_number}'}")
                    comic_data = xkcd_handler.get_comic(comic_number)
                    
                    if comic_data:
                        logger.info(f"Responding with XKCD #{comic_data['num']}: {comic_data['title']}")
                        response = response_formatter.format_comic_response(comic_data)
                        comment.reply(response)
                        processed_comments.add(comment.id)
                        logger.debug("Waiting for rate limit...")
                        time.sleep(2)  # Reddit API rate limiting
                    else:
                        logger.error("Failed to fetch comic data")
        
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.info("Waiting 60 seconds before retrying...")
            time.sleep(60)

if __name__ == "__main__":
    run_bot() 