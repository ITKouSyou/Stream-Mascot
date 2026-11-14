import pygame
import random
import math
from config import COLOR_DESK, COLOR_OUTLINE, COLOR_CAT, COLOR_PAW

class Particle:
    def __init__(self, x, y, color, ptype="heart"):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1) # 向上飘
        self.life = random.randint(30, 60) # 存活帧数
        self.max_life = self.life
        self.color = color
        self.ptype = ptype
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1 # 模拟重力（稍微有点下坠感）
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        
        # 创建一个临时 Surface 来画带透明度的粒子
        temp = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        
        if self.ptype == "heart":
            # 简笔画爱心
            pygame.draw.circle(temp, c, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(temp, c, (self.size*1.5, self.size//2), self.size//2)
            pygame.draw.polygon(temp, c, [
                (0, self.size//2), 
                (self.size*2, self.size//2), 
                (self.size, self.size*2)
            ])
        else:
            # 星星/圆点
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
    def __init__(self, x, y, options):
        self.rect = pygame.Rect(x, y, 100, len(options) * 30 + 10)
        self.options = options # 列表格式: [("比心", "heart"), ("生气", "angry")]
        self.hover_index = -1

    def draw(self, surface, font):
        # 画菜单背景
        pygame.draw.rect(surface, (40, 40, 45), self.rect, border_radius=6)
        pygame.draw.rect(surface, (100, 200, 255), self.rect, 2, border_radius=6)
        
        # 画选项
        for i, (text, action) in enumerate(self.options):
            item_rect = pygame.Rect(self.rect.x, self.rect.y + 5 + i*30, self.rect.width, 30)
            if i == self.hover_index:
                pygame.draw.rect(surface, (70, 70, 75), item_rect)
            
            text_surf = font.render(text, True, (255, 255, 255))
            surface.blit(text_surf, (item_rect.x + 15, item_rect.y + 6))

    def check_click(self, pos):
        if not self.rect.collidepoint(pos):
            return None
        for i, (text, action) in enumerate(self.options):
            item_rect = pygame.Rect(self.rect.x, self.rect.y + 5 + i*30, self.rect.width, 30)
            if item_rect.collidepoint(pos):
                return action
        return None
        
    def update_hover(self, pos):
        self.hover_index = -1
        if self.rect.collidepoint(pos):
            for i in range(len(self.options)):
                item_rect = pygame.Rect(self.rect.x, self.rect.y + 5 + i*30, self.rect.width, 30)
                if item_rect.collidepoint(pos):
                    self.hover_index = i
                    break