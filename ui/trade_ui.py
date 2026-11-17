import pygame
import random
from config import *
from systems import merchant as торговец

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