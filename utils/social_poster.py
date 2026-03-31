"""
Social media posting utility using Arcade AI.
"""
import os
from typing import Dict, Optional, List
import time

from arcadepy import Arcade


class ArcadeSocialPoster:
    """Posts content to social media platforms using Arcade AI."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the poster with Arcade API key.

        Args:
            api_key: Arcade API key. If not provided, reads from ARCADE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ARCADE_API_KEY')
        if not self.api_key:
            raise ValueError("ARCADE_API_KEY must be provided or set in environment")

        self.client = Arcade(api_key=self.api_key)
        self.user_id = os.getenv('ARCADE_USER_ID')

    def check_auth(self, provider: str) -> Dict:
        """
        Check authorization status for a provider.

        Args:
            provider: Provider ID (e.g. 'arcade-x', 'arcade-linkedin')

        Returns:
            Authorization status dictionary
        """
        auth = self.client.auth.start(
            user_id=self.user_id,
            provider=provider
        )
        return {
            "status": auth.status,
            "url": auth.url,
            "provider": provider
        }

    def post_to_twitter(self, content: str, url: Optional[str] = None) -> Dict:
        """
        Post content to Twitter/X using Arcade.

        Args:
            content: The text content to post
            url: Optional URL to include in the post

        Returns:
            Response dictionary from Arcade API
        """
        full_content = content
        if url:
            full_content = f"{content}\n\n{url}"

        try:
            response = self.client.tools.execute(
                tool_name="X.PostTweet",
                input={"tweet_text": full_content},
                user_id=self.user_id
            )
            return {
                "success": response.success,
                "platform": "twitter",
                "response": response.output.value if response.output else None,
                "content": full_content
            }
        except Exception as e:
            return {
                "success": False,
                "platform": "twitter",
                "error": str(e),
                "content": full_content
            }

    def post_to_linkedin(self, content: str, url: Optional[str] = None, page_id: Optional[str] = None) -> Dict:
        """
        Post content to LinkedIn using Arcade.

        Args:
            content: The text content to post
            url: Optional URL to include in the post
            page_id: LinkedIn page ID (unused, posts to authenticated user's profile)

        Returns:
            Response dictionary from Arcade API
        """
        full_content = content
        if url:
            full_content = f"{content}\n\nLearn more: {url}"

        try:
            response = self.client.tools.execute(
                tool_name="Linkedin.CreateTextPost",
                input={"text": full_content},
                user_id=self.user_id
            )
            return {
                "success": response.success,
                "platform": "linkedin",
                "response": response.output.value if response.output else None,
                "content": full_content
            }
        except Exception as e:
            return {
                "success": False,
                "platform": "linkedin",
                "error": str(e),
                "content": full_content
            }
    
    def post_to_all_platforms(
        self, 
        twitter_content: str, 
        linkedin_content: str, 
        url: Optional[str] = None,
        linkedin_page_id: Optional[str] = None,
        delay_between_posts: int = 5
    ) -> List[Dict]:
        """
        Post to both Twitter and LinkedIn with a delay between posts.
        
        Args:
            twitter_content: Content for Twitter post
            linkedin_content: Content for LinkedIn post
            url: Optional URL to include in posts
            linkedin_page_id: LinkedIn page ID for company page posting
            delay_between_posts: Seconds to wait between posts (default: 5)
            
        Returns:
            List of response dictionaries from both platforms
        """
        results = []
        
        # Post to Twitter first
        print("Posting to Twitter/X...")
        twitter_result = self.post_to_twitter(twitter_content, url)
        results.append(twitter_result)
        
        # Wait between posts
        if delay_between_posts > 0:
            print(f"Waiting {delay_between_posts} seconds before posting to LinkedIn...")
            time.sleep(delay_between_posts)
        
        # Post to LinkedIn
        print("Posting to LinkedIn...")
        linkedin_result = self.post_to_linkedin(linkedin_content, url, linkedin_page_id)
        results.append(linkedin_result)
        
        return results
