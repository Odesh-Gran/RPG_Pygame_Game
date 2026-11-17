import pygame
from config import *
from entities import locations as локации
from systems import time_system as время

def draw_status(game):
    """Отрисовка красивого статус-бара"""
    panel_x = 380
    panel_y = HEIGHT - 180
    panel_width = 450
    panel_height = 180

    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

    for i in range(panel_height):
        ratio = i / panel_height
        r = int(15 + 20 * ratio)
        g = int(15 + 15 * ratio)
        b = int(30 + 30 * ratio)
        color = (r, g, b, 220)
        pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

    pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)

    corner_size = 10
    corners = [(2, 2), (panel_width - corner_size - 2, 2), (2, panel_height - corner_size - 2),
               (panel_width - corner_size - 2, panel_height - corner_size - 2)]
    for cx, cy in corners:
        pygame.draw.rect(panel_surface, GOLD, (cx, cy, corner_size, corner_size), 2)

    game.screen.blit(panel_surface, (panel_x, panel_y))

    title = game.font_medium.render("ГЕРОЙ", True, GOLD)
    game.screen.blit(title, (panel_x + 15, panel_y + 8))

    name_text = game.font_small.render(f"{game.игрок['имя']} | {game.игрок['класс'] or 'Без класса'}", True, WHITE)
    game.screen.blit(name_text, (panel_x + 15, panel_y + 35))

    время_строка = время.показать_время()
    день = время.получить_день()

    час = время.получить_час()
    if 6 <= час < 12:
        цвет_времени = (255, 200, 100)
        иконка = ""
    elif 12 <= час < 18:
        цвет_времени = (255, 255, 200)
        иконка = ""
    elif 18 <= час < 22:
        цвет_времени = (255, 150, 50)
        иконка = ""
    else:
        цвет_времени = (100, 150, 255)
        иконка = ""

    время_текст = game.font_small.render(f"{иконка} {время_строка} | День {день}", True, цвет_времени)
    время_x = panel_x + panel_width - время_текст.get_width() - 15
    game.screen.blit(время_текст, (время_x, panel_y + 10))

    left_x = panel_x + 15
    left_width = 175

    hp_y = panel_y + 60
    hp_text = game.font_small.render("HP", True, HEALTH_GREEN)
    game.screen.blit(hp_text, (left_x, hp_y))

    hp_bar_x = left_x + 35
    hp_bar_y = hp_y + 2
    hp_bar_width = left_width - 35
    hp_bar_height = 18

    pygame.draw.rect(game.screen, (40, 40, 50), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
    pygame.draw.rect(game.screen, (60, 60, 80), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 1)

    if game.игрок['макс_здоровье'] <= 0:
        game.игрок['макс_здоровье'] = 100

    hp_percent = game.игрок['здоровье'] / game.игрок['макс_здоровье']

    if hp_percent > 0.6:
        hp_color = HEALTH_GREEN
    elif hp_percent > 0.3:
        hp_color = HEALTH_YELLOW
    else:
        hp_color = HEALTH_RED

    hp_fill = int(hp_bar_width * hp_percent)
    if hp_fill > 0:
        pygame.draw.rect(game.screen, hp_color, (hp_bar_x + 1, hp_bar_y + 1, hp_fill - 2, hp_bar_height - 2))

    hp_value = game.font_small.render(f"{game.игрок['здоровье']}/{game.игрок['макс_здоровье']}", True, WHITE)
    hp_value_x = hp_bar_x + hp_bar_width // 2 - hp_value.get_width() // 2
    game.screen.blit(hp_value, (hp_value_x, hp_bar_y + 2))

    mana_y = hp_y + hp_bar_height + 8
    mana_text = game.font_small.render("MP", True, (120, 180, 255))
    game.screen.blit(mana_text, (left_x, mana_y))

    mana_bar_x = hp_bar_x
    mana_bar_y = mana_y + 2
    mana_bar_width = hp_bar_width
    mana_bar_height = 18

    pygame.draw.rect(game.screen, (40, 40, 50), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
    pygame.draw.rect(game.screen, (60, 60, 80), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 1)

    if game.игрок.get('макс_мана', 50) > 0:
        mana_percent = game.игрок.get('мана', 0) / game.игрок.get('макс_мана', 50)
        mana_fill = int(mana_bar_width * mana_percent)
        if mana_fill > 0:
            pygame.draw.rect(game.screen, (80, 150, 255),
                             (mana_bar_x + 1, mana_bar_y + 1, mana_fill - 2, mana_bar_height - 2))

    mana_value = game.font_small.render(f"{game.игрок.get('мана', 0)}/{game.игрок.get('макс_мана', 50)}", True, WHITE)
    mana_value_x = mana_bar_x + mana_bar_width // 2 - mana_value.get_width() // 2
    game.screen.blit(mana_value, (mana_value_x, mana_bar_y + 2))

    right_x = panel_x + panel_width - 190
    right_width = 155

    hunger_y = panel_y + 60
    hunger_text = game.font_small.render("Голод", True, (200, 180, 150))
    game.screen.blit(hunger_text, (right_x - 1, hunger_y))

    hunger_bar_x = right_x + 55
    hunger_bar_y = hunger_y + 2
    hunger_bar_width = right_width - 55
    hunger_bar_height = 18

    pygame.draw.rect(game.screen, (40, 40, 50), (hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height))
    pygame.draw.rect(game.screen, (60, 60, 80), (hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height), 1)

    сытость = game.игрок.get("сытость", 100)
    hunger_fill = int(hunger_bar_width * (сытость / 100))

    if сытость > 70:
        hunger_color = HEALTH_GREEN
    elif сытость > 40:
        hunger_color = HEALTH_YELLOW
    else:
        hunger_color = HEALTH_RED

    if hunger_fill > 0:
        pygame.draw.rect(game.screen, hunger_color,
                         (hunger_bar_x + 1, hunger_bar_y + 1, hunger_fill - 2, hunger_bar_height - 2))

    hunger_value = game.font_small.render(f"{сытость}%", True, WHITE)
    hunger_value_x = hunger_bar_x + hunger_bar_width // 2 - hunger_value.get_width() // 2
    game.screen.blit(hunger_value, (hunger_value_x, hunger_bar_y + 2))

    thirst_y = hunger_y + hunger_bar_height + 8
    thirst_text = game.font_small.render("Жажда", True, (100, 200, 255))
    game.screen.blit(thirst_text, (right_x - 10, thirst_y))

    thirst_bar_x = hunger_bar_x
    thirst_bar_y = thirst_y + 2
    thirst_bar_width = hunger_bar_width
    thirst_bar_height = 18

    pygame.draw.rect(game.screen, (40, 40, 50), (thirst_bar_x, thirst_bar_y, thirst_bar_width, thirst_bar_height))
    pygame.draw.rect(game.screen, (60, 60, 80), (thirst_bar_x, thirst_bar_y, thirst_bar_width, thirst_bar_height), 1)

    жажда = game.игрок.get("жажда", 100)
    thirst_fill = int(thirst_bar_width * (жажда / 100))

    if жажда > 70:
        thirst_color = (100, 200, 255)
    elif жажда > 40:
        thirst_color = HEALTH_YELLOW
    else:
        thirst_color = HEALTH_RED

    if thirst_fill > 0:
        pygame.draw.rect(game.screen, thirst_color,
                         (thirst_bar_x + 1, thirst_bar_y + 1, thirst_fill - 2, thirst_bar_height - 2))

    thirst_value = game.font_small.render(f"{жажда}%", True, WHITE)
    thirst_value_x = thirst_bar_x + thirst_bar_width // 2 - thirst_value.get_width() // 2
    game.screen.blit(thirst_value, (thirst_value_x, thirst_bar_y + 2))

    bottom_y = max(mana_y + mana_bar_height + 8, thirst_y + thirst_bar_height + 8) + 8
    level_text = game.font_small.render(f"LVL {game.игрок['уровень']}", True, GOLD)
    game.screen.blit(level_text, (left_x, bottom_y))

    exp_bar_x = left_x + 60
    exp_bar_y = bottom_y + 2
    exp_bar_width = panel_width - 80 - 170
    exp_bar_height = 16

    pygame.draw.rect(game.screen, (40, 40, 50), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height))
    pygame.draw.rect(game.screen, (60, 60, 80), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height), 1)

    if game.игрок['опыта_до_след_уровня'] > 0:
        exp_percent = game.игрок['опыт'] / game.игрок['опыта_до_след_уровня']
        exp_fill = int(exp_bar_width * exp_percent)
        if exp_fill > 0:
            for i in range(exp_fill):
                ratio = i / exp_fill
                r = int(150 + 105 * ratio)
                g = int(50 + 165 * ratio)
                b = int(200 - 100 * ratio)
                pygame.draw.line(game.screen, (r, g, b), (exp_bar_x + 1 + i, exp_bar_y + 1),
                                 (exp_bar_x + 1 + i, exp_bar_y + exp_bar_height - 1))

    exp_value = game.font_small.render(f"{game.игрок['опыт']}/{game.игрок['опыта_до_след_уровня']}", True, WHITE)
    exp_value_x = exp_bar_x + exp_bar_width // 2 - exp_value.get_width() // 2
    game.screen.blit(exp_value, (exp_value_x, exp_bar_y + 2))

    coins_text = game.font_small.render(f"Gold: {game.игрок.get('монета', 0)}", True, GOLD)
    coins_x = panel_x + panel_width - coins_text.get_width() - 15
    game.screen.blit(coins_text, (coins_x, bottom_y))


def draw_location(game):
    """Отрисовка описания локации с фоном"""
    if game.режим == "видео_переход":
        return

    if game.текущая_локация in game.backgrounds:
        game.screen.blit(game.backgrounds[game.текущая_локация], (0, 0))
    else:
        game.screen.fill(BLACK)

    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    game.screen.blit(s, (0, 0))

    title_text = game.font_large.render(game.текущая_локация, True, GOLD)
    game.screen.blit(title_text, (5, 5))

    if game.show_description:
        локация = локации.локации[game.текущая_локация]
        lines = локация["описание"].split('\n')
        y = 40
        for line in lines:
            if line:
                desc_text = game.font_small.render(line.strip(), True, WHITE)
                game.screen.blit(desc_text, (15, y))
                y += 25

        game.description_timer += 1
        if game.description_timer >= game.description_duration:
            game.show_description = False
            game.description_timer = 0
            print("⏰ Описание скрыто")

    if game.transition_active and game.transition_alpha > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(game.transition_alpha)))
        game.screen.blit(overlay, (0, 0))


def draw_actions(game):
    """Отрисовка горизонтальной панели действий с иконками"""
    локация = локации.локации[game.текущая_локация]
    game.buttons = []

    icon_size = 64
    icon_spacing = 10
    panel_padding = 15

    icon_list = []

    if game.текущая_локация == "Зачарованный лес":
        icon_list.append(("ц", "inventory", "Инвентарь"))
        icon_list.append(("о", "skills", "Навыки"))
        icon_list.append(("с", "exit", "Выход"))
    else:
        if not локация.get("хаб", False):
            icon_list.append(("й", "search", "Обыск"))

        icon_list.append(("ц", "inventory", "Инвентарь"))
        icon_list.append(("у", "map", "Карта"))
        icon_list.append(("о", "skills", "Навыки"))

        if локация.get("хаб", False):
            icon_list.append(("о_хаб", "rest", "Отдохнуть"))
            icon_list.append(("я", "chest", "Сундук"))

        if локация.get("торговец", False):
            icon_list.append(("т", "trade", "Торговец"))
        if локация.get("верстак", False):
            icon_list.append(("в", "craft", "Верстак"))
        if game.текущая_локация == "Пруд":
            icon_list.append(("в_пруд", "examine", "Осмотреть"))

        if game.текущая_локация == "Сад":
            icon_list.append(("о_лес", "explore", "Исследовать лес"))

        if game.текущая_локация == "Темница":
            icon_list.append(("о_склеп", "explore", "Войти в склеп"))

        icon_list.append(("к", "save", "Сохранить"))
        icon_list.append(("с", "exit", "Выход"))

    panel_width = len(icon_list) * (icon_size + icon_spacing) + panel_padding
    panel_height = icon_size + panel_padding * 2

    panel_x = (WIDTH - panel_width) // 1
    panel_y = HEIGHT - panel_height - 0

    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill((26, 26, 46, 180))
    pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)
    game.screen.blit(panel_surface, (panel_x, panel_y))

    start_x = panel_x + panel_padding

    for i, (action, icon_key, tooltip) in enumerate(icon_list):
        x = start_x + i * (icon_size + icon_spacing)
        y = panel_y + panel_padding

        icon_rect = pygame.Rect(x, y, icon_size, icon_size)
        is_hover = icon_rect.collidepoint(pygame.mouse.get_pos())

        if is_hover:
            pygame.draw.rect(game.screen, GOLD, icon_rect)
            tooltip_text = game.font_small.render(tooltip, True, WHITE)
            tooltip_x = x + icon_size // 2 - tooltip_text.get_width() // 2
            tooltip_y = y - 25
            tip_bg = pygame.Surface((tooltip_text.get_width() + 10, 25), pygame.SRCALPHA)
            tip_bg.fill((0, 0, 0, 200))
            game.screen.blit(tip_bg, (tooltip_x - 5, tooltip_y - 5))
            game.screen.blit(tooltip_text, (tooltip_x, tooltip_y))
        else:
            pygame.draw.rect(game.screen, DARK_RED, icon_rect)
            pygame.draw.rect(game.screen, GOLD, icon_rect, 2)

        if icon_key in game.action_icons and game.action_icons[icon_key]:
            icon = game.action_icons[icon_key]
            icon = pygame.transform.scale(icon, (icon_size - 8, icon_size - 8))
            game.screen.blit(icon, (x + 4, y + 4))

        game.buttons.append((action, icon_rect))