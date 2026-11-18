import pygame
import random
from config import *
from systems import merchant as торговец
from entities import items as предметы
from ui.widgets import разбить_текст_на_строки

def draw_quest_trade_menu(game):
    """Рисует меню выбора: Квесты или Торговля"""
    if not hasattr(game, 'quest_trade_animation_progress'):
        game.quest_trade_animation_progress = 0

    if game.quest_trade_animation_progress < 1:
        game.quest_trade_animation_progress += 0.08
        if game.quest_trade_animation_progress > 1:
            game.quest_trade_animation_progress = 1

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    game.screen.blit(overlay, (0, 0))

    panel_width = 500
    panel_height = 350
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    title = game.font_large.render("СТРАННИК", True, GOLD)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 25))

    greeting = game.font_small.render('"Чем могу помочь?"', True, (200, 200, 180))
    greeting_x = panel_x + panel_width // 2 - greeting.get_width() // 2
    game.screen.blit(greeting, (greeting_x, panel_y + 75))

    pygame.draw.line(game.screen, GOLD,
                     (panel_x + 30, panel_y + 110),
                     (panel_x + panel_width - 30, panel_y + 110), 2)

    mouse_pos = pygame.mouse.get_pos()

    # Кнопка "КВЕСТЫ"
    quest_rect = pygame.Rect(panel_x + 60, panel_y + 135, 380, 60)
    if quest_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, quest_rect)
        quest_text = game.font_medium.render("📜 КВЕСТЫ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, quest_rect)
        pygame.draw.rect(game.screen, GOLD, quest_rect, 2)
        quest_text = game.font_medium.render("📜 КВЕСТЫ", True, WHITE)

    quest_text_x = quest_rect.x + quest_rect.width // 2 - quest_text.get_width() // 2
    quest_text_y = quest_rect.y + quest_rect.height // 2 - quest_text.get_height() // 2
    game.screen.blit(quest_text, (quest_text_x, quest_text_y))
    game.quest_trade_buttons = [("quests", quest_rect)]

    # Кнопка "ТОРГОВЛЯ"
    trade_rect = pygame.Rect(panel_x + 60, panel_y + 215, 380, 60)
    if trade_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, trade_rect)
        trade_text = game.font_medium.render("💰 ТОРГОВЛЯ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, trade_rect)
        pygame.draw.rect(game.screen, GOLD, trade_rect, 2)
        trade_text = game.font_medium.render("💰 ТОРГОВЛЯ", True, WHITE)

    trade_text_x = trade_rect.x + trade_rect.width // 2 - trade_text.get_width() // 2
    trade_text_y = trade_rect.y + trade_rect.height // 2 - trade_text.get_height() // 2
    game.screen.blit(trade_text, (trade_text_x, trade_text_y))
    game.quest_trade_buttons.append(("trade", trade_rect))

    # Кнопка "НАЗАД"
    back_rect = pygame.Rect(panel_x + panel_width // 2 - 70, panel_y + panel_height - 50, 140, 35)
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
    game.quest_trade_buttons.append(("back", back_rect))

    game.quest_trade_back = back_rect


def handle_trade_click(game, pos):
    """Обработка кликов в окне торговца"""
    if not hasattr(game, 'trade_buttons'):
        return

    if not hasattr(game, 'trade_scroll'):
        game.trade_scroll = 0

    for action, *data in game.trade_buttons:
        if action == "back" and data[0].collidepoint(pos):
            game.режим = "игра"
            if hasattr(game, 'trade_buttons'):
                delattr(game, 'trade_buttons')
            if hasattr(game, 'trade_scroll'):
                delattr(game, 'trade_scroll')
            return

        elif action == "buy_mode" and data[0].collidepoint(pos):
            game.trade_mode = "buy"
            game.trade_scroll = 0
            return

        elif action == "sell_mode" and data[0].collidepoint(pos):
            game.trade_mode = "sell"
            game.trade_scroll = 0
            return

        elif action == "ask_tip" and data[0].collidepoint(pos):
            торговец_данные = торговец.торговцы.get(game.trade_location, {})
            советы = торговец_данные.get("советы", [])
            if советы:
                if len(советы) > 1:
                    новый_совет = random.choice(советы)
                    if hasattr(game, 'current_tip') and game.current_tip == новый_совет:
                        другие_советы = [с for с in советы if с != game.current_tip]
                        if другие_советы:
                            новый_совет = random.choice(другие_советы)
                    game.current_tip = новый_совет
                else:
                    game.current_tip = советы[0]
                game.add_to_log(f" {game.trader_name} дал новый совет")
            return

    if hasattr(game, 'trade_items'):
        for item_data in game.trade_items:
            if item_data[0] == "buy_1":
                action, предмет, rect = item_data
                if rect.collidepoint(pos):
                    game.trade_buy_item(предмет, 1)
                    return

            elif item_data[0] == "buy_5":
                action, предмет, rect = item_data
                if rect.collidepoint(pos):
                    game.trade_buy_item(предмет, 5)
                    return

            elif item_data[0] == "sell_1":
                action, предмет, rect, цена = item_data
                if rect.collidepoint(pos):
                    game.trade_sell_item(предмет, 1, цена)
                    return

            elif item_data[0] == "sell_all":
                action, предмет, rect, цена, количество = item_data
                if rect.collidepoint(pos):
                    game.trade_sell_item(предмет, количество, цена)
                    return
def draw_trade(game):
    """Отрисовка окна торговца с анимацией"""
    if not hasattr(game, 'trade_animation_progress'):
        game.trade_animation_progress = 0

    if game.trade_animation_progress < 1:
        game.trade_animation_progress += 0.08
        if game.trade_animation_progress > 1:
            game.trade_animation_progress = 1

    panel_width = 900
    panel_height = 620
    start_x = -panel_width
    current_x = start_x + (panel_width * game.trade_animation_progress)
    panel_x = int(current_x)
    panel_y = 50

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 10))
    game.screen.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    for i in range(panel_height):
        ratio = i / panel_height
        r = int(26 + 15 * ratio)
        g = int(26 + 10 * ratio)
        b = int(46 + 20 * ratio)
        color = (r, g, b)
        pygame.draw.line(game.screen, color,
                         (panel_x, panel_y + i),
                         (panel_x + panel_width, panel_y + i))

    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    corner_size = 20
    corners = [
        (panel_x, panel_y),
        (panel_x + panel_width - corner_size, panel_y),
        (panel_x, panel_y + panel_height - corner_size),
        (panel_x + panel_width - corner_size, panel_y + panel_height - corner_size)
    ]
    for cx, cy in corners:
        pygame.draw.rect(game.screen, GOLD, (cx, cy, corner_size, corner_size), 2)
        pygame.draw.line(game.screen, GOLD, (cx + 5, cy + 5), (cx + corner_size - 5, cy + corner_size - 5), 1)
        pygame.draw.line(game.screen, GOLD, (cx + corner_size - 5, cy + 5), (cx + 5, cy + corner_size - 5), 1)

    title = game.font_large.render(game.trader_name, True, GOLD)
    title_shadow = game.font_large.render(game.trader_name, True, (80, 60, 30))
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title_shadow, (title_x + 3, panel_y + 23))
    game.screen.blit(title, (title_x, panel_y + 20))

    greeting = game.font_small.render(f"\"{game.trader_greeting}\"", True, (200, 200, 180))
    greeting_x = panel_x + panel_width // 2 - greeting.get_width() // 2
    game.screen.blit(greeting, (greeting_x, panel_y + 70))

    line_y = panel_y + 105
    for i in range(2):
        line_width = panel_width - 150 - i * 20
        line_x = panel_x + 75 + i * 10
        pygame.draw.line(game.screen, (GOLD[0], GOLD[1], GOLD[2], 100 - i * 30),
                         (line_x, line_y + i),
                         (line_x + line_width, line_y + i), 2)

    coins_text = game.font_medium.render(f"Монеты: {game.игрок.get('монета', 0)}", True, GOLD)
    game.screen.blit(coins_text, (panel_x + 30, panel_y + 125))

    game.trade_buttons = []

    buy_rect = pygame.Rect(panel_x + panel_width - 280, panel_y + 120, 120, 40)
    sell_rect = pygame.Rect(panel_x + panel_width - 150, panel_y + 120, 120, 40)

    mouse_pos = pygame.mouse.get_pos()

    # Кнопка "КУПИТЬ"
    if buy_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, buy_rect)
        buy_text = game.font_medium.render("КУПИТЬ", True, BLACK)
        glow_rect = pygame.Rect(buy_rect.x - 3, buy_rect.y - 3, buy_rect.width + 6, buy_rect.height + 6)
        pygame.draw.rect(game.screen, (255, 215, 0, 100), glow_rect, 2)
    else:
        if game.trade_mode == "buy":
            pygame.draw.rect(game.screen, GOLD, buy_rect)
            buy_text = game.font_medium.render("КУПИТЬ", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, buy_rect)
            pygame.draw.rect(game.screen, GOLD, buy_rect, 2)
            buy_text = game.font_medium.render("КУПИТЬ", True, WHITE)

    text_x = buy_rect.x + buy_rect.width // 2 - buy_text.get_width() // 2
    text_y = buy_rect.y + buy_rect.height // 2 - buy_text.get_height() // 2
    game.screen.blit(buy_text, (text_x, text_y))

    # Кнопка "ПРОДАТЬ"
    if sell_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, sell_rect)
        sell_text = game.font_medium.render("ПРОДАТЬ", True, BLACK)
        glow_rect = pygame.Rect(sell_rect.x - 3, sell_rect.y - 3, sell_rect.width + 6, sell_rect.height + 6)
        pygame.draw.rect(game.screen, (255, 215, 0, 100), glow_rect, 2)
    else:
        if game.trade_mode == "sell":
            pygame.draw.rect(game.screen, GOLD, sell_rect)
            sell_text = game.font_medium.render("ПРОДАТЬ", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, sell_rect)
            pygame.draw.rect(game.screen, GOLD, sell_rect, 2)
            sell_text = game.font_medium.render("ПРОДАТЬ", True, WHITE)

    text_x = sell_rect.x + sell_rect.width // 2 - sell_text.get_width() // 2
    text_y = sell_rect.y + sell_rect.height // 2 - sell_text.get_height() // 2
    game.screen.blit(sell_text, (text_x, text_y))

    game.trade_buttons.append(("buy_mode", buy_rect))
    game.trade_buttons.append(("sell_mode", sell_rect))

    # ===== ПАНЕЛЬ СОВЕТОВ =====
    _draw_trade_tips(game, panel_x, panel_y, panel_width, panel_height)

    headers = ["ПРЕДМЕТ", "ХАРАКТЕРИСТИКИ", "ЦЕНА", "ДЕЙСТВИЕ"]
    header_x = [panel_x + 80, panel_x + 280, panel_x + 550, panel_x + 700]

    for i, header in enumerate(headers):
        header_text = game.font_small.render(header, True, GOLD)
        game.screen.blit(header_text, (header_x[i], panel_y + 175))

    pygame.draw.line(game.screen, GOLD,
                     (panel_x + 50, panel_y + 205),
                     (panel_x + panel_width - 50, panel_y + 205), 2)

    if game.trade_mode == "buy":
        _draw_trade_buy(game, panel_x, panel_y, panel_width, panel_height)
    else:
        _draw_trade_sell(game, panel_x, panel_y, panel_width, panel_height)

    back_rect = pygame.Rect(panel_x + panel_width // 2 - 80, panel_y + panel_height - 60, 160, 40)

    if back_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, back_rect)
        back_text = game.font_medium.render("НАЗАД", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, back_rect)
        pygame.draw.rect(game.screen, GOLD, back_rect, 2)
        back_text = game.font_medium.render("НАЗАД", True, WHITE)

    text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
    text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
    game.screen.blit(back_text, (text_x, text_y))

    game.trade_buttons.append(("back", back_rect))


def _draw_trade_buy(game, panel_x, panel_y, panel_width, panel_height):
    """Отрисовка режима покупки"""
    товары_список = sorted(game.trade_goods.items(), key=lambda x: x[0])

    if not hasattr(game, 'trade_scroll'):
        game.trade_scroll = 0

    visible_items = 6
    item_height = 55
    start_y = panel_y + 220
    max_scroll = max(0, len(товары_список) - visible_items)

    if len(товары_список) > visible_items:
        up_rect = pygame.Rect(panel_x + panel_width - 60, start_y, 40, 30)
        if up_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, up_rect)
            up_text = game.font_medium.render("▲", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, up_rect)
            pygame.draw.rect(game.screen, GOLD, up_rect, 1)
            up_text = game.font_medium.render("▲", True, WHITE)
        game.screen.blit(up_text, (up_rect.x + 12, up_rect.y + 3))
        game.trade_buttons.append(("scroll_up", up_rect))

        down_rect = pygame.Rect(panel_x + panel_width - 60, start_y + visible_items * item_height, 40, 30)
        if down_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, down_rect)
            down_text = game.font_medium.render("▼", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, down_rect)
            pygame.draw.rect(game.screen, GOLD, down_rect, 1)
            down_text = game.font_medium.render("▼", True, WHITE)
        game.screen.blit(down_text, (down_rect.x + 12, down_rect.y + 3))
        game.trade_buttons.append(("scroll_down", down_rect))

    game.trade_items = []
    start_index = game.trade_scroll
    end_index = min(start_index + visible_items, len(товары_список))

    for i in range(start_index, end_index):
        предмет, данные = товары_список[i]
        y = start_y + (i - start_index) * item_height

        row_rect = pygame.Rect(panel_x + 50, y, panel_width - 100, item_height - 2)
        if row_rect.collidepoint(pygame.mouse.get_pos()):
            hover_bg = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            hover_bg.fill((GOLD[0], GOLD[1], GOLD[2], 30))
            game.screen.blit(hover_bg, row_rect)

        if предмет in game.item_icons:
            icon = game.item_icons[предмет]
            icon = pygame.transform.scale(icon, (40, 40))
            game.screen.blit(icon, (panel_x + 60, y + 5))
            name_x = panel_x + 110
        else:
            name_x = panel_x + 70

        name_text = game.font_small.render(предмет, True, WHITE)
        game.screen.blit(name_text, (name_x, y + 15))

        item_data = предметы.предметы.get(предмет, {})
        item_type = item_data.get("тип", "")

        if item_type == "оружие":
            stats = f"Урон: +{item_data.get('урон', 0)}"
        elif item_type == "броня":
            stats = f"Защита: +{item_data.get('защита', 0)}"
        elif item_type == "еда":
            stats = f"Восст.: {item_data.get('здоровье', 0)} HP"
        else:
            stats = item_type.capitalize()

        stats_text = game.font_tiny.render(stats, True, (180, 180, 160))
        game.screen.blit(stats_text, (name_x, y + 35))

        price_text = game.font_small.render(f"{данные['цена']}", True, GOLD)
        game.screen.blit(price_text, (panel_x + 560, y + 18))

        btn1_rect = pygame.Rect(panel_x + 700, y + 10, 45, 30)
        btn5_rect = pygame.Rect(panel_x + 755, y + 10, 45, 30)

        if btn1_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, btn1_rect)
            btn1_text = game.font_small.render("x1", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, btn1_rect)
            pygame.draw.rect(game.screen, GOLD, btn1_rect, 1)
            btn1_text = game.font_small.render("x1", True, WHITE)
        game.screen.blit(btn1_text, (btn1_rect.x + 12, btn1_rect.y + 5))
        game.trade_items.append(("buy_1", предмет, btn1_rect))

        if btn5_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, btn5_rect)
            btn5_text = game.font_small.render("x5", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, btn5_rect)
            pygame.draw.rect(game.screen, GOLD, btn5_rect, 1)
            btn5_text = game.font_small.render("x5", True, WHITE)
        game.screen.blit(btn5_text, (btn5_rect.x + 12, btn5_rect.y + 5))
        game.trade_items.append(("buy_5", предмет, btn5_rect))


def _draw_trade_tips(game, panel_x, panel_y, panel_width, panel_height):
    """Рисует панель советов торговца"""
    торговец_данные = торговец.торговцы.get(game.trade_location, {})
    советы = торговец_данные.get("советы", [])

    if not советы:
        return

    if not hasattr(game, 'current_tip') or game.current_tip is None:
        game.current_tip = random.choice(советы)

    tips_width = 300
    tips_height = 100
    tips_x = panel_x + 925
    tips_y = panel_y + 510

    tips_rect = pygame.Rect(tips_x, tips_y, tips_width, tips_height)
    pygame.draw.rect(game.screen, (0, 0, 0, 200), tips_rect)
    pygame.draw.rect(game.screen, GOLD, tips_rect, 2)

    tips_title = game.font_small.render("СОВЕТ ТОРГОВЦА", True, GOLD)
    game.screen.blit(tips_title, (tips_x + 10, tips_y + 8))

    pygame.draw.line(game.screen, GOLD,
                     (tips_x + 10, tips_y + 32),
                     (tips_x + tips_width - 10, tips_y + 32), 1)

    совет = game.current_tip
    max_width = tips_width - 25

    # Передаем строку "совет", а не объект game
    строки = разбить_текст_на_строки(совет, max_width, game.font_small)
    строки = строки[:2]

    y_offset = tips_y + 38
    for i, строка in enumerate(строки):
        tip_text = game.font_small.render(f"\"{строка}\"", True, (220, 220, 200))
        game.screen.blit(tip_text, (tips_x + 10, y_offset + i * 18))

    if len(советы) > 1:
        tip_button_rect = pygame.Rect(tips_x + tips_width - 55, tips_y + tips_height - 22, 45, 18)
        if tip_button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, tip_button_rect)
            tip_button_text = game.font_tiny.render("ЕЩЁ", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, tip_button_rect)
            pygame.draw.rect(game.screen, GOLD, tip_button_rect, 1)
            tip_button_text = game.font_tiny.render("ЕЩЁ", True, WHITE)
        game.screen.blit(tip_button_text, (tip_button_rect.x + 12, tip_button_rect.y + 3))
        game.trade_buttons.append(("ask_tip", tip_button_rect))

def _draw_trade_sell(game, panel_x, panel_y, panel_width, panel_height):
    """Отрисовка режима продажи с прокруткой"""

    if not game.игрок["инвентарь"]:
        empty_text = game.font_medium.render("Инвентарь пуст", True, GRAY)
        text_x = panel_x + panel_width // 2 - empty_text.get_width() // 2
        game.screen.blit(empty_text, (text_x, panel_y + 300))
        return

    подсчёт = {}
    for предмет in game.игрок["инвентарь"]:
        подсчёт[предмет] = подсчёт.get(предмет, 0) + 1

    предметы_список = sorted(list(подсчёт.items()), key=lambda x: x[0])

    if not hasattr(game, 'trade_scroll'):
        game.trade_scroll = 0

    visible_items = 6
    item_height = 55
    start_y = panel_y + 220
    max_scroll = max(0, len(предметы_список) - visible_items)

    game.trade_items = []
    start_index = game.trade_scroll
    end_index = min(start_index + visible_items, len(предметы_список))

    for i in range(start_index, end_index):
        предмет, количество = предметы_список[i]
        y = start_y + (i - start_index) * item_height

        row_rect = pygame.Rect(panel_x + 50, y, panel_width - 100, item_height - 2)
        if row_rect.collidepoint(pygame.mouse.get_pos()):
            hover_bg = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            hover_bg.fill((GOLD[0], GOLD[1], GOLD[2], 30))
            game.screen.blit(hover_bg, row_rect)

        if предмет in game.item_icons:
            icon = game.item_icons[предмет]
            icon = pygame.transform.scale(icon, (40, 40))
            game.screen.blit(icon, (panel_x + 60, y + 5))
            name_x = panel_x + 110
        else:
            name_x = panel_x + 70

        name_text = game.font_small.render(предмет, True, WHITE)
        game.screen.blit(name_text, (name_x, y + 15))

        qty_text = game.font_small.render(f"x{количество}", True, GOLD)
        game.screen.blit(qty_text, (panel_x + 400, y + 18))

        цена_продажи = 1
        if предмет in предметы.предметы:
            цена_покупки = предметы.предметы[предмет].get("цена", 2)
            цена_продажи = max(1, цена_покупки // 2)

        price_text = game.font_small.render(f"{цена_продажи}", True, GOLD)
        game.screen.blit(price_text, (panel_x + 560, y + 18))

        btn1_rect = pygame.Rect(panel_x + 700, y + 10, 45, 30)
        btn_all_rect = pygame.Rect(panel_x + 755, y + 10, 50, 30)

        if btn1_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, btn1_rect)
            btn1_text = game.font_small.render("1", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, btn1_rect)
            pygame.draw.rect(game.screen, GOLD, btn1_rect, 1)
            btn1_text = game.font_small.render("1", True, WHITE)
        game.screen.blit(btn1_text, (btn1_rect.x + 15, btn1_rect.y + 5))
        game.trade_items.append(("sell_1", предмет, btn1_rect, цена_продажи))

        if btn_all_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, btn_all_rect)
            btn_all_text = game.font_small.render("ВСЕ", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, btn_all_rect)
            pygame.draw.rect(game.screen, GOLD, btn_all_rect, 1)
            btn_all_text = game.font_small.render("ВСЕ", True, WHITE)
        game.screen.blit(btn_all_text, (btn_all_rect.x + 10, btn_all_rect.y + 5))
        game.trade_items.append(("sell_all", предмет, btn_all_rect, цена_продажи, количество))



