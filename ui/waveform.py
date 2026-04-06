"""
Waveform Visualization Module for JARVIS HUD

Creates animated waveforms to visualize voice activity.
Shows microphone listening and speaking states.
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
import time


@dataclass
class WavePoint:
    """A single point in the waveform."""
    x: float
    y: float
    magnitude: float


class WaveformVisualizer:
    """
    Creates animated waveforms for voice visualization.
    
    Features:
    - Frequency-based waveform generation
    - Smooth animations
    - Listening and speaking states
    - Custom colors
    """
    
    def __init__(self, width: int = 400, height: int = 80, bars: int = 20):
        """
        Initialize waveform visualizer.
        
        Args:
            width: Canvas width
            height: Canvas height
            bars: Number of bars to display
        """
        self.width = width
        self.height = height
        self.bars = bars
        self.bar_width = width / bars
        self.center_y = height / 2
        
        # Animation state
        self.time = 0.0
        self.frequencies = [0.5] * bars  # Current frequencies
        self.target_frequencies = [0.5] * bars  # Target frequencies
        self.animation_speed = 0.1
        
        # States
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        
        # Colors (RGB tuples)
        self.color_idle = (100, 150, 200)  # Calm blue
        self.color_listening = (100, 200, 150)  # Green
        self.color_speaking = (255, 150, 100)  # Orange
        self.color_processing = (200, 100, 255)  # Purple
        
        self.current_color = self.color_idle
    
    def update(self, delta_time: float = 0.016):
        """
        Update animation state.
        
        Args:
            delta_time: Time since last update (seconds)
        """
        self.time += delta_time
        
        # Smoothly interpolate frequencies
        for i in range(self.bars):
            diff = self.target_frequencies[i] - self.frequencies[i]
            self.frequencies[i] += diff * self.animation_speed
        
        # Determine current color based on state
        if self.is_speaking:
            self.current_color = self.color_speaking
        elif self.is_listening:
            self.current_color = self.color_listening
        elif self.is_processing:
            self.current_color = self.color_processing
        else:
            self.current_color = self.color_idle
    
    def generate_waveform(self) -> List[WavePoint]:
        """
        Generate waveform points for rendering.
        
        Returns:
            List of WavePoint objects
        """
        points = []
        
        for i in range(self.bars):
            x = (i + 0.5) * self.bar_width
            
            # Get frequency for this bar
            freq = self.frequencies[i]
            
            # Create smooth wave using sine
            wave_height = math.sin(self.time * 3 + i * 0.5) * 0.3 + 0.7
            magnitude = freq * wave_height
            
            # Cap magnitude
            magnitude = min(magnitude, 1.0)
            
            # Height from center
            y_offset = (magnitude - 0.5) * self.height
            
            points.append(WavePoint(
                x=x,
                y=self.center_y + y_offset,
                magnitude=magnitude
            ))
        
        return points
    
    def set_frequency_data(self, frequencies: List[float]):
        """
        Set frequency data (typically from audio analysis).
        
        Args:
            frequencies: List of frequency magnitudes (0.0-1.0)
        """
        self.target_frequencies = frequencies[:self.bars]
        
        # Pad if too short
        while len(self.target_frequencies) < self.bars:
            self.target_frequencies.append(0.5)
    
    def set_listening(self, listening: bool = True):
        """Set listening state."""
        self.is_listening = listening
        if listening:
            # Random frequencies for listening animation
            import random
            self.target_frequencies = [0.3 + random.random() * 0.4 for _ in range(self.bars)]
    
    def set_speaking(self, speaking: bool = True):
        """Set speaking state."""
        self.is_speaking = speaking
        if speaking:
            # Animated frequencies for speaking
            self.target_frequencies = [
                0.5 + 0.3 * math.sin(self.time * 5 + i * 0.3) for i in range(self.bars)
            ]
    
    def set_processing(self, processing: bool = True):
        """Set processing/thinking state."""
        self.is_processing = processing
        if processing:
            # Subtle pulsing for processing
            pulse = 0.5 + 0.2 * math.sin(self.time * 2)
            self.target_frequencies = [pulse] * self.bars
    
    def set_idle(self):
        """Set to idle state (no activity)."""
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        self.target_frequencies = [0.5] * self.bars
    
    def get_svg(self, scale: float = 1.0) -> str:
        """
        Generate SVG representation of waveform.
        
        Args:
            scale: Scale factor for rendering
            
        Returns:
            SVG string
        """
        points = self.generate_waveform()
        
        # Build SVG path
        svg_parts = []
        svg_parts.append(f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">')
        
        # Background
        r, g, b = self.current_color
        svg_parts.append(f'<rect width="{self.width}" height="{self.height}" fill="rgba(0,0,0,0.1)"/>')
        
        # Center line
        svg_parts.append(f'<line x1="0" y1="{self.center_y}" x2="{self.width}" y2="{self.center_y}" stroke="rgba({r},{g},{b},0.2)" stroke-width="1"/>')
        
        # Waveform path
        path_data = f'M 0 {self.center_y}'
        for point in points:
            path_data += f' L {point.x} {point.y}'
        
        svg_parts.append(f'<path d="{path_data}" stroke="rgb({r},{g},{b})" stroke-width="2" fill="none" stroke-linecap="round"/>')
        
        # Add bars
        for i, point in enumerate(points):
            bar_x = i * self.bar_width
            bar_height = (point.magnitude - 0.5) * self.height
            
            if bar_height > 0:
                svg_parts.append(f'''
                <rect 
                    x="{bar_x}" 
                    y="{self.center_y - bar_height}" 
                    width="{self.bar_width * 0.8}" 
                    height="{bar_height}" 
                    fill="rgba({r},{g},{b},0.3)"
                    rx="2"
                />
                ''')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def get_ascii_art(self) -> str:
        """
        Generate ASCII art representation of waveform.
        
        Returns:
            ASCII art string
        """
        points = self.generate_waveform()
        
        lines = []
        
        # Create grid
        for row in range(10):
            line = ""
            for col in range(len(points)):
                point = points[col]
                
                # Normalize magnitude to row
                normalized_y = int((1.0 - (point.magnitude - 0.5) * 2) * 10)
                
                if row == normalized_y:
                    line += "█"
                elif abs(row - normalized_y) == 1:
                    line += "▄" if row > normalized_y else "▀"
                else:
                    line += " "
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def get_html_visualization(self) -> str:
        """
        Generate HTML/CSS visualization.
        
        Returns:
            HTML string
        """
        points = self.generate_waveform()
        r, g, b = self.current_color
        
        html = f"""
        <div style="display: flex; align-items: flex-end; gap: 2px; height: 80px; padding: 10px;">
        """
        
        for point in points:
            height = (point.magnitude - 0.5) * 2 * 100
            html += f"""
            <div style="
                width: 12px;
                height: {max(height, 5)}%;
                background: rgb({r},{g},{b});
                border-radius: 2px;
                opacity: 0.8;
            "></div>
            """
        
        html += """
        </div>
        """
        
        return html


class CircleWaveform:
    """
    Circular/radial waveform visualization.
    Useful for central HUD display.
    """
    
    def __init__(self, radius: int = 50, segments: int = 30):
        """
        Initialize circular waveform.
        
        Args:
            radius: Base radius of circle
            segments: Number of segments
        """
        self.radius = radius
        self.segments = segments
        self.time = 0.0
        self.magnitudes = [0.5] * segments
        self.state = "idle"  # idle, listening, speaking, processing
    
    def update(self, delta_time: float = 0.016):
        """Update animation."""
        self.time += delta_time
        
        # Update based on state
        if self.state == "listening":
            import random
            self.magnitudes = [0.3 + random.random() * 0.4 for _ in range(self.segments)]
        elif self.state == "speaking":
            self.magnitudes = [
                0.5 + 0.3 * math.sin(self.time * 5 + i * 2 * math.pi / self.segments)
                for i in range(self.segments)
            ]
        elif self.state == "processing":
            pulse = 0.5 + 0.2 * math.sin(self.time * 3)
            self.magnitudes = [pulse] * self.segments
        else:  # idle
            self.magnitudes = [0.5] * self.segments
    
    def get_svg(self, center_x: float = 60, center_y: float = 60) -> str:
        """Generate SVG for circular waveform."""
        svg_parts = []
        svg_parts.append(f'<svg width="120" height="120" xmlns="http://www.w3.org/2000/svg">')
        
        # State-based color
        colors = {
            'idle': (100, 150, 200),
            'listening': (100, 200, 150),
            'speaking': (255, 150, 100),
            'processing': (200, 100, 255)
        }
        r, g, b = colors.get(self.state, colors['idle'])
        
        # Draw segments
        for i in range(self.segments):
            angle = (i / self.segments) * 2 * math.pi
            inner_r = self.radius * 0.7
            outer_r = self.radius * self.magnitudes[i]
            
            x1 = center_x + inner_r * math.cos(angle)
            y1 = center_y + inner_r * math.sin(angle)
            x2 = center_x + outer_r * math.cos(angle)
            y2 = center_y + outer_r * math.sin(angle)
            
            svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgb({r},{g},{b})" stroke-width="2"/>')
        
        # Center dot
        svg_parts.append(f'<circle cx="{center_x}" cy="{center_y}" r="3" fill="rgb({r},{g},{b})"/>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)


# Example usage
if __name__ == "__main__":
    print("🌊 Waveform Visualizer Test")
    
    # Create visualizer
    waveform = WaveformVisualizer(width=60, height=20, bars=15)
    
    print("\n🎤 Listening state:")
    waveform.set_listening()
    for _ in range(5):
        waveform.update(0.1)
        print(waveform.get_ascii_art())
        print()
    
    print("\n🗣️ Speaking state:")
    waveform.set_speaking()
    for _ in range(5):
        waveform.update(0.1)
        print(waveform.get_ascii_art())
        print()
    
    print("\n🧠 Processing state:")
    waveform.set_processing()
    for _ in range(5):
        waveform.update(0.1)
        print(waveform.get_ascii_art())
        print()
    
    # Circular waveform
    print("\n⭕ Circular Waveform Test:")
    circle = CircleWaveform(radius=50, segments=12)
    circle.state = "speaking"
    print(circle.get_svg())
