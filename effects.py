import pygame
import random
import math
from config import COLOR_DESK, COLOR_OUTLINE, COLOR_CAT, COLOR_PAW

class Particle:
    def __init__(self, x, y, color, ptype="heart"):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.life = random.randint(30, 60)
        self.max_life = self.life
        self.color = color
        self.ptype = ptype
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        temp = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        
        if self.ptype == "heart":
            pygame.draw.circle(temp, c, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(temp, c, (self.size*1.5, self.size//2), self.size//2)
            pygame.draw.polygon(temp, c, [(0, self.size//2), (self.size*2, self.size//2), (self.size, self.size*2)])
        else:
            pygame.draw.circle(temp, c, (self.size, self.size), self.size)
            
        surface.blit(temp, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=5, color=(255, 100, 150), ptype="heart"):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, ptype))

    def update_and_draw(self, surface):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
            else:
                p.draw(surface)


class ContextMenu:
    def __init__(self, x, y, options, font):
        self.options = options
        self.hover_index = -1
        
        # 动态计算菜单宽度
        self.item_h = 32
        max_w = 100
        for text, _ in options:
            w, _ = font.size(text)
            max_w = max(max_w, w + 40)  # 左右留白
            
        self.rect = pygame.Rect(x, y, max_w, len(options) * self.item_h + 10)

    def draw(self, surface, font):
        # 画菜单背景阴影/边框
        pygame.draw.rect(surface, (40, 40, 45), self.rect, border_radius=8)
        pygame.draw.rect(surface, (100, 200, 255), self.rect, 2, border_radius=8)
        
        # 画选项
        for i, (text, action) in enumerate(self.options):
            item_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 5 + i*self.item_h, self.rect.width - 4, self.item_h)
            if i == self.hover_index:
                pygame.draw.rect(surface, (70, 70, 75), item_rect, border_radius=4)
            
            text_surf = font.render(text, True, (255, 255, 255))
            # 居中偏左对齐
            surface.blit(text_surf, (item_rect.x + 15, item_rect.y + (self.item_h - text_surf.get_height()) // 2))

    def check_click(self, pos):
        if not self.rect.collidepoint(pos):
            return None
        for i, (text, action) in enumerate(self.options):
            item_rect = pygame.Rect(self.rect.x, self.rect.y + 5 + i*self.item_h, self.rect.width, self.item_h)
            if item_rect.collidepoint(pos):
                return action
        return None
        
    def update_hover(self, pos):
        self.hover_index = -1
        if self.rect.collidepoint(pos):
            for i in range(len(self.options)):
                item_rect = pygame.Rect(self.rect.x, self.rect.y + 5 + i*self.item_h, self.rect.width, self.item_h)
                if item_rect.collidepoint(pos):
                    self.hover_index = i
                    break