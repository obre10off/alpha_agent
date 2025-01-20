from typing import List, Dict, Any
from .base import BaseCollector
from composio_llamaindex import ComposioToolSet, Action
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.agent import FunctionCallingAgentWorker

class RedditCollector(BaseCollector):
    """Collector for Reddit content."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Reddit collector."""
        super().__init__(config)
        self.llm = OpenAI(model="gpt-4o-mini")
        self.toolset = ComposioToolSet()
        self.tools = self.toolset.get_tools(actions=['REDDIT_RETRIEVE_REDDIT_POST'])
        
        # Set up agent
        prefix_messages = [
            ChatMessage(
                role="system",
                content="You are a Reddit content collector. Your task is to retrieve posts from specified subreddits."
            )
        ]
        
        self.agent = FunctionCallingAgentWorker(
            tools=self.tools,
            llm=self.llm,
            prefix_messages=prefix_messages,
            max_function_calls=10,
            allow_parallel_tool_calls=False,
            verbose=True
        ).as_agent()
        
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect posts from configured subreddits."""
        posts = []
        for subreddit in self.config["subreddits"]:
            try:
                prompt = f"Retrieve the latest posts from the subreddit '{subreddit}'"
                response = await self.agent.achat(prompt)
                
                # Process the response
                if hasattr(response, 'response') and isinstance(response.response, dict):
                    results = [response.response]
                elif hasattr(response, 'response') and isinstance(response.response, list):
                    results = response.response
                else:
                    results = []
                
                # Filter posts based on keywords
                for post in results:
                    if any(keyword.lower() in str(post.get("title", "")).lower() or 
                          keyword.lower() in str(post.get("selftext", "")).lower() 
                          for keyword in self.config["keywords"]):
                        # Add platform identifier
                        post["platform"] = "Reddit"
                        post["text"] = post.get("selftext", "")
                        post["url"] = f"https://reddit.com{post.get('permalink', '')}"
                        posts.append(post)
            except Exception as e:
                print(f"Error retrieving posts from r/{subreddit}: {str(e)}")
                continue
        return posts
    
    async def filter_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter Reddit posts based on score and relevance."""
        filtered = []
        for post in content:
            try:
                score = int(post.get("score", 0))
                if score >= self.config["min_score"]:
                    filtered.append(post)
            except (ValueError, TypeError):
                continue  # Skip posts with invalid scores
        return filtered
    
    def validate_config(self) -> bool:
        """Validate Reddit collector configuration."""
        required_fields = ["subreddits", "keywords", "min_score"]
        return all(field in self.config for field in required_fields) 