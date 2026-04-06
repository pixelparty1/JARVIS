# JARVIS Integrations Guide

Complete reference for the JARVIS ecosystem integration system (Phase 6).

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Integrations](#integrations)
4. [Setup & Authentication](#setup-authentication)
5. [Workflow Automation](#workflow-automation)
6. [Events & Triggers](#events-triggers)
7. [Orchestrator Bridge](#orchestrator-bridge)
8. [Examples](#examples)
9. [API Reference](#api-reference)

---

## Overview

Phase 6 transforms JARVIS into a unified ecosystem controller, seamlessly orchestrating across:

- **Email** (Gmail, Outlook)
- **Calendar** (Google Calendar, Outlook Calendar)
- **Notion** (Knowledge management)
- **GitHub** (Development workflow)
- **Slack** (Team communication)
- **IoT/Smart Home** (Device control)
- **Events** (Trigger-based automation)

### Key Features

✅ **Modular Architecture** - Plug-and-play integrations  
✅ **OAuth Support** - Secure credential management  
✅ **Async-First** - Non-blocking operations  
✅ **Tool Registry** - Self-describing APIs  
✅ **Workflow Engine** - Multi-step orchestration  
✅ **Event System** - Real-time triggers  
✅ **Orchestrator Bridge** - Unified tool discovery & execution  

---

## Architecture

### Module Structure

```
integrations/
├── __init__.py                 # Module exports
├── base.py                     # Base classes & infrastructure
├── auth_manager.py             # Credential management
├── email.py                    # Email integration
├── calendar.py                 # Calendar integration
├── notion.py                   # Notion integration
├── github.py                   # GitHub integration
├── slack.py                    # Slack/Discord integration
├── iot.py                      # Smart home control
├── events.py                   # Event-driven automation
└── orchestrator_bridge.py      # JARVIS orchestrator bridge
```

### Component Relationships

```
JARVIS Orchestrator (Phase 4)
    ↓
OrchestratorBridge
    ├── IntegrationRegistry (tool discovery)
    ├── PlannerToolInterface (for Planner agent)
    ├── ExecutorExecutionInterface (for Executor agent)
    └── WorkflowEngine
        ├── EmailIntegration
        ├── CalendarIntegration
        ├── NotionIntegration
        ├── GitHubIntegration
        ├── SlackIntegration
        ├── IoTIntegration
        └── EventsIntegration
            ├── AuthManager (credentials)
            └── EventBus (pub/sub)
```

---

## Integrations

### Email Integration

**Service**: Gmail, Outlook

**Purpose**: Read, search, summarize, and send emails

#### Available Tools

```python
# Read inbox
read_inbox(limit=10, unread_only=True)
# Returns: List[Email]

# Search emails
search_emails(query="from:boss", limit=20)
# Returns: List[Email]

# Summarize email
summarize_email(email_id="123", max_length=500)
# Returns: str (summarized content)

# Draft reply
draft_reply(email_id="123", tone="professional")
# Returns: str (draft text)

# Send email
send_email(to="user@example.com", subject="Hi", body="Hello")
# Returns: bool
```

#### High-Level Assistant

```python
from integrations.email import EmailAssistant

assistant = EmailAssistant(email_integration)

# Get morning briefing
briefing = await assistant.morning_briefing()
# Returns: str (summary of unread emails)

# Get inbox summary
summary = await assistant.inbox_summary(limit=10)
# Returns: str (formatted inbox overview)
```

#### Usage Example

```python
import asyncio
from integrations.email import EmailIntegration

async def main():
    email = EmailIntegration()
    await email.authenticate()
    
    # Read emails
    emails = await email.read_inbox(limit=5, unread_only=True)
    for email in emails:
        print(f"From: {email.sender}")
        print(f"Subject: {email.subject}")
        print()

asyncio.run(main())
```

---

### Calendar Integration

**Service**: Google Calendar, Outlook Calendar

**Purpose**: View, create, and manage calendar events with smart scheduling

#### Available Tools

```python
# Get events in date range
get_events(start_date="2024-01-01", end_date="2024-01-31", limit=50)
# Returns: List[CalendarEvent]

# Find free slot
find_free_slot(duration_minutes=30, date="2024-01-15", start_hour=9, end_hour=17)
# Returns: Tuple[str, str] (start_time, end_time)

# Create event
create_event(
    title="Team Standup",
    start="2024-01-15T09:00:00",
    end="2024-01-15T09:30:00",
    description="Daily sync",
    location="Conference Room"
)
# Returns: bool

# Modify event
modify_event(event_id="123", title="Updated", start="2024-01-15T10:00:00")
# Returns: bool

# Delete event
delete_event(event_id="123")
# Returns: bool
```

#### Smart Scheduling

The `find_free_slot()` tool intelligently finds available time:

- Analyzes existing calendar events
- Finds first gap >= requested duration
- Respects work hours (default 9 AM - 5 PM)
- Returns exact ISO timestamp for start and end

```python
# Find 30-minute slot on Jan 15
slot = await calendar.find_free_slot(
    duration_minutes=30,
    date="2024-01-15",
    start_hour=9,
    end_hour=17
)
# Returns: ("2024-01-15T10:00:00", "2024-01-15T10:30:00")

# Auto-schedule
await calendar.create_event(
    title="Team Meeting",
    start=slot[0],
    end=slot[1]
)
```

---

### Notion Integration

**Service**: Notion

**Purpose**: Create and manage knowledge base, sync with JARVIS memory

#### Available Tools

```python
# Create page
create_page(
    title="Project X Kickoff",
    content="# Project Overview\n\nKey points...",
    database="projects",
    tags=["urgent", "Q1"]
)
# Returns: str (page_id)

# Update page
update_page(page_id="123", title="New Title", content="Updated content")
# Returns: bool

# Get page
get_page(page_id="123")
# Returns: NotionPage

# Query database
query_database(database="projects", query="priority:high", limit=20)
# Returns: List[NotionPage]

# Delete page
delete_page(page_id="123")
# Returns: bool
```

#### Memory System Integration

Notion automatically syncs with JARVIS memory system:

```python
from integrations.notion import NotionIntegration

notion = NotionIntegration()

# Sync JARVIS memories to Notion
await notion.sync_from_memory(jarvis_memories)
# Automatically creates Notion pages from memory objects
```

---

### GitHub Integration

**Service**: GitHub

**Purpose**: Manage repositories, track issues, monitor pull requests

#### Available Tools

```python
# List repositories
list_repos(limit=20)
# Returns: List[GitHubRepo]

# Get issues
get_issues(repo="jarvis-ai", state="open", limit=50)
# Returns: List[GitHubIssue]

# Create issue
create_issue(
    repo="jarvis-ai",
    title="Bug: Voice recognition fails",
    body="Steps to reproduce...",
    labels=["bug", "high-priority"]
)
# Returns: int (issue_number)

# Close issue
close_issue(repo="jarvis-ai", issue_number=42)
# Returns: bool

# Search issues
search_issues(query="voice recognition", limit=10)
# Returns: List[GitHubIssue]
```

---

### Slack Integration

**Service**: Slack, Discord

**Purpose**: Send messages, notifications, and daily digests

#### Available Tools

```python
# Send message
send_message(channel="#engineering", content="Deployment complete ✅")
# Returns: bool

# Read messages
read_messages(channel="#engineering", limit=50)
# Returns: List[Message]

# Mention user
mention_user(channel="#engineering", username="john", content="Review needed")
# Returns: bool

# React to message
react(message_id="123", emoji="thumbsup")
# Returns: bool

# Send notification
notify(
    channel="#alerts",
    title="High CPU Usage",
    content="Server temp-2 at 95% CPU"
)
# Returns: bool
```

---

### IoT Integration

**Service**: Smart home hub (HTTP-based)

**Purpose**: Control lights, thermostats, and other smart devices

#### Available Tools

```python
# List devices
list_devices(device_type="light", room="living_room")
# Returns: List[SmartDevice]

# Get device status
get_device(device_id="light_1")
# Returns: SmartDevice

# Control device
control_device(device_id="light_1", command="turn_on", parameters={})
# Returns: bool

# Set light
set_light(device_id="light_1", power=True, brightness=80, color="warm_white")
# Returns: bool

# Set temperature
set_temperature(device_id="thermostat_1", temperature=72)
# Returns: bool

# Activate scene
activate_scene(scene_name="morning")
# Returns: bool
```

#### Smart Home Scenes

Pre-configured scenes for common scenarios:

```python
# Morning scene: Lights on, speaker on
await iot.activate_scene("morning")

# Night scene: Lights off, temp to 68°F
await iot.activate_scene("night")

# Work scene: Bright lights, no speaker
await iot.activate_scene("work")
```

---

### Events Integration

**Service**: Event system

**Purpose**: Monitor events and trigger automated workflows

#### Available Tools

```python
# Create trigger
create_trigger(
    trigger_name="high_priority_email",
    event_type="EMAIL_RECEIVED",
    conditions=[{"field": "data.priority", "operator": "equals", "value": "high"}]
)
# Returns: Trigger

# Create automation
create_automation(
    automation_name="notify_important",
    trigger_id="trigger_1",
    actions=["slack.notify", "calendar.reminder"]
)
# Returns: Automation

# List triggers
list_triggers()
# Returns: List[Trigger]

# Get automation details
get_automation(automation_id="auto_1")
# Returns: Automation

# Emit event
emit_event(
    event_type="EMAIL_RECEIVED",
    source="gmail",
    data={"sender": "boss@company.com", "priority": "high"}
)
# Returns: Event
```

#### Event Types

```python
EMAIL_RECEIVED = "email.received"
EMAIL_READ = "email.read"
CALENDAR_EVENT = "calendar.event_created"
GITHUB_PR_CREATED = "github.pr_created"
GITHUB_ISSUE_CREATED = "github.issue_created"
SLACK_MESSAGE = "slack.message"
DEVICE_STATE_CHANGE = "device.state_changed"
DEVICE_OFFLINE = "device.offline"
```

---

## Setup & Authentication

### OAuth Setup

#### Gmail

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Store credentials in `jarvis_config/credentials.json`:

```json
{
  "email_service": {
    "type": "oauth",
    "service": "gmail",
    "client_id": "your_client_id",
    "client_secret": "your_secret",
    "refresh_token": "your_refresh_token",
    "expires_at": "2024-12-31T23:59:59"
  }
}
```

#### Google Calendar

Similar to Gmail:

1. Enable Google Calendar API in Cloud Console
2. Use same OAuth credentials
3. Store in credentials.json with service name "google_calendar"

#### GitHub

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` and `read:user` scopes
3. Store as API key:

```json
{
  "github": {
    "type": "api_key",
    "token": "gh_xxxxxxxxxxxx"
  }
}
```

#### Slack

1. Go to [Slack API](https://api.slack.com)
2. Create new app
3. Get Bot Token from OAuth & Permissions
4. Store:

```json
{
  "slack": {
    "type": "api_key",
    "token": "xoxb-xxxxxxxxxxxx"
  }
}
```

#### Notion

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create new integration
3. Get API key
4. Store:

```json
{
  "notion": {
    "type": "api_key",
    "token": "secret_xxxxxxxxxxxx"
  }
}
```

### Credential Management

```python
from integrations.auth_manager import AuthManager

auth = AuthManager()

# Store credentials
auth.store_credentials(
    service="gmail",
    cred_type="oauth",
    data={
        "access_token": "ya29...",
        "refresh_token": "1//..."
    },
    expires_in=3600  # 1 hour
)

# Retrieve credentials
cred = auth.get_credentials("gmail")
if cred and not cred.is_expired():
    access_token = cred.data["access_token"]

# Register refresh callback
def refresh_gmail_token():
    # Implement token refresh logic
    new_token = get_new_token_from_google()
    return new_token

auth.register_refresh_callback("gmail", refresh_gmail_token)

# Rotate credentials
auth.rotate_credentials("gmail", new_data)

# Remove credentials
auth.remove_credentials("gmail")
```

---

## Workflow Automation

### Workflow Definition

Define multi-step workflows using the DAG (directed acyclic graph) model:

```python
from integrations.workflow import Workflow, WorkflowStep, WorkflowEngine

# Create workflow
workflow = Workflow(name="morning_briefing")

# Define steps
step1 = WorkflowStep(
    id="read_emails",
    action="email.read_inbox",
    parameters={"limit": 10, "unread_only": True}
)

step2 = WorkflowStep(
    id="summarize",
    action="email.summarize_email",
    parameters={"email_id": "$.read_emails[0].id", "max_length": 200}
)

step3 = WorkflowStep(
    id="notify_slack",
    action="slack.send_message",
    parameters={
        "channel": "#morning-briefing",
        "content": "Morning Summary:\n$.summarize"
    }
)

# Connect steps
workflow.add_step(step1, as_start=True)
workflow.add_step(step2)
workflow.add_step(step3)

workflow.connect_steps("read_emails", "summarize")
workflow.connect_steps("summarize", "notify_slack")

# Execute workflow
engine = WorkflowEngine()
engine.register_workflow(workflow.name, workflow)
engine.register_integration("email", email_integration)
engine.register_integration("slack", slack_integration)

execution = await engine.execute("morning_briefing", context={})
print(f"Status: {execution.status}")
print(f"Duration: {execution.duration}s")
```

### Context Variables

Steps can reference results from previous steps using `$.step_id` notation:

```python
# Step 1 reads emails, returns List[Email]
# Result stored as: context["read_emails"] = [Email, Email, ...]

# Step 2 can reference:
"email_id": "$.read_emails[0].id"  # Gets ID of first email
"subject": "$.read_emails[0].subject"  # Gets subject

# Step 3 can reference step 2 result:
"content": "Summary: $.summarize"  # Embeds summarized text
```

### Predefined Workflows

Three example workflows included:

#### 1. Email to Notion

```python
workflow = create_email_to_notion_workflow()
# Flow: Read emails → Summarize → Create Notion page
```

#### 2. Calendar Reminder

```python
workflow = create_calendar_reminder_workflow()
# Flow: Get upcoming events → Format → Send Slack notification
```

#### 3. GitHub Digest

```python
workflow = create_github_digest_workflow()
# Flow: List repos → Get issues → Create summary → Notion page
```

### Error Handling

Steps can have error handlers:

```python
step = WorkflowStep(
    id="critical_task",
    action="email.send_email",
    parameters={"to": "admin@company.com", "subject": "Alert"},
    on_error="send_fallback_notification"  # Alternative step on failure
)
```

---

## Events & Triggers

### Creating Triggers

```python
from integrations.events import EventsIntegration, TriggerCondition

events = EventsIntegration()

# Example 1: High-priority email trigger
trigger = await events.create_trigger(
    trigger_name="high_priority_email",
    event_type="EMAIL_RECEIVED",
    conditions=[
        {"field": "data.priority", "operator": "equals", "value": "high"},
        {"field": "data.sender", "operator": "contains", "value": "boss"}
    ]
)

# Example 2: Any device offline
trigger = await events.create_trigger(
    trigger_name="device_down",
    event_type="DEVICE_OFFLINE",
    conditions=[]  # Matches all events of this type
)
```

### Creating Automations

```python
# Link trigger to actions
automation = await events.create_automation(
    automation_name="alert_important_email",
    trigger_id=trigger.id,
    actions=[
        "slack.notify",
        "email.draft_reply",
        "calendar.create_event"
    ]
)
```

### Emitting Events

```python
# Simulate or emit real events
event = await events.emit_event(
    event_type="EMAIL_RECEIVED",
    source="gmail",
    data={
        "sender": "boss@company.com",
        "priority": "high",
        "subject": "Urgent: Q1 Planning"
    }
)
# Triggers matching automations automatically execute
```

---

## Orchestrator Bridge

### Tool Discovery (for Planner)

The Planner agent discovers available tools:

```python
from integrations.orchestrator_bridge import OrchestratorBridge

bridge = OrchestratorBridge()

# Register all integrations
bridge.register_all_integrations([
    email_integration,
    calendar_integration,
    github_integration,
    slack_integration,
    notion_integration,
    iot_integration,
    events_integration
])

# Discover tools
tools = await bridge.tool_discovery()
# Returns: {
#   "email": [
#     {"id": "email.read_inbox", "description": "..."},
#     {"id": "email.send_email", "description": "..."},
#     ...
#   ],
#   "calendar": [...],
#   ...
# }
```

### Tool Execution (for Executor)

The Executor runs selected tools:

```python
# Execute a single tool
result = await bridge.executor_interface.execute(
    tool_id="email.read_inbox",
    limit=10,
    unread_only=True
)

# Result:
# List[Email] with 10 unread emails
```

### Multi-Step Execution

```python
# Plan several actions
actions = [
    {
        "tool_id": "email.read_inbox",
        "parameters": {"limit": 5, "unread_only": True}
    },
    {
        "tool_id": "email.summarize_email",
        "parameters": {"email_id": "123", "max_length": 300}
    },
    {
        "tool_id": "slack.send_message",
        "parameters": {"channel": "#updates", "content": "Summary..."}
    }
]

# Execute plan
results = await bridge.execute_plan(actions)
```

---

## Examples

### Example 1: Morning Briefing Workflow

```python
import asyncio
from integrations import email, calendar, slack, notion
from integrations.workflow import Workflow, WorkflowStep, WorkflowEngine

async def morning_briefing():
    # Setup
    email_int = email.EmailIntegration()
    calendar_int = calendar.CalendarIntegration()
    slack_int = slack.SlackIntegration()
    
    for integration in [email_int, calendar_int, slack_int]:
        await integration.authenticate()
    
    # Create workflow
    workflow = Workflow(name="morning_briefing")
    
    # Step 1: Get unread emails
    step1 = WorkflowStep(
        id="get_emails",
        action="email.read_inbox",
        parameters={"limit": 5, "unread_only": True}
    )
    
    # Step 2: Get today's calendar
    step2 = WorkflowStep(
        id="get_calendar",
        action="calendar.get_events",
        parameters={"start_date": "2024-01-15", "end_date": "2024-01-15"}
    )
    
    # Step 3: Send Slack message
    step3 = WorkflowStep(
        id="notify",
        action="slack.send_message",
        parameters={
            "channel": "#morning",
            "content": "Good morning! 📅\n\nEmails: $.get_emails\n\nCalendar: $.get_calendar"
        }
    )
    
    # Connect
    workflow.add_step(step1, as_start=True)
    workflow.add_step(step2)
    workflow.add_step(step3)
    
    workflow.connect_steps("get_emails", "notify")
    workflow.connect_steps("get_calendar", "notify")
    
    # Execute
    engine = WorkflowEngine()
    engine.register_workflow("morning_briefing", workflow)
    engine.register_integration("email", email_int)
    engine.register_integration("calendar", calendar_int)
    engine.register_integration("slack", slack_int)
    
    execution = await engine.execute("morning_briefing", context={})
    
    print(f"✅ Workflow complete")
    print(f"   Status: {execution.status}")
    print(f"   Duration: {execution.duration:.1f}s")

asyncio.run(morning_briefing())
```

### Example 2: Smart Home Evening Scene

```python
import asyncio
from integrations.iot import IoTIntegration, SmartHomeAssistant

async def evening_routine():
    iot = IoTIntegration()
    await iot.authenticate()
    
    assistant = SmartHomeAssistant(iot)
    await assistant.setup_scenes()
    
    # Activate evening scene
    print("Setting up for evening...\n")
    
    # Turn off work lights
    await iot.set_light(
        device_id="light_1",
        power=False
    )
    
    # Dim bedroom lights
    await iot.set_light(
        device_id="light_2",
        power=True,
        brightness=30
    )
    
    # Lower thermostat for sleep
    await iot.set_temperature(
        device_id="temp_1",
        temperature=68
    )
    
    # Activate night scene
    await iot.activate_scene("night")
    
    print("\n🌙 Evening mode activated")

asyncio.run(evening_routine())
```

### Example 3: GitHub Issue to Notion

```python
import asyncio
from integrations import github, notion
from integrations.workflow import WorkflowEngine

async def github_issues_to_notion():
    github_int = github.GitHubIntegration()
    notion_int = notion.NotionIntegration()
    
    for integration in [github_int, notion_int]:
        await integration.authenticate()
    
    # Get open issues
    issues = await github_int.get_issues(
        repo="jarvis-ai",
        state="open",
        limit=10
    )
    
    # Create Notion page for each issue
    for issue in issues:
        page_id = await notion_int.create_page(
            title=f"[GitHub] {issue.title}",
            content=f"""
# Issue #{issue.number}

**Status**: {issue.state}
**Labels**: {', '.join(issue.labels)}

## Description
{issue.body}

[View on GitHub]({issue.html_url})
            """,
            database="github_tracking",
            tags=issue.labels + ["github"]
        )
        
        print(f"✅ Created Notion page: {page_id}")

asyncio.run(github_issues_to_notion())
```

---

## API Reference

### IntegrationRegistry

Core tool registry for all integrations.

```python
registry = IntegrationRegistry()

# Register
registry.register_integration(email_integration)

# Discovery
registry.discover_tools()  # Dict[str, List[ToolDefinition]]
registry.list_all_tools()  # List[Dict]

# Execution
result = await registry.execute_tool("email", "read_inbox", limit=10)

# History
registry.get_execution_history(limit=100)  # List[ToolExecution]
registry.get_stats()  # Dict with stats
```

### WorkflowEngine

Orchestrates multi-step workflows.

```python
engine = WorkflowEngine()

# Registration
engine.register_workflow("name", workflow)
engine.register_integration("email", email_integration)

# Execution
execution = await engine.execute("workflow_name", context={})

# History
engine.get_execution_history(limit=50)
engine.get_workflow_stats()
```

### AuthManager

Manages credentials across services.

```python
auth = AuthManager()

# Storage
auth.store_credentials("gmail", "oauth", data, expires_in=3600)
auth.get_credentials("gmail")
auth.has_credentials("gmail")

# Refresh
auth.register_refresh_callback("gmail", refresh_func)
auth.refresh_token("gmail")

# Rotation
auth.rotate_credentials("gmail", new_data)
auth.remove_credentials("gmail")
```

---

## Best Practices

1. **Always authenticate** before using integrations
2. **Use workflows** for multi-step operations
3. **Implement error handlers** for critical workflows
4. **Cache credentials** securely
5. **Log execution history** for debugging
6. **Use events** for real-time automation
7. **Test workflows** before deploying
8. **Monitor integration health** regularly

---

## Troubleshooting

### Authentication Failures

- Verify credentials in `jarvis_config/credentials.json`
- Check token expiration and refresh
- Ensure OAuth scopes are correct
- Check integration-specific permissions

### Workflow Execution Errors

- Verify all tools are registered
- Check context variables reference correct steps
- Enable debug logging
- Check error handlers

### Missing Integrations

- Ensure integration is imported
- Register with orchestrator bridge
- Verify authentication
- Check tool discovery

---

## Contributing New Integrations

To add a new integration:

1. Create `new_service.py` in integrations/
2. Extend `BaseIntegration`
3. Implement `_call_tool()` method
4. Register tools with `ToolDefinition`
5. Add to `orchestrator_bridge` registration
6. Update this guide with new integration details

Example template:

```python
from .base import BaseIntegration, ToolDefinition

class NewServiceIntegration(BaseIntegration):
    def __init__(self, auth_manager=None):
        super().__init__("new_service", auth_manager=auth_manager)
        self._register_tools()
    
    def _register_tools(self):
        self.register_tool(ToolDefinition(
            name="example_tool",
            description="Does something useful",
            parameters={"param1": str},
            returns="str",
            category="new_service"
        ))
    
    async def authenticate(self):
        # Implement authentication
        pass
    
    async def _call_tool(self, tool_name, **kwargs):
        if tool_name == "example_tool":
            return await self.example_tool(**kwargs)
    
    async def example_tool(self, param1):
        # Implement tool logic
        pass
```

---

*Last Updated: Phase 6 Integration Step*  
*JARVIS Framework v5.0+*
