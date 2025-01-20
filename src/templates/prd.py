from typing import Dict, Any
import yaml
from datetime import datetime
from llama_index.llms.openai import OpenAI

class PRDGenerator:
    """Generate Product Requirements Documents from content."""
    
    def __init__(self, template_path: str):
        """Initialize the PRD generator."""
        with open(template_path, 'r') as f:
            templates = yaml.safe_load(f)
        self.template = templates["prd_template"]
        self.llm = OpenAI(model="gpt-4o-mini")
        
    async def generate_section(self, content: Dict[str, Any], section: str) -> str:
        """Generate a specific section of the PRD using LLM."""
        prompt = f"""
        Based on the following content about an AI agent idea, generate the {section} section for a PRD.
        Make it detailed, professional, and actionable.
        
        Content:
        Title: {content.get('title', '')}
        Text: {content.get('text', '')}
        URL: {content.get('url', '')}
        
        Generate the {section} section:
        """
        
        response = await self.llm.acomplete(prompt)
        return response.text.strip()
        
    async def generate_prd(self, content: Dict[str, Any]) -> str:
        """Generate a complete PRD from the content."""
        sections = {
            "title": content.get("title", "Untitled AI Agent Concept"),
            "overview": await self.generate_section(content, "Overview"),
            "problem_statement": await self.generate_section(content, "Problem Statement"),
            "solution": await self.generate_section(content, "Proposed Solution"),
            "features": await self.generate_section(content, "Key Features"),
            "technical_requirements": await self.generate_section(content, "Technical Requirements"),
            "market_analysis": await self.generate_section(content, "Market Analysis"),
            "timeline": await self.generate_section(content, "Implementation Timeline"),
            "resources": await self.generate_section(content, "Resources Required"),
            "metrics": await self.generate_section(content, "Success Metrics"),
            "source_url": content.get("url", ""),
            "platform": content.get("platform", "Unknown"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return self.template.format(**sections) 