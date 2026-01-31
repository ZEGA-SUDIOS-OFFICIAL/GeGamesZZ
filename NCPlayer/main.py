import pygame
import requests
import io
import random
import math
from PIL import Image, ImageSequence

# ZEGA Engineering Specs
BRAND_GREEN = (88, 240, 27)  # #58f01b
BG_COLOR = (5, 5, 10)
RAINBOW_COLORS = [
    (255, 0, 0), (255, 153, 0), (255, 255, 0),
    (51, 255, 0), (0, 153, 255), (102, 51, 255)
]

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

class ZEGANyanEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Initialize Sound Engine
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ZEGA OS - Nyan Flight Protocol v1.3")
        self.clock = pygame.time.Clock()
        
        # Audio Integration
        try:
            pygame.mixer.music.load("music.mp3")
            pygame.mixer.music.play(-1) # Loop indefinitely
        except:
            print("Audio file 'music.mp3' not found. Silent mode active.")

        # Typography
        try:
            self.font = pygame.font.Font("slkscr.ttf", 22)
        except:
            self.font = pygame.font.SysFont("monospace", 18, bold=True)

        # Assets & Particles
        self.stars = [[random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), random.random()] for _ in range(60)]
        self.frames = self.load_gif("https://www.nyan.cat/cats/technyancolor.gif")
        
        # Flight Variables
        self.pos = pygame.Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.trail = [] 
        self.wave_timer = 0
        self.frame_index = 0
        self.running = True

    def load_gif(self, url):
        res = requests.get(url)
        img = Image.open(io.BytesIO(res.content))
        frames = []
        for frame in ImageSequence.Iterator(img):
            f = frame.convert("RGBA").resize((110, 70), Image.NEAREST)
            frames.append(pygame.image.fromstring(f.tobytes(), f.size, "RGBA"))
        return frames

    def update(self):
        # Parallax background
        for s in self.stars:
            s[0] -= (s[2] * 4) + 1
            if s[0] < 0: s[0] = WINDOW_WIDTH

        # Movement handling
        keys = pygame.key.get_pressed()
        vel = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: vel.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: vel.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: vel.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vel.x = 1
        
        if vel.length() > 0:
            self.pos += vel.normalize() * 9
        
        # Trail Logic: Store position for the rainbow
        # We store the "back" of the cat (x-20)
        self.trail.insert(0, (self.pos.x, self.pos.y))
        if len(self.trail) > 50: self.trail.pop()
        
        self.wave_timer += 0.3

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # 1. Starfield
        for s in self.stars:
            pygame.draw.circle(self.screen, (255, 255, 255), (int(s[0]), int(s[1])), 1)

        # 2. Rainbow Waves (Trailing Behind)
        for i, color in enumerate(RAINBOW_COLORS):
            points = []
            for idx, (tx, ty) in enumerate(self.trail):
                # The wave effect oscillates based on trail index and timer
                wave = math.sin(self.wave_timer + (idx * 0.6)) * 6
                # Shift trail to the left of the cat's current position
                px = tx - (idx * 5) + 10
                py = ty + (i * 9) + wave + 8
                points.append((px, py))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, color, False, points, 10)

        # 3. Nyan Pilot
        self.frame_index = (self.frame_index + 0.5) % len(self.frames)
        self.screen.blit(self.frames[int(self.frame_index)], (self.pos.x, self.pos.y))

        # 4. ZEGA HUD
        pygame.draw.rect(self.screen, BRAND_GREEN, (0,0, WINDOW_WIDTH, WINDOW_HEIGHT), 4)
        header = self.font.render("ZEGA RAINBOW-FLIGHT v1.3", True, BRAND_GREEN)
        self.screen.blit(header, (25, 25))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    ZEGANyanEngine().run()