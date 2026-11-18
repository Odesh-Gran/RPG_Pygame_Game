import pygame
from config import WIDTH, HEIGHT, DARK_BLUE, GOLD, DARK_RED, BLACK, WHITE, HEALTH_GREEN, BLOOD_RED

def draw_loot_panel(game):
    """Рисует выезжающую панель лута в стиле игры"""
    if not game.loot_panel_active:
        return

    # Параметры панели
    panel_width = 320
    panel_height = 250
    panel_y = HEIGHT // 2 - panel_height // 2

    # Анимация выезжания
    if game.loot_animation_progress < 1:
        game.loot_animation_progress += 0.05
        if game.loot_animation_progress > 1:
            game.loot_animation_progress = 1

    current_x = -panel_width + (panel_width * game.loot_animation_progress)
    panel_x = int(current_x)

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    # ===== ФОН =====
    pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)
    pygame.draw.rect(game.screen, GOLD, (panel_x + 5, panel_y + 5, panel_width - 10, panel_height - 10), 1)

    # ===== ЗАГОЛОВОК =====
    title = game.font_medium.render("ПОБЕДА!", True, GOLD)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 12))

    # Разделитель
    pygame.draw.line(game.screen, GOLD,
                     (panel_x + 15, panel_y + 42),
                     (panel_x + panel_width - 15, panel_y + 42), 2)

    # ===== ОПЫТ =====
    exp_text = game.font_small.render(f"Опыт: +{game.loot_exp}", True, HEALTH_GREEN)
    game.screen.blit(exp_text, (panel_x + 20, panel_y + 55))

    # ===== ЗАГОЛОВОК ПРЕДМЕТОВ =====
    items_title = game.font_small.render("ПОЛУЧЕНО:", True, GOLD)
    game.screen.blit(items_title, (panel_x + 20, panel_y + 85))

    # ===== СПИСОК ПРЕДМЕТОВ =====
    y_offset = panel_y + 110
    item_height = 28

    for i, item in enumerate(game.loot_items):
        if item in game.item_icons:
            icon = game.item_icons[item]
            icon = pygame.transform.scale(icon, (24, 24))
            game.screen.blit(icon, (panel_x + 20, y_offset + i * item_height - 2))
            text_x = panel_x + 50
        else:
            text_x = panel_x + 20

        item_text = game.font_small.render(f"• {item}", True, WHITE)
        game.screen.blit(item_text, (text_x, y_offset + i * item_height))

    # ===== РЕДКИЙ ПРЕДМЕТ =====
    if game.loot_rare_item:
        rare_y = y_offset + len(game.loot_items) * item_height + 5

        pygame.draw.line(game.screen, GOLD,
                         (panel_x + 15, rare_y - 2),
                         (panel_x + panel_width - 15, rare_y - 2), 1)

        rare_title = game.font_small.render("РЕДКИЙ ДРОП!", True, BLOOD_RED)
        game.screen.blit(rare_title, (panel_x + 100, rare_y))

        if game.loot_rare_item in game.item_icons:
            icon = game.item_icons[game.loot_rare_item]
            icon = pygame.transform.scale(icon, (24, 24))
            game.screen.blit(icon, (panel_x + 20, rare_y + 18))
            text_x = panel_x + 50
        else:
            text_x = panel_x + 20

        rare_text = game.font_small.render(game.loot_rare_item, True, BLOOD_RED)
        game.screen.blit(rare_text, (text_x, rare_y + 23))

    # ===== КНОПКА "ЗАБРАТЬ" =====
    button_rect = pygame.Rect(panel_x + panel_width // 2 - 70,
                              panel_y + panel_height - 48,
                              140, 32)

    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, button_rect)
        button_text = game.font_small.render("ЗАБРАТЬ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, button_rect)
        pygame.draw.rect(game.screen, GOLD, button_rect, 2)
        button_text = game.font_small.render("ЗАБРАТЬ", True, WHITE)

    text_x = button_rect.x + button_rect.width // 2 - button_text.get_width() // 2
    text_y = button_rect.y + button_rect.height // 2 - button_text.get_height() // 2
    game.screen.blit(button_text, (text_x, text_y))

    game.loot_button = button_rect  # Сохраняем кнопку в объект игры