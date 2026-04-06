"""
Email Integration - Gmail/Outlook Support

Features:
- Read emails
- Search inbox
- Summarize emails (with Groq)
- Draft and send replies
- Manage labels/folders
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from .base import Integration, ToolDefinition, IntegrationError


@dataclass
class Email:
    """Email message."""
    id: str
    subject: str
    from_address: str
    to_address: str
    body: str
    timestamp: str
    read: bool = False
    labels: List[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class EmailIntegration(Integration):
    """
    Email service integration.
    
    Supports: Gmail, Outlook (via mock HTTP API)
    """
    
    def __init__(self, auth_manager=None, provider: str = "gmail"):
        """
        Initialize email integration.
        
        Args:
            auth_manager: AuthManager instance
            provider: "gmail" or "outlook"
        """
        super().__init__(f"email_{provider}", auth_manager=auth_manager)
        self.provider = provider
        self.mock_emails = []  # Mock data for testing
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="read_inbox",
            description="Read emails from inbox",
            parameters={"limit": int, "unread_only": bool},
            returns="List[Email]",
            category="email"
        ))
        
        self.register_tool(ToolDefinition(
            name="summarize_email",
            description="Summarize an email using Groq",
            parameters={"email_id": str, "max_length": int},
            returns="str",
            category="email"
        ))
        
        self.register_tool(ToolDefinition(
            name="draft_reply",
            description="Draft a reply to an email",
            parameters={"email_id": str, "tone": str},
            returns="str",
            category="email"
        ))
        
        self.register_tool(ToolDefinition(
            name="send_email",
            description="Send an email",
            parameters={"to": str, "subject": str, "body": str},
            returns="bool",
            category="email"
        ))
        
        self.register_tool(ToolDefinition(
            name="search_emails",
            description="Search emails by query",
            parameters={"query": str, "limit": int},
            returns="List[Email]",
            category="email"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate with email provider."""
        if not self.auth_manager:
            print(f"⚠️  No auth manager for {self.provider}")
            self.is_authenticated = True  # Mock auth
            return True
        
        cred = self.auth_manager.get_credentials(self.provider)
        if cred:
            self.is_authenticated = True
            return True
        
        print(f"❌ No credentials for {self.provider}")
        return False
    
    async def health_check(self) -> bool:
        """Check email service health."""
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "read_inbox":
            return await self.read_inbox(
                limit=kwargs.get("limit", 10),
                unread_only=kwargs.get("unread_only", False)
            )
        elif tool_name == "search_emails":
            return await self.search_emails(
                query=kwargs.get("query", ""),
                limit=kwargs.get("limit", 10)
            )
        elif tool_name == "summarize_email":
            return await self.summarize_email(
                email_id=kwargs.get("email_id"),
                max_length=kwargs.get("max_length", 200)
            )
        elif tool_name == "draft_reply":
            return await self.draft_reply(
                email_id=kwargs.get("email_id"),
                tone=kwargs.get("tone", "professional")
            )
        elif tool_name == "send_email":
            return await self.send_email(
                to=kwargs.get("to"),
                subject=kwargs.get("subject"),
                body=kwargs.get("body")
            )
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    async def read_inbox(self, limit: int = 10,
                        unread_only: bool = False) -> List[Email]:
        """
        Read emails from inbox.
        
        Args:
            limit: Max emails to retrieve
            unread_only: Only unread emails
            
        Returns:
            List of Email objects
        """
        # In production: Call Gmail/Outlook API
        # For now: Return mock data
        
        emails = self._get_mock_emails()
        
        if unread_only:
            emails = [e for e in emails if not e.read]
        
        return emails[:limit]
    
    async def search_emails(self, query: str, limit: int = 10) -> List[Email]:
        """
        Search emails by query.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching emails
        """
        emails = self._get_mock_emails()
        
        # Simple mock search
        results = []
        for email in emails:
            if (query.lower() in email.subject.lower() or
                query.lower() in email.body.lower() or
                query.lower() in email.from_address.lower()):
                results.append(email)
        
        return results[:limit]
    
    async def summarize_email(self, email_id: str,
                            max_length: int = 200) -> str:
        """
        Summarize an email.
        
        In production: Use Groq to summarize
        """
        email = next((e for e in self._get_mock_emails() if e.id == email_id), None)
        if not email:
            return "Email not found"
        
        # Mock summarization (in production: use Groq)
        body = email.body
        if len(body) > max_length:
            return body[:max_length] + "..."
        return body
    
    async def draft_reply(self, email_id: str, tone: str = "professional") -> str:
        """
        Draft a reply to an email.
        
        In production: Use Groq to generate reply
        """
        email = next((e for e in self._get_mock_emails() if e.id == email_id), None)
        if not email:
            return "Email not found"
        
        # Mock reply generation
        tones = {
            "professional": "Thank you for your email. I appreciate your input.",
            "casual": "Thanks for reaching out! Appreciate the message.",
            "urgent": "Thanks for this. Let me get back to you quickly."
        }
        
        return tones.get(tone, tones["professional"])
    
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            Success status
        """
        # In production: Call Gmail/Outlook API
        print(f"✉️  Sending email to {to}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body[:50]}...")
        
        # Mock sending
        return True
    
    def _get_mock_emails(self) -> List[Email]:
        """Get mock emails for testing."""
        if self.mock_emails:
            return self.mock_emails
        
        now = datetime.now()
        self.mock_emails = [
            Email(
                id="1",
                subject="Welcome to JARVIS",
                from_address="team@jarvis.ai",
                to_address="user@example.com",
                body="Welcome to your new ecosystem controller! Get started with integrations.",
                timestamp=(now - timedelta(hours=1)).isoformat(),
                read=False,
                labels=["INBOX"]
            ),
            Email(
                id="2",
                subject="Project Update",
                from_address="manager@company.com",
                to_address="user@example.com",
                body="Here's the latest project status and timeline for Q2.",
                timestamp=(now - timedelta(hours=3)).isoformat(),
                read=True,
                labels=["INBOX", "WORK"]
            ),
            Email(
                id="3",
                subject="Meeting Tomorrow",
                from_address="colleague@company.com",
                to_address="user@example.com",
                body="Can we reschedule our meeting to 2 PM tomorrow?",
                timestamp=(now - timedelta(hours=6)).isoformat(),
                read=False,
                labels=["INBOX", "MEETING"]
            ),
        ]
        
        return self.mock_emails


class EmailAssistant:
    """High-level email assistant."""
    
    def __init__(self, email_integration: EmailIntegration, brain=None):
        """
        Initialize email assistant.
        
        Args:
            email_integration: EmailIntegration instance
            brain: JARVIS brain (for Groq)
        """
        self.email = email_integration
        self.brain = brain
    
    async def morning_briefing(self) -> str:
        """Generate morning email briefing."""
        emails = await self.email.read_inbox(limit=5, unread_only=True)
        
        if not emails:
            return "✅ No unread emails - inbox is clear!"
        
        summary = f"📧 Morning Briefing: {len(emails)} unread email(s)\n\n"
        
        for email in emails:
            summary += f"• {email.subject}\n"
            summary += f"  From: {email.from_address}\n"
            summary += f"  Preview: {email.body[:80]}...\n\n"
        
        return summary
    
    async def inbox_summary(self, limit: int = 10) -> str:
        """Summarize inbox with key points."""
        emails = await self.email.read_inbox(limit=limit)
        
        summary = f"📊 Inbox Summary: {len(emails)} email(s)\n\n"
        
        for email in emails:
            summary += f"• [{email.from_address}] {email.subject}\n"
        
        return summary


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_email():
        print("🧪 Email Integration Test\n")
        
        email = EmailIntegration(provider="gmail")
        await email.authenticate()
        
        # Read inbox
        emails = await email.read_inbox(limit=3)
        print(f"✅ Found {len(emails)} emails\n")
        
        for email_obj in emails:
            print(f"From: {email_obj.from_address}")
            print(f"Subject: {email_obj.subject}")
            print(f"Read: {email_obj.read}\n")
    
    asyncio.run(test_email())
