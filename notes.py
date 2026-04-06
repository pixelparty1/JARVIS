"""
JARVIS Notes Module
Handles notes management and summarization using AI
"""

from typing import List, Dict, Optional
from brain import JarvisBrain
from memory import Memory

class NotesManager:
    """Notes management with AI summarization"""
    
    def __init__(self):
        self.memory = Memory()
        self.brain = JarvisBrain()
    
    def create_note(self, title: str, content: str, tags: List[str] = None) -> str:
        """
        Create a new note
        
        Args:
            title: Note title
            content: Note content
            tags: Optional tags
            
        Returns:
            Note ID
        """
        note_id = self.memory.add_note(title, content, tags)
        print(f"✅ Note created: {title} (ID: {note_id})")
        return note_id
    
    def summarize_note(self, note_id: str) -> Optional[str]:
        """
        Summarize a note using AI
        
        Args:
            note_id: Note ID to summarize
            
        Returns:
            Summary or None if note not found
        """
        note = self.memory.get_note(note_id)
        
        if not note:
            print(f"❌ Note not found: {note_id}")
            return None
        
        # Use Groq to summarize
        prompt = f"""Please provide a concise summary (2-3 sentences) of the following note:

Title: {note['title']}
Content: {note['content']}

Summary:"""
        
        summary = self.brain.query(prompt)
        return summary
    
    def list_notes(self, tag: str = None) -> str:
        """
        List notes
        
        Args:
            tag: Optional filter by tag
            
        Returns:
            Formatted string of notes
        """
        notes = self.memory.get_notes(tag)
        
        if not notes:
            return "No notes found"
        
        result = f"📝 Notes ({len(notes)}):\n"
        for note in notes:
            tags_str = f" [{', '.join(note['tags'])}]" if note['tags'] else ""
            result += f"  • {note['title']}{tags_str}\n    ID: {note['id']}\n"
        
        return result
    
    def view_note(self, note_id: str) -> str:
        """View full note content"""
        note = self.memory.get_note(note_id)
        
        if not note:
            return f"❌ Note not found: {note_id}"
        
        result = f"📝 {note['title']}\n"
        result += f"ID: {note['id']}\n"
        result += f"Created: {note['created_at']}\n"
        if note['tags']:
            result += f"Tags: {', '.join(note['tags'])}\n"
        result += f"\n{note['content']}"
        
        return result
    
    def search_notes(self, query: str) -> str:
        """
        Search notes
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        results = self.memory.search_notes(query)
        
        if not results:
            return f"No notes found matching: {query}"
        
        result_str = f"🔍 Found {len(results)} note(s) matching '{query}':\n"
        for note in results:
            result_str += f"  • {note['title']} (ID: {note['id']})\n"
        
        return result_str
    
    def update_note(self, note_id: str, title: str = None, content: str = None) -> str:
        """Update note content"""
        success = self.memory.update_note(note_id, title, content)
        
        if success:
            return f"✅ Note updated: {note_id}"
        else:
            return f"❌ Note not found: {note_id}"
    
    def delete_note(self, note_id: str) -> str:
        """Delete a note"""
        success = self.memory.delete_note(note_id)
        
        if success:
            return f"✅ Note deleted: {note_id}"
        else:
            return f"❌ Note not found: {note_id}"
    
    def add_to_note(self, note_id: str, additional_content: str) -> str:
        """Add content to existing note"""
        note = self.memory.get_note(note_id)
        
        if not note:
            return f"❌ Note not found: {note_id}"
        
        new_content = note["content"] + "\n\n" + additional_content
        self.memory.update_note(note_id, content=new_content)
        
        return f"✅ Content added to note: {note_id}"
    
    def get_note_statistics(self) -> str:
        """Get statistics about notes"""
        notes = self.memory.get_notes()
        
        all_tags = set()
        for note in notes:
            all_tags.update(note.get('tags', []))
        
        result = f"📊 Notes Statistics:\n"
        result += f"  • Total notes: {len(notes)}\n"
        result += f"  • Unique tags: {len(all_tags)}\n"
        
        if all_tags:
            result += f"  • Tags: {', '.join(sorted(all_tags))}\n"
        
        return result
