"""Module for formatting Reddit comment responses."""
from typing import Optional, Dict, Any

class ResponseFormatter:
    @staticmethod
    def format_comic_response(comic_data: Optional[Dict[str, Any]]) -> str:
        """
        Create a formatted Reddit comment with the comic information.
        
        Args:
            comic_data: Dictionary containing comic data
            
        Returns:
            Formatted string for Reddit comment
        """
        if not comic_data:
            return "Sorry, I couldn't fetch that XKCD comic. Please try again!"
        
        return f"""**[{comic_data['title']}](https://xkcd.com/{comic_data['num']})**

{comic_data['alt']}

Direct image link: {comic_data['img']}

^(I am a bot | [Source](https://github.com/samarthrawat1/xkcd-bot))"""

    @staticmethod
    def format_error_response(error_type: str) -> str:
        """
        Create a formatted error response.
        
        Args:
            error_type: Type of error to format response for
            
        Returns:
            Formatted error message
        """
        error_messages = {
            "invalid_number": "Sorry, that doesn't seem to be a valid comic number. Please try again with a positive number!",
            "not_found": "Sorry, I couldn't find that comic. Please try another number!",
            "rate_limit": "I'm a bit busy right now. Please try again in a few minutes!",
            "general": "Oops! Something went wrong. Please try again later!"
        }
        return error_messages.get(error_type, error_messages["general"]) 