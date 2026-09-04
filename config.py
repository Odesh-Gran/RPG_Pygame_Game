import pygame

# ===== РАЗМЕРЫ ЭКРАНА =====
WIDTH, HEIGHT = 1920, 1080
FPS = 60

# ===== ЦВЕТА =====
BLACK = (10, 10, 10)
DARK_BLUE = (26, 26, 46)
DARK_RED = (45, 27, 27)
GOLD = (184, 134, 11)
BLOOD_RED = (158, 43, 43)
WHITE = (200, 200, 200)
GRAY = (80, 80, 80)
DARK_PURPLE = (40, 30, 60)

HEALTH_GREEN = (0, 255, 0)
HEALTH_YELLOW = (255, 255, 0)
HEALTH_RED = (255, 0, 0)
HEALTH_BG = (60, 60, 60)

# ===== ШРИФТЫ (создаются при вызове) =====
def get_fonts():
    """Возвращает шрифты. Вызывать ПОСЛЕ pygame.init()"""
    return {
        "tiny": pygame.font.Font(None, 12),
        "small": pygame.font.Font(None, 24),
        "medium": pygame.font.Font(None, 32),
        "large": pygame.font.Font(None, 48)
    }