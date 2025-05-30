"""
Matrix-style background effect for Process Dashboard.

This module implements a subtle matrix rain animation that runs
behind the main dashboard interface.
"""

import random
import string
from typing import List, Optional
from textual.widget import Widget
from textual.geometry import Size
from rich.console import RenderableType
from rich.text import Text
import logging

logger = logging.getLogger("dashboard.background")

class RainDrop:
    """Represents a single column of falling characters."""
    
    def __init__(self, x: int, length: int, speed: float, intensity: float = 0.3):
        """Initialize a rain drop.
        
        Args:
            x: X coordinate of the drop
            length: Length of the character trail
            speed: Movement speed (cells per frame)
            intensity: Visual intensity (0.0-1.0)
        """
        self.x = x
        self.y = 0.0  # Using float for smooth movement
        self.length = length
        self.speed = speed
        self.intensity = intensity
        self.chars = [self._random_char() for _ in range(length)]
        self.active = True

    def update(self, height: int) -> None:
        """Update drop position.
        
        Args:
            height: Screen height
        """
        self.y += self.speed
        
        # Randomize some characters
        if random.random() < 0.1:
            idx = random.randint(0, self.length - 1)
            self.chars[idx] = self._random_char()
        
        # Deactivate if completely off screen
        if self.y - self.length > height:
            self.active = False

    def _random_char(self) -> str:
        """Generate a random matrix character."""
        return random.choice(string.ascii_letters + string.digits + "☯←→↑↓○●◐◑◒◓◔◕⬤")

    def get_chars(self) -> List[tuple[int, str, str]]:
        """Get current character positions and styles.
        
        Returns:
            List of (y_position, character, style) tuples
        """
        chars = []
        for i in range(self.length):
            y = int(self.y) - i
            if y >= 0:  # Only return visible characters
                # Fade intensity based on position in trail
                fade = 1.0 - (i / self.length)
                if i == 0:  # Leading character
                    style = "bold bright_green"
                else:
                    alpha = fade * self.intensity
                    if alpha > 0.7:
                        style = "green"
                    elif alpha > 0.4:
                        style = "dark_green"
                    else:
                        style = "dim dark_green"
                chars.append((y, self.chars[i], style))
        return chars

class MatrixBackground(Widget):
    """Matrix rain background widget."""

    DEFAULT_CSS = """
    MatrixBackground {
        layer: background;
        width: 100%;
        height: 100%;
        opacity: 0.3;
    }
    """

    def __init__(self):
        """Initialize the background effect."""
        super().__init__()
        self.drops: List[RainDrop] = []
        self.width = 0
        self.height = 0
        self.frame = 0
        self.intensity = 0.3  # Overall effect intensity
        self._size: Optional[Size] = None

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._size = self.size
        self.width = self._size.width
        self.height = self._size.height
        # Start animation timer
        self.set_interval(0.1, self.animate)

    def animate(self) -> None:
        """Update animation state."""
        self.frame += 1

        # Add new drops
        if self.frame % 3 == 0:  # Control drop frequency
            if random.random() < 0.3:  # 30% chance to add drop
                self._add_drop()

        # Update existing drops
        self.drops = [drop for drop in self.drops if drop.active]
        for drop in self.drops:
            drop.update(self.height)

        self.refresh()

    def _add_drop(self) -> None:
        """Add a new rain drop."""
        x = random.randint(0, self.width - 1)
        length = random.randint(5, 15)
        speed = random.uniform(0.5, 2.0)
        intensity = random.uniform(0.2, 0.4)
        self.drops.append(RainDrop(x, length, speed, intensity))

    def render(self) -> RenderableType:
        """Render the background effect.
        
        Returns:
            Rich renderable for display
        """
        if not self._size:
            return Text()

        # Create empty canvas
        canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]
        styles = [[None for _ in range(self.width)] for _ in range(self.height)]

        # Draw rain drops
        for drop in self.drops:
            for y, char, style in drop.get_chars():
                if 0 <= y < self.height:
                    canvas[y][drop.x] = char
                    styles[y][drop.x] = style

        # Create text output
        text = Text()
        for y in range(self.height):
            for x in range(self.width):
                char = canvas[y][x]
                style = styles[y][x]
                text.append(char, style=style if style else "")
            text.append("\n")

        return text

    def watch_size(self, new_size: Size) -> None:
        """Handle widget resize.
        
        Args:
            new_size: New widget size
        """
        self._size = new_size
        self.width = new_size.width
        self.height = new_size.height
        # Clear existing drops when resized
        self.drops.clear()
