import os
import asyncio
import yaml
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collectors.github import GitHubCollector
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
            
        # Initialize components
        self.github_collector = GitHubCollector(self.config["github"])
        
        # Content filtering
        self.content_filter = ContentFilter({
            "min_relevance_score": 0.7,
            "max_repos_per_batch": 3
        })
        
        self.prd_generator = PRDGenerator("config/templates.yaml")
        self.email_delivery = GmailDelivery(
            api_key=os.getenv("COMPOSIO_API_KEY"),
            config_path="config/templates.yaml"
        )
        
    async def process_content(self, content: dict) -> bool:
        """Process a single repository."""
        try:
            self.logger.info(f"Generating PRD for: {content.get('title', 'Untitled')}")
            
            # Add repository details to content
            content["key_points"] = [
                f"Stars: {content.get('stars', 0)}",
                f"Language: {content.get('language', 'Unknown')}",
                f"Topics: {', '.join(content.get('topics', []))}",
                f"Last updated: {content.get('updated_at', 'Unknown')}"
            ]
            
            # Generate PRD using both description and README
            content["text"] = f"""
            Description: {content.get('text', '')}
            
            README:
            {content.get('readme', '')}
            """
            
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
        """Scan GitHub and process repositories."""
        try:
            self.logger.info("Starting GitHub scan...")
            
            # Collect repositories
            repositories = await self.github_collector.collect()
            self.logger.info(f"Found {len(repositories)} repositories")
            
            # Filter repositories
            filtered_repos = await self.github_collector.filter_content(repositories)
            self.logger.info(f"Filtered to {len(filtered_repos)} relevant repositories")
            
            # Take only the top repositories
            top_repos = filtered_repos[:self.config["filters"]["max_repos_per_batch"]]
            
            # Process each repository
            for repo in top_repos:
                self.logger.info(f"Processing repository: {repo.get('title', 'Untitled')}")
                await self.process_content(repo)
                
        except Exception as e:
            self.logger.error(f"Error in scan_and_process: {str(e)}")

async def run_agent():
    """Run the agent with scheduler."""
    agent = AIAlphaAgent()
    
    # Set up scheduler for daily runs
    scheduler = AsyncIOScheduler()
    scheduler.add_job(agent.scan_and_process, 'interval', hours=24)
    
    try:
        scheduler.start()
        print("Agent started. Scanning GitHub daily...")
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