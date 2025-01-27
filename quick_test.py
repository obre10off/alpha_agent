import asyncio
import logging
from src.main import AIAlphaAgent

async def test_agent():
    """Test the AI Alpha Agent with new filtering."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize agent
        logger.info("Initializing AI Alpha Agent...")
        agent = AIAlphaAgent()
        
        # Run single scan
        logger.info("Starting test scan...")
        await agent.scan_and_process()
        
        logger.info("Test completed!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_agent()) 