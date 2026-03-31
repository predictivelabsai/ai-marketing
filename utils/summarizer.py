"""
Tender summarization utility using XAI API.
"""
import os
from datetime import date
from openai import OpenAI
from typing import Dict, Optional


class TenderSummarizer:
    """Summarizes tender information for social media posts using XAI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarizer with XAI API key.
        
        Args:
            api_key: XAI API key. If not provided, reads from XAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('XAI_API_KEY')
        if not self.api_key:
            raise ValueError("XAI_API_KEY must be provided or set in environment")
        
        # Initialize OpenAI client with XAI endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
    
    def summarize_for_twitter(self, tender: Dict) -> str:
        """
        Create a Twitter/X post summary of a tender (max 280 characters).
        
        Args:
            tender: Dictionary containing tender information
            
        Returns:
            Twitter-formatted summary string
        """
        prompt = f"""Create a concise, engaging Twitter post (max 280 characters) about this tender:

Title: {tender.get('title')}
Organization: {tender.get('organization')}
Budget: {tender.get('budget')}
Deadline: {tender.get('deadline')}
Category: {tender.get('category')}
Description: {tender.get('description')}

Requirements:
- Maximum 280 characters
- Include key details (budget, deadline)
- Make it engaging and professional
- Use relevant emoji sparingly
- Include hashtags: #PublicProcurement #Tenders
- Do NOT include URLs (they will be added separately)
"""
        
        response = self.client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": f"You are a professional social media manager specializing in public procurement and tender announcements. Today's date is {date.today()}. Always reference current trends and the current year."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def summarize_for_linkedin(self, tender: Dict) -> str:
        """
        Create a LinkedIn post summary of a tender (more detailed).
        
        Args:
            tender: Dictionary containing tender information
            
        Returns:
            LinkedIn-formatted summary string
        """
        prompt = f"""Create a professional LinkedIn post about this tender opportunity:

Title: {tender.get('title')}
Organization: {tender.get('organization')}
Budget: {tender.get('budget')}
Deadline: {tender.get('deadline')}
Category: {tender.get('category')}
Description: {tender.get('description')}
CPV Codes: {tender.get('cpv_codes', [])}

Requirements:
- Professional tone suitable for LinkedIn
- 2-3 paragraphs (max 1000 characters)
- Highlight key opportunity aspects
- Include relevant hashtags
- Make it engaging for procurement professionals
- Do NOT include URLs (they will be added separately)
"""
        
        response = self.client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": f"You are a professional B2B content writer specializing in public procurement and business opportunities. Today's date is {date.today()}. Always reference current trends and the current year."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def create_hashtags(self, tender: Dict) -> list:
        """
        Generate relevant hashtags for a tender.
        
        Args:
            tender: Dictionary containing tender information
            
        Returns:
            List of hashtag strings
        """
        category = tender.get('category', '').lower()
        
        # Base hashtags
        hashtags = ['#PublicProcurement', '#Tenders', '#Tendly']
        
        # Category-specific hashtags
        if 'it' in category or 'software' in category:
            hashtags.extend(['#ITTenders', '#SoftwareDevelopment'])
        elif 'construction' in category or 'infrastructure' in category:
            hashtags.extend(['#Construction', '#Infrastructure'])
        elif 'healthcare' in category or 'health' in category:
            hashtags.extend(['#Healthcare', '#HealthIT'])
        elif 'energy' in category or 'green' in category:
            hashtags.extend(['#GreenEnergy', '#Sustainability'])
        elif 'cybersecurity' in category or 'security' in category:
            hashtags.extend(['#Cybersecurity', '#InfoSec'])
        elif 'transport' in category or 'smart city' in category:
            hashtags.extend(['#SmartCity', '#Transportation'])
        
        # Add Estonia-specific tag
        hashtags.append('#Estonia')
        
        return hashtags
