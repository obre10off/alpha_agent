import asyncio
import os
from dotenv import load_dotenv
from src.delivery.gmail import GmailDelivery
from src.analysis.filter import ContentFilter
from src.templates.prd import PRDGenerator
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
        
        # Test data with detailed, realistic content
        test_posts = [
            {
                "title": "AutoGPT-Next: Advanced Multi-Agent Framework",
                "text": """
                Just released AutoGPT-Next, a framework for building autonomous AI agents with advanced capabilities.
                
                Key Features:
                - Multi-agent orchestration with built-in communication protocols
                - Memory management system with vector storage
                - Tool integration framework for API connections
                - Safety mechanisms and monitoring
                - Scalable architecture for enterprise deployment
                
                The framework solves common issues in agent development like context management,
                tool integration, and inter-agent communication. It's built on top of LangChain
                and supports multiple LLM providers.
                
                Technical Stack:
                - Python 3.9+
                - FastAPI backend
                - Redis for memory management
                - Docker support
                - Prometheus metrics
                
                Already being used by several companies for automation and research.
                Looking for contributors and feedback from the community.
                """,
                "created_utc": int(datetime.now().timestamp()),
                "score": 850,
                "points": 850,
                "url": "https://github.com/example/autogpt-next",
                "source": "Reddit",
                "platform": "Reddit",
                "key_points": [
                    "Advanced multi-agent orchestration",
                    "Built-in memory management",
                    "Enterprise-ready architecture",
                    "Active community and corporate adoption",
                    "Open source with MIT license"
                ]
            }
        ]
        
        # Initialize components
        filter_config = {
            "max_age_days": 30,
            "min_relevance_score": 0.1,
            "min_points": 1,
            "max_posts_per_source": 5
        }
        
        content_filter = ContentFilter(filter_config)
        prd_generator = PRDGenerator("config/templates.yaml")
        
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
                # Generate full PRD using the template
                prd_content = await prd_generator.generate_prd(post)
                
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