"""
JARVIS File Manager Module
Handles file operations and navigation
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class FileManager:
    """File system operations and navigation"""
    
    @staticmethod
    def list_files(path: str = None, show_hidden: bool = False) -> str:
        """
        List files in directory
        
        Args:
            path: Directory path (default: current directory)
            show_hidden: Whether to show hidden files
            
        Returns:
            Formatted file listing
        """
        if path is None:
            path = os.getcwd()
        
        try:
            path = os.path.expanduser(path)
            
            if not os.path.isdir(path):
                return f"❌ Not a directory: {path}"
            
            items = os.listdir(path)
            
            if not show_hidden:
                items = [i for i in items if not i.startswith('.')]
            
            files = []
            dirs = []
            
            for item in sorted(items):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    dirs.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    size_str = FileManager._format_size(size)
                    files.append(f"📄 {item} ({size_str})")
            
            result = f"📂 Contents of {path}\n\n"
            
            if dirs:
                result += "Directories:\n"
                for d in dirs:
                    result += f"  {d}\n"
                result += "\n"
            
            if files:
                result += "Files:\n"
                for f in files:
                    result += f"  {f}\n"
            
            if not dirs and not files:
                result += "(empty)"
            
            return result
        
        except Exception as e:
            return f"❌ Error listing files: {e}"
    
    @staticmethod
    def search_files(query: str, search_path: str = None, recursive: bool = True) -> str:
        """
        Search for files
        
        Args:
            query: Search query (filename pattern)
            search_path: Path to search in (default: current directory)
            recursive: Whether to search recursively
            
        Returns:
            Search results
        """
        if search_path is None:
            search_path = os.getcwd()
        
        try:
            search_path = os.path.expanduser(search_path)
            query = query.lower()
            results = []
            
            if recursive:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if query in file.lower():
                            full_path = os.path.join(root, file)
                            size = os.path.getsize(full_path)
                            results.append({
                                "path": full_path,
                                "size": size,
                                "name": file
                            })
            else:
                for item in os.listdir(search_path):
                    if query in item.lower():
                        item_path = os.path.join(search_path, item)
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            results.append({
                                "path": item_path,
                                "size": size,
                                "name": item
                            })
            
            if not results:
                return f"❌ No files found matching: {query}"
            
            result = f"🔍 Found {len(results)} file(s) matching '{query}':\n\n"
            
            for item in results[:20]:  # Show first 20
                size_str = FileManager._format_size(item["size"])
                result += f"  • {item['name']} ({size_str})\n"
                result += f"    Path: {item['path']}\n\n"
            
            if len(results) > 20:
                result += f"... and {len(results) - 20} more"
            
            return result
        
        except Exception as e:
            return f"❌ Search error: {e}"
    
    @staticmethod
    def open_file(path: str) -> str:
        """
        Open a file with default application
        
        Args:
            path: File path
            
        Returns:
            Status message
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                return f"❌ File not found: {path}"
            
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
            
            return f"✅ Opening: {path}"
        
        except Exception as e:
            return f"❌ Error opening file: {e}"
    
    @staticmethod
    def open_folder(path: str) -> str:
        """
        Open a folder in file explorer
        
        Args:
            path: Folder path
            
        Returns:
            Status message
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.isdir(path):
                return f"❌ Directory not found: {path}"
            
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
            
            return f"✅ Opening folder: {path}"
        
        except Exception as e:
            return f"❌ Error opening folder: {e}"
    
    @staticmethod
    def get_file_info(path: str) -> str:
        """Get detailed file information"""
        try:
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                return f"❌ File not found: {path}"
            
            stat = os.stat(path)
            
            result = f"📄 File Information: {path}\n\n"
            result += f"Size: {FileManager._format_size(stat.st_size)}\n"
            result += f"Created: {datetime.fromtimestamp(stat.st_ctime)}\n"
            result += f"Modified: {datetime.fromtimestamp(stat.st_mtime)}\n"
            result += f"Accessed: {datetime.fromtimestamp(stat.st_atime)}\n"
            
            if os.path.isfile(path):
                result += f"Type: File\n"
                # Get extension
                _, ext = os.path.splitext(path)
                result += f"Extension: {ext}\n"
            else:
                result += f"Type: Directory\n"
            
            return result
        
        except Exception as e:
            return f"❌ Error getting file info: {e}"
    
    @staticmethod
    def delete_file(path: str, confirm: bool = True) -> str:
        """
        Delete a file
        
        Args:
            path: File path
            confirm: Require confirmation (for safety)
            
        Returns:
            Status message
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                return f"❌ File not found: {path}"
            
            if os.path.isdir(path):
                return "❌ Use delete_folder for directories"
            
            os.remove(path)
            return f"✅ Deleted: {path}"
        
        except Exception as e:
            return f"❌ Error deleting file: {e}"
    
    @staticmethod
    def delete_folder(path: str) -> str:
        """
        Delete a folder and contents
        
        Args:
            path: Folder path
            
        Returns:
            Status message
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.isdir(path):
                return f"❌ Directory not found: {path}"
            
            shutil.rmtree(path)
            return f"✅ Deleted folder: {path}"
        
        except Exception as e:
            return f"❌ Error deleting folder: {e}"
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @staticmethod
    def get_current_directory() -> str:
        """Get current working directory"""
        return os.getcwd()
    
    @staticmethod
    def change_directory(path: str) -> str:
        """Change working directory"""
        try:
            path = os.path.expanduser(path)
            
            if not os.path.isdir(path):
                return f"❌ Directory not found: {path}"
            
            os.chdir(path)
            return f"✅ Changed to: {os.getcwd()}"
        
        except Exception as e:
            return f"❌ Error changing directory: {e}"
