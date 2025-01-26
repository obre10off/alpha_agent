import dotenv
from typing import Dict, Any, List
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.agent import FunctionCallingAgentWorker
from composio_llamaindex import Action, ComposioToolSet
import yaml
import logging
from datetime import datetime
import os

dotenv.load_dotenv()

class GmailDelivery:
    """Handle email delivery of PRDs and AI opportunity alerts."""
    
    def __init__(self, api_key: str, config_path: str):
        """
        Initialize the Gmail delivery system.
        
        Args:
            api_key: Composio API key
            config_path: Path to email templates configuration
        """
        self.llm = OpenAI(model="gpt-4o")
        self.composio_toolset = ComposioToolSet(api_key=api_key)
        self.tools = self.composio_toolset.get_tools(actions=['GMAIL_SEND_EMAIL'])
        
        # Load email template (changed from templates to template)
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self.template = config.get('email_template', '')  # Changed from email_templates
            if not self.template:
                raise ValueError("Email template not found in configuration file")
            
        self.agent = FunctionCallingAgentWorker(
            tools=self.tools,
            llm=self.llm,
            prefix_messages=[
                ChatMessage(
                    role="system",
                    content="You are now a integration agent, and what ever you are requested, "
                           "you will try to execute utilizing your tools."
                ),
            ],
            max_function_calls=10,
            allow_parallel_tool_calls=False,
            verbose=True,
        ).as_agent()
        
    async def send_opportunity_alert(self, 
                                   recipient: str, 
                                   opportunities: List[Dict[str, Any]], 
                                   prd_content: str = None) -> bool:
        """
        Send an email alert about new AI opportunities.
        
        Args:
            recipient: Email recipient
            opportunities: List of opportunity dictionaries
            prd_content: Optional PRD content to attach
        """
        try:
            # Format email content using template
            email_content = self._format_opportunity_email(opportunities)
            
            # Prepare email request
            email_request = (
                f"Send an email to {recipient} "
                f"with the subject: 'AI Opportunity Alert - {datetime.now().strftime('%Y-%m-%d')}' "
                f"and the following body:\n\n{email_content}"
            )
            
            # Add attachment if PRD is provided
            if prd_content:
                email_request += (
                    f"\n\nPlease attach the following content as 'opportunity_prd.md':\n"
                    f"{prd_content}"
                )
            
            # Send email using agent
            response = await self.agent.achat(email_request)
            
            logging.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False
            
    def _format_opportunity_email(self, opportunities: List[Dict[str, Any]]) -> str:
        """Format opportunities into email content using template."""
        template = self.template
        
        # Format each opportunity
        opportunity_sections = []
        for opp in opportunities:
            section = (
                f"Title: {opp.get('title', 'Untitled Opportunity')}\n"
                f"Source: {opp.get('source', 'Unknown')}\n"
                f"Relevance Score: {int(opp.get('relevance_score', 0) * 100)}%\n"
                f"URL: {opp.get('url', 'No URL provided')}\n"
                f"Summary: {opp.get('summary', 'No summary available')[:500]}...\n"
                f"Key Points:\n{self._format_key_points(opp.get('key_points', []))}\n"
            )
            opportunity_sections.append(section)
            
        # Combine all sections
        all_opportunities = "\n\n".join(opportunity_sections)
        
        # Format final email
        return template.format(
            date=datetime.now().strftime('%Y-%m-%d'),
            opportunities=all_opportunities,
            total_count=len(opportunities)
        )
        
    def _format_key_points(self, points: List[str]) -> str:
        """Format key points into bullet points."""
        return "\n".join(f"- {point}" for point in points)

    async def send_email(self, content: Dict[str, Any], prd_content: str) -> bool:
        """Send email with content and PRD."""
        try:
            # Format email using template
            email_content = self.template.format(
                title=content.get('title', 'Untitled'),
                platform=content.get('source', 'Unknown'),
                relevance_score=int(content.get('relevance_score', 0) * 10),
                summary=content.get('text', 'No summary available')[:300],
                key_points=self._format_key_points(content.get('key_points', [])),
                recipient=os.getenv('EMAIL_RECIPIENT', 'User')
            )

            # Create temporary PRD file
            temp_prd_path = "temp_prd.md"
            with open(temp_prd_path, "w") as f:
                f.write(prd_content)

            try:
                # Prepare email request
                email_request = {
                    "recipient_email": os.getenv('EMAIL_RECIPIENT'),
                    "subject": f"AI Agent Opportunity: {content.get('title', 'New Opportunity')}",
                    "body": email_content,
                    "attachment": temp_prd_path  # Use file path instead of content directly
                }

                # Send email using agent
                response = await self.agent.achat(
                    f"Send this email with the attachment: {str(email_request)}"
                )
                
                return True
            finally:
                # Clean up temporary file
                if os.path.exists(temp_prd_path):
                    os.remove(temp_prd_path)
                
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False 