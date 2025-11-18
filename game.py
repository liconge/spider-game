import pygame
import random
from typing import List, Tuple, Set
from collections import deque

class Player:
    """Represents the fly controlled by the player."""

    def __init__(self, x: int, y: int, speed: int = 4):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 4
        self.is_drawing = False
        # Store floating point for precise movement
        self._px = float(x)
        self._py = float(y)
        self.current_path: List[Tuple[int, int]] = []

    def move(self, dx: int, dy: int, width: int, height: int, is_safe_func):
        """Move the player."""
        # Update position
        self._px = max(0, min(width - 1, self._px + dx * self.speed))
        self._py = max(0, min(height - 1, self._py + dy * self.speed))

        self.x = int(self._px)
        self.y = int(self._py)

        is_safe = is_safe_func(self.x, self.y)

        if not self.is_drawing:
            # If we were safe and moved into unsafe, START drawing
            if not is_safe:
                self.is_drawing = True
                # Add the take-off point (safe point) from previous frame
                self.current_path = [(int(self.x - dx*self.speed), int(self.y - dy*self.speed))]
                self.current_path.append((self.x, self.y))
        else:
            # We are drawing
            if not self.current_path or \
               abs(self.x - self.current_path[-1][0]) > 0 or \
               abs(self.y - self.current_path[-1][1]) > 0:
                self.current_path.append((self.x, self.y))

    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)


class Spider:
    """Represents the enemy spider."""

    def __init__(self, x: int, y: int, speed: float = 2.0):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.trail: deque = deque(maxlen=40)

    def update(self, width: int, height: int, is_safe_func):
        """Update spider position, bouncing off REVEALED edges."""
        next_x = self.x + self.direction[0] * self.speed
        next_y = self.y + self.direction[1] * self.speed

        # Bounce logic: Check if the NEXT position is Safe (Revealed/Border)
        # If it is safe, we bounce because spiders can only live in the Dark (Unsafe).

        hit_wall_x = False
        hit_wall_y = False

        # Check bounds and safe zones
        if next_x <= 0 or next_x >= width - 1 or is_safe_func(int(next_x), int(self.y)):
            hit_wall_x = True

        if next_y <= 0 or next_y >= height - 1 or is_safe_func(int(self.x), int(next_y)):
            hit_wall_y = True

        if hit_wall_x:
            self.direction[0] *= -1
            next_x = self.x # Cancel move

        if hit_wall_y:
            self.direction[1] *= -1
            next_y = self.y # Cancel move

        self.x = next_x
        self.y = next_y
        self.trail.append((int(self.x), int(self.y)))

    def get_position(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))


class GameState:
    """Manages the game state using a Grid System."""

    def __init__(self, width: int, height: int, difficulty: str = "medium"):
        self.width = width
        self.height = height

        # LOGIC GRID: Downscale for performance.
        # A 800x600 screen becomes roughly a 100x75 grid.
        self.scale = 8

        # Calculate grid dimensions to fully cover the screen pixels
        self.grid_w = (width - 1) // self.scale + 1
        self.grid_h = (height - 1) // self.scale + 1

        # Grid: False = Covered (Danger), True = Revealed (Safe)
        self.grid = [[False for _ in range(self.grid_w)] for _ in range(self.grid_h)]

        # --- FIX: MARK BORDERS AS SAFE ON THE GRID ---
        # This ensures that when the player connects to the right/bottom edge,
        # the grid actually recognizes it as a closed loop.

        # Mark Top and Bottom rows
        for x in range(self.grid_w):
            self.grid[0][x] = True
            self.grid[self.grid_h - 1][x] = True

        # Mark Left and Right columns
        for y in range(self.grid_h):
            self.grid[y][0] = True
            self.grid[y][self.grid_w - 1] = True

        # ---------------------------------------------

        self.newly_revealed_rects: List[Tuple[int,int,int,int]] = []

        # Difficulty settings
        spider_speeds = {"easy": 2.0, "medium": 3.0, "hard": 4.0}
        spider_counts = {"easy": 1, "medium": 2, "hard": 3}

        speed = spider_speeds.get(difficulty, 3.0)
        count = spider_counts.get(difficulty, 2)

        self.player = Player(0, 0, speed=4)

        self.spiders: List[Spider] = []
        for _ in range(count):
            sx = random.randint(100, width - 100)
            sy = random.randint(100, height - 100)
            self.spiders.append(Spider(sx, sy, speed=speed))

        self.game_over = False
        self.won = False
        self.total_revealed_pixels = 0

    def is_safe_pixel(self, x: int, y: int) -> bool:
        """Check if a pixel coordinate is safe (revealed or border)."""
        # Clamp coordinates to grid bounds
        gx = int(x) // self.scale
        gy = int(y) // self.scale

        if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
            return self.grid[gy][gx]

        # Fallback for out of bounds (should be safe)
        return True

    def check_collision_with_spider(self) -> bool:
        """Check collision between player/path and spider."""
        player_pos = self.player.get_position()

        # 1. Check collision with player body
        for spider in self.spiders:
            spos = spider.get_position()
            dist = ((player_pos[0] - spos[0])**2 + (player_pos[1] - spos[1])**2)**0.5
            if dist < 15:
                return True

        # 2. Check collision with path being drawn
        if len(self.player.current_path) > 1:
            path_set = set()
            for px, py in self.player.current_path:
                path_set.add((px // 10, py // 10))

            for spider in self.spiders:
                spos = spider.get_position()
                # Check spider body
                if (spos[0] // 10, spos[1] // 10) in path_set:
                    return True
                # Check trail
                if len(spider.trail) > 0:
                    for tx, ty in spider.trail:
                        if (tx // 10, ty // 10) in path_set:
                            return True
        return False

    def process_capture(self):
        path = self.player.current_path
        if not path:
            return

        # 1. Rasterize path to grid solid wall (Bresenham)
        path_grid_points = set()

        def plot_line(x0, y0, x1, y1):
            points = []
            gx0, gy0 = x0 // self.scale, y0 // self.scale
            gx1, gy1 = x1 // self.scale, y1 // self.scale

            dx = abs(gx1 - gx0)
            dy = abs(gy1 - gy0)
            sx = 1 if gx0 < gx1 else -1
            sy = 1 if gy0 < gy1 else -1
            err = dx - dy

            while True:
                if 0 <= gx0 < self.grid_w and 0 <= gy0 < self.grid_h:
                    # Only mark if it's not already safe
                    if not self.grid[gy0][gx0]:
                        self.grid[gy0][gx0] = True
                        points.append((gx0, gy0))

                if gx0 == gx1 and gy0 == gy1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    gx0 += sx
                if e2 < dx:
                    err += dx
                    gy0 += sy
            return points

        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i+1]
            segment_points = plot_line(p1[0], p1[1], p2[0], p2[1])
            path_grid_points.update(segment_points)

        # 2. Prepare Flood Fill
        covered_points = set()
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if not self.grid[y][x]:
                    covered_points.add((x, y))

        # 3. Flood Fill from Spiders
        queue = deque()
        visited = set()

        for spider in self.spiders:
            sgx, sgy = int(spider.x) // self.scale, int(spider.y) // self.scale

            start_nodes = []
            # Check the spider's current cell
            if (sgx, sgy) in covered_points:
                start_nodes.append((sgx, sgy))
            else:
                # Spider might be overlapping the newly drawn wall slightly
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                     if (sgx+dx, sgy+dy) in covered_points:
                         start_nodes.append((sgx+dx, sgy+dy))

            for node in start_nodes:
                if node not in visited:
                    queue.append(node)
                    visited.add(node)

        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in covered_points and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # 4. Reveal Captured
        captured_pixels = 0
        for gx, gy in covered_points:
            if (gx, gy) not in visited:
                self.grid[gy][gx] = True
                self.newly_revealed_rects.append(
                    (gx * self.scale, gy * self.scale, self.scale, self.scale)
                )
                captured_pixels += 1

        # Add path to updates
        for gx, gy in path_grid_points:
             self.newly_revealed_rects.append(
                (gx * self.scale, gy * self.scale, self.scale, self.scale)
            )

        self.total_revealed_pixels += captured_pixels * (self.scale * self.scale)

    def update(self):
        self.newly_revealed_rects = []

        for spider in self.spiders:
            spider.update(self.width, self.height, self.is_safe_pixel)

        if self.check_collision_with_spider():
            self.game_over = True
            return

        current_safe = self.is_safe_pixel(self.player.x, self.player.y)

        if self.player.is_drawing and current_safe:
            self.player.is_drawing = False
            self.process_capture()
            self.player.current_path = []

        if (self.total_revealed_pixels / (self.width * self.height)) > 0.75:
            self.won = True
