"""
Slack/Discord Integration - Communication

Features:
- Send messages
- Read messages
- Create threads
- React to messages
- Mention users
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .base import Integration, ToolDefinition, IntegrationError


@dataclass
class Message:
    """Chat message."""
    id: str
    author: str
    content: str
    channel: str
    timestamp: str
    reactions: Dict[str, int] = None
    thread_id: Optional[str] = None
    
    def __post_init__(self):
        if self.reactions is None:
            self.reactions = {}


class SlackIntegration(Integration):
    """
    Slack/Discord integration.
    
    Enables messaging and notifications.
    """
    
    def __init__(self, auth_manager=None, platform: str = "slack"):
        """
        Initialize communication integration.
        
        Args:
            auth_manager: AuthManager instance
            platform: "slack" or "discord"
        """
        super().__init__(f"communication_{platform}", auth_manager=auth_manager)
        self.platform = platform
        self.mock_messages = []
        self.channels = ["general", "jarvis", "notifications"]
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="send_message",
            description="Send a message to a channel",
            parameters={"channel": str, "content": str, "thread_id": str},
            returns="str",  # message_id
            category="communication"
        ))
        
        self.register_tool(ToolDefinition(
            name="read_messages",
            description="Read messages from a channel",
            parameters={"channel": str, "limit": int},
            returns="List[Message]",
            category="communication"
        ))
        
        self.register_tool(ToolDefinition(
            name="mention_user",
            description="Mention a user in a message",
            parameters={"channel": str, "username": str, "content": str},
            returns="str",  # message_id
            category="communication"
        ))
        
        self.register_tool(ToolDefinition(
            name="react",
            description="Add reaction to a message",
            parameters={"message_id": str, "emoji": str},
            returns="bool",
            category="communication"
        ))
        
        self.register_tool(ToolDefinition(
            name="notify",
            description="Send urgent notification",
            parameters={"channel": str, "title": str, "content": str},
            returns="str",  # message_id
            category="communication"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate with platform."""
        if not self.auth_manager:
            self.is_authenticated = True
            return True
        
        cred = self.auth_manager.get_credentials(self.platform)
        if cred:
            self.is_authenticated = True
            return True
        
        return False
    
    async def health_check(self) -> bool:
        """Check platform health."""
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "send_message":
            return await self.send_message(
                channel=kwargs.get("channel"),
                content=kwargs.get("content"),
                thread_id=kwargs.get("thread_id")
            )
        elif tool_name == "read_messages":
            return await self.read_messages(
                channel=kwargs.get("channel"),
                limit=kwargs.get("limit", 20)
            )
        elif tool_name == "mention_user":
            return await self.mention_user(
                channel=kwargs.get("channel"),
                username=kwargs.get("username"),
                content=kwargs.get("content")
            )
        elif tool_name == "react":
            return await self.react(
                message_id=kwargs.get("message_id"),
                emoji=kwargs.get("emoji")
            )
        elif tool_name == "notify":
            return await self.notify(
                channel=kwargs.get("channel"),
                title=kwargs.get("title"),
                content=kwargs.get("content")
            )
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    async def send_message(self, channel: str, content: str,
                          thread_id: str = None) -> str:
        """
        Send a message.
        
        Args:
            channel: Target channel
            content: Message content
            thread_id: Optional thread ID
            
        Returns:
            Message ID
        """
        message_id = f"msg_{len(self.mock_messages)}"
        
        message = Message(
            id=message_id,
            author="JARVIS",
            content=content,
            channel=channel,
            timestamp=datetime.now().isoformat(),
            thread_id=thread_id
        )
        
        self.mock_messages.append(message)
        
        print(f"✉️  Message sent to #{channel}")
        return message_id
    
    async def read_messages(self, channel: str, limit: int = 20) -> List[Message]:
        """
        Read messages from a channel.
        
        Args:
            channel: Channel name
            limit: Max messages
            
        Returns:
            List of messages
        """
        messages = [m for m in self.mock_messages if m.channel == channel]
        return messages[-limit:]
    
    async def mention_user(self, channel: str, username: str,
                          content: str) -> str:
        """
        Mention a user in a message.
        
        Args:
            channel: Target channel
            username: User to mention
            content: Message content
            
        Returns:
            Message ID
        """
        full_message = f"@{username} {content}"
        return await self.send_message(channel, full_message)
    
    async def react(self, message_id: str, emoji: str) -> bool:
        """
        Add reaction to a message.
        
        Args:
            message_id: Message to react to
            emoji: Emoji reaction
            
        Returns:
            Success status
        """
        message = next((m for m in self.mock_messages if m.id == message_id), None)
        if message:
            message.reactions[emoji] = message.reactions.get(emoji, 0) + 1
            return True
        return False
    
    async def notify(self, channel: str, title: str, content: str) -> str:
        """
        Send urgent notification.
        
        Args:
            channel: Target channel
            title: Notification title
            content: Notification content
            
        Returns:
            Message ID
        """
        message = f"🚨 **{title}**\n{content}"
        return await self.send_message(channel, message)


class CommunicationAssistant:
    """High-level communication assistant."""
    
    def __init__(self, slack_integration: SlackIntegration):
        """
        Initialize communication assistant.
        
        Args:
            slack_integration: SlackIntegration instance
        """
        self.slack = slack_integration
    
    async def send_daily_digest(self, channel: str = "general") -> str:
        """Send daily digest to channel."""
        digest = """
📋 **Daily Digest** 

Good morning! Here's your summary for today:

✅ **Completed Tasks**
- Email briefing sent
- Calendar synced
- GitHub issues reviewed

📅 **Today's Schedule**
- 9:00 AM: Team Standup
- 2:00 PM: Project Meeting
- 4:00 PM: Focus Time

💬 **Pending Items**
- 3 unread emails
- 1 open issue awaiting review

Start your day strong! 💪
        """
        
        return await self.slack.send_message(channel, digest)
    
    async def notify_important_event(self, event: str) -> str:
        """Notify about important event."""
        return await self.slack.notify(
            channel="notifications",
            title="Important Event",
            content=event
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_slack():
        print("🧪 Slack Integration Test\n")
        
        slack = SlackIntegration(platform="slack")
        await slack.authenticate()
        
        # Send message
        msg_id = await slack.send_message("general", "Hello from JARVIS!")
        print(f"✅ Sent message: {msg_id}\n")
        
        # Read messages
        messages = await slack.read_messages("general", limit=5)
        print(f"📨 Found {len(messages)} messages\n")
    
    asyncio.run(test_slack())
