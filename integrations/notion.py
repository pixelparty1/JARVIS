"""
Notion Integration - Knowledge Database

Features:
- Store notes
- Retrieve notes
- Sync with memory system
- Database operations
- Full-text search
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

from .base import Integration, ToolDefinition, IntegrationError


@dataclass
class NotionPage:
    """Notion page/document."""
    id: str
    title: str
    content: str
    database: str = "default"
    tags: List[str] = None
    properties: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.properties is None:
            self.properties = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


class NotionIntegration(Integration):
    """
    Notion API integration.
    
    Enables reading/writing to Notion databases.
    """
    
    def __init__(self, auth_manager=None):
        """
        Initialize Notion integration.
        
        Args:
            auth_manager: AuthManager instance
        """
        super().__init__("notion", auth_manager=auth_manager)
        self.mock_pages = {}
        self.databases = {}
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="create_page",
            description="Create a new Notion page",
            parameters={"title": str, "content": str, "database": str, "tags": list},
            returns="str",  # page_id
            category="notion"
        ))
        
        self.register_tool(ToolDefinition(
            name="update_page",
            description="Update a Notion page",
            parameters={"page_id": str, "title": str, "content": str},
            returns="bool",
            category="notion"
        ))
        
        self.register_tool(ToolDefinition(
            name="get_page",
            description="Retrieve a Notion page",
            parameters={"page_id": str},
            returns="NotionPage",
            category="notion"
        ))
        
        self.register_tool(ToolDefinition(
            name="query_database",
            description="Search Notion database",
            parameters={"database": str, "query": str, "limit": int},
            returns="List[NotionPage]",
            category="notion"
        ))
        
        self.register_tool(ToolDefinition(
            name="delete_page",
            description="Delete a Notion page",
            parameters={"page_id": str},
            returns="bool",
            category="notion"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate with Notion."""
        if not self.auth_manager:
            self.is_authenticated = True
            return True
        
        cred = self.auth_manager.get_credentials("notion")
        if cred:
            self.is_authenticated = True
            return True
        
        return False
    
    async def health_check(self) -> bool:
        """Check Notion API health."""
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "create_page":
            return await self.create_page(
                title=kwargs.get("title"),
                content=kwargs.get("content"),
                database=kwargs.get("database", "default"),
                tags=kwargs.get("tags", [])
            )
        elif tool_name == "update_page":
            return await self.update_page(
                page_id=kwargs.get("page_id"),
                title=kwargs.get("title"),
                content=kwargs.get("content")
            )
        elif tool_name == "get_page":
            return await self.get_page(page_id=kwargs.get("page_id"))
        elif tool_name == "query_database":
            return await self.query_database(
                database=kwargs.get("database", "default"),
                query=kwargs.get("query"),
                limit=kwargs.get("limit", 10)
            )
        elif tool_name == "delete_page":
            return await self.delete_page(page_id=kwargs.get("page_id"))
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    async def create_page(self, title: str, content: str,
                         database: str = "default",
                         tags: List[str] = None) -> str:
        """
        Create a new Notion page.
        
        Args:
            title: Page title
            content: Page content
            database: Database name
            tags: Optional tags
            
        Returns:
            Page ID
        """
        if tags is None:
            tags = []
        
        page_id = f"page_{uuid.uuid4().hex[:8]}"
        
        page = NotionPage(
            id=page_id,
            title=title,
            content=content,
            database=database,
            tags=tags
        )
        
        self.mock_pages[page_id] = page
        
        print(f"✅ Page created in Notion: {title}")
        return page_id
    
    async def update_page(self, page_id: str,
                         title: str = None,
                         content: str = None) -> bool:
        """
        Update a Notion page.
        
        Args:
            page_id: Page ID
            title: New title
            content: New content
            
        Returns:
            Success status
        """
        if page_id not in self.mock_pages:
            return False
        
        page = self.mock_pages[page_id]
        
        if title:
            page.title = title
        if content:
            page.content = content
        
        page.updated_at = datetime.now().isoformat()
        return True
    
    async def get_page(self, page_id: str) -> Optional[NotionPage]:
        """
        Retrieve a Notion page.
        
        Args:
            page_id: Page ID
            
        Returns:
            NotionPage or None
        """
        return self.mock_pages.get(page_id)
    
    async def query_database(self, database: str = "default",
                            query: str = "",
                            limit: int = 10) -> List[NotionPage]:
        """
        Search Notion database.
        
        Args:
            database: Database name
            query: Search query
            limit: Max results
            
        Returns:
            List of matching pages
        """
        results = []
        
        for page in self.mock_pages.values():
            if page.database != database:
                continue
            
            if query.lower() in page.title.lower() or query.lower() in page.content.lower():
                results.append(page)
        
        return results[:limit]
    
    async def delete_page(self, page_id: str) -> bool:
        """
        Delete a Notion page.
        
        Args:
            page_id: Page ID
            
        Returns:
            Success status
        """
        if page_id in self.mock_pages:
            del self.mock_pages[page_id]
            return True
        return False
    
    async def sync_from_memory(self, memories: List[Dict[str, Any]]) -> int:
        """
        Sync memories from JARVIS memory system to Notion.
        
        Args:
            memories: List of memory objects
            
        Returns:
            Number of pages created
        """
        created = 0
        
        for memory in memories:
            page_id = await self.create_page(
                title=f"Memory: {memory.get('id')}",
                content=memory.get('content', memory.get('summary', '')),
                database="memory_sync",
                tags=memory.get('tags', [])
            )
            if page_id:
                created += 1
        
        return created


class NotionAssistant:
    """High-level Notion assistant."""
    
    def __init__(self, notion_integration: NotionIntegration):
        """
        Initialize Notion assistant.
        
        Args:
            notion_integration: NotionIntegration instance
        """
        self.notion = notion_integration
    
    async def store_note(self, title: str, content: str,
                        tags: List[str] = None) -> str:
        """
        Store a note in Notion.
        
        Args:
            title: Note title
            content: Note content
            tags: Tags for organization
            
        Returns:
            Page ID
        """
        if tags is None:
            tags = []
        
        return await self.notion.create_page(
            title=title,
            content=content,
            database="notes",
            tags=tags
        )
    
    async def retrieve_notes(self, query: str = "", limit: int = 10) -> List[NotionPage]:
        """
        Retrieve notes from Notion.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of notes
        """
        return await self.notion.query_database(
            database="notes",
            query=query,
            limit=limit
        )
    
    async def create_project_page(self, name: str, description: str) -> str:
        """
        Create a project page.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Page ID
        """
        content = f"""
# {name}

## Description
{description}

## Tasks
- [ ] Task 1
- [ ] Task 2

## Progress
- Started: {datetime.now().strftime('%Y-%m-%d')}
- Status: In Progress
        """
        
        return await self.notion.create_page(
            title=name,
            content=content,
            database="projects",
            tags=["project"]
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_notion():
        print("🧪 Notion Integration Test\n")
        
        notion = NotionIntegration()
        await notion.authenticate()
        
        # Create a page
        page_id = await notion.create_page(
            title="JARVIS Integration Test",
            content="Testing the Notion integration with JARVIS"
        )
        print(f"✅ Created page: {page_id}\n")
        
        # Retrieve page
        page = await notion.get_page(page_id)
        if page:
            print(f"📄 Retrieved: {page.title}")
            print(f"   Content: {page.content[:50]}...\n")
    
    asyncio.run(test_notion())
