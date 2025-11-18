#!/usr/bin/env python3
import pygame
import sys
import os
from game import GameState

class GameRenderer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Picture Reveal Game - Qix Style")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 50, 50)
        self.CYAN = (0, 255, 255)

        # COVER CONFIGURATION
        # We use MAGENTA as the "Color Key". Any pixel with this color
        # becomes fully transparent.
        self.TRANSPARENT_KEY = (255, 0, 255)
        self.COVER_COLOR = (60, 60, 60) # Opaque Dark Gray

        self.background = self._load_background()

        # The Cover Surface
        self.cover_surface = pygame.Surface((width, height))
        self.cover_surface.fill(self.COVER_COLOR)
        self.cover_surface.set_colorkey(self.TRANSPARENT_KEY)

        self.font = pygame.font.Font(None, 36)

    def _load_background(self):
        image_paths = ["assets/background.jpg", "assets/background.png"]
        for path in image_paths:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    return pygame.transform.scale(img, (self.width, self.height))
                except: pass

        # Generate a placeholder pattern
        surf = pygame.Surface((self.width, self.height))
        for x in range(0, self.width, 40):
            for y in range(0, self.height, 40):
                c = (x % 255, y % 255, (x+y)%255)
                pygame.draw.rect(surf, c, (x, y, 40, 40))
        return surf

    def render(self, game_state: GameState):
        # 1. Update the cover surface based on new captures
        if game_state.newly_revealed_rects:
            for rx, ry, rw, rh in game_state.newly_revealed_rects:
                # Draw the "Transparent Key" color to cut holes
                pygame.draw.rect(self.cover_surface, self.TRANSPARENT_KEY, (rx, ry, rw, rh))

        # 2. Draw Background
        self.screen.blit(self.background, (0, 0))

        # 3. Draw Cover (The holes will show the background)
        self.screen.blit(self.cover_surface, (0, 0))

        # 4. Draw Player Drawing Line
        if game_state.player.is_drawing and len(game_state.player.current_path) > 1:
            pygame.draw.lines(self.screen, self.CYAN, False, game_state.player.current_path, 3)

        # 5. Draw Spiders
        for spider in game_state.spiders:
            spos = spider.get_position()
            # Draw Spider Trail
            if len(spider.trail) > 1:
                pygame.draw.lines(self.screen, (255, 100, 100), False, list(spider.trail), 2)
            # Draw Spider Body
            pygame.draw.circle(self.screen, self.RED, spos, 8)

        # 6. Draw Player
        pygame.draw.circle(self.screen, self.CYAN, game_state.player.get_position(), 6)

        # 7. UI
        percent = (game_state.total_revealed_pixels / (self.width * self.height)) * 100
        txt = self.font.render(f"Revealed: {percent:.1f}%", True, self.WHITE)
        self.screen.blit(txt, (10, 10))

        pygame.display.flip()

    def render_game_over(self, won: bool):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        msg = "YOU WIN!" if won else "GAME OVER"
        col = (0, 255, 0) if won else (255, 0, 0)

        txt = self.font.render(msg, True, col)
        tr = txt.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(txt, tr)

        info = self.font.render("Press SPACE to Restart", True, self.WHITE)
        ir = info.get_rect(center=(self.width//2, self.height//2 + 50))
        self.screen.blit(info, ir)

        pygame.display.flip()

def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    clock = pygame.time.Clock()

    renderer = GameRenderer(WIDTH, HEIGHT)
    game_state = GameState(WIDTH, HEIGHT, "medium")

    running = True
    game_over_screen = False

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over_screen:
                    game_state = GameState(WIDTH, HEIGHT, "medium")
                    renderer = GameRenderer(WIDTH, HEIGHT) # Reset cover
                    game_over_screen = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if not game_over_screen:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]: dx = -1
            elif keys[pygame.K_RIGHT]: dx = 1
            elif keys[pygame.K_UP]: dy = -1
            elif keys[pygame.K_DOWN]: dy = 1

            # Pass is_safe_func to move so player knows when they start drawing
            game_state.player.move(dx, dy, WIDTH, HEIGHT, game_state.is_safe_pixel)
            game_state.update()

            if game_state.game_over or game_state.won:
                game_over_screen = True

            renderer.render(game_state)
        else:
            renderer.render_game_over(game_state.won)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
