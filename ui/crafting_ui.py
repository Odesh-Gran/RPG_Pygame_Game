import pygame
from config import *
from entities import items as предметы
from systems.crafting import craft_item

def draw_craft(game):
    """Отрисовка окна верстака с категориями и прокруткой"""
    game.craft_buttons = []
    game.craft_items = []

    categories = {
        "ОРУЖИЕ": ["лезвие", "призрачный меч"],
        "БРОНЯ": ["кожаная броня", "кольчужная броня"],
        "ЕДА": ["блины", "рыба", "зелье здоровья"],
        "МАТЕРИАЛЫ": ["шестерёнка"]
    }

    if not hasattr(game, 'craft_category'):
        game.craft_category = list(categories.keys())[0]

    if not hasattr(game, 'craft_scroll'):
        game.craft_scroll = 0

    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    game.screen.blit(s, (0, 0))

    craft_rect = pygame.Rect(100, 50, 1080, 650)
    pygame.draw.rect(game.screen, DARK_BLUE, craft_rect)
    pygame.draw.rect(game.screen, GOLD, craft_rect, 3)

    title = game.font_large.render("ВЕРСТАК", True, GOLD)
    game.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

    y_res = 120
    ресурсы_текст = game.font_medium.render("ТВОИ РЕСУРСЫ:", True, GOLD)
    game.screen.blit(ресурсы_текст, (120, y_res))

    ресурсы = {}
    for предмет in game.игрок["инвентарь"]:
        if предмет in предметы.предметы and предметы.предметы[предмет]["тип"] == "ресурс":
            ресурсы[предмет] = ресурсы.get(предмет, 0) + 1

    if ресурсы:
        ресурсы_список = []
        for предмет, количество in ресурсы.items():
            ресурсы_список.append(f"{предмет} x{количество}")
        ресурсы_строка = " | ".join(ресурсы_список)

        if len(ресурсы_строка) > 80:
            ресурсы_строка = ресурсы_строка[:80] + "..."

        res_display = game.font_small.render(ресурсы_строка, True, WHITE)
        game.screen.blit(res_display, (120, y_res + 25))
    else:
        res_display = game.font_small.render("Нет ресурсов", True, GRAY)
        game.screen.blit(res_display, (120, y_res + 25))

    pygame.draw.line(game.screen, GOLD, (120, 180), (1060, 180), 2)

    # ===== КАТЕГОРИИ =====
    cat_x = 120
    cat_y = 190
    cat_spacing = 120

    game.category_buttons = []
    for i, category in enumerate(categories.keys()):
        cat_rect = pygame.Rect(cat_x + i * cat_spacing, cat_y, 110, 30)

        if category == game.craft_category:
            pygame.draw.rect(game.screen, GOLD, cat_rect)
            cat_text = game.font_small.render(category, True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, cat_rect)
            pygame.draw.rect(game.screen, GOLD, cat_rect, 2)
            cat_text = game.font_small.render(category, True, WHITE)

        game.screen.blit(cat_text, (cat_rect.x + 5, cat_rect.y + 5))
        game.category_buttons.append((category, cat_rect))

    # ===== СПИСОК РЕЦЕПТОВ =====
    name_header = game.font_small.render("РЕЦЕПТ", True, GOLD)
    resources_header = game.font_small.render("НУЖНО", True, GOLD)

    game.screen.blit(name_header, (120, 230))
    game.screen.blit(resources_header, (450, 230))

    category_recipes = []
    for recipe_name in categories[game.craft_category]:
        if recipe_name in game.craft_recipes:
            category_recipes.append((recipe_name, game.craft_recipes[recipe_name]))

    y_start = 260
    item_height = 45
    visible_items = 7

    if len(category_recipes) > visible_items:
        up_rect = pygame.Rect(1000, 230, 30, 30)
        if up_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, up_rect)
            up_text = game.font_medium.render("▲", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, up_rect)
            pygame.draw.rect(game.screen, GOLD, up_rect, 2)
            up_text = game.font_medium.render("▲", True, WHITE)
        game.screen.blit(up_text, (1005, 235))
        game.craft_buttons.append(("scroll_up", up_rect))

        down_rect = pygame.Rect(1000, 570, 30, 30)
        if down_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, down_rect)
            down_text = game.font_medium.render("▼", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, down_rect)
            pygame.draw.rect(game.screen, GOLD, down_rect, 2)
            down_text = game.font_medium.render("▼", True, WHITE)
        game.screen.blit(down_text, (1005, 575))
        game.craft_buttons.append(("scroll_down", down_rect))

    start_index = game.craft_scroll
    end_index = min(start_index + visible_items, len(category_recipes))

    y = y_start
    for i in range(start_index, end_index):
        название, рецепт = category_recipes[i]

        нужные_ресурсы = {}
        for ресурс in рецепт["ресурсы"]:
            нужные_ресурсы[ресурс] = нужные_ресурсы.get(ресурс, 0) + 1

        есть_все = True
        for ресурс, нужно in нужные_ресурсы.items():
            if ресурсы.get(ресурс, 0) < нужно:
                есть_все = False
                break

        item_rect = pygame.Rect(120, y - 3, 800, 35)
        if item_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, DARK_RED, item_rect)

        name_text = game.font_small.render(название, True, WHITE)
        game.screen.blit(name_text, (120, y))

        ресурсы_текст = []
        for ресурс, нужно in нужные_ресурсы.items():
            if нужно > 1:
                ресурсы_текст.append(f"{ресурс} x{нужно}")
            else:
                ресурсы_текст.append(ресурс)

        res_text = game.font_small.render(", ".join(ресурсы_текст), True, WHITE)
        game.screen.blit(res_text, (450, y + 2))

        indicator = "+" if есть_все else "-"
        ind_text = game.font_small.render(indicator, True, WHITE)
        game.screen.blit(ind_text, (920, y))

        if есть_все:
            btn_rect = pygame.Rect(960, y - 3, 100, 30)
            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(game.screen, GOLD, btn_rect)
                btn_text = game.font_small.render("СОЗДАТЬ", True, BLACK)
            else:
                pygame.draw.rect(game.screen, DARK_RED, btn_rect)
                pygame.draw.rect(game.screen, GOLD, btn_rect, 1)
                btn_text = game.font_small.render("СОЗДАТЬ", True, WHITE)
            game.screen.blit(btn_text, (btn_rect.x + 10, btn_rect.y + 5))
            game.craft_items.append((название, рецепт, btn_rect))

        y += item_height

    back_rect = pygame.Rect(WIDTH // 2 - 100, 620, 200, 50)
    pygame.draw.rect(game.screen, DARK_RED, back_rect)
    pygame.draw.rect(game.screen, GOLD, back_rect, 2)
    back_text = game.font_medium.render("НАЗАД", True, WHITE)
    game.screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 635))
    game.craft_buttons.append(("back", back_rect))


def handle_craft_click(game, pos):
    """Обработка кликов в верстаке"""
    for action, rect in game.craft_buttons:
        if action == "back" and rect.collidepoint(pos):
            game.режим = "игра"
            return
        elif action == "scroll_up" and rect.collidepoint(pos):
            game.craft_scroll = max(0, game.craft_scroll - 1)
            return
        elif action == "scroll_down" and rect.collidepoint(pos):
            рецепты_категории = []
            for recipe_name in game.craft_categories[game.craft_category]:
                if recipe_name in game.craft_recipes:
                    рецепты_категории.append(recipe_name)

            max_scroll = len(рецепты_категории) - 7
            game.craft_scroll = min(max_scroll, game.craft_scroll + 1)
            return

    if hasattr(game, 'category_buttons'):
        for category, rect in game.category_buttons:
            if rect.collidepoint(pos):
                game.craft_category = category
                game.craft_scroll = 0
                return

    for название, рецепт, btn_rect in game.craft_items:
        if btn_rect.collidepoint(pos):
            craft_item(game, название, рецепт)
            return