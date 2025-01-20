from typing import Dict, Any
import yaml
from composio_llamaindex import ComposioToolSet, Action

class EmailDelivery:
    """Handle email delivery of PRDs."""
    
    def __init__(self, template_path: str, recipient: str):
        """Initialize the email delivery system."""
        with open(template_path, 'r') as f:
            templates = yaml.safe_load(f)
        self.template = templates["email_template"]
        self.recipient = recipient
        self.toolset = ComposioToolSet()
        self.tools = self.toolset.get_tools(actions=[Action.GMAIL_SEND_EMAIL])
        
    def format_email(self, content: Dict[str, Any], prd_content: str) -> Dict[str, str]:
        """Format the email content using the template."""
        email_content = self.template.format(
            recipient=self.recipient,
            title=content.get("title", "Untitled AI Agent Concept"),
            platform=content.get("platform", "Unknown"),
            relevance_score=int(content.get("relevance_score", 0) * 10),
            summary=content.get("text", "")[:500] + "...",
            key_points=self._extract_key_points(content)
        )
        
        return {
            "subject": f"AI Agent Opportunity Alert: {content.get('title', 'New Opportunity')}",
            "body": email_content,
            "attachment": prd_content
        }
        
    def _extract_key_points(self, content: Dict[str, Any]) -> str:
        """Extract key points from the content."""
        # This could be enhanced with LLM for better extraction
        return "\n".join([
            "- Original post has high engagement",
            "- Matches current AI agent trends",
            "- Technical implementation appears feasible",
            "- Market opportunity identified"
        ])
        
    async def send_email(self, content: Dict[str, Any], prd_content: str) -> bool:
        """Send the email with the PRD attached."""
        email_data = self.format_email(content, prd_content)
        
        try:
            await self.tools.gmail_send_email(
                to=self.recipient,
                subject=email_data["subject"],
                body=email_data["body"],
                attachments=[{
                    "filename": "opportunity_prd.md",
                    "content": prd_content
                }]
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False 