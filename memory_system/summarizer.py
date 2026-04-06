"""
Summarizer - Intelligent Information Compression

Uses Groq to create concise summaries of long content.
Extracts key points and auto-generates tags.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SummaryResult:
    """Result of summarization."""
    original_length: int
    summary_length: int
    compression_ratio: float
    summary: str
    key_points: List[str]
    tags: List[str]
    generated_at: str


class Summarizer:
    """
    Intelligent summarization engine using Groq.
    
    Features:
    - Compress long text while keeping key info
    - Extract key points
    - Auto-generate tags
    - Async processing
    """
    
    def __init__(self, brain=None, max_summary_length: int = 500):
        """
        Initialize summarizer.
        
        Args:
            brain: JARVIS brain instance (must have ask_groq method)
            max_summary_length: Target summary length in characters
        """
        self.brain = brain
        self.max_summary_length = max_summary_length
        self.summary_history = []
    
    async def summarize(self, text: str, 
                       max_points: int = 5,
                       generate_tags: bool = True) -> Optional[SummaryResult]:
        """
        Summarize text using Groq.
        
        Args:
            text: Text to summarize
            max_points: Max key points to extract
            generate_tags: Whether to generate tags
            
        Returns:
            SummaryResult or None if no brain
        """
        if self.brain is None:
            return self._fallback_summarize(text, max_points, generate_tags)
        
        if len(text) < 200:
            # Text is short enough, just extract points
            return await self._extract_points(text, max_points, generate_tags)
        
        try:
            prompt = f"""Summarize the following text concisely. Keep it under {self.max_summary_length} characters.

TEXT:
{text}

Provide a JSON response with:
{{
    "summary": "concise summary here",
    "key_points": ["point 1", "point 2", "point 3"],
    "tags": ["tag1", "tag2", "tag3"]
}}

Only return valid JSON."""
            
            response = await asyncio.to_thread(
                self.brain.ask_groq,
                prompt,
                temperature=0.5
            )
            
            # Parse response
            try:
                result_data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    result_data = {
                        "summary": response[:self.max_summary_length],
                        "key_points": [],
                        "tags": []
                    }
            
            # Create result
            compression_ratio = len(text) / len(result_data.get('summary', text))
            
            result = SummaryResult(
                original_length=len(text),
                summary_length=len(result_data.get('summary', '')),
                compression_ratio=compression_ratio,
                summary=result_data.get('summary', ''),
                key_points=result_data.get('key_points', [])[:max_points],
                tags=result_data.get('tags', []),
                generated_at=datetime.now().isoformat()
            )
            
            self.summary_history.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return None
    
    async def _extract_points(self, text: str,
                             max_points: int,
                             generate_tags: bool) -> Optional[SummaryResult]:
        """Extract points from short text."""
        if self.brain is None:
            return self._fallback_extract_points(text, max_points, generate_tags)
        
        try:
            prompt = f"""Extract key points and tags from this text:

TEXT:
{text}

Provide JSON with:
{{
    "key_points": ["point 1", "point 2"],
    "tags": ["tag1", "tag2"]
}}

Return only JSON."""
            
            response = await asyncio.to_thread(
                self.brain.ask_groq,
                prompt,
                temperature=0.5
            )
            
            try:
                result_data = json.loads(response)
            except json.JSONDecodeError:
                result_data = {"key_points": [], "tags": []}
            
            result = SummaryResult(
                original_length=len(text),
                summary_length=len(text),
                compression_ratio=1.0,
                summary=text,
                key_points=result_data.get('key_points', [])[:max_points],
                tags=result_data.get('tags', []),
                generated_at=datetime.now().isoformat()
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Point extraction error: {e}")
            return None
    
    def _fallback_summarize(self, text: str,
                           max_points: int,
                           generate_tags: bool) -> SummaryResult:
        """Fallback summarization without Groq (simple heuristic)."""
        # Extract first max_summary_length characters
        summary = text[:self.max_summary_length]
        if len(text) > self.max_summary_length:
            summary = summary.rsplit(' ', 1)[0] + '...'
        
        # Extract sentences as key points
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        key_points = sentences[:max_points]
        
        # Extract tags from capitalized words
        words = text.split()
        tags = [w.strip('.,!?') for w in words 
               if w[0].isupper() and len(w) > 3][:5]
        
        compression_ratio = len(text) / len(summary) if summary else 1
        
        return SummaryResult(
            original_length=len(text),
            summary_length=len(summary),
            compression_ratio=compression_ratio,
            summary=summary,
            key_points=key_points,
            tags=tags,
            generated_at=datetime.now().isoformat()
        )
    
    def _fallback_extract_points(self, text: str,
                                max_points: int,
                                generate_tags: bool) -> SummaryResult:
        """Fallback point extraction without Groq."""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        key_points = sentences[:max_points]
        
        words = text.split()
        tags = [w.strip('.,!?') for w in words 
               if w[0].isupper() and len(w) > 3][:5]
        
        return SummaryResult(
            original_length=len(text),
            summary_length=len(text),
            compression_ratio=1.0,
            summary=text,
            key_points=key_points,
            tags=tags,
            generated_at=datetime.now().isoformat()
        )
    
    def batch_summarize(self, texts: List[str]) -> List[Optional[SummaryResult]]:
        """
        Summarize multiple texts (blocking).
        
        Args:
            texts: List of texts to summarize
            
        Returns:
            List of summary results
        """
        results = []
        for text in texts:
            try:
                # Use simple blocking approach
                result = self._fallback_summarize(text, max_points=5, generate_tags=True)
                results.append(result)
            except Exception as e:
                print(f"❌ Error summarizing text: {e}")
                results.append(None)
        
        return results
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.summary_history:
            return {'total_summaries': 0}
        
        total_original = sum(s.original_length for s in self.summary_history)
        total_summary = sum(s.summary_length for s in self.summary_history)
        total_compression = total_original / total_summary if total_summary > 0 else 0
        
        return {
            'total_summaries': len(self.summary_history),
            'total_original_length': total_original,
            'total_summary_length': total_summary,
            'avg_compression_ratio': total_compression,
            'last_summary': self.summary_history[-1] if self.summary_history else None
        }


class SmartNoter:
    """
    Structured note system with auto-tagging and summarization.
    """
    
    def __init__(self, summarizer: Optional[Summarizer] = None):
        """
        Initialize note system.
        
        Args:
            summarizer: Optional summarizer instance
        """
        self.summarizer = summarizer
        self.notes: Dict[str, Dict[str, Any]] = {}
        self.notes_list = []
    
    def create_note(self, title: str, content: str,
                   tags: Optional[List[str]] = None,
                   auto_summarize: bool = True) -> Dict[str, Any]:
        """
        Create a structured note.
        
        Args:
            title: Note title
            content: Note content
            tags: Optional tags
            auto_summarize: Whether to auto-summarize
            
        Returns:
            Note dict
        """
        note_id = f"note_{len(self.notes)}_{int(__import__('time').time() * 1000)}"
        
        note = {
            'id': note_id,
            'title': title,
            'content': content,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'summary': None,
            'key_points': [],
            'importance': 0.5
        }
        
        # Auto-summarize if enabled
        if auto_summarize and self.summarizer and len(content) > 200:
            result = self.summarizer._fallback_summarize(content, max_points=3)
            note['summary'] = result.summary
            note['key_points'] = result.key_points
            note['tags'] = list(set(note['tags'] + result.tags))
        
        self.notes[note_id] = note
        self.notes_list.append(note)
        
        return note
    
    def search_notes(self, query: str, by_tag: bool = False) -> List[Dict[str, Any]]:
        """
        Search notes by title/content or tags.
        
        Args:
            query: Search query
            by_tag: Search by tag if True, else by content
            
        Returns:
            List of matching notes
        """
        results = []
        query_lower = query.lower()
        
        for note in self.notes_list:
            if by_tag:
                # Search by tags
                if any(query_lower in tag.lower() for tag in note['tags']):
                    results.append(note)
            else:
                # Search by title and content
                if (query_lower in note['title'].lower() or
                    query_lower in note['content'].lower()):
                    results.append(note)
        
        return results
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get note by ID."""
        return self.notes.get(note_id)
    
    def update_note(self, note_id: str, **updates) -> bool:
        """Update a note."""
        if note_id not in self.notes:
            return False
        
        note = self.notes[note_id]
        note.update(updates)
        note['updated_at'] = datetime.now().isoformat()
        
        return True
    
    def get_notes_stats(self) -> Dict[str, Any]:
        """Get notes statistics."""
        all_tags = set()
        for note in self.notes_list:
            all_tags.update(note['tags'])
        
        return {
            'total_notes': len(self.notes_list),
            'unique_tags': len(all_tags),
            'total_content_length': sum(len(n['content']) for n in self.notes_list),
            'avg_note_length': sum(len(n['content']) for n in self.notes_list) / len(self.notes_list) if self.notes_list else 0,
            'tags': list(all_tags)
        }


# Example usage
if __name__ == "__main__":
    print("📝 Summarizer Test\n")
    
    text = """
    Artificial Intelligence is transforming how we work and live. Machine learning 
    algorithms can now recognize patterns in data that humans might miss. Deep learning 
    neural networks have achieved remarkable success in image recognition, natural language 
    processing, and game playing. However, these systems require large amounts of data 
    and computational resources. The field is advancing rapidly with new architectures 
    and techniques emerging regularly.
    """
    
    summarizer = Summarizer()
    
    # Test fallback summarization
    print("📋 Original text length:", len(text))
    result = summarizer._fallback_summarize(text, max_points=3)
    
    print(f"Summary length: {result.summary_length}")
    print(f"Compression ratio: {result.compression_ratio:.2f}x\n")
    
    print("Summary:")
    print(f"  {result.summary}\n")
    
    print("Key points:")
    for i, point in enumerate(result.key_points, 1):
        print(f"  {i}. {point}")
    
    print("\nTags:", ", ".join(result.tags))
    
    # Test note system
    print("\n" + "="*50)
    print("📓 Note System Test\n")
    
    noter = SmartNoter(summarizer)
    
    note = noter.create_note(
        title="AI Learning",
        content=text,
        tags=["AI", "ML"],
        auto_summarize=True
    )
    
    print(f"Created note: {note['title']}")
    print(f"Tags: {note['tags']}")
    print(f"Summary: {note['summary']}")
    
    # Search
    print("\nSearching for 'learning':")
    results = noter.search_notes("learning")
    for result in results:
        print(f"  Found: {result['title']}")
