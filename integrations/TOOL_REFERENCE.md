# JARVIS Integrations - Complete Tool Reference

Quick reference for all available tools across integrations.

---

## Email Integration

### Tools

#### `email.read_inbox`
Read emails from inbox.

```python
read_inbox(limit: int = 10, unread_only: bool = True) -> List[Email]
```

**Parameters:**
- `limit`: Max emails to return (default: 10)
- `unread_only`: Only unread emails (default: True)

**Returns:** List of Email objects with sender, subject, body, timestamp

**Example:**
```python
emails = await email_int.read_inbox(limit=5, unread_only=True)
```

---

#### `email.search_emails`
Search emails by query.

```python
search_emails(query: str, limit: int = 20) -> List[Email]
```

**Parameters:**
- `query`: Search query (e.g., "from:boss@company.com")
- `limit`: Max results (default: 20)

**Returns:** List of matching Email objects

**Example:**
```python
emails = await email_int.search_emails(query="from:boss", limit=10)
```

---

#### `email.summarize_email`
Summarize email content using AI.

```python
summarize_email(email_id: str, max_length: int = 500) -> str
```

**Parameters:**
- `email_id`: Email ID to summarize
- `max_length`: Max summary length (default: 500 chars)

**Returns:** Summarized text

**Example:**
```python
summary = await email_int.summarize_email(email_id="123", max_length=300)
```

---

#### `email.draft_reply`
Generate draft reply to email.

```python
draft_reply(email_id: str, tone: str = "professional") -> str
```

**Parameters:**
- `email_id`: Email to reply to
- `tone`: Response tone ("professional", "casual", "formal")

**Returns:** Draft reply text

**Example:**
```python
draft = await email_int.draft_reply(email_id="123", tone="professional")
```

---

#### `email.send_email`
Send email.

```python
send_email(to: str, subject: str, body: str) -> bool
```

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body

**Returns:** Success status

**Example:**
```python
success = await email_int.send_email(
    to="user@example.com",
    subject="Hello",
    body="This is a test email"
)
```

---

## Calendar Integration

### Tools

#### `calendar.get_events`
Get calendar events in date range.

```python
get_events(start_date: str, end_date: str, limit: int = 50) -> List[CalendarEvent]
```

**Parameters:**
- `start_date`: Start date (ISO format: "2024-01-15")
- `end_date`: End date (ISO format: "2024-01-31")
- `limit`: Max events (default: 50)

**Returns:** List of CalendarEvent objects

**Example:**
```python
events = await calendar_int.get_events(
    start_date="2024-01-15",
    end_date="2024-01-31"
)
```

---

#### `calendar.find_free_slot`
Find next available time slot.

```python
find_free_slot(
    duration_minutes: int,
    date: str,
    start_hour: int = 9,
    end_hour: int = 17
) -> Tuple[str, str]
```

**Parameters:**
- `duration_minutes`: Required slot duration
- `date`: Date to search (ISO format: "2024-01-15")
- `start_hour`: Work day start hour (default: 9)
- `end_hour`: Work day end hour (default: 17)

**Returns:** Tuple of (start_time, end_time) in ISO format

**Example:**
```python
start, end = await calendar_int.find_free_slot(
    duration_minutes=30,
    date="2024-01-15",
    start_hour=9,
    end_hour=17
)
# Returns: ("2024-01-15T10:00:00", "2024-01-15T10:30:00")
```

---

#### `calendar.create_event`
Create new calendar event.

```python
create_event(
    title: str,
    start: str,
    end: str,
    description: str = "",
    location: str = "",
    attendees: List[str] = None
) -> bool
```

**Parameters:**
- `title`: Event title
- `start`: Start time (ISO format: "2024-01-15T09:00:00")
- `end`: End time (ISO format: "2024-01-15T10:00:00")
- `description`: Event description
- `location`: Event location
- `attendees`: List of email addresses

**Returns:** Success status

**Example:**
```python
success = await calendar_int.create_event(
    title="Team Meeting",
    start="2024-01-15T10:00:00",
    end="2024-01-15T10:30:00",
    location="Conference Room A",
    attendees=["john@company.com", "jane@company.com"]
)
```

---

#### `calendar.modify_event`
Modify existing event.

```python
modify_event(
    event_id: str,
    title: str = None,
    start: str = None,
    end: str = None
) -> bool
```

**Parameters:**
- `event_id`: Event ID to modify
- `title`: New title (optional)
- `start`: New start time (optional)
- `end`: New end time (optional)

**Returns:** Success status

**Example:**
```python
success = await calendar_int.modify_event(
    event_id="123",
    title="Updated Meeting Title",
    start="2024-01-15T11:00:00"
)
```

---

#### `calendar.delete_event`
Delete calendar event.

```python
delete_event(event_id: str) -> bool
```

**Parameters:**
- `event_id`: Event ID to delete

**Returns:** Success status

**Example:**
```python
success = await calendar_int.delete_event(event_id="123")
```

---

## GitHub Integration

### Tools

#### `github.list_repos`
List user repositories.

```python
list_repos(limit: int = 20) -> List[GitHubRepo]
```

**Parameters:**
- `limit`: Max repos to return (default: 20)

**Returns:** List of GitHubRepo objects

**Example:**
```python
repos = await github_int.list_repos(limit=10)
```

---

#### `github.get_issues`
Get issues from repository.

```python
get_issues(repo: str, state: str = "open", limit: int = 50) -> List[GitHubIssue]
```

**Parameters:**
- `repo`: Repository name
- `state`: Issue state ("open", "closed", "all")
- `limit`: Max issues (default: 50)

**Returns:** List of GitHubIssue objects

**Example:**
```python
issues = await github_int.get_issues(repo="jarvis-ai", state="open")
```

---

#### `github.create_issue`
Create new GitHub issue.

```python
create_issue(
    repo: str,
    title: str,
    body: str,
    labels: List[str] = None
) -> int
```

**Parameters:**
- `repo`: Repository name
- `title`: Issue title
- `body`: Issue description
- `labels`: Issue labels (optional)

**Returns:** Issue number

**Example:**
```python
issue_num = await github_int.create_issue(
    repo="jarvis-ai",
    title="Bug: Voice recognition fails",
    body="Steps to reproduce:\n1. Enable voice\n2. Speak",
    labels=["bug", "high-priority"]
)
```

---

#### `github.close_issue`
Close GitHub issue.

```python
close_issue(repo: str, issue_number: int) -> bool
```

**Parameters:**
- `repo`: Repository name
- `issue_number`: Issue number to close

**Returns:** Success status

**Example:**
```python
success = await github_int.close_issue(repo="jarvis-ai", issue_number=42)
```

---

#### `github.search_issues`
Search issues across repositories.

```python
search_issues(query: str, limit: int = 10) -> List[GitHubIssue]
```

**Parameters:**
- `query`: Search query
- `limit`: Max results (default: 10)

**Returns:** List of GitHubIssue objects

**Example:**
```python
issues = await github_int.search_issues(query="voice recognition", limit=5)
```

---

## Slack Integration

### Tools

#### `slack.send_message`
Send message to Slack channel.

```python
send_message(channel: str, content: str, thread_id: str = None) -> bool
```

**Parameters:**
- `channel`: Channel name (e.g., "#general")
- `content`: Message content
- `thread_id`: Thread ID for threaded reply (optional)

**Returns:** Success status

**Example:**
```python
success = await slack_int.send_message(
    channel="#alerts",
    content="⚠️ Deployment in progress..."
)
```

---

#### `slack.read_messages`
Read messages from channel.

```python
read_messages(channel: str, limit: int = 50) -> List[Message]
```

**Parameters:**
- `channel`: Channel name
- `limit`: Max messages (default: 50)

**Returns:** List of Message objects

**Example:**
```python
messages = await slack_int.read_messages(channel="#general", limit=20)
```

---

#### `slack.mention_user`
Mention user in message.

```python
mention_user(channel: str, username: str, content: str) -> bool
```

**Parameters:**
- `channel`: Channel name
- `username`: Username to mention
- `content`: Message content

**Returns:** Success status

**Example:**
```python
success = await slack_int.mention_user(
    channel="#engineering",
    username="john",
    content="Can you review this PR?"
)
```

---

#### `slack.react`
Add emoji reaction to message.

```python
react(message_id: str, emoji: str) -> bool
```

**Parameters:**
- `message_id`: Message ID
- `emoji`: Emoji name (e.g., "thumbsup", "heart")

**Returns:** Success status

**Example:**
```python
success = await slack_int.react(message_id="123", emoji="thumbsup")
```

---

#### `slack.notify`
Send urgent notification.

```python
notify(channel: str, title: str, content: str) -> bool
```

**Parameters:**
- `channel`: Channel name
- `title`: Notification title
- `content`: Notification content

**Returns:** Success status

**Example:**
```python
success = await slack_int.notify(
    channel="#alerts",
    title="High CPU Usage",
    content="Server temp-1 at 95% CPU"
)
```

---

## Notion Integration

### Tools

#### `notion.create_page`
Create Notion page.

```python
create_page(
    title: str,
    content: str,
    database: str = "default",
    tags: List[str] = None
) -> str
```

**Parameters:**
- `title`: Page title
- `content`: Page content (Markdown)
- `database`: Target database
- `tags`: Page tags (optional)

**Returns:** Page ID

**Example:**
```python
page_id = await notion_int.create_page(
    title="Meeting Notes",
    content="# Q1 Planning\n\n- Action 1\n- Action 2",
    database="notes",
    tags=["meeting", "q1"]
)
```

---

#### `notion.update_page`
Update Notion page.

```python
update_page(page_id: str, title: str = None, content: str = None) -> bool
```

**Parameters:**
- `page_id`: Page ID to update
- `title`: New title (optional)
- `content`: New content (optional)

**Returns:** Success status

**Example:**
```python
success = await notion_int.update_page(
    page_id="123",
    title="Updated Title",
    content="New content here"
)
```

---

#### `notion.get_page`
Get Notion page.

```python
get_page(page_id: str) -> NotionPage
```

**Parameters:**
- `page_id`: Page ID

**Returns:** NotionPage object

**Example:**
```python
page = await notion_int.get_page(page_id="123")
print(page.title)
print(page.content)
```

---

#### `notion.query_database`
Query Notion database.

```python
query_database(database: str, query: str = "", limit: int = 20) -> List[NotionPage]
```

**Parameters:**
- `database`: Database name
- `query`: Search query (optional)
- `limit`: Max results (default: 20)

**Returns:** List of NotionPage objects

**Example:**
```python
pages = await notion_int.query_database(
    database="projects",
    query="status:active",
    limit=10
)
```

---

#### `notion.delete_page`
Delete Notion page.

```python
delete_page(page_id: str) -> bool
```

**Parameters:**
- `page_id`: Page ID

**Returns:** Success status

**Example:**
```python
success = await notion_int.delete_page(page_id="123")
```

---

## IoT Integration

### Tools

#### `iot.list_devices`
List smart devices.

```python
list_devices(device_type: str = None, room: str = None) -> List[SmartDevice]
```

**Parameters:**
- `device_type`: Filter by device type (optional)
- `room`: Filter by room (optional)

**Returns:** List of SmartDevice objects

**Example:**
```python
# All devices
all_devices = await iot_int.list_devices()

# Just lights
lights = await iot_int.list_devices(device_type="light")

# Devices in bedroom
bedroom = await iot_int.list_devices(room="bedroom")
```

---

#### `iot.get_device`
Get device status.

```python
get_device(device_id: str) -> SmartDevice
```

**Parameters:**
- `device_id`: Device ID

**Returns:** SmartDevice object

**Example:**
```python
device = await iot_int.get_device(device_id="light_1")
print(f"Power: {device.power}")
print(f"Brightness: {device.brightness}")
```

---

#### `iot.control_device`
Send command to device.

```python
control_device(device_id: str, command: str, parameters: Dict = None) -> bool
```

**Parameters:**
- `device_id`: Device ID
- `command`: Command name
- `parameters`: Command parameters (optional)

**Returns:** Success status

**Example:**
```python
success = await iot_int.control_device(
    device_id="speaker_1",
    command="play",
    parameters={"track": "relaxing_music"}
)
```

---

#### `iot.set_light`
Control light.

```python
set_light(
    device_id: str,
    power: bool = None,
    brightness: int = None,
    color: str = None
) -> bool
```

**Parameters:**
- `device_id`: Light device ID
- `power`: Turn on/off (optional)
- `brightness`: Brightness 0-100 (optional)
- `color`: Color name (optional)

**Returns:** Success status

**Example:**
```python
# Turn on 80% brightness
success = await iot_int.set_light(
    device_id="light_1",
    power=True,
    brightness=80,
    color="warm_white"
)

# Just turn off
success = await iot_int.set_light(device_id="light_1", power=False)
```

---

#### `iot.set_temperature`
Set thermostat.

```python
set_temperature(device_id: str, temperature: int) -> bool
```

**Parameters:**
- `device_id`: Thermostat device ID
- `temperature`: Target temperature (°F)

**Returns:** Success status

**Example:**
```python
success = await iot_int.set_temperature(
    device_id="thermostat_1",
    temperature=72
)
```

---

#### `iot.activate_scene`
Activate smart home scene.

```python
activate_scene(scene_name: str) -> bool
```

**Parameters:**
- `scene_name`: Scene name ("morning", "night", "work", etc.)

**Returns:** Success status

**Example:**
```python
success = await iot_int.activate_scene(scene_name="evening")
```

---

## Events Integration

### Tools

#### `events.create_trigger`
Create event trigger.

```python
create_trigger(
    trigger_name: str,
    event_type: str,
    conditions: List[Dict] = None
) -> Trigger
```

**Parameters:**
- `trigger_name`: Trigger name
- `event_type`: Event type to monitor
- `conditions`: List of condition dicts (optional)

**Returns:** Trigger object

**Example:**
```python
trigger = await events_int.create_trigger(
    trigger_name="important_email",
    event_type="EMAIL_RECEIVED",
    conditions=[
        {"field": "data.priority", "operator": "equals", "value": "high"}
    ]
)
```

---

#### `events.create_automation`
Create automation rule.

```python
create_automation(
    automation_name: str,
    trigger_id: str,
    actions: List[str] = None
) -> Automation
```

**Parameters:**
- `automation_name`: Automation name
- `trigger_id`: Associated trigger ID
- `actions`: List of actions to execute

**Returns:** Automation object

**Example:**
```python
automation = await events_int.create_automation(
    automation_name="alert_important_email",
    trigger_id=trigger.id,
    actions=["slack.notify", "calendar.create_event"]
)
```

---

#### `events.list_triggers`
List all triggers.

```python
list_triggers() -> List[Trigger]
```

**Returns:** List of Trigger objects

**Example:**
```python
triggers = await events_int.list_triggers()
```

---

#### `events.get_automation`
Get automation details.

```python
get_automation(automation_id: str) -> Automation
```

**Parameters:**
- `automation_id`: Automation ID

**Returns:** Automation object

**Example:**
```python
automation = await events_int.get_automation(automation_id="auto_1")
```

---

#### `events.emit_event`
Emit event and trigger automations.

```python
emit_event(event_type: str, source: str, data: Dict = None) -> Event
```

**Parameters:**
- `event_type`: Event type
- `source`: Event source (integration name)
- `data`: Event data dict

**Returns:** Event object

**Example:**
```python
event = await events_int.emit_event(
    event_type="EMAIL_RECEIVED",
    source="gmail",
    data={"sender": "boss@company.com", "priority": "high"}
)
```

---

## Workflow Engine

### Methods

#### `register_workflow`
Register a workflow definition.

```python
engine.register_workflow(name: str, workflow: Workflow) -> None
```

---

#### `execute`
Execute workflow.

```python
await engine.execute(workflow_name: str, context: Dict = None) -> WorkflowExecution
```

**Returns:** WorkflowExecution with status, duration, results

---

#### `get_execution_history`
Get past executions.

```python
engine.get_execution_history(limit: int = 50) -> List[WorkflowExecution]
```

---

## Orchestrator Bridge

### Methods

#### `discover_tools`
Discover all available tools.

```python
await bridge.tool_discovery() -> Dict[str, List[Dict]]
```

**Returns:** Dict mapping integration names to tool specs

---

#### `execute_plan`
Execute multiple actions in sequence.

```python
await bridge.execute_plan(actions: List[Dict]) -> List[Dict]
```

**Parameters:**
```python
actions = [
    {
        "tool_id": "email.read_inbox",
        "parameters": {"limit": 5}
    },
    {
        "tool_id": "slack.send_message",
        "parameters": {"channel": "#alerts", "content": "..."}
    }
]
```

---

## Data Types

### Email

```python
@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    read: bool = False
    labels: List[str] = None
```

### CalendarEvent

```python
@dataclass
class CalendarEvent:
    id: str
    title: str
    start: str  # ISO format
    end: str    # ISO format
    description: str = ""
    location: str = ""
    attendees: List[str] = None
```

### SmartDevice

```python
@dataclass
class SmartDevice:
    id: str
    name: str
    type: DeviceType
    room: str
    power: bool
    brightness: int  # For lights
    temperature: int # For thermostats
```

### Event

```python
@dataclass
class Event:
    id: str
    type: EventType
    source: str
    timestamp: str
    data: Dict[str, Any]
    processed: bool = False
```

---

## Status Codes

### Workflow Execution Status

- `PENDING`: Not started
- `RUNNING`: Currently executing
- `SUCCESS`: Completed successfully
- `FAILED`: Execution failed
- `CANCELLED`: Manually cancelled

---

## Common Patterns

### Chaining Tools

```python
# Get email → Summarize → Send to Slack
emails = await email_int.read_inbox(limit=1)
summary = await email_int.summarize_email(email_id=emails[0].id)
await slack_int.send_message(channel="#digest", content=summary)
```

### Conditional Execution

```python
devices = await iot_int.list_devices(device_type="light")
if any(d.power for d in devices):
    await iot_int.set_light(device_id=devices[0].id, power=False)
```

### Batch Operations

```python
issues = await github_int.get_issues(repo="myrepo", limit=10)
for issue in issues:
    await notion_int.create_page(
        title=f"[GitHub] {issue.title}",
        content=issue.body,
        database="issues",
        tags=["github"] + issue.labels
    )
```

---

*Last Updated: Phase 6 Ecosystem Controller*  
*JARVIS Framework v5.0+*
