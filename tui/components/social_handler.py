"""Social media posting handler for TUI."""
import asyncio
import os
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from utils.social_poster import ArcadeSocialPoster
from utils.summarizer import TenderSummarizer
from .command_processor import Command, Channel, Action


@dataclass
class PostResult:
    """Result of a social media post."""
    success: bool
    channel: str
    content: str
    post_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = ""


class SocialMediaHandler:
    """Handles social media posting operations."""

    def __init__(self):
        """Initialize the handler with API clients."""
        try:
            self.poster = ArcadeSocialPoster()
            self.summarizer = TenderSummarizer()
        except ValueError as e:
            raise ValueError(f"Failed to initialize handlers: {str(e)}")
        
        self.results_dir = Path(__file__).parent.parent.parent / "post_results"
        self.results_dir.mkdir(exist_ok=True)

    async def execute_command(self, cmd: Command) -> PostResult:
        """
        Execute a parsed command.
        
        Args:
            cmd: Parsed command structure
            
        Returns:
            PostResult with execution details
        """
        if not cmd.is_valid:
            return PostResult(
                success=False,
                channel="unknown",
                content="",
                error=cmd.error_message
            )

        try:
            # Normalize channel name
            channel_name = self._normalize_channel(cmd.channel)
            
            # Handle different actions
            if cmd.action in [Action.SUMMARISE, Action.SUMMARIZE]:
                return await self._handle_summarise(cmd, channel_name)
            
            elif cmd.action == Action.POST:
                return await self._handle_post(cmd, channel_name)
            
            elif cmd.action == Action.PREVIEW:
                return await self._handle_preview(cmd, channel_name)
            
            else:
                return PostResult(
                    success=False,
                    channel=channel_name,
                    content="",
                    error=f"Unknown action: {cmd.action}"
                )
        
        except Exception as e:
            return PostResult(
                success=False,
                channel=self._normalize_channel(cmd.channel) if cmd.channel else "unknown",
                content="",
                error=f"Execution error: {str(e)}"
            )

    async def _handle_summarise(self, cmd: Command, channel_name: str) -> PostResult:
        """Handle summarise action - fetch URL, summarise, and post."""
        try:
            # For now, create a mock tender from URL
            # In production, this would fetch and parse the actual content
            tender = {
                "title": f"Content from {cmd.url}",
                "organization": "Tendly",
                "budget": "TBD",
                "deadline": "TBD",
                "category": "General",
                "description": f"Content from {cmd.url}",
                "cpv_codes": []
            }
            
            # Generate summary based on channel
            if channel_name == "x":
                summary = self.summarizer.summarize_for_twitter(tender)
            else:  # linkedin
                summary = self.summarizer.summarize_for_linkedin(tender)
            
            # Add URL to summary
            full_content = f"{summary}\n\n{cmd.url}"
            
            # Post to the specified channel
            if channel_name == "x":
                result = self.poster.post_to_twitter(summary, cmd.url)
            else:  # linkedin
                result = self.poster.post_to_linkedin(summary, cmd.url)
            
            # Extract post URL from response
            post_url = self._extract_post_url(result.get("response", {}), channel_name)
            
            post_result = PostResult(
                success=result.get("success", False),
                channel=channel_name,
                content=full_content,
                post_url=post_url,
                error=result.get("error") if not result.get("success") else None,
                timestamp=datetime.now().isoformat()
            )
            
            # Save result
            self._save_result(post_result)
            
            return post_result
        
        except Exception as e:
            return PostResult(
                success=False,
                channel=channel_name,
                content="",
                error=f"Summarise error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    async def _handle_post(self, cmd: Command, channel_name: str) -> PostResult:
        """Handle post action - post content directly."""
        try:
            content = cmd.content or ""
            url = cmd.url
            
            # Post to the specified channel
            if channel_name == "x":
                result = self.poster.post_to_twitter(content, url)
            else:  # linkedin
                result = self.poster.post_to_linkedin(content, url)
            
            # Extract post URL from response
            post_url = self._extract_post_url(result.get("response", {}), channel_name)
            
            # Combine content with URL if URL provided
            full_content = content
            if url:
                full_content = f"{content}\n\n{url}"
            
            post_result = PostResult(
                success=result.get("success", False),
                channel=channel_name,
                content=full_content,
                post_url=post_url,
                error=result.get("error") if not result.get("success") else None,
                timestamp=datetime.now().isoformat()
            )
            
            # Save result
            self._save_result(post_result)
            
            return post_result
        
        except Exception as e:
            return PostResult(
                success=False,
                channel=channel_name,
                content="",
                error=f"Post error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    async def _handle_preview(self, cmd: Command, channel_name: str) -> PostResult:
        """Handle preview action - show what would be posted without posting."""
        try:
            # Create a mock tender from URL
            tender = {
                "title": f"Content from {cmd.url}",
                "organization": "Tendly",
                "budget": "TBD",
                "deadline": "TBD",
                "category": "General",
                "description": f"Content from {cmd.url}",
                "cpv_codes": []
            }
            
            # Generate summary based on channel
            if channel_name == "x":
                summary = self.summarizer.summarize_for_twitter(tender)
            else:  # linkedin
                summary = self.summarizer.summarize_for_linkedin(tender)
            
            # Add URL to summary
            full_content = f"{summary}\n\n{cmd.url}"
            
            # Return as preview (not actually posted)
            return PostResult(
                success=True,
                channel=channel_name,
                content=full_content,
                post_url=None,
                error=None,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            return PostResult(
                success=False,
                channel=channel_name,
                content="",
                error=f"Preview error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def _normalize_channel(self, channel: Channel) -> str:
        """Normalize channel to standard name."""
        if channel in [Channel.X, Channel.TWITTER]:
            return "x"
        elif channel in [Channel.LINKEDIN, Channel.LINKEDIN_FULL]:
            return "linkedin"
        return channel.value

    def _extract_post_url(self, response: Dict, channel: str) -> Optional[str]:
        """Extract post URL from API response."""
        if not response:
            return None
        
        # Try common URL field names
        for key in ['url', 'post_url', 'link', 'permalink', 'tweet_url', 'status_url']:
            if key in response and isinstance(response[key], str):
                if response[key].startswith('http'):
                    return response[key]
        
        # Try recursive search in nested structures
        def find_url(obj, depth=0):
            if depth > 5:
                return None
            
            if isinstance(obj, dict):
                for key in ['url', 'post_url', 'link', 'permalink']:
                    if key in obj and isinstance(obj[key], str) and obj[key].startswith('http'):
                        return obj[key]
                
                for value in obj.values():
                    result = find_url(value, depth + 1)
                    if result:
                        return result
            
            elif isinstance(obj, list):
                for item in obj:
                    result = find_url(item, depth + 1)
                    if result:
                        return result
            
            return None
        
        return find_url(response)

    def _save_result(self, result: PostResult) -> None:
        """Save post result to file."""
        try:
            filename = f"{result.channel}_{result.timestamp.replace(':', '-')}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'success': result.success,
                    'channel': result.channel,
                    'content': result.content,
                    'post_url': result.post_url,
                    'error': result.error,
                    'timestamp': result.timestamp
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save result: {e}")

    def get_results_summary(self) -> str:
        """Get summary of recent posting results."""
        try:
            results = list(self.results_dir.glob("*.json"))
            if not results:
                return "No posting results yet."
            
            # Get last 5 results
            recent = sorted(results, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            
            summary = "Recent Posting Results:\n"
            for result_file in recent:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    status = "✓ Success" if data['success'] else "✗ Failed"
                    summary += f"\n{status} | {data['channel'].upper()} | {data['timestamp']}"
                    if data.get('error'):
                        summary += f"\n  Error: {data['error']}"
            
            return summary
        except Exception as e:
            return f"Error reading results: {str(e)}"
