import pygame
import math
from config import COLOR_OUTLINE, COLOR_PAW

class BaseExpression:
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        pass

class NormalExpression(BaseExpression):
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        eye_color = COLOR_OUTLINE
        l_eye = (cx - 50, cy + 5)
        r_eye = (cx + 50, cy + 5)
        mouth_cx, mouth_cy = cx, cy + 10

        if is_talking:
            pygame.draw.arc(surface, eye_color, (l_eye[0] - 15, l_eye[1] - 10, 30, 20), 3.14, 0, 4)
            pygame.draw.arc(surface, eye_color, (r_eye[0] - 15, r_eye[1] - 10, 30, 20), 3.14, 0, 4)
            if mouth_open:
                pygame.draw.ellipse(surface, eye_color, (mouth_cx - 15, mouth_cy + 5, 30, 22))
                pygame.draw.ellipse(surface, (200, 80, 100), (mouth_cx - 12, mouth_cy + 8, 24, 16))
                pygame.draw.ellipse(surface, COLOR_PAW, (mouth_cx - 7, mouth_cy + 15, 14, 7))
            else:
                pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)
        elif is_blinking:
            pygame.draw.line(surface, eye_color, (l_eye[0] - 10, l_eye[1]), (l_eye[0] + 10, l_eye[1]), 4)
            pygame.draw.line(surface, eye_color, (r_eye[0] - 10, r_eye[1]), (r_eye[0] + 10, r_eye[1]), 4)
            pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)
        else:
            pygame.draw.circle(surface, eye_color, l_eye, 7)
            pygame.draw.circle(surface, eye_color, r_eye, 7)
            pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)

class HeartExpression(BaseExpression):
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        eye_color = COLOR_OUTLINE
        pink = (255, 100, 150)
        l_eye = (cx - 50, cy + 5)
        r_eye = (cx + 50, cy + 5)
        mouth_cx, mouth_cy = cx, cy + 10
        
        for px, py in [l_eye, r_eye]:
            pygame.draw.circle(surface, pink, (px - 4, py - 5), 6)
            pygame.draw.circle(surface, pink, (px + 4, py - 5), 6)
            pygame.draw.polygon(surface, pink, [(px - 10, py - 2), (px + 10, py - 2), (px, py + 10)])
        pygame.draw.lines(surface, eye_color, False, [(mouth_cx - 15, mouth_cy), (mouth_cx - 8, mouth_cy + 8), (mouth_cx, mouth_cy), (mouth_cx + 8, mouth_cy + 8), (mouth_cx + 15, mouth_cy)], 4)

class AngryExpression(BaseExpression):
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        eye_color = COLOR_OUTLINE
        l_eye = (cx - 50, cy + 5)
        r_eye = (cx + 50, cy + 5)
        mouth_cx, mouth_cy = cx, cy + 10
        
        pygame.draw.line(surface, eye_color, (l_eye[0] - 10, l_eye[1] - 10), (l_eye[0] + 10, l_eye[1] + 3), 5)
        pygame.draw.line(surface, eye_color, (r_eye[0] + 10, r_eye[1] - 10), (r_eye[0] - 10, r_eye[1] + 3), 5)
        pygame.draw.line(surface, eye_color, (mouth_cx - 10, mouth_cy + 10), (mouth_cx + 10, mouth_cy + 10), 4)

class CryExpression(BaseExpression):
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        eye_color = COLOR_OUTLINE
        l_eye = (cx - 50, cy + 5)
        r_eye = (cx + 50, cy + 5)
        mouth_cx, mouth_cy = cx, cy + 10
        
        pygame.draw.arc(surface, eye_color, (l_eye[0] - 10, l_eye[1] - 10, 20, 15), 3.14, 0, 3)
        pygame.draw.arc(surface, eye_color, (r_eye[0] - 10, r_eye[1] - 10, 20, 15), 3.14, 0, 3)
        pygame.draw.ellipse(surface, (100, 200, 255), (l_eye[0] - 5, l_eye[1] + 5, 6, 12))
        pygame.draw.ellipse(surface, (100, 200, 255), (r_eye[0] - 5, r_eye[1] + 5, 6, 12))
        pygame.draw.arc(surface, eye_color, (mouth_cx - 10, mouth_cy + 5, 10, 10), 3.14, 0, 3)
        pygame.draw.arc(surface, eye_color, (mouth_cx, mouth_cy + 5, 10, 10), 0, 3.14, 3)

class SurprisedExpression(BaseExpression):
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        eye_color = COLOR_OUTLINE
        l_eye = (cx - 50, cy + 5)
        r_eye = (cx + 50, cy + 5)
        mouth_cx, mouth_cy = cx, cy + 10
        
        pygame.draw.circle(surface, eye_color, l_eye, 10, 4)
        pygame.draw.circle(surface, eye_color, r_eye, 10, 4)
        pygame.draw.circle(surface, eye_color, (mouth_cx, mouth_cy + 10), 7, 3)

class SpeechlessExpression(BaseExpression):
    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open):
        eye_color = COLOR_OUTLINE
        l_eye = (cx - 50, cy + 5)
        r_eye = (cx + 50, cy + 5)
        mouth_cx, mouth_cy = cx, cy + 10
        
        pygame.draw.line(surface, eye_color, (l_eye[0] - 10, l_eye[1]), (l_eye[0] + 10, l_eye[1]), 4)
        pygame.draw.line(surface, eye_color, (r_eye[0] - 10, r_eye[1]), (r_eye[0] + 10, r_eye[1]), 4)
        pygame.draw.line(surface, eye_color, (mouth_cx - 10, mouth_cy + 5), (mouth_cx + 10, mouth_cy + 5), 3)
        pygame.draw.ellipse(surface, (100, 200, 255), (r_eye[0] + 15, r_eye[1] - 25, 6, 12))

class ExpressionManager:
    def __init__(self):
        self.expressions = {
            "normal": NormalExpression(),
            "heart": HeartExpression(),
            "angry": AngryExpression(),
            "cry": CryExpression(),
            "surprised": SurprisedExpression(),
            "speechless": SpeechlessExpression()
        }

    def draw(self, surface, cx, cy, is_blinking, is_talking, mouth_open, expression_name):
        # 如果找不到表情，默认回退到 normal
        exp = self.expressions.get(expression_name, self.expressions["normal"])
        exp.draw(surface, cx, cy, is_blinking, is_talking, mouth_open)