"""
Animations Module for JARVIS HUD

Provides smooth transitions and animations for UI elements.
"""

import math
import time
from typing import Callable, Optional
from dataclasses import dataclass
from enum import Enum


class EasingFunction(Enum):
    """Available easing functions."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    SMOOTH = "smooth"


@dataclass
class AnimationState:
    """Tracks state of an animation."""
    start_value: float
    end_value: float
    duration: float
    elapsed: float
    repeat: bool
    on_complete: Optional[Callable] = None
    easing: EasingFunction = EasingFunction.EASE_IN_OUT


class Animator:
    """
    Manages smooth animations for UI elements.
    
    Features:
    - Multiple easing functions
    - Repeat and loop support
    - Completion callbacks
    - Batch animations
    """
    
    def __init__(self):
        """Initialize animator."""
        self.animations = {}  # {id: AnimationState}
        self.animation_counter = 0
    
    def animate(
        self,
        start: float,
        end: float,
        duration: float,
        easing: EasingFunction = EasingFunction.EASE_IN_OUT,
        repeat: bool = False,
        on_complete: Optional[Callable] = None
    ) -> str:
        """
        Start a new animation.
        
        Args:
            start: Starting value
            end: Ending value
            duration: Duration in seconds
            easing: Easing function to use
            repeat: Whether to repeat animation
            on_complete: Callback when animation completes
            
        Returns:
            Animation ID
        """
        anim_id = f"anim_{self.animation_counter}"
        self.animation_counter += 1
        
        self.animations[anim_id] = AnimationState(
            start_value=start,
            end_value=end,
            duration=duration,
            elapsed=0.0,
            repeat=repeat,
            on_complete=on_complete,
            easing=easing
        )
        
        return anim_id
    
    def update(self, delta_time: float):
        """
        Update all animations.
        
        Args:
            delta_time: Time since last update (seconds)
        """
        completed = []
        
        for anim_id, state in self.animations.items():
            state.elapsed += delta_time
            
            # Check if animation should repeat
            if state.elapsed >= state.duration:
                if state.repeat:
                    state.elapsed = state.elapsed % state.duration
                else:
                    completed.append((anim_id, state))
        
        # Remove completed animations
        for anim_id, state in completed:
            if state.on_complete:
                state.on_complete()
            del self.animations[anim_id]
    
    def get_value(self, anim_id: str) -> Optional[float]:
        """
        Get current animated value.
        
        Args:
            anim_id: Animation ID
            
        Returns:
            Current interpolated value
        """
        if anim_id not in self.animations:
            return None
        
        state = self.animations[anim_id]
        progress = state.elapsed / state.duration
        progress = min(progress, 1.0)  # Clamp to [0, 1]
        
        # Apply easing
        eased = self._apply_easing(progress, state.easing)
        
        # Interpolate
        value = state.start_value + (state.end_value - state.start_value) * eased
        
        return value
    
    def stop(self, anim_id: str):
        """Stop an animation."""
        if anim_id in self.animations:
            del self.animations[anim_id]
    
    def stop_all(self):
        """Stop all animations."""
        self.animations.clear()
    
    @staticmethod
    def _apply_easing(progress: float, easing: EasingFunction) -> float:
        """
        Apply easing function to progress.
        
        Args:
            progress: Progress value (0.0-1.0)
            easing: Easing function
            
        Returns:
            Eased progress value
        """
        if easing == EasingFunction.LINEAR:
            return progress
        
        elif easing == EasingFunction.EASE_IN:
            return progress * progress
        
        elif easing == EasingFunction.EASE_OUT:
            return 1.0 - (1.0 - progress) * (1.0 - progress)
        
        elif easing == EasingFunction.EASE_IN_OUT:
            if progress < 0.5:
                return 2.0 * progress * progress
            else:
                return 1.0 - 2.0 * (1.0 - progress) * (1.0 - progress)
        
        elif easing == EasingFunction.SMOOTH:
            # Smooth step function
            return progress * progress * (3.0 - 2.0 * progress)
        
        elif easing == EasingFunction.BOUNCE:
            # Bounce effect
            if progress < 0.5:
                return 0.5 * math.sin(progress * math.pi * 3)
            else:
                return 0.5 + 0.5 * math.sin((progress - 0.5) * math.pi)
        
        elif easing == EasingFunction.ELASTIC:
            # Elastic effect
            return math.sin(progress * math.pi * 5) * math.exp(-progress * 3)
        
        else:
            return progress


class Keyframe:
    """Represents a keyframe in an animation sequence."""
    
    def __init__(self, time: float, value: float):
        """
        Initialize keyframe.
        
        Args:
            time: Time at which this keyframe occurs (0.0-1.0)
            value: Value at this time
        """
        self.time = time
        self.value = value


class Sequence:
    """
    Manages a sequence of animated values (timeline).
    
    Features:
    - Multiple keyframes
    - Smooth interpolation between keyframes
    - Can repeat
    """
    
    def __init__(self, repeat: bool = False):
        """
        Initialize sequence.
        
        Args:
            repeat: Whether to repeat the sequence
        """
        self.keyframes = []
        self.repeat = repeat
        self.elapsed = 0.0
        self.total_duration = 0.0
    
    def add_keyframe(self, time: float, value: float):
        """Add keyframe to sequence."""
        self.keyframes.append(Keyframe(time, value))
        self.keyframes.sort(key=lambda k: k.time)
        
        # Update total duration
        if self.keyframes:
            self.total_duration = self.keyframes[-1].time
    
    def update(self, delta_time: float):
        """Update sequence."""
        self.elapsed += delta_time
        
        if self.repeat and self.elapsed >= self.total_duration:
            self.elapsed = self.elapsed % self.total_duration
    
    def get_value(self) -> float:
        """Get current value in sequence."""
        if not self.keyframes:
            return 0.0
        
        progress = self.elapsed / self.total_duration if self.total_duration > 0 else 0.0
        
        # Find surrounding keyframes
        for i in range(len(self.keyframes) - 1):
            if self.keyframes[i].time <= progress <= self.keyframes[i + 1].time:
                # Interpolate between keyframes
                k1, k2 = self.keyframes[i], self.keyframes[i + 1]
                
                # Normalize progress between these keyframes
                frame_progress = (progress - k1.time) / (k2.time - k1.time)
                frame_progress = max(0.0, min(1.0, frame_progress))
                
                # Smooth interpolation
                eased = frame_progress * frame_progress * (3.0 - 2.0 * frame_progress)
                value = k1.value + (k2.value - k1.value) * eased
                
                return value
        
        # Return last keyframe value
        return self.keyframes[-1].value


class FadeTransition:
    """Fade in/out animation."""
    
    def __init__(self, duration: float = 0.5):
        """
        Initialize fade transition.
        
        Args:
            duration: Duration in seconds
        """
        self.duration = duration
        self.elapsed = 0.0
        self.fading_in = True
    
    def update(self, delta_time: float):
        """Update fade."""
        self.elapsed += delta_time
        if self.elapsed > self.duration:
            self.elapsed = self.duration
    
    def get_opacity(self) -> float:
        """Get current opacity (0.0-1.0)."""
        progress = self.elapsed / self.duration
        if self.fading_in:
            return progress
        else:
            return 1.0 - progress
    
    def is_complete(self) -> bool:
        """Check if fade is complete."""
        return self.elapsed >= self.duration
    
    def reset(self):
        """Reset fade animation."""
        self.elapsed = 0.0


class SlideTransition:
    """Slide in/out animation."""
    
    def __init__(self, dx: float = 0, dy: float = 0, duration: float = 0.5):
        """
        Initialize slide transition.
        
        Args:
            dx: Horizontal distance to slide
            dy: Vertical distance to slide
            duration: Duration in seconds
        """
        self.dx = dx
        self.dy = dy
        self.duration = duration
        self.elapsed = 0.0
        self.sliding_in = True
    
    def update(self, delta_time: float):
        """Update slide."""
        self.elapsed += delta_time
        if self.elapsed > self.duration:
            self.elapsed = self.duration
    
    def get_offset(self) -> tuple:
        """Get current offset (x, y)."""
        progress = self.elapsed / self.duration
        
        # Ease in/out
        eased = progress * progress * (3.0 - 2.0 * progress)
        
        if self.sliding_in:
            return (self.dx * (1.0 - eased), self.dy * (1.0 - eased))
        else:
            return (self.dx * eased, self.dy * eased)
    
    def is_complete(self) -> bool:
        """Check if slide is complete."""
        return self.elapsed >= self.duration


class ScaleTransition:
    """Scale animation."""
    
    def __init__(self, from_scale: float = 0.0, to_scale: float = 1.0, duration: float = 0.5):
        """
        Initialize scale transition.
        
        Args:
            from_scale: Starting scale
            to_scale: Ending scale
            duration: Duration in seconds
        """
        self.from_scale = from_scale
        self.to_scale = to_scale
        self.duration = duration
        self.elapsed = 0.0
    
    def update(self, delta_time: float):
        """Update scale."""
        self.elapsed += delta_time
        if self.elapsed > self.duration:
            self.elapsed = self.duration
    
    def get_scale(self) -> float:
        """Get current scale."""
        progress = self.elapsed / self.duration
        
        # Ease in/out
        eased = progress * progress * (3.0 - 2.0 * progress)
        
        return self.from_scale + (self.to_scale - self.from_scale) * eased
    
    def is_complete(self) -> bool:
        """Check if animation is complete."""
        return self.elapsed >= self.duration


# Example usage
if __name__ == "__main__":
    print("🎬 Animation Test")
    
    # Test animator
    animator = Animator()
    
    # Create animations
    anim1 = animator.animate(0, 100, 2.0, EasingFunction.EASE_IN_OUT)
    anim2 = animator.animate(0, 1, 1.0, EasingFunction.BOUNCE, repeat=True)
    
    print("\n📊 Animating values...")
    for i in range(20):
        animator.update(0.1)
        val1 = animator.get_value(anim1)
        val2 = animator.get_value(anim2)
        print(f"Frame {i}: Value1={val1:.1f}, Value2={val2:.2f}")
    
    # Test sequence
    print("\n📈 Sequence Test:")
    seq = Sequence(repeat=True)
    seq.add_keyframe(0.0, 0.0)
    seq.add_keyframe(0.3, 50.0)
    seq.add_keyframe(0.7, 25.0)
    seq.add_keyframe(1.0, 100.0)
    
    for i in range(10):
        seq.update(0.15)
        print(f"Frame {i}: {seq.get_value():.1f}")
    
    # Test transitions
    print("\n🔄 Transition Tests:")
    fade = FadeTransition(duration=1.0)
    print("Fade in: ", end="")
    for i in range(5):
        fade.update(0.2)
        print(f"{fade.get_opacity():.2f} ", end="")
    print()
    
    slide = SlideTransition(dx=100, dy=50, duration=1.0)
    print("Slide: ", end="")
    for i in range(5):
        slide.update(0.2)
        offset = slide.get_offset()
        print(f"({offset[0]:.0f},{offset[1]:.0f}) ", end="")
    print()
