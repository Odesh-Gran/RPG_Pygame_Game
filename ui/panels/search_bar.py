import pygame
from config import WIDTH, HEIGHT, GOLD, WHITE

def draw_search_bar(game):
    """Рисует шкалу прогресса обыска"""
    if not game.обыск_активен:
        return

    # Параметры шкалы
    ширина = 400
    высота = 30
    x = game.обыск_x
    y = game.обыск_y

    # ===== ЗАТЕМНЕНИЕ ФОНА =====
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    game.screen.blit(s, (0, 0))

    # ===== ФОН ШКАЛЫ =====
    bg_rect = pygame.Rect(x, y, ширина, высота)
    pygame.draw.rect(game.screen, (40, 40, 60), bg_rect)
    pygame.draw.rect(game.screen, GOLD, bg_rect, 2)

    # ===== ЗАПОЛНЕНИЕ ШКАЛЫ =====
    if game.обыск_прогресс > 0:
        заполнение = int(ширина * game.обыск_прогресс)
        fill_rect = pygame.Rect(x + 2, y + 2, заполнение - 4, высота - 4)

        if game.обыск_прогресс < 0.5:
            r = 255
            g = int(255 * (game.обыск_прогресс * 2))
            b = 0
        else:
            r = int(255 * (1 - (game.обыск_прогресс - 0.5) * 2))
            g = 255
            b = 0

        pygame.draw.rect(game.screen, (r, g, b), fill_rect)

    # ===== ТЕКСТ =====
    title_text = game.font_medium.render("ОБЫСК", True, GOLD)
    title_x = x + ширина // 2 - title_text.get_width() // 2
    game.screen.blit(title_text, (title_x, y - 35))

    процент = int(game.обыск_прогресс * 100)
    percent_text = game.font_small.render(f"{процент}%", True, WHITE)
    percent_x = x + ширина // 2 - percent_text.get_width() // 2
    percent_y = y + высота // 2 - percent_text.get_height() // 2
    game.screen.blit(percent_text, (percent_x, percent_y))

    # Анимированная иконка (оставил как было в оригинале, пустые строки)
    if game.обыск_прогресс < 0.5:
        icon = ""
    elif game.обыск_прогресс < 0.8:
        icon = ""
    else:
        icon = ""

    icon_text = game.font_medium.render(icon, True, GOLD)
    game.screen.blit(icon_text, (x - 40, y + 2))

    # Свечение
    glow_rect = pygame.Rect(x - 4, y - 4, ширина + 8, высота + 8)
    glow_alpha = int(50 + 100 * abs(pygame.time.get_ticks() % 500 - 250) / 250)
    pygame.draw.rect(game.screen, (GOLD[0], GOLD[1], GOLD[2], glow_alpha), glow_rect, 2)

def запустить_шкалу_обыска(game):
    """Запускает анимацию шкалы прогресса обыска"""
    game.обыск_активен = True
    game.обыск_прогресс = 0
    game.обыск_таймер = 0
    game.обыск_длительность = 60
    print("🔍 Шкала обыска запущена!")