import pygame
from config import WIDTH, HEIGHT, DARK_BLUE, GOLD, DARK_RED, BLACK, WHITE, GRAY, HEALTH_YELLOW

def draw_quests(game):
    """Отображает окно квестов"""

    # Анимация появления
    if not hasattr(game, 'quest_animation_progress'):
        game.quest_animation_progress = 0

    if game.quest_animation_progress < 1:
        game.quest_animation_progress += 0.08
        if game.quest_animation_progress > 1:
            game.quest_animation_progress = 1

    # Параметры панели
    panel_width = 600
    panel_height = 500
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2

    # Затемнение
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    game.screen.blit(overlay, (0, 0))

    # Фон панели
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    # Заголовок
    title = game.font_large.render("КВЕСТЫ", True, GOLD)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 20))

    # Информация
    активные = len(game.игрок.get("активные_квесты", []))
    завершенные = len(game.игрок.get("завершенные_квесты", []))
    info_text = game.font_small.render(f"Активных: {активные}  |  Завершено: {завершенные}", True, WHITE)
    game.screen.blit(info_text, (panel_x + panel_width // 2 - info_text.get_width() // 2, panel_y + 60))

    # Разделитель
    pygame.draw.line(game.screen, GOLD,
                     (panel_x + 20, panel_y + 90),
                     (panel_x + panel_width - 20, panel_y + 90), 2)

    # Активные квесты
    y = panel_y + 105
    активные_квесты = game.игрок.get("активные_квесты", [])

    if активные_квесты:
        for квест_id in активные_квесты:
            квест = game.quest_system.получить_квест(квест_id)
            if not квест:
                continue

            # Название
            name_text = game.font_medium.render(f"📜 {квест['название']}", True, GOLD)
            game.screen.blit(name_text, (panel_x + 20, y))
            y += 25

            # Описание
            desc_text = game.font_small.render(квест['описание'], True, WHITE)
            game.screen.blit(desc_text, (panel_x + 30, y))
            y += 22

            # Прогресс
            прогресс_строки = game.quest_system.получить_прогресс_строку(квест_id)
            for строка in прогресс_строки:
                prog_text = game.font_tiny.render(f"  • {строка}", True, HEALTH_YELLOW)
                game.screen.blit(prog_text, (panel_x + 30, y))
                y += 18

            y += 10
    else:
        empty_text = game.font_medium.render("Нет активных квестов", True, GRAY)
        game.screen.blit(empty_text, (panel_x + panel_width // 2 - empty_text.get_width() // 2, panel_y + 200))

    # Кнопка "Назад"
    back_rect = pygame.Rect(panel_x + panel_width // 2 - 80, panel_y + panel_height - 50, 160, 40)
    mouse_pos = pygame.mouse.get_pos()

    if back_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, back_rect)
        back_text = game.font_medium.render("НАЗАД", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, back_rect)
        pygame.draw.rect(game.screen, GOLD, back_rect, 2)
        back_text = game.font_medium.render("НАЗАД", True, WHITE)

    back_text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
    back_text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
    game.screen.blit(back_text, (back_text_x, back_text_y))

    game.quest_back = back_rect  # Сохраняем кнопку в объект игры