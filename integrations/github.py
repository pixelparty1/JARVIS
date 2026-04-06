"""
GitHub Integration - Developer Workflow

Features:
- List repositories
- Read issues
- Create/close issues
- View pull requests
- Monitor status
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .base import Integration, ToolDefinition, IntegrationError


@dataclass
class GitHubRepo:
    """GitHub repository."""
    name: str
    url: str
    description: str = ""
    stars: int = 0
    open_issues: int = 0
    language: str = ""


@dataclass
class GitHubIssue:
    """GitHub issue."""
    id: str
    number: int
    title: str
    body: str
    repo: str
    state: str = "open"  # open, closed
    labels: List[str] = None
    assignees: List[str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if self.assignees is None:
            self.assignees = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class GitHubIntegration(Integration):
    """
    GitHub API integration.
    
    Enables managing repositories, issues, and PRs.
    """
    
    def __init__(self, auth_manager=None, username: str = "user"):
        """
        Initialize GitHub integration.
        
        Args:
            auth_manager: AuthManager instance
            username: GitHub username
        """
        super().__init__("github", auth_manager=auth_manager)
        self.username = username
        self.mock_repos = []
        self.mock_issues = []
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="list_repos",
            description="List user's repositories",
            parameters={"limit": int},
            returns="List[GitHubRepo]",
            category="github"
        ))
        
        self.register_tool(ToolDefinition(
            name="get_issues",
            description="Get issues from a repository",
            parameters={"repo": str, "state": str, "limit": int},
            returns="List[GitHubIssue]",
            category="github"
        ))
        
        self.register_tool(ToolDefinition(
            name="create_issue",
            description="Create a new issue",
            parameters={"repo": str, "title": str, "body": str, "labels": list},
            returns="str",  # issue_id
            category="github"
        ))
        
        self.register_tool(ToolDefinition(
            name="close_issue",
            description="Close an issue",
            parameters={"repo": str, "issue_number": int},
            returns="bool",
            category="github"
        ))
        
        self.register_tool(ToolDefinition(
            name="search_issues",
            description="Search issues across repos",
            parameters={"query": str, "limit": int},
            returns="List[GitHubIssue]",
            category="github"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate with GitHub."""
        if not self.auth_manager:
            self.is_authenticated = True
            return True
        
        cred = self.auth_manager.get_credentials("github")
        if cred:
            self.is_authenticated = True
            return True
        
        return False
    
    async def health_check(self) -> bool:
        """Check GitHub API health."""
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "list_repos":
            return await self.list_repos(limit=kwargs.get("limit", 10))
        elif tool_name == "get_issues":
            return await self.get_issues(
                repo=kwargs.get("repo"),
                state=kwargs.get("state", "open"),
                limit=kwargs.get("limit", 20)
            )
        elif tool_name == "create_issue":
            return await self.create_issue(
                repo=kwargs.get("repo"),
                title=kwargs.get("title"),
                body=kwargs.get("body"),
                labels=kwargs.get("labels", [])
            )
        elif tool_name == "close_issue":
            return await self.close_issue(
                repo=kwargs.get("repo"),
                issue_number=kwargs.get("issue_number")
            )
        elif tool_name == "search_issues":
            return await self.search_issues(
                query=kwargs.get("query"),
                limit=kwargs.get("limit", 10)
            )
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    async def list_repos(self, limit: int = 10) -> List[GitHubRepo]:
        """
        List user's repositories.
        
        Args:
            limit: Max repos to return
            
        Returns:
            List of repositories
        """
        repos = self._get_mock_repos()
        return repos[:limit]
    
    async def get_issues(self, repo: str, state: str = "open",
                        limit: int = 20) -> List[GitHubIssue]:
        """
        Get issues from a repository.
        
        Args:
            repo: Repository name
            state: "open" or "closed"
            limit: Max issues to return
            
        Returns:
            List of issues
        """
        issues = self._get_mock_issues()
        
        filtered = [i for i in issues if i.repo == repo and i.state == state]
        return filtered[:limit]
    
    async def create_issue(self, repo: str, title: str, body: str,
                          labels: List[str] = None) -> str:
        """
        Create a new issue.
        
        Args:
            repo: Repository name
            title: Issue title
            body: Issue description
            labels: Issue labels
            
        Returns:
            Issue ID
        """
        if labels is None:
            labels = []
        
        issue_number = len(self._get_mock_issues()) + 1
        issue_id = f"issue_{issue_number}"
        
        issue = GitHubIssue(
            id=issue_id,
            number=issue_number,
            title=title,
            body=body,
            repo=repo,
            labels=labels
        )
        
        self.mock_issues.append(issue)
        
        print(f"✅ Issue created: {title}")
        return issue_id
    
    async def close_issue(self, repo: str, issue_number: int) -> bool:
        """
        Close an issue.
        
        Args:
            repo: Repository name
            issue_number: Issue number
            
        Returns:
            Success status
        """
        for issue in self.mock_issues:
            if issue.repo == repo and issue.number == issue_number:
                issue.state = "closed"
                issue.updated_at = datetime.now().isoformat()
                return True
        
        return False
    
    async def search_issues(self, query: str, limit: int = 10) -> List[GitHubIssue]:
        """
        Search issues.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching issues
        """
        issues = self._get_mock_issues()
        
        results = []
        for issue in issues:
            if (query.lower() in issue.title.lower() or
                query.lower() in issue.body.lower()):
                results.append(issue)
        
        return results[:limit]
    
    def _get_mock_repos(self) -> List[GitHubRepo]:
        """Get mock repositories."""
        if self.mock_repos:
            return self.mock_repos
        
        self.mock_repos = [
            GitHubRepo(
                name="jarvis-ai",
                url="https://github.com/user/jarvis-ai",
                description="Autonomous AI ecosystem controller",
                stars=42,
                open_issues=5,
                language="Python"
            ),
            GitHubRepo(
                name="neural-net",
                url="https://github.com/user/neural-net",
                description="Deep learning research project",
                stars=28,
                open_issues=3,
                language="Python"
            ),
            GitHubRepo(
                name="web-app",
                url="https://github.com/user/web-app",
                description="Full-stack web application",
                stars=15,
                open_issues=2,
                language="JavaScript"
            ),
        ]
        
        return self.mock_repos
    
    def _get_mock_issues(self) -> List[GitHubIssue]:
        """Get mock issues."""
        if self.mock_issues:
            return self.mock_issues
        
        self.mock_issues = [
            GitHubIssue(
                id="1",
                number=1,
                title="Add email integration",
                body="Connect JARVIS with email services",
                repo="jarvis-ai",
                labels=["feature", "integration"],
                state="open"
            ),
            GitHubIssue(
                id="2",
                number=2,
                title="Fix memory search bug",
                body="Vector search returning incorrect results",
                repo="jarvis-ai",
                labels=["bug"],
                state="open"
            ),
            GitHubIssue(
                id="3",
                number=3,
                title="Optimize graph traversal",
                body="Knowledge graph path finding is slow",
                repo="jarvis-ai",
                labels=["performance"],
                state="open"
            ),
        ]
        
        return self.mock_issues


class GitHubAssistant:
    """High-level GitHub assistant."""
    
    def __init__(self, github_integration: GitHubIntegration):
        """
        Initialize GitHub assistant.
        
        Args:
            github_integration: GitHubIntegration instance
        """
        self.github = github_integration
    
    async def get_status_report(self) -> str:
        """Generate GitHub status report."""
        repos = await self.github.list_repos()
        
        report = "📊 GitHub Status Report\n\n"
        report += f"Total repositories: {len(repos)}\n\n"
        
        total_issues = 0
        for repo in repos:
            report += f"• {repo.name}\n"
            report += f"  Stars: ⭐ {repo.stars} | Issues: 🔴 {repo.open_issues}\n"
            total_issues += repo.open_issues
        
        report += f"\nTotal open issues: {total_issues}"
        
        return report
    
    async def get_my_issues(self, repo: str = None) -> str:
        """Get open issues assigned to me."""
        if repo:
            issues = await self.github.get_issues(repo, state="open")
        else:
            # Get issues from all repos
            repos = await self.github.list_repos()
            issues = []
            for r in repos:
                repo_issues = await self.github.get_issues(r.name, state="open")
                issues.extend(repo_issues)
        
        report = "📋 My Issues\n\n"
        
        if not issues:
            return report + "✅ All caught up!"
        
        for issue in issues:
            report += f"• [{issue.repo}] {issue.title}\n"
            if issue.labels:
                report += f"  Labels: {', '.join(issue.labels)}\n"
        
        return report


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_github():
        print("🧪 GitHub Integration Test\n")
        
        github = GitHubIntegration(username="jarvis-user")
        await github.authenticate()
        
        # List repos
        repos = await github.list_repos(limit=3)
        print(f"✅ Found {len(repos)} repositories\n")
        
        for repo in repos:
            print(f"📦 {repo.name}: {repo.description}")
            print(f"   Stars: ${repo.stars} | Issues: {repo.open_issues}\n")
    
    asyncio.run(test_github())
