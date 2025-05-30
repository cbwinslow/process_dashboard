"""
Matrix-style background rain effect.
"""

import random
from typing import List
from textual.geometry import Size
from textual.widget import Widget
from textual.message import Message
from rich.segment import Segment
from rich.style import Style
import asyncio

MATRIX_CHARS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ1234567890"

class RainDrop:
    """A single matrix rain drop."""
    
    def __init__(self, x: int, height: int):
        self.x = x
        self.y = -random.randint(1, 10)
        self.speed = random.uniform(0.3, 1.0)
        self.length = random.randint(3, 10)
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.length)]
        self.intensities = [1.0] * self.length
        self.height = height

    def update(self) -> None:
        """Update raindrop position and characters."""
        self.y += self.speed
        if random.random() < 0.1:
            self.chars[random.randint(0, self.length - 1)] = random.choice(MATRIX_CHARS)
        for i in range(self.length):
            self.intensities[i] = max(0.1, self.intensities[i] - 0.05)

    def is_visible(self) -> bool:
        """Check if the raindrop is still visible."""
        return self.y - self.length < self.height

class MatrixBackground(Widget):
    """Matrix rain background effect widget."""

    DEFAULT_CSS = """
    MatrixBackground {
        layer: background;
        width: 100%;
        height: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        self.raindrops: List[RainDrop] = []
        self._running = True

    def on_mount(self) -> None:
        """Start the animation when mounted."""
        self.set_interval(0.1, self.animate)

    def animate(self) -> None:
        """Update the rain animation."""
        # Update existing raindrops
        self.raindrops = [drop for drop in self.raindrops if drop.is_visible()]
        for drop in self.raindrops:
            drop.update()

        # Add new raindrops
        if random.random() < 0.3:
            x = random.randint(0, self.size.width - 1)
            self.raindrops.append(RainDrop(x, self.size.height))

        self.refresh()

    def render(self) -> List[List[Segment]]:
        """Render the current frame of the matrix rain."""
        width = self.size.width
        height = self.size.height
        canvas = [[Segment(" ")] * width for _ in range(height)]

        for drop in self.raindrops:
            for i, (char, intensity) in enumerate(zip(drop.chars, drop.intensities)):
                y = int(drop.y) - i
                if 0 <= y < height:
                    green = int(255 * intensity)
                    style = Style(color=f"rgb(0,{green},0)", opacity=0.5)
                    canvas[y][drop.x] = Segment(char, style)

        return canvas

