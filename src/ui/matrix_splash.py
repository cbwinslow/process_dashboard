"""
Matrix-style splash screen with digital rain effect.
"""

import asyncio
import random
from typing import List, Tuple, Optional
from textual.widget import Widget
from textual.message import Message
from textual.geometry import Size
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style
from rich import box
from datetime import datetime

# Matrix rain characters (mix of Katakana and other symbols)
MATRIX_CHARS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ1234567890"

class RainDrop:
    """Represents a single column of matrix rain."""
    
    def __init__(self, x: int, height: int):
        self.x = x
        self.height = height
        self.speed = random.uniform(0.5, 2.0)
        self.y = random.randint(-height // 2, 0)
        self.length = random.randint(5, 15)
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.length)]
        self.intensities = [1.0] * self.length  # Start bright
        self.fade_rate = random.uniform(0.05, 0.15)
        self.active = True
        self.last_update = datetime.now().timestamp()

    def update(self, time_delta: float) -> None:
        """Update raindrop position and intensity."""
        if not self.active:
            return

        # Update position
        self.y += self.speed * time_delta * 15

        # Update character intensities
        for i in range(self.length):
            self.intensities[i] = max(0.0, self.intensities[i] - self.fade_rate)
            if random.random() < 0.1:  # 10% chance to change character
                self.chars[i] = random.choice(MATRIX_CHARS)

        # Deactivate if completely off screen
        if self.y - self.length > self.height:
            self.active = False

    def render(self) -> List[Tuple[int, str, float]]:
        """Render the raindrop.

        Returns:
            List of tuples containing (y-position, character, intensity)
        """
        result = []
        for i in range(self.length):
            y = int(self.y) - i
            if 0 <= y < self.height:
                result.append((y, self.chars[i], self.intensities[i]))
        return result

class MatrixSplash(Widget):
    """Matrix-style splash screen widget."""

    class Completed(Message):
        """Sent when the splash animation is complete."""

    DEFAULT_CSS = """
    MatrixSplash {
        width: 100%;
        height: 100%;
        background: #000000;
    }
    """

    def __init__(self):
        super().__init__()
        self.raindrops: List[RainDrop] = []
        self.start_time = 0.0
        self.duration = 3.0  # Animation duration in seconds
        self.fade_in = 0.5   # Fade in duration
        self.fade_out = 0.5  # Fade out duration
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def on_mount(self) -> None:
        """Initialize the animation when the widget is mounted."""
        self.start_time = self.app.time
        self._running = True
        self._task = asyncio.create_task(self._animate())

    def _create_raindrops(self) -> None:
        """Create initial raindrops."""
        width = self.size.width
        height = self.size.height
        
        # Create a raindrop for approximately half the columns
        for x in range(width):
            if random.random() < 0.5:  # 50% chance for each column
                self.raindrops.append(RainDrop(x, height))

    def _get_opacity(self, elapsed: float) -> float:
        """Calculate current opacity based on elapsed time."""
        if elapsed < self.fade_in:
            return elapsed / self.fade_in
        elif elapsed > self.duration - self.fade_out:
            return max(0.0, (self.duration - elapsed) / self.fade_out)
        return 1.0

    async def _animate(self) -> None:
        """Animate the matrix rain effect."""
        self._create_raindrops()
        last_time = self.app.time

        while self._running and (self.app.time - self.start_time) < self.duration:
            # Calculate time delta
            current_time = self.app.time
            time_delta = current_time - last_time
            last_time = current_time

            # Update existing raindrops
            for drop in self.raindrops:
                drop.update(time_delta)

            # Add new raindrops
            if random.random() < 0.1:  # 10% chance each frame
                x = random.randint(0, self.size.width - 1)
                self.raindrops.append(RainDrop(x, self.size.height))

            # Remove inactive raindrops
            self.raindrops = [drop for drop in self.raindrops if drop.active]

            # Trigger a refresh
            self.refresh()
            await asyncio.sleep(1/30)  # Cap at ~30 FPS

        # Animation complete
        self._running = False
        self.post_message(self.Completed())

    def render(self) -> RenderResult:
        """Render the current frame of the matrix rain."""
        width = self.size.width
        height = self.size.height

        # Create a blank canvas
        canvas = [[" " for _ in range(width)] for _ in range(height)]
        intensities = [[0.0 for _ in range(width)] for _ in range(height)]

        # Get overall opacity for fade effect
        elapsed = self.app.time - self.start_time
        opacity = self._get_opacity(elapsed)

        # Render all raindrops
        for drop in self.raindrops:
            for y, char, intensity in drop.render():
                if 0 <= y < height and 0 <= drop.x < width:
                    canvas[y][drop.x] = char
                    intensities[y][drop.x] = intensity * opacity

        # Convert to segments
        segments = []
        for y in range(height):
            line_segments = []
            for x in range(width):
                intensity = intensities[y][x]
                if intensity > 0:
                    # Calculate color based on intensity
                    green = int(255 * intensity)
                    style = Style(color=f"rgb(0,{green},0)")
                    line_segments.append(Segment(canvas[y][x], style))
                else:
                    line_segments.append(Segment(" "))
            segments.append(line_segments)
            segments.append(Segment.line())

        return segments

    async def on_unmount(self) -> None:
        """Clean up when widget is unmounted."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


