"""Module for handling XKCD comic data fetching and processing."""
import requests
from typing import Optional, Dict, Any

class XKCDHandler:
    BASE_URL = "https://xkcd.com"
    
    @staticmethod
    def get_comic(comic_number: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch XKCD comic data from the API.
        
        Args:
            comic_number: Optional comic number. If None, fetches the latest comic.
            
        Returns:
            Dictionary containing comic data or None if fetch fails.
        """
        url = f"{XKCDHandler.BASE_URL}/{'info.0.json' if not comic_number else f'{comic_number}/info.0.json'}"
        
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
    
    @staticmethod
    def validate_comic_number(comic_number: str) -> Optional[int]:
        """
        Validate and convert comic number string to integer.
        
        Args:
            comic_number: String representation of comic number
            
        Returns:
            Integer comic number if valid, None otherwise
        """
        try:
            number = int(comic_number)
            if number <= 0:
                return None
            return number
        except (ValueError, TypeError):
            return None 