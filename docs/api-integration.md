# API Integration Guide

This document provides detailed information about the API integrations used in Tendly Social.

## XAI (Grok) API Integration

### Overview

XAI's Grok API powers the content generation capabilities of Tendly Social. The integration uses OpenAI-compatible client libraries to communicate with the Grok-3 model.

### Configuration

The XAI integration is configured in `utils/summarizer.py`:

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv('XAI_API_KEY'),
    base_url="https://api.x.ai/v1"
)
```

### API Endpoints

**Base URL**: `https://api.x.ai/v1`

**Endpoint**: `/chat/completions`

**Method**: POST

### Request Format

```json
{
  "model": "grok-3",
  "messages": [
    {
      "role": "system",
      "content": "You are a professional social media manager..."
    },
    {
      "role": "user",
      "content": "Create a concise, engaging Twitter post..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 150
}
```

### Response Format

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "grok-3",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Generated content here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200
  }
}
```

### Content Generation Parameters

#### Twitter Summary Generation

- **Model**: grok-3
- **Temperature**: 0.7
- **Max Tokens**: 150
- **System Prompt**: "You are a professional social media manager specializing in public procurement and tender announcements."
- **Constraints**: Maximum 280 characters, include key details, engaging tone

#### LinkedIn Summary Generation

- **Model**: grok-3
- **Temperature**: 0.7
- **Max Tokens**: 500
- **System Prompt**: "You are a professional B2B content writer specializing in public procurement and business opportunities."
- **Constraints**: 2-3 paragraphs, professional tone, max 1000 characters

### Error Handling

The integration includes error handling for common API issues:

```python
try:
    response = self.client.chat.completions.create(...)
    return response.choices[0].message.content.strip()
except openai.APIError as e:
    # Handle API errors
    raise Exception(f"XAI API Error: {str(e)}")
except openai.RateLimitError as e:
    # Handle rate limiting
    raise Exception(f"Rate limit exceeded: {str(e)}")
```

### Rate Limits

**Current Limits** (as of November 2025):
- Requests per minute: 60
- Tokens per minute: 90,000
- Requests per day: Unlimited (within token limits)

**Recommendations**:
- Implement request throttling for batch operations
- Cache generated content when possible
- Use exponential backoff for retry logic

### Cost Optimization

**Pricing** (approximate):
- Input tokens: $0.01 per 1K tokens
- Output tokens: $0.03 per 1K tokens

**Optimization Strategies**:
1. Minimize prompt length while maintaining quality
2. Use appropriate max_tokens settings
3. Cache frequently generated content
4. Batch similar requests when possible

## Arcade AI Integration

### Overview

Arcade AI provides unified social media posting capabilities through a single API. The integration handles authentication and posting to Twitter/X and LinkedIn.

### Configuration

The Arcade AI integration is configured in `utils/social_poster.py`:

```python
self.base_url = "https://api.arcade-ai.com/v1"
self.headers = {
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json"
}
```

### Authentication

Arcade AI uses Bearer token authentication:

```python
headers = {
    "Authorization": f"Bearer {ARCADE_API_KEY}",
    "Content-Type": "application/json"
}
```

### User Authorization

Before posting, users must be authorized:

```python
def authorize_user(self) -> Dict:
    payload = {
        "email": self.user_email,
        "password": self.user_password
    }
    
    response = requests.post(
        f"{self.base_url}/auth/authorize",
        headers=self.headers,
        json=payload
    )
    
    return response.json()
```

### Twitter/X Posting

**Tool**: `X.PostTweet`

**Endpoint**: `/tools/execute`

**Request Format**:

```json
{
  "tool": "X.PostTweet",
  "inputs": {
    "text": "Your tweet content here with URL"
  }
}
```

**Example**:

```python
payload = {
    "tool": "X.PostTweet",
    "inputs": {
        "text": "🚀 Exciting opportunity! Budget: €450,000...\n\nhttps://tendly.eu/tenders/T001"
    }
}

response = requests.post(
    f"{self.base_url}/tools/execute",
    headers=self.headers,
    json=payload
)
```

### LinkedIn Posting

**Tool**: `LinkedIn.CreatePost`

**Endpoint**: `/tools/execute`

**Request Format**:

```json
{
  "tool": "LinkedIn.CreatePost",
  "inputs": {
    "text": "Your LinkedIn post content here",
    "page_id": "company-page-id"
  }
}
```

**Example**:

```python
payload = {
    "tool": "LinkedIn.CreatePost",
    "inputs": {
        "text": "Exciting opportunity in Healthcare IT...\n\nLearn more: https://tendly.eu/tenders/T003",
        "page_id": "tendly-eu"
    }
}

response = requests.post(
    f"{self.base_url}/tools/execute",
    headers=self.headers,
    json=payload
)
```

### Response Handling

**Success Response** (200/201):

```json
{
  "success": true,
  "data": {
    "post_id": "12345...",
    "url": "https://twitter.com/user/status/12345...",
    "created_at": "2025-11-16T15:30:00Z"
  }
}
```

**Error Response** (4xx/5xx):

```json
{
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials provided",
    "details": {}
  }
}
```

### Error Handling

```python
if response.status_code in [200, 201]:
    return {
        "success": True,
        "platform": "twitter",
        "response": response.json()
    }
else:
    return {
        "success": False,
        "platform": "twitter",
        "error": f"{response.status_code} - {response.text}"
    }
```

### Rate Limiting

**Recommended Delays**:
- Between posts to same platform: 5 seconds
- Between posts to different platforms: 3 seconds
- Batch operations: 10 seconds between batches

**Implementation**:

```python
import time

def post_to_all_platforms(self, twitter_content, linkedin_content, delay=5):
    # Post to Twitter
    twitter_result = self.post_to_twitter(twitter_content)
    
    # Wait before posting to LinkedIn
    time.sleep(delay)
    
    # Post to LinkedIn
    linkedin_result = self.post_to_linkedin(linkedin_content)
    
    return [twitter_result, linkedin_result]
```

### Best Practices

1. **Authentication**
   - Store credentials securely in environment variables
   - Refresh tokens before expiration
   - Handle authentication errors gracefully

2. **Content Formatting**
   - Validate content length before posting
   - Ensure URLs are properly formatted
   - Test with special characters and emojis

3. **Error Recovery**
   - Implement retry logic with exponential backoff
   - Log all API interactions for debugging
   - Provide clear error messages to users

4. **Testing**
   - Use dry-run mode for development
   - Test with various content types
   - Validate posting to both personal and company pages

## Tendly.eu API Integration (Future)

### Overview

Future integration with Tendly.eu will enable automatic fetching of live tender data.

### Planned Endpoints

**Base URL**: `https://api.tendly.eu/v1`

**Authentication**: OAuth 2.0 or API Key

**Endpoints**:
- `GET /tenders` - List all tenders
- `GET /tenders/{id}` - Get tender details
- `GET /insights` - Get market insights
- `GET /companies/{id}` - Get company information

### Implementation Plan

1. **Authentication**
   - Implement OAuth 2.0 flow
   - Store access tokens securely
   - Handle token refresh

2. **Data Fetching**
   - Create API client class
   - Implement pagination for large result sets
   - Add filtering and search capabilities

3. **Data Processing**
   - Parse tender data into standard format
   - Extract relevant fields for summarization
   - Handle missing or incomplete data

4. **Caching**
   - Cache tender data to reduce API calls
   - Implement cache invalidation strategy
   - Store processed data in local database

## Security Considerations

### API Key Management

1. **Storage**
   - Never commit API keys to version control
   - Use environment variables or secret management services
   - Rotate keys regularly

2. **Access Control**
   - Limit API key permissions to minimum required
   - Use separate keys for development and production
   - Monitor API key usage for anomalies

### Data Protection

1. **Sensitive Information**
   - Never log API keys or credentials
   - Sanitize error messages before displaying to users
   - Encrypt stored credentials

2. **HTTPS**
   - Always use HTTPS for API communications
   - Verify SSL certificates
   - Implement certificate pinning for critical endpoints

### Rate Limiting

1. **Client-Side**
   - Implement request throttling
   - Use exponential backoff for retries
   - Queue requests during high load

2. **Monitoring**
   - Track API usage metrics
   - Set up alerts for rate limit warnings
   - Log all API errors for analysis

## Monitoring and Logging

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# Log API requests
logger.info(f"Posting to Twitter: {content[:50]}...")

# Log API responses
logger.info(f"Twitter post successful: {post_id}")

# Log errors
logger.error(f"Failed to post to Twitter: {error_message}")
```

### Metrics to Track

1. **API Performance**
   - Response times
   - Success/failure rates
   - Token usage

2. **Content Generation**
   - Average generation time
   - Content quality metrics
   - User edit frequency

3. **Posting Activity**
   - Posts per day/week/month
   - Platform distribution
   - Engagement metrics (if available)

## Testing API Integrations

### Unit Testing

```python
def test_xai_integration():
    summarizer = TenderSummarizer()
    summary = summarizer.summarize_for_twitter(sample_tender)
    assert len(summary) <= 280
    assert summary is not None
```

### Integration Testing

```python
def test_end_to_end_posting():
    # Generate content
    summarizer = TenderSummarizer()
    content = summarizer.summarize_for_twitter(tender)
    
    # Post to social media
    poster = ArcadeSocialPoster()
    result = poster.post_to_twitter(content)
    
    assert result['success'] == True
```

### Mock Testing

```python
from unittest.mock import Mock, patch

@patch('requests.post')
def test_twitter_posting_mock(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'post_id': '12345'}
    
    poster = ArcadeSocialPoster()
    result = poster.post_to_twitter("Test content")
    
    assert result['success'] == True
```

## Troubleshooting

### Common API Issues

**Issue**: "Invalid API Key"
- Verify API key is correct
- Check if key has required permissions
- Ensure key hasn't expired

**Issue**: "Rate Limit Exceeded"
- Implement request throttling
- Use exponential backoff
- Consider upgrading API plan

**Issue**: "Timeout Error"
- Increase timeout settings
- Check network connectivity
- Verify API endpoint status

### Debugging Tips

1. Enable verbose logging
2. Use API testing tools (Postman, curl)
3. Check API status pages
4. Review API documentation for changes
5. Test with minimal examples

## Additional Resources

- [XAI API Documentation](https://docs.x.ai/)
- [Arcade AI Documentation](https://docs.arcade-ai.com/)
- [OpenAI Python Client](https://github.com/openai/openai-python)
- [Requests Library Documentation](https://requests.readthedocs.io/)
