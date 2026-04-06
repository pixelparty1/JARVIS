"""
Behavior Tracking System for JARVIS

Tracks user patterns, app usage, command history, and time patterns.
Provides data for predictive engine.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict
import sqlite3


class BehaviorDatabase:
    """
    SQLite database for behavior tracking.
    Efficient storage and querying of usage patterns.
    """
    
    def __init__(self, db_path: str = "behavior.db"):
        """Initialize behavior database."""
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # App usage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY,
                app_name TEXT NOT NULL,
                timestamp REAL NOT NULL,
                duration_seconds REAL,
                day_of_week INTEGER,
                hour_of_day INTEGER
            )
        ''')
        
        # Command history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY,
                command TEXT NOT NULL,
                timestamp REAL NOT NULL,
                success BOOLEAN,
                execution_time REAL,
                context TEXT
            )
        ''')
        
        # Time patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_patterns (
                id INTEGER PRIMARY KEY,
                activity_type TEXT NOT NULL,
                hour_of_day INTEGER,
                day_of_week INTEGER,
                frequency INTEGER,
                last_seen REAL
            )
        ''')
        
        # Prediction accuracy table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_accuracy (
                id INTEGER PRIMARY KEY,
                prediction TEXT NOT NULL,
                actual TEXT,
                timestamp REAL NOT NULL,
                correct BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_app_usage(self, app_name: str, duration: float):
        """Record app usage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = time.time()
        dt = datetime.fromtimestamp(now)
        
        cursor.execute('''
            INSERT INTO app_usage (app_name, timestamp, duration_seconds, day_of_week, hour_of_day)
            VALUES (?, ?, ?, ?, ?)
        ''', (app_name, now, duration, dt.weekday(), dt.hour))
        
        conn.commit()
        conn.close()
    
    def record_command(self, command: str, success: bool, exec_time: float, context: str = ""):
        """Record command execution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO command_history (command, timestamp, success, execution_time, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (command, time.time(), success, exec_time, context))
        
        conn.commit()
        conn.close()
    
    def get_app_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get app usage statistics for last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - (days * 24 * 3600)
        
        cursor.execute('''
            SELECT app_name, COUNT(*) as usage_count, SUM(duration_seconds) as total_duration
            FROM app_usage
            WHERE timestamp > ?
            GROUP BY app_name
            ORDER BY total_duration DESC
        ''', (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {}
        for app_name, count, duration in results:
            stats[app_name] = {
                'usage_count': count,
                'total_duration_seconds': duration or 0
            }
        
        return stats
    
    def get_commands(self, limit: int = 100) -> List[Dict]:
        """Get recent commands."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT command, timestamp, success, execution_time, context
            FROM command_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        commands = []
        for cmd, ts, success, exec_time, context in results:
            commands.append({
                'command': cmd,
                'timestamp': ts,
                'success': success,
                'execution_time': exec_time,
                'context': context
            })
        
        return commands
    
    def get_hourly_pattern(self, activity: str) -> Dict[int, int]:
        """Get activity frequency by hour of day."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hour_of_day, COUNT(*) as frequency
            FROM app_usage
            WHERE app_name = ?
            GROUP BY hour_of_day
        ''', (activity,))
        
        results = cursor.fetchall()
        conn.close()
        
        pattern = {h: 0 for h in range(24)}
        for hour, freq in results:
            pattern[hour] = freq
        
        return pattern


class BehaviorTracker:
    """
    High-level behavior tracking system.
    
    Monitors:
    - App usage patterns
    - Command execution history
    - Time-based patterns
    - User preferences
    """
    
    def __init__(self, db_path: str = "behavior.db", json_backup: str = "behavior.json"):
        """
        Initialize behavior tracker.
        
        Args:
            db_path: Path to SQLite database
            json_backup: Path to JSON backup file
        """
        self.db = BehaviorDatabase(db_path)
        self.json_backup = Path(json_backup)
        
        # In-memory caching
        self.current_app = None
        self.app_start_time = None
        self.session_commands = []
        
        # Analytics
        self.activity_patterns = defaultdict(list)
        self.hourly_patterns = defaultdict(dict)
        
        # Load existing data
        self._load_backup()
        
        print("✅ Behavior Tracker initialized")
    
    def start_app_tracking(self, app_name: str):
        """Start tracking an app."""
        # End previous app
        if self.current_app and self.app_start_time:
            duration = time.time() - self.app_start_time
            self.db.record_app_usage(self.current_app, duration)
        
        # Start new app
        self.current_app = app_name
        self.app_start_time = time.time()
    
    def end_app_tracking(self):
        """End tracking current app."""
        if self.current_app and self.app_start_time:
            duration = time.time() - self.app_start_time
            self.db.record_app_usage(self.current_app, duration)
            self.current_app = None
            self.app_start_time = None
    
    def record_action(self, action: str, success: bool = True, exec_time: float = 0.0):
        """Record user action/command."""
        self.db.record_command(action, success, exec_time)
        self.session_commands.append({
            'action': action,
            'timestamp': datetime.now(),
            'success': success
        })
    
    def get_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.db.get_app_usage_stats(days)
    
    def get_recent_actions(self, limit: int = 50) -> List[str]:
        """Get recent actions."""
        commands = self.db.get_commands(limit)
        return [cmd['command'] for cmd in commands]
    
    def get_app_frequency(self, days: int = 7) -> Dict[str, int]:
        """Get app usage frequency."""
        stats = self.get_usage_stats(days)
        return {app: data['usage_count'] for app, data in stats.items()}
    
    def get_hourly_pattern(self, app: str) -> Dict[int, int]:
        """Get hourly usage pattern for an app."""
        return self.db.get_hourly_pattern(app)
    
    def get_most_used_apps(self, days: int = 7, limit: int = 5) -> List[str]:
        """Get most used apps."""
        stats = self.get_usage_stats(days)
        sorted_apps = sorted(
            stats.items(),
            key=lambda x: x[1]['total_duration_seconds'],
            reverse=True
        )
        return [app for app, _ in sorted_apps[:limit]]
    
    def get_activity_at_time(self, hour: int = None) -> List[str]:
        """Get typical activities at a given hour."""
        if hour is None:
            hour = datetime.now().hour
        
        actions = self.get_recent_actions(limit=100)
        # Filter by time (simplified - would need timestamps)
        return actions[:5]
    
    def predict_next_action(self) -> Optional[str]:
        """
        Predict next likely action based on patterns.
        Simple heuristic version.
        """
        if not self.session_commands:
            return None
        
        # Get recent actions
        recent = [cmd['action'] for cmd in self.session_commands[-5:]]
        
        # Check for patterns
        action_counts = defaultdict(int)
        actions = self.get_recent_actions(limit=50)
        for action in actions:
            action_counts[action] += 1
        
        # Return most frequent
        if action_counts:
            return max(action_counts, key=action_counts.get)
        
        return None
    
    def get_time_pattern_analysis(self) -> Dict[str, Any]:
        """Analyze time-based patterns."""
        stats = self.get_usage_stats(days=7)
        
        analysis = {
            'most_active_apps': self.get_most_used_apps(),
            'current_hour': datetime.now().hour,
            'current_day': datetime.now().strftime('%A'),
            'today_actions': self.session_commands,
        }
        
        # Get patterns for top apps
        for app in analysis['most_active_apps']:
            analysis[f'{app}_hourly'] = self.get_hourly_pattern(app)
        
        return analysis
    
    def get_intervention_recommendations(self) -> List[str]:
        """
        Suggest interventions based on behavior.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze usage
        today_actions = len(self.session_commands)
        if today_actions > 100:
            recommendations.append("You've completed 100+ actions. Time for a break?")
        
        # Check for unusual patterns
        most_used = self.get_most_used_apps()
        if most_used:
            current = self.current_app
            if current and current not in most_used:
                recommendations.append(f"You're using an unusual app: {current}")
        
        return recommendations
    
    def export_report(self) -> Dict[str, Any]:
        """Export comprehensive behavior report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'usage_stats': self.get_usage_stats(),
            'most_used_apps': self.get_most_used_apps(),
            'time_patterns': self.get_time_pattern_analysis(),
            'recent_actions': self.get_recent_actions(limit=20),
            'recommendations': self.get_intervention_recommendations()
        }
    
    def save_backup(self):
        """Save JSON backup of behavior data."""
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'session_commands': [
                {
                    'action': cmd['action'],
                    'timestamp': cmd['timestamp'].isoformat(),
                    'success': cmd['success']
                }
                for cmd in self.session_commands
            ],
            'current_app': self.current_app
        }
        
        try:
            with open(self.json_backup, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print(f"💾 Behavior backup saved to {self.json_backup}")
        except Exception as e:
            print(f"❌ Backup error: {e}")
    
    def _load_backup(self):
        """Load JSON backup if it exists."""
        if self.json_backup.exists():
            try:
                with open(self.json_backup, 'r') as f:
                    backup_data = json.load(f)
                    print(f"✅ Loaded {len(backup_data.get('session_commands', []))} backed-up commands")
            except Exception as e:
                print(f"⚠️  Could not load backup: {e}")


# Global tracker instance
_behavior_tracker = None


def get_behavior_tracker() -> BehaviorTracker:
    """Get or create global behavior tracker."""
    global _behavior_tracker
    if _behavior_tracker is None:
        _behavior_tracker = BehaviorTracker()
    return _behavior_tracker


# Example usage
if __name__ == "__main__":
    print("📊 Behavior Tracker Test")
    
    tracker = get_behavior_tracker()
    
    # Test app tracking
    print("\n📱 App Usage Tracking:")
    tracker.start_app_tracking("VS Code")
    time.sleep(0.1)
    tracker.end_app_tracking()
    
    tracker.start_app_tracking("Chrome")
    time.sleep(0.1)
    tracker.end_app_tracking()
    
    # Test action logging
    print("\n📋 Action Logging:")
    tracker.record_action("search_web", success=True, exec_time=0.5)
    tracker.record_action("create_note", success=True, exec_time=0.2)
    
    # Get stats
    print("\n📊 Statistics:")
    stats = tracker.get_usage_stats()
    for app, data in stats.items():
        print(f"   {app}: {data}")
    
    # Export report
    print("\n📈 Report:")
    report = tracker.export_report()
    print(f"   Most used apps: {report['most_used_apps']}")
    print(f"   Recent actions: {len(report['recent_actions'])}")
    print(f"   Recommendations: {report['recommendations']}")
