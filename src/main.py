import os
import asyncio
import yaml
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collectors.reddit import RedditCollector
from collectors.hackernews import HackerNewsCollector
from analysis.filter import ContentFilter
from templates.prd import PRDGenerator
from delivery.gmail import GmailDelivery
import logging

class AIAlphaAgent:
    """Main application class for AI Alpha Agent."""
    
    def __init__(self):
        """Initialize the AI Alpha Agent."""
        load_dotenv()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load configurations
        with open("config/sources.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        # Initialize components with stricter filters
        self.reddit_collector = RedditCollector(self.config["reddit"])
        self.hackernews_collector = HackerNewsCollector(self.config["hackernews"])
        
        # Stricter filtering criteria
        self.content_filter = ContentFilter({
            "max_age_days": 7,  # More recent content
            "min_relevance_score": 0.6,  # Higher relevance requirement
            "min_points": 100,  # Higher points threshold
            "max_posts_per_source": 2  # Fewer posts
        })
        
        self.prd_generator = PRDGenerator("config/templates.yaml")
        self.email_delivery = GmailDelivery(
            api_key=os.getenv("COMPOSIO_API_KEY"),
            config_path="config/templates.yaml"
        )
        
    async def process_content(self, content: dict) -> bool:
        """Process a single piece of content."""
        try:
            self.logger.info(f"Generating PRD for: {content.get('title', 'Untitled')}")
            prd_content = await self.prd_generator.generate_prd(content)
            
            self.logger.info("Sending email...")
            success = await self.email_delivery.send_email(content, prd_content)
            
            if success:
                self.logger.info("Email sent successfully")
            else:
                self.logger.error("Failed to send email")
                
            return success
        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            return False
            
    async def scan_and_process(self):
        """Scan sources and process content."""
        try:
            self.logger.info("Starting content scan...")
            
            # Collect content with limits
            reddit_content = await self.reddit_collector.collect()
            reddit_content = reddit_content[:5]  # Limit initial results
            self.logger.info(f"Found {len(reddit_content)} Reddit posts")
            
            hackernews_content = await self.hackernews_collector.collect()
            hackernews_content = hackernews_content[:5]  # Limit initial results
            self.logger.info(f"Found {len(hackernews_content)} HackerNews posts")
            
            # Filter content
            reddit_filtered = await self.content_filter.filter_content(reddit_content)
            self.logger.info(f"Filtered to {len(reddit_filtered)} relevant Reddit posts")
            
            hackernews_filtered = await self.content_filter.filter_content(hackernews_content)
            self.logger.info(f"Filtered to {len(hackernews_filtered)} relevant HackerNews posts")
            
            # Take only the top posts from each source
            filtered_posts = (reddit_filtered + hackernews_filtered)[:2]
            
            # Process filtered content
            for content in filtered_posts:
                self.logger.info(f"Processing: {content.get('title', 'Untitled')}")
                await self.process_content(content)
                
        except Exception as e:
            self.logger.error(f"Error in scan_and_process: {str(e)}")

async def run_agent():
    """Run the agent with scheduler."""
    agent = AIAlphaAgent()
    
    # Set up scheduler for 2-hour intervals
    scheduler = AsyncIOScheduler()
    scheduler.add_job(agent.scan_and_process, 'interval', hours=2)
    
    try:
        scheduler.start()
        print("Agent started. Scanning every 2 hours...")
        # Run initial scan
        await agent.scan_and_process()
        # Keep running
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nAgent stopped.")

if __name__ == "__main__":
    asyncio.run(run_agent()) 