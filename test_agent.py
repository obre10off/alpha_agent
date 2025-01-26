import asyncio
import os
from dotenv import load_dotenv
from src.delivery.gmail import GmailDelivery
from src.analysis.filter import ContentFilter
import logging
from datetime import datetime

async def test_filter_and_email():
    """Test the filtering and email delivery"""
    try:
        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv()
        
        # Test data with more detailed content
        test_posts = [
            {
                "title": "AI Agent Framework",
                "text": "Building autonomous AI agents with LLMs",
                "created_utc": int(datetime.now().timestamp()),  # Current timestamp
                "score": 100,
                "points": 100,  # Added points explicitly
                "url": "https://github.com/example/ai-agent",
                "source": "Reddit"
            }
        ]
        
        # Initialize filter with very lenient config
        filter_config = {
            "max_age_days": 30,
            "min_relevance_score": 0.1,
            "min_points": 1,
            "max_posts_per_source": 5
        }
        
        content_filter = ContentFilter(filter_config)
        
        # Test filtering
        print("\nTesting content filter...")
        filtered_posts = await content_filter.filter_content(test_posts)
        print(f"Filtered {len(test_posts)} posts to {len(filtered_posts)} relevant posts")
        
        if filtered_posts:
            print("\nFiltered posts:")
            for post in filtered_posts:
                print(f"Title: {post['title']}")
                print(f"Score: {post.get('relevance_score', 'No score')}")
            
            # Initialize email delivery
            gmail_delivery = GmailDelivery(
                api_key=os.getenv('COMPOSIO_API_KEY'),
                config_path="config/templates.yaml"
            )
            
            # Test email delivery
            print("\nTesting email delivery...")
            for post in filtered_posts:
                # Create a more detailed PRD
                prd_content = f"""
                # {post['title']}
                
                ## Overview
                {post.get('text', 'No content available')}
                
                ## Key Points
                {chr(10).join([f"- {point}" for point in post.get('key_points', [])])}
                
                ## Source Details
                - Platform: {post.get('source', 'Unknown')}
                - URL: {post.get('url', 'No URL available')}
                - Score: {post.get('score', 0)}
                """
                
                # Send email
                success = await gmail_delivery.send_email(post, prd_content)
                if success:
                    print(f"Successfully sent email for: {post['title']}")
                else:
                    print(f"Failed to send email for: {post['title']}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_filter_and_email()) 