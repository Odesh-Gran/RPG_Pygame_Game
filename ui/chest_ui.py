import pygame
from config import *

def draw_chest(game):
    """Отрисовка окна сундука для хранения предметов"""
    if not hasattr(game, 'chest_inventory'):
        game.chest_inventory = []

    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    game.screen.blit(s, (0, 0))

    chest_rect = pygame.Rect(150, 60, 980, 600)
    pygame.draw.rect(game.screen, DARK_BLUE, chest_rect)
    pygame.draw.rect(game.screen, GOLD, chest_rect, 3)

    title = game.font_large.render("СУНДУК", True, GOLD)
    game.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    inv_title = game.font_medium.render("ИНВЕНТАРЬ", True, GOLD)
    game.screen.blit(inv_title, (200, 130))

    chest_title = game.font_medium.render("СУНДУК", True, GOLD)
    game.screen.blit(chest_title, (700, 130))

    инвентарь_словарь = {}
    for предмет in game.игрок["инвентарь"]:
        инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

    сундук_словарь = {}
    for предмет in game.chest_inventory:
        сундук_словарь[предмет] = сундук_словарь.get(предмет, 0) + 1

    # Отображаем предметы инвентаря (слева)
    y = 170
    game.chest_inventory_items = []

    for предмет, количество in инвентарь_словарь.items():
        name_text = game.font_small.render(предмет, True, WHITE)
        game.screen.blit(name_text, (200, y))

        count_text = game.font_small.render(f"x{количество}", True, GOLD)
        game.screen.blit(count_text, (350, y))

        btn_rect = pygame.Rect(450, y - 3, 80, 25)
        if btn_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, btn_rect)
            btn_text = game.font_small.render(">", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, btn_rect)
            pygame.draw.rect(game.screen, GOLD, btn_rect, 1)
            btn_text = game.font_small.render(">", True, WHITE)
        game.screen.blit(btn_text, (btn_rect.x + 30, btn_rect.y + 3))

        game.chest_inventory_items.append(("to_chest", предмет, btn_rect))
        y += 35

    # Отображаем предметы сундука (справа)
    y = 170
    for предмет, количество in сундук_словарь.items():
        name_text = game.font_small.render(предмет, True, WHITE)
        game.screen.blit(name_text, (700, y))

        count_text = game.font_small.render(f"x{количество}", True, GOLD)
        game.screen.blit(count_text, (850, y))

        btn_rect = pygame.Rect(950, y - 3, 80, 25)
        if btn_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, btn_rect)
            btn_text = game.font_small.render("<", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, btn_rect)
            pygame.draw.rect(game.screen, GOLD, btn_rect, 1)
            btn_text = game.font_small.render("<", True, WHITE)
        game.screen.blit(btn_text, (btn_rect.x + 30, btn_rect.y + 3))

        game.chest_inventory_items.append(("to_inventory", предмет, btn_rect))
        y += 35

    back_rect = pygame.Rect(WIDTH // 2 - 100, 620, 200, 50)
    pygame.draw.rect(game.screen, DARK_RED, back_rect)
    pygame.draw.rect(game.screen, GOLD, back_rect, 2)
    back_text = game.font_medium.render("НАЗАД", True, WHITE)
    game.screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 635))
    game.chest_back = back_rect


def handle_chest_click(game, pos):
    """Обработка кликов в окне сундука"""
    if not hasattr(game, 'chest_inventory'):
        game.chest_inventory = []

    if hasattr(game, 'chest_back') and game.chest_back.collidepoint(pos):
        game.режим = "игра"
        return

    if hasattr(game, 'chest_inventory_items'):
        for action, предмет, rect in game.chest_inventory_items:
            if rect.collidepoint(pos):
                if action == "to_chest":
                    if game.inventory.has_item(предмет):
                        game.inventory.remove_item(предмет)
                        game.chest_inventory.append(предмет)
                        game.add_to_log(f"📦 {предмет} перемещён в сундук")

                elif action == "to_inventory":
                    if предмет in game.chest_inventory:
                        game.chest_inventory.remove(предмет)
                        game.inventory.add_item(предмет)
                        game.add_to_log(f"📦 {предмет} взят из сундука")

                return