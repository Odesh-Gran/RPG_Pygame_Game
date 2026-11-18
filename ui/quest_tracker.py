import pygame
from config import *
from ui.widgets import разбить_текст_на_строки

def draw_quest_tracker(game):
    """Отображает активные квесты на экране"""
    if not game.показывать_квесты:
        return

    if game.режим == "бой":
        return

    активные_квесты = game.игрок.get("активные_квесты", [])
    if not активные_квесты:
        return

    # ===== ПАРАМЕТРЫ =====
    panel_width = 320
    panel_height = 30 + len(активные_квесты) * 75
    panel_x = game.квесты_позиция_x
    panel_y = game.квесты_позиция_y

    if panel_height > 400:
        panel_height = 400

    # ===== ФОН =====
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

    for i in range(panel_height):
        ratio = i / panel_height
        r = int(10 + 15 * ratio)
        g = int(10 + 10 * ratio)
        b = int(20 + 20 * ratio)
        color = (r, g, b, 200)
        pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

    pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 1)
    game.screen.blit(panel_surface, (panel_x, panel_y))

    # ===== ЗАГОЛОВОК =====
    title = game.font_medium.render("КВЕСТЫ", True, GOLD)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 6))

    # Разделитель
    pygame.draw.line(game.screen, GOLD,
                     (panel_x + 10, panel_y + 28),
                     (panel_x + panel_width - 10, panel_y + 28), 1)

    # ===== КВЕСТЫ =====
    y = panel_y + 34
    max_quests = min(len(активные_квесты), 5)

    for i, квест_id in enumerate(активные_квесты[:max_quests]):
        квест = game.quest_system.получить_квест(квест_id)
        if not квест:
            continue

        name = квест.get("название", "???")
        name_text = game.font_small.render(name, True, (255, 215, 0))
        game.screen.blit(name_text, (panel_x + 12, y))
        y += 18

        description = квест.get("описание", "")
        # ВНИМАНИЕ: game._разбить_текст_на_строки должен существовать в Game
        desc_lines = разбить_текст_на_строки(description, panel_width - 30, game.font_small)
        desc_lines = desc_lines[:2]

        for line in desc_lines:
            desc_text = game.font_small.render(line, True, (180, 180, 180))
            game.screen.blit(desc_text, (panel_x + 14, y))
            y += 16

        прогресс_строки = game.quest_system.получить_прогресс_строку(квест_id, game.игрок)
        if прогресс_строки:
            prog_text = game.font_small.render(прогресс_строки[0][:35], True, (200, 200, 200))
            game.screen.blit(prog_text, (panel_x + 14, y))
            y += 16
        else:
            status_text = game.font_small.render("В процессе...", True, (150, 150, 150))
            game.screen.blit(status_text, (panel_x + 14, y))
            y += 16

        if i < len(активные_квесты[:max_quests]) - 1:
            pygame.draw.line(game.screen, (80, 80, 100),
                             (panel_x + 12, y),
                             (panel_x + panel_width - 12, y), 1)
            y += 6

    if len(активные_квесты) > 5:
        more_text = game.font_small.render(f"... и ещё {len(активные_квесты) - 5}", True, GRAY)
        game.screen.blit(more_text, (panel_x + 12, y + 4))


def draw_daily_quest_tracker(game):
    """Отображает ежедневные квесты на экране"""
    if not hasattr(game, 'quest_system'):
        return

    if not hasattr(game.quest_system, 'ежедневные_квесты'):
        return

    if "ежедневные_квесты" not in game.игрок:
        game.игрок["ежедневные_квесты"] = []
        game.игрок["ежедневные_квесты_прогресс"] = {}
        game.игрок["ежедневные_квесты_дата"] = ""

    if not game.игрок["ежедневные_квесты"]:
        game.quest_system.загрузить_ежедневные_квесты(game.игрок)

    активные = game.игрок.get("ежедневные_квесты", [])

    активные_незавершенные = []
    for квест_ид in активные:
        if not game.quest_system.проверить_ежедневный_квест(квест_ид, game.игрок):
            for квест in game.quest_system.ежедневные_квесты:
                if квест.get("id") == квест_ид:
                    активные_незавершенные.append(квест)
                    break

    if not активные_незавершенные:
        return

    panel_width = 280
    panel_height = 30 + len(активные_незавершенные) * 80
    panel_x = WIDTH - panel_width - 20
    panel_y = 200

    if panel_height > 380:
        panel_height = 380

    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

    for i in range(panel_height):
        ratio = i / panel_height
        r = int(10 + 15 * ratio)
        g = int(30 + 20 * ratio)
        b = int(10 + 10 * ratio)
        color = (r, g, b, 200)
        pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

    pygame.draw.rect(panel_surface, HEALTH_GREEN, panel_surface.get_rect(), 2)

    corner_size = 8
    corners = [(2, 2), (panel_width - corner_size - 2, 2),
               (2, panel_height - corner_size - 2), (panel_width - corner_size - 2, panel_height - corner_size - 2)]
    for cx, cy in corners:
        pygame.draw.rect(panel_surface, HEALTH_GREEN, (cx, cy, corner_size, corner_size), 2)

    game.screen.blit(panel_surface, (panel_x, panel_y))

    title = game.font_medium.render("ЕЖЕДНЕВНЫЕ", True, HEALTH_GREEN)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 6))

    pygame.draw.line(game.screen, HEALTH_GREEN,
                     (panel_x + 10, panel_y + 30),
                     (panel_x + panel_width - 10, panel_y + 30), 1)

    y = panel_y + 36
    max_quests = min(len(активные_незавершенные), 4)

    for i in range(max_quests):
        квест = активные_незавершенные[i]
        квест_ид = квест.get("id")

        if not квест_ид:
            continue

        name = квест.get("название", "???")
        name_text = game.font_small.render(name, True, HEALTH_GREEN)
        game.screen.blit(name_text, (panel_x + 12, y))
        y += 18

        прогресс = game.игрок.get("ежедневные_квесты_прогресс", {}).get(квест_ид, {})
        текущее = прогресс.get("текущее", 0)
        цель = квест.get("цели", {}).get("количество", 1)

        тип = квест.get("тип", "убить")
        if тип == "убить":
            прог_текст = f"Убито: {текущее}/{цель}"
        elif тип == "найти":
            прог_текст = f"Найдено: {текущее}/{цель}"
        elif тип == "посетить":
            прог_текст = f"Посещено: {текущее}/{цель}"
        elif тип == "крафт":
            прог_текст = f"Создано: {текущее}/{цель}"
        elif тип == "монеты":
            прог_текст = f"Монет: {текущее}/{цель}"
        else:
            прог_текст = f"Прогресс: {текущее}/{цель}"

        prog_text = game.font_small.render(прог_текст, True, (200, 200, 200))
        game.screen.blit(prog_text, (panel_x + 14, y))
        y += 16

        bar_width = panel_width - 30
        bar_height = 6
        bar_x = panel_x + 14
        bar_y = y

        pygame.draw.rect(game.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        if цель > 0:
            fill_width = int(bar_width * (текущее / цель))
            fill_width = min(fill_width, bar_width)
            if fill_width > 0:
                for j in range(fill_width):
                    ratio = j / bar_width
                    r = int(200 + 55 * ratio)
                    g = int(200 - 55 * ratio)
                    color = (r, g, 0)
                    pygame.draw.line(game.screen, color,
                                     (bar_x + j, bar_y + 1),
                                     (bar_x + j, bar_y + bar_height - 1))

        pygame.draw.rect(game.screen, HEALTH_GREEN, (bar_x, bar_y, bar_width, bar_height), 1)
        y += 14

        награда = квест.get("награда", {})
        награда_текст = []
        if награда.get("опыт"):
            награда_текст.append(f"+{награда['опыт']} опыта")
        if награда.get("монеты"):
            награда_текст.append(f"{награда['монеты']} монет")

        if награда_текст:
            reward_text = game.font_tiny.render(" " + " ".join(награда_текст), True, GOLD)
            game.screen.blit(reward_text, (panel_x + 14, y))
            y += 16

        if i < max_quests - 1:
            pygame.draw.line(game.screen, (40, 60, 40),
                             (panel_x + 12, y),
                             (panel_x + panel_width - 12, y), 1)
            y += 4

    if len(активные_незавершенные) > 4:
        more_text = game.font_tiny.render(f"... и ещё {len(активные_незавершенные) - 4}", True, GRAY)
        game.screen.blit(more_text, (panel_x + 12, y + 4))