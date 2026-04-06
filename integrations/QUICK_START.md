# JARVIS Integrations - Quick Start Guide

Get JARVIS ecosystem integrations running in minutes.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Authentication Setup](#authentication-setup)
4. [First Workflow](#first-workflow)
5. [Next Steps](#next-steps)

---

## Installation

### Prerequisites

- Python 3.8+
- JARVIS core installed (Phase 4: Orchestrator)
- pip

### Install Dependencies

```bash
# Add to pyproject.toml or requirements.txt
pip install aiohttp django pydantic groq
```

### Verify Installation

```bash
python -c "from integrations import email, calendar; print('✅ Integrations ready')"
```

---

## Quick Start (5 minutes)

### 1. Import & Initialize

```python
import asyncio
from integrations import (
    email,
    calendar,
    github,
    slack,
    notion,
    iot,
    events
)

async def main():
    # Create integrations
    email_int = email.EmailIntegration()
    calendar_int = calendar.CalendarIntegration()
    slack_int = slack.SlackIntegration()
    
    # Authenticate
    for integration in [email_int, calendar_int, slack_int]:
        await integration.authenticate()
    
    print("✅ All integrations authenticated")

asyncio.run(main())
```

### 2. Try a Tool

```python
async def read_emails():
    await integration.authenticate()
    
    # Read inbox
    emails = await integration.read_inbox(limit=5, unread_only=True)
    
    for email in emails:
        print(f"From: {email.sender}")
        print(f"Subject: {email.subject}")
        print()

asyncio.run(read_emails())
```

### 3. Create Your First Workflow

```python
from integrations.workflow import Workflow, WorkflowStep, WorkflowEngine

async def simple_workflow():
    # Create workflow
    workflow = Workflow(name="hello_world")
    
    # Step: Read emails
    step1 = WorkflowStep(
        id="read_emails",
        action="email.read_inbox",
        parameters={"limit": 3, "unread_only": True}
    )
    
    # Step: Send Slack notification
    step2 = WorkflowStep(
        id="notify",
        action="slack.send_message",
        parameters={
            "channel": "#general",
            "content": "✅ You have $.read_emails unread emails"
        }
    )
    
    # Connect steps
    workflow.add_step(step1, as_start=True)
    workflow.add_step(step2)
    workflow.connect_steps("read_emails", "notify")
    
    # Execute
    engine = WorkflowEngine()
    engine.register_workflow("hello_world", workflow)
    engine.register_integration("email", email.EmailIntegration())
    engine.register_integration("slack", slack.SlackIntegration())
    
    result = await engine.execute("hello_world", context={})
    print(f"Workflow status: {result.status}")

asyncio.run(simple_workflow())
```

---

## Authentication Setup

### Step 1: Create Config Directory

```bash
mkdir -p jarvis_config
```

### Step 2: Get API Keys/Tokens

Choose which services to integrate:

#### Email (Gmail)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON

#### Calendar (Google Calendar)

Same as Gmail - use existing credentials

#### GitHub

1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Copy token

#### Slack

1. [Slack API](https://api.slack.com/apps)
2. Create new app
3. OAuth & Permissions → Copy Bot Token
4. Copy token

#### Notion

1. [Notion Integrations](https://www.notion.so/my-integrations)
2. Create new integration
3. Copy API key

### Step 3: Store Credentials

Create `jarvis_config/credentials.json`:

```json
{
  "email_service": {
    "type": "oauth",
    "service": "gmail",
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "refresh_token": "YOUR_REFRESH_TOKEN"
  },
  "github": {
    "type": "api_key",
    "token": "ghp_XXXXXXXXXXXX"
  },
  "slack": {
    "type": "api_key",
    "token": "xoxb-XXXXXXXXXXXX"
  },
  "notion": {
    "type": "api_key",
    "token": "secret_XXXXXXXXXXXX"
  }
}
```

### Step 4: Verify Setup

```python
from integrations.auth_manager import AuthManager

auth = AuthManager()

# Check stored credentials
if auth.has_credentials("email_service"):
    print("✅ Gmail credentials found")

if auth.has_credentials("github"):
    print("✅ GitHub token found")

if auth.has_credentials("slack"):
    print("✅ Slack token found")

if auth.has_credentials("notion"):
    print("✅ Notion token found")
```

---

## First Workflow

### Example: Email Summary to Slack

```python
import asyncio
from integrations import email, slack
from integrations.workflow import Workflow, WorkflowStep, WorkflowEngine

async def email_to_slack():
    """
    Workflow:
    1. Read latest email
    2. Get subject
    3. Send to Slack
    """
    
    # Create integrations
    email_int = email.EmailIntegration()
    slack_int = slack.SlackIntegration()
    
    # Authenticate
    await email_int.authenticate()
    await slack_int.authenticate()
    
    # Create workflow
    workflow = Workflow(name="email_to_slack")
    
    # Step 1: Read email
    step1 = WorkflowStep(
        id="get_email",
        action="email.read_inbox",
        parameters={"limit": 1, "unread_only": True}
    )
    
    # Step 2: Summarize
    step2 = WorkflowStep(
        id="summarize_email",
        action="email.summarize_email",
        parameters={"email_id": "$.get_email[0].id", "max_length": 200}
    )
    
    # Step 3: Send Slack message
    step3 = WorkflowStep(
        id="notify_slack",
        action="slack.send_message",
        parameters={
            "channel": "#alerts",
            "content": """
📧 New Email Alert

From: $.get_email[0].sender
Subject: $.get_email[0].subject

Summary:
$.summarize_email
            """
        }
    )
    
    # Connect workflow
    workflow.add_step(step1, as_start=True)
    workflow.add_step(step2)
    workflow.add_step(step3)
    
    workflow.connect_steps("get_email", "summarize_email")
    workflow.connect_steps("summarize_email", "notify_slack")
    
    # Execute
    engine = WorkflowEngine()
    engine.register_workflow("email_to_slack", workflow)
    engine.register_integration("email", email_int)
    engine.register_integration("slack", slack_int)
    
    print("Running workflow: email_to_slack\n")
    execution = await engine.execute("email_to_slack", context={})
    
    print(f"\n✅ Workflow complete")
    print(f"   Status: {execution.status}")
    print(f"   Duration: {execution.duration:.2f}s")
    print(f"   Steps executed: {len(execution.steps_executed)}")

# Run it
asyncio.run(email_to_slack())
```

**Output:**

```
Running workflow: email_to_slack

✅ Workflow complete
   Status: success
   Duration: 2.34s
   Steps executed: 3
```

---

## Common Workflows

### Morning Briefing

```python
async def morning_briefing():
    """Email + Calendar → Slack notification"""
    from integrations import email, calendar, slack
    
    email_int = email.EmailIntegration()
    calendar_int = calendar.CalendarIntegration()
    slack_int = slack.SlackIntegration()
    
    # Authenticate all
    for integration in [email_int, calendar_int, slack_int]:
        await integration.authenticate()
    
    # Get unread emails
    emails = await email_int.read_inbox(limit=5, unread_only=True)
    
    # Get today's calendar
    today_events = await calendar_int.get_events(
        start_date="2024-01-15",
        end_date="2024-01-15"
    )
    
    # Format message
    message = f"""
☀️ Good Morning!

📧 Unread Emails: {len(emails)}
📅 Today's Events: {len(today_events)}

Have a great day! 🚀
    """
    
    # Send to Slack
    await slack_int.send_message(
        channel="#morning-briefing",
        content=message
    )

asyncio.run(morning_briefing())
```

### Smart Home Automation

```python
async def evening_mode():
    """Control smart home devices"""
    from integrations.iot import IoTIntegration, SmartHomeAssistant
    
    iot = IoTIntegration()
    await iot.authenticate()
    
    assistant = SmartHomeAssistant(iot)
    await assistant.setup_scenes()
    
    # Get status
    status = await assistant.home_status()
    print(status)
    
    # Activate night scene
    await iot.activate_scene("night")

asyncio.run(evening_mode())
```

### GitHub Issue Tracking

```python
async def track_issues():
    """Sync GitHub issues to Notion"""
    from integrations import github, notion
    
    github_int = github.GitHubIntegration()
    notion_int = notion.NotionIntegration()
    
    for integration in [github_int, notion_int]:
        await integration.authenticate()
    
    # Get open issues
    issues = await github_int.get_issues(
        repo="myrepo",
        state="open",
        limit=10
    )
    
    # Create Notion page for each
    for issue in issues:
        await notion_int.create_page(
            title=f"[GitHub] Issue #{issue.number}",
            content=f"**Status**: {issue.state}\n\n{issue.body}",
            database="github-issues",
            tags=["github"] + issue.labels
        )

asyncio.run(track_issues())
```

---

## Event-Driven Automation

### Create a Trigger

```python
from integrations.events import EventsIntegration

async def setup_automation():
    events = EventsIntegration()
    
    # Create trigger: High-priority email
    trigger = await events.create_trigger(
        trigger_name="important_email",
        event_type="EMAIL_RECEIVED",
        conditions=[
            {"field": "data.priority", "operator": "equals", "value": "high"}
        ]
    )
    
    # Create automation: Send Slack + Save to Notion
    automation = await events.create_automation(
        automation_name="alert_important",
        trigger_id=trigger.id,
        actions=["slack.notify", "notion.create_page"]
    )
    
    print(f"✅ Automation created: {automation.name}")
    print(f"   Trigger: {automation.trigger.name}")
    print(f"   Actions: {', '.join(automation.actions)}")

asyncio.run(setup_automation())
```

---

## Using Orchestrator Bridge

Connect all integrations to JARVIS Orchestrator:

```python
from integrations.orchestrator_bridge import OrchestratorBridge
from integrations import email, calendar, github, slack, notion, iot

async def setup_orchestrator():
    # Create bridge
    bridge = OrchestratorBridge()
    
    # Register all integrations
    bridge.register_all_integrations([
        email.EmailIntegration(),
        calendar.CalendarIntegration(),
        github.GitHubIntegration(),
        slack.SlackIntegration(),
        notion.NotionIntegration(),
        iot.IoTIntegration(),
    ])
    
    # Discover tools (for Planner)
    tools = await bridge.tool_discovery()
    print("Available tools:")
    for integration, tools_list in tools.items():
        print(f"  {integration}: {len(tools_list)} tools")
    
    # Execute a tool directly (for Executor)
    result = await bridge.executor_interface.execute(
        tool_id="email.read_inbox",
        limit=5,
        unread_only=True
    )
    
    print(f"\n✅ Read {len(result)} emails via bridge")

asyncio.run(setup_orchestrator())
```

---

## Debugging

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("integrations")

# Now all integration calls will log details
```

### Check Integration Health

```python
async def health_check():
    email_int = email.EmailIntegration()
    
    if not await email_int.authenticate():
        print("❌ Email authentication failed")
        return
    
    if not await email_int.health_check():
        print("❌ Email service is down")
        return
    
    print("✅ Email integration is healthy")

asyncio.run(health_check())
```

### Test Tools Individually

```python
async def test_tools():
    email_int = email.EmailIntegration()
    await email_int.authenticate()
    
    # List available tools
    tools = email_int.get_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Execute a tool directly
    result = await email_int._execute_tool("read_inbox", limit=3)
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")

asyncio.run(test_tools())
```

---

## Next Steps

### 1. Explore Individual Integrations

- [Email Integration Guide](INTEGRATIONS_GUIDE.md#email-integration)
- [Calendar Integration Guide](INTEGRATIONS_GUIDE.md#calendar-integration)
- [GitHub Integration Guide](INTEGRATIONS_GUIDE.md#github-integration)
- [Slack Integration Guide](INTEGRATIONS_GUIDE.md#slack-integration)

### 2. Build Complex Workflows

Create multi-step workflows combining multiple services:
- Email → summarize → Notion + Slack
- GitHub → issues → Calendar reminder
- Calendar events → prepare agenda → Notion

### 3. Setup Event Triggers

Automate based on real-time events:
- High-priority emails → Alert to Slack
- New GitHub PR → Create Notion task
- Device offline → Send notification

### 4. Customize Integration

Add more services:
- Jira for project tracking
- Linear for issues
- Discord for notifications
- Zapier for additional connections

### 5. Monitor & Analyze

Track integration usage:
- View execution history
- Get statistics
- Debug errors
- Optimize performance

---

## Troubleshooting

### "Integration authentication failed"

**Problem**: Authentication error on startup

**Solution**:
1. Check `jarvis_config/credentials.json` exists
2. Verify credentials are valid
3. Check token expiration
4. Renew OAuth token if needed

```python
auth = AuthManager()
cred = auth.get_credentials("email_service")
if cred and cred.is_expired():
    print("⚠️  Credentials expired, need refresh")
```

### "Tool not found"

**Problem**: Tool execution fails with "Tool not found"

**Solution**:
1. Verify tool name spelling
2. Check integration is registered
3. List available tools

```python
integration = email.EmailIntegration()
tools = integration.get_tools()
print([t.name for t in tools])  # See available tools
```

### "Workflow execution failed"

**Problem**: Workflow doesn't complete

**Solution**:
1. Check error message in execution log
2. Verify context variables reference correct steps
3. Check all tools are registered

```python
execution = await engine.execute("workflow_name")
print(f"Status: {execution.status}")
print(f"Error: {execution.error}")
for step in execution.steps_executed:
    print(f"  {step}: {execution.results.get(step)}")
```

---

## Getting Help

- Check [INTEGRATIONS_GUIDE.md](INTEGRATIONS_GUIDE.md) for detailed API reference
- Review example workflows in [Examples](#common-workflows) section
- Check integration-specific documentation
- Enable debug logging for detailed output

---

## What's Next?

Phase 6 Ecosystem Controller is complete! 🎉

Next phases:
- **Phase 7**: Frontend UI dashboard
- **Phase 8**: Mobile app
- **Phase 9**: Advanced analytics
- **Phase 10**: Enterprise deployment

---

*Happy integrating!* 🚀

Last Updated: Phase 6 Ecosystem Controller - Complete
