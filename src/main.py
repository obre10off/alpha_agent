import os
import asyncio
import yaml
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.collectors.reddit import RedditCollector
from src.collectors.hackernews import HackerNewsCollector
from src.analysis.filter import ContentFilter
from src.templates.prd import PRDGenerator
from src.delivery.gmail import EmailDelivery

class AIAlphaAgent:
    """Main application class for AI Alpha Agent."""
    
    def __init__(self):
        """Initialize the AI Alpha Agent."""
        load_dotenv()
        
        # Load configurations
        with open("config/sources.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        # Initialize components
        self.reddit_collector = RedditCollector(self.config["reddit"])
        self.hackernews_collector = HackerNewsCollector(self.config["hackernews"])
        self.content_filter = ContentFilter(self.config["filters"])
        self.prd_generator = PRDGenerator("config/templates.yaml")
        self.email_delivery = EmailDelivery(
            "config/templates.yaml",
            os.getenv("EMAIL_RECIPIENT")
        )
        
    async def process_content(self, content: dict) -> bool:
        """Process a single piece of content."""
        try:
            # Generate PRD
            prd_content = await self.prd_generator.generate_prd(content)
            
            # Send email
            success = await self.email_delivery.send_email(content, prd_content)
            return success
        except Exception as e:
            print(f"Error processing content: {str(e)}")
            return False
            
    async def scan_and_process(self):
        """Scan sources and process content."""
        try:
            print("Starting content scan...")
            # Collect content
            reddit_content = await self.reddit_collector.collect()
            print(f"Found {len(reddit_content)} Reddit posts")
            hackernews_content = await self.hackernews_collector.collect()
            print(f"Found {len(hackernews_content)} HackerNews posts")
            
            # Filter content
            reddit_filtered = await self.content_filter.filter_content(reddit_content)
            print(f"Filtered to {len(reddit_filtered)} relevant Reddit posts")
            hackernews_filtered = await self.content_filter.filter_content(hackernews_content)
            print(f"Filtered to {len(hackernews_filtered)} relevant HackerNews posts")
            
            # Process filtered content
            for content in reddit_filtered + hackernews_filtered:
                print(f"Processing content: {content.get('title', 'Untitled')}")
                await self.process_content(content)
                
        except Exception as e:
            print(f"Error in scan_and_process: {str(e)}")

async def run_agent():
    """Run the agent with scheduler."""
    # Initialize agent
    agent = AIAlphaAgent()
    
    # Set up scheduler
    scheduler = AsyncIOScheduler()
    interval = int(os.getenv("SCAN_INTERVAL_MINUTES", "60"))
    scheduler.add_job(agent.scan_and_process, 'interval', minutes=interval)
    
    try:
        scheduler.start()
        print(f"Agent started. Scanning every {interval} minutes...")
        # Run initial scan immediately
        await agent.scan_and_process()
        # Keep running
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nAgent stopped.")

def main():
    """Main entry point."""
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main() 