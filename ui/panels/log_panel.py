import pygame
from config import *
from ui.widgets import разбить_текст_на_строки

def draw_log_panel(game):
    """Отрисовка панели с логом событий с разбивкой длинного текста"""

    # Параметры панели
    panel_width = 350
    panel_height = 200
    panel_x = 0
    panel_y = 870

    # Полупрозрачный фон
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill((26, 26, 46, 180))
    pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)
    game.screen.blit(panel_surface, (panel_x, panel_y))

    # Заголовок
    title_text = game.font_medium.render("СОБЫТИЯ", True, GOLD)
    game.screen.blit(title_text, (panel_x + 10, panel_y + 5))

    # Линия разделителя
    pygame.draw.line(game.screen, GOLD, (panel_x + 10, panel_y + 30),
                     (panel_x + panel_width - 10, panel_y + 30), 1)

    # Максимальная ширина текста
    max_text_width = panel_width - 25  # 275 пикселей

    # Сначала разбиваем ВСЕ сообщения на строки
    все_строки = []
    for msg in game.log_messages:
        строки_сообщения = разбить_текст_на_строки(msg, max_text_width, game.font_small)
        все_строки.append(строки_сообщения)

    # Отображаем строки, начиная с нижней части панели
    line_height = 18
    start_y = panel_y + panel_height - line_height - 5  # от нижнего края

    # Идём снизу вверх
    текущая_y = start_y
    for строки_сообщения in reversed(все_строки):
        # Отображаем строки сообщения снизу вверх
        for строка in reversed(строки_сообщения):
            if текущая_y < panel_y + 35:  # не выше заголовка
                break
            msg_text = game.font_small.render(строка, True, WHITE)
            game.screen.blit(msg_text, (panel_x + 15, текущая_y))
            текущая_y -= line_height
        текущая_y -= 2  # небольшой отступ между сообщениями