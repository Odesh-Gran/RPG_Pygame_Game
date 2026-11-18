import pygame
from config import *
from entities import items as предметы
from ui.widgets import draw_item_tooltip

def draw_inventory(game):
    """Инвентарь с анимацией в стиле игры"""
    if not hasattr(game, 'inventory_animation_progress'):
        game.inventory_animation_progress = 0

    if game.inventory_animation_progress < 1:
        game.inventory_animation_progress += 0.08
        if game.inventory_animation_progress > 1:
            game.inventory_animation_progress = 1

    mouse_pos = pygame.mouse.get_pos()

    panel_width = 1300
    panel_height = 620
    start_y = -panel_height
    current_y = start_y + (panel_height * game.inventory_animation_progress)
    panel_y = int(current_y)
    panel_x = WIDTH // 2 - panel_width // 2

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

    title = game.font_large.render("ИНВЕНТАРЬ", True, GOLD)
    title_shadow = game.font_large.render("ИНВЕНТАРЬ", True, (80, 60, 30))
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title_shadow, (title_x + 3, panel_y + 23))
    game.screen.blit(title, (title_x, panel_y + 20))

    line_y = panel_y + 70
    for i in range(2):
        line_width = panel_width - 150 - i * 20
        line_x = panel_x + 75 + i * 10
        pygame.draw.line(game.screen, (GOLD[0], GOLD[1], GOLD[2], 100 - i * 30),
                         (line_x, line_y + i),
                         (line_x + line_width, line_y + i), 2)

    # ===== ЛЕВАЯ ПАНЕЛЬ - ЭКИПИРОВКА =====
    equip_panel_x = panel_x + 30
    equip_panel_y = panel_y + 95
    equip_panel_width = 280
    equip_panel_height = 480

    pygame.draw.rect(game.screen, (26, 26, 46), (equip_panel_x, equip_panel_y, equip_panel_width, equip_panel_height))
    pygame.draw.rect(game.screen, GOLD, (equip_panel_x, equip_panel_y, equip_panel_width, equip_panel_height), 1)

    equip_title = game.font_medium.render("ЭКИПИРОВКА", True, GOLD)
    equip_title_x = equip_panel_x + equip_panel_width // 2 - equip_title.get_width() // 2
    game.screen.blit(equip_title, (equip_title_x, equip_panel_y + 10))

    pygame.draw.line(game.screen, GOLD,
                     (equip_panel_x + 15, equip_panel_y + 40),
                     (equip_panel_x + equip_panel_width - 15, equip_panel_y + 40), 1)

    cell_size = 80
    spacing = 30
    start_x = equip_panel_x + 30
    row1_y = equip_panel_y + 55

    # Ячейка оружия
    weapon_rect = pygame.Rect(start_x, row1_y, cell_size, cell_size)
    pygame.draw.rect(game.screen, DARK_RED, weapon_rect)
    pygame.draw.rect(game.screen, GOLD, weapon_rect, 2)

    if game.игрок['оружие']:
        if game.игрок['оружие'] in game.item_icons:
            icon = game.item_icons[game.игрок['оружие']]
            icon = pygame.transform.scale(icon, (64, 64))
            icon_x = start_x + (cell_size - 64) // 2
            icon_y = row1_y + (cell_size - 64) // 2
            game.screen.blit(icon, (icon_x, icon_y))
        else:
            weapon_name = game.font_small.render(game.игрок['оружие'], True, WHITE)
            if len(game.игрок['оружие']) > 12:
                weapon_name = game.font_small.render(game.игрок['оружие'][:10] + "...", True, WHITE)
            text_x = start_x + (cell_size - weapon_name.get_width()) // 2
            text_y = row1_y + cell_size // 2 - 10
            game.screen.blit(weapon_name, (text_x, text_y))

            if game.игрок['оружие'] in предметы.предметы:
                урон = предметы.предметы[game.игрок['оружие']].get("урон", 0)
                dmg_text = game.font_tiny.render(f"+{урон}", True, BLOOD_RED)
                game.screen.blit(dmg_text, (start_x + 5, row1_y + cell_size - 20))
    else:
        empty_text = game.font_small.render("ПУСТО", True, GRAY)
        text_x = start_x + (cell_size - empty_text.get_width()) // 2
        text_y = row1_y + cell_size // 2 - 5
        game.screen.blit(empty_text, (text_x, text_y))

    weapon_label = game.font_tiny.render("ОРУЖИЕ", True, GOLD)
    game.screen.blit(weapon_label, (start_x + cell_size // 2 - weapon_label.get_width() // 2, row1_y + cell_size + 5))
    game.equip_weapon_rect = weapon_rect

    # Ячейка брони
    armor_x = start_x + cell_size + spacing
    armor_rect = pygame.Rect(armor_x, row1_y, cell_size, cell_size)
    pygame.draw.rect(game.screen, DARK_RED, armor_rect)
    pygame.draw.rect(game.screen, GOLD, armor_rect, 2)

    if game.игрок.get("броня"):
        if game.игрок["броня"] in game.item_icons:
            icon = game.item_icons[game.игрок["броня"]]
            icon = pygame.transform.scale(icon, (64, 64))
            icon_x = armor_x + (cell_size - 64) // 2
            icon_y = row1_y + (cell_size - 64) // 2
            game.screen.blit(icon, (icon_x, icon_y))
        else:
            armor_name = game.font_small.render(game.игрок["броня"], True, WHITE)
            if len(game.игрок["броня"]) > 12:
                armor_name = game.font_small.render(game.игрок["броня"][:10] + "...", True, WHITE)
            text_x = armor_x + (cell_size - armor_name.get_width()) // 2
            text_y = row1_y + cell_size // 2 - 10
            game.screen.blit(armor_name, (text_x, text_y))

            if game.игрок["броня"] in предметы.предметы:
                защита = предметы.предметы[game.игрок["броня"]].get("защита", 0)
                def_text = game.font_tiny.render(f"+{защита}", True, HEALTH_GREEN)
                game.screen.blit(def_text, (armor_x + 5, row1_y + cell_size - 20))
    else:
        empty_text = game.font_small.render("ПУСТО", True, GRAY)
        text_x = armor_x + (cell_size - empty_text.get_width()) // 2
        text_y = row1_y + cell_size // 2 - 5
        game.screen.blit(empty_text, (text_x, text_y))

    armor_label = game.font_tiny.render("БРОНЯ", True, GOLD)
    game.screen.blit(armor_label, (armor_x + cell_size // 2 - armor_label.get_width() // 2, row1_y + cell_size + 5))
    game.equip_armor_rect = armor_rect

    # ===== РЯД 2: АМУЛЕТ =====
    row2_y = row1_y + cell_size + 40
    amulet_rect = pygame.Rect(start_x, row2_y, cell_size, cell_size)
    pygame.draw.rect(game.screen, DARK_RED, amulet_rect)
    pygame.draw.rect(game.screen, GOLD, amulet_rect, 2)

    if game.игрок.get("амулет"):
        if game.игрок["амулет"] in game.item_icons:
            icon = game.item_icons[game.игрок["амулет"]]
            icon = pygame.transform.scale(icon, (64, 64))
            icon_x = start_x + (cell_size - 64) // 2
            icon_y = row2_y + (cell_size - 64) // 2
            game.screen.blit(icon, (icon_x, icon_y))
        else:
            amulet_name = game.font_small.render(game.игрок["амулет"], True, WHITE)
            if len(game.игрок["амулет"]) > 12:
                amulet_name = game.font_small.render(game.игрок["амулет"][:10] + "...", True, WHITE)
            text_x = start_x + (cell_size - amulet_name.get_width()) // 2
            text_y = row2_y + cell_size // 2 - 10
            game.screen.blit(amulet_name, (text_x, text_y))
    else:
        empty_text = game.font_small.render("ПУСТО", True, GRAY)
        text_x = start_x + (cell_size - empty_text.get_width()) // 2
        text_y = row2_y + cell_size // 2 - 5
        game.screen.blit(empty_text, (text_x, text_y))

    amulet_label = game.font_tiny.render("АМУЛЕТ", True, GOLD)
    game.screen.blit(amulet_label, (start_x + cell_size // 2 - amulet_label.get_width() // 2, row2_y + cell_size + 5))
    game.equip_amulet_rect = amulet_rect

    # ===== ХАРАКТЕРИСТИКИ С ЗДОРОВЬЕМ И МАНОЙ =====
    stats_y = row2_y + cell_size + 30
    stats_title = game.font_small.render("СОСТОЯНИЕ", True, GOLD)
    game.screen.blit(stats_title, (equip_panel_x + equip_panel_width // 2 - stats_title.get_width() // 2, stats_y))

    health_text = game.font_small.render(f"Здоровье: {game.игрок['здоровье']}/{game.игрок['макс_здоровье']}", True, HEALTH_GREEN)
    game.screen.blit(health_text, (equip_panel_x + 20, stats_y + 25))

    mana_current = game.игрок.get('мана', 0)
    mana_max = game.игрок.get('макс_мана', 50)
    mana_text = game.font_small.render(f"Мана: {mana_current}/{mana_max}", True, (120, 180, 255))
    game.screen.blit(mana_text, (equip_panel_x + 20, stats_y + 45))

    stats_title2 = game.font_small.render("ХАРАКТЕРИСТИКИ", True, GOLD)
    game.screen.blit(stats_title2, (equip_panel_x + equip_panel_width // 2 - stats_title2.get_width() // 2, stats_y + 70))

    сила = game.игрок.get('сила', 0) + game.игрок.get('сила_бонус', 0)
    стойкость = game.игрок.get('стойкость', 0)
    ловкость = game.игрок.get('ловкость', 0)
    интеллект = game.игрок.get('интеллект', 0)
    кулинария = game.игрок.get('кулинария', 0)

    stats = [
        f"Сила: {сила}",
        f"Стойкость: {стойкость}",
        f"Ловкость: {ловкость}",
        f"Интеллект: {интеллект}",
        f"Кулинария: {кулинария}"
    ]

    if game.игрок.get('сила_бонус', 0) > 0:
        stats[0] = f"Сила: {сила} (+{game.игрок['сила_бонус']})"

    for i, stat in enumerate(stats):
        stat_text = game.font_small.render(stat, True, WHITE)
        game.screen.blit(stat_text, (equip_panel_x + 20, stats_y + 95 + i * 20))

    # ===== ПРАВАЯ ПАНЕЛЬ - ИНВЕНТАРЬ =====
    inv_panel_x = equip_panel_x + equip_panel_width + 0
    inv_panel_y = equip_panel_y
    inv_panel_width = panel_width - (equip_panel_x + equip_panel_width + 20) - 30
    inv_panel_height = equip_panel_height

    pygame.draw.rect(game.screen, (26, 26, 46), (inv_panel_x, inv_panel_y, inv_panel_width, inv_panel_height))
    pygame.draw.rect(game.screen, GOLD, (inv_panel_x, inv_panel_y, inv_panel_width, inv_panel_height), 1)

    inv_title = game.font_medium.render("ИНВЕНТАРЬ", True, GOLD)
    inv_title_x = inv_panel_x + inv_panel_width // 2 - inv_title.get_width() // 2
    game.screen.blit(inv_title, (inv_title_x, inv_panel_y + 10))

    pygame.draw.line(game.screen, GOLD,
                     (inv_panel_x + 15, inv_panel_y + 40),
                     (inv_panel_x + inv_panel_width - 15, inv_panel_y + 40), 1)

    # ===== ЯЧЕЙКИ ИНВЕНТАРЯ =====
    cell_size_inv = 70
    cols = (inv_panel_width - 50) // (cell_size_inv + 10)
    rows = 5
    spacing_inv = 10

    start_x_inv = inv_panel_x + 25
    start_y_inv = inv_panel_y + 55

    предметы_игрока = game.игрок["инвентарь"]
    подсчёт = {}
    for предмет in предметы_игрока:
        подсчёт[предмет] = подсчёт.get(предмет, 0) + 1

    уникальные_предметы = sorted(list(подсчёт.keys()))
    game.inventory_items = []

    icon_size_inv = 48

    for row in range(rows):
        for col in range(cols):
            x = start_x_inv + col * (cell_size_inv + spacing_inv)
            y = start_y_inv + row * (cell_size_inv + spacing_inv)

            cell_rect = pygame.Rect(x, y, cell_size_inv, cell_size_inv)

            pygame.draw.rect(game.screen, DARK_RED, cell_rect)
            pygame.draw.rect(game.screen, GOLD, cell_rect, 2)

            index = row * cols + col
            if index < len(уникальные_предметы):
                предмет = уникальные_предметы[index]
                количество = подсчёт[предмет]

                if предмет in game.item_icons:
                    icon = game.item_icons[предмет]
                    icon = pygame.transform.scale(icon, (icon_size_inv, icon_size_inv))
                    icon_x = x + (cell_size_inv - icon_size_inv) // 2
                    icon_y = y + (cell_size_inv - icon_size_inv) // 2 - 5
                    game.screen.blit(icon, (icon_x, icon_y))
                else:
                    короткое_название = предмет[:8] + ".." if len(предмет) > 8 else предмет
                    item_text = game.font_tiny.render(короткое_название, True, WHITE)
                    text_x = x + (cell_size_inv - item_text.get_width()) // 2
                    text_y = y + cell_size_inv // 2 - 5
                    game.screen.blit(item_text, (text_x, text_y))

                if количество > 1:
                    count_text = game.font_tiny.render(f"x{количество}", True, GOLD)
                    count_x = x + cell_size_inv - count_text.get_width() - 3
                    count_y = y + cell_size_inv - count_text.get_height() - 2
                    game.screen.blit(count_text, (count_x, count_y))

                данные = предметы.предметы.get(предмет, {})
                if данные.get("тип") == "еда":
                    belt_btn = pygame.Rect(x + cell_size_inv - 50, y + cell_size_inv - 28, 24, 24)
                    if belt_btn.collidepoint(mouse_pos):
                        pygame.draw.rect(game.screen, GOLD, belt_btn)
                        btn_text = game.font_tiny.render("П", True, BLACK)
                    else:
                        pygame.draw.rect(game.screen, DARK_RED, belt_btn)
                        pygame.draw.rect(game.screen, GOLD, belt_btn, 1)
                        btn_text = game.font_tiny.render("П", True, WHITE)
                    game.screen.blit(btn_text, (belt_btn.x + 4, belt_btn.y + 2))
                    game.inventory_items.append((belt_btn, "belt", предмет))

                game.inventory_items.append((cell_rect, предмет))

    # ===== ПАНЕЛЬ ПОЯСА (СПРАВА ОТ ИНВЕНТАРЯ, ВЕРТИКАЛЬНО) =====
    belt_panel_x = inv_panel_x + inv_panel_width
    belt_panel_y = panel_y + 95
    belt_panel_width = 85
    belt_panel_height = equip_panel_height

    pygame.draw.rect(game.screen, (26, 26, 46), (belt_panel_x, belt_panel_y, belt_panel_width, belt_panel_height))
    pygame.draw.rect(game.screen, GOLD, (belt_panel_x, belt_panel_y, belt_panel_width, belt_panel_height), 2)

    belt_title = game.font_small.render("ПОЯС", True, GOLD)
    title_x = belt_panel_x + belt_panel_width // 2 - belt_title.get_width() // 2
    game.screen.blit(belt_title, (title_x, belt_panel_y + 10))

    pygame.draw.line(game.screen, GOLD,
                     (belt_panel_x + 10, belt_panel_y + 40),
                     (belt_panel_x + belt_panel_width - 10, belt_panel_y + 40), 1)

    пояс = game.игрок.get("пояс", [])
    belt_slot_size = 60
    belt_spacing = 8
    start_y = belt_panel_y + 55
    start_x = belt_panel_x + (belt_panel_width - belt_slot_size) // 2

    for i in range(5):
        y = start_y + i * (belt_slot_size + belt_spacing)
        x = start_x

        belt_rect = pygame.Rect(x, y, belt_slot_size, belt_slot_size)

        shadow_rect = pygame.Rect(x + 2, y + 2, belt_slot_size, belt_slot_size)
        pygame.draw.rect(game.screen, (0, 0, 0, 50), shadow_rect)

        if i < len(пояс) and пояс[i] is not None:
            for j in range(belt_slot_size):
                ratio = j / belt_slot_size
                r = int(20 + 30 * ratio)
                g = int(40 + 20 * ratio)
                b = int(80 + 30 * ratio)
                color = (r, g, b)
                pygame.draw.line(game.screen, color, (x, y + j), (x + belt_slot_size, y + j))

            pygame.draw.rect(game.screen, GOLD, belt_rect, 2)

            item = пояс[i]
            if item in game.item_icons:
                icon = game.item_icons[item]
                icon = pygame.transform.scale(icon, (belt_slot_size - 12, belt_slot_size - 12))
                game.screen.blit(icon, (x + 6, y + 6))
            else:
                name = game.font_tiny.render(item[:8], True, WHITE)
                game.screen.blit(name, (x + 5, y + belt_slot_size // 2 - 5))

            num_bg = pygame.Surface((18, 18), pygame.SRCALPHA)
            num_bg.fill((0, 0, 0, 180))
            game.screen.blit(num_bg, (x + 2, y + 2))
            num = game.font_tiny.render(str(i + 1), True, GOLD)
            game.screen.blit(num, (x + 5, y + 2))

            remove_btn = pygame.Rect(x + belt_slot_size - 22, y + belt_slot_size - 22, 18, 18)
            if remove_btn.collidepoint(mouse_pos):
                pygame.draw.rect(game.screen, BLOOD_RED, remove_btn)
                btn_text = game.font_tiny.render("В", True, WHITE)
                pygame.draw.rect(game.screen, GOLD, remove_btn, 1)
            else:
                pygame.draw.rect(game.screen, (100, 0, 0, 150), remove_btn)
                pygame.draw.rect(game.screen, GOLD, remove_btn, 1)
                btn_text = game.font_tiny.render("В", True, WHITE)
            game.screen.blit(btn_text, (remove_btn.x + 3, remove_btn.y + 1))

            game.inventory_items.append((remove_btn, "belt_remove", i))

            if belt_rect.collidepoint(mouse_pos):
                tip_text = game.font_tiny.render(f"{item}", True, WHITE)
                tip_x = x + belt_slot_size // 2 - tip_text.get_width() // 2
                tip_y = y - 20
                tip_bg = pygame.Surface((tip_text.get_width() + 10, 18), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 200))
                game.screen.blit(tip_bg, (tip_x - 5, tip_y - 2))
                game.screen.blit(tip_text, (tip_x, tip_y))

        else:
            pygame.draw.rect(game.screen, (30, 30, 40), belt_rect)
            pygame.draw.rect(game.screen, (80, 80, 90), belt_rect, 2)

            num_bg = pygame.Surface((18, 18), pygame.SRCALPHA)
            num_bg.fill((0, 0, 0, 150))
            game.screen.blit(num_bg, (x + 2, y + 2))
            num = game.font_tiny.render(str(i + 1), True, (60, 60, 70))
            game.screen.blit(num, (x + 5, y + 2))

            empty = game.font_tiny.render("пусто", True, (60, 60, 70))
            game.screen.blit(empty, (x + belt_slot_size // 2 - empty.get_width() // 2, y + belt_slot_size // 2 - 5))

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

    text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
    text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
    game.screen.blit(back_text, (text_x, text_y))

    game.inventory_back = back_rect

    hovered_item = None
    hover_pos = None

    if weapon_rect.collidepoint(mouse_pos) and game.игрок['оружие']:
        hovered_item = game.игрок['оружие']
        hover_pos = (weapon_rect.centerx + 20, weapon_rect.centery)
    elif armor_rect.collidepoint(mouse_pos) and game.игрок.get("броня"):
        hovered_item = game.игрок["броня"]
        hover_pos = (armor_rect.centerx + 20, armor_rect.centery)
    elif amulet_rect.collidepoint(mouse_pos) and game.игрок.get("амулет"):
        hovered_item = game.игрок["амулет"]
        hover_pos = (amulet_rect.centerx + 20, amulet_rect.centery)
    else:
        for item in game.inventory_items:
            if len(item) == 2:
                cell_rect, item_name = item
                if cell_rect.collidepoint(mouse_pos):
                    hovered_item = item_name
                    hover_pos = (cell_rect.centerx + 20, cell_rect.centery)
                    break

    if hovered_item and hover_pos:
        # Вызываем метод из Game, так как тултип тоже там
        draw_item_tooltip(game, hovered_item, hover_pos[0], hover_pos[1])


def handle_inventory_click(game, pos):
    if hasattr(game, 'inventory_back') and game.inventory_back.collidepoint(pos):
        if hasattr(game, 'previous_mode') and game.previous_mode == "эксплорейшн":
            game.режим = "эксплорейшн"
            game.previous_mode = None
        else:
            game.режим = "игра"
        return

    if hasattr(game, 'equip_weapon_rect') and game.equip_weapon_rect.collidepoint(pos):
        if game.игрок['оружие']:
            оружие = game.игрок['оружие']
            game.игрок["инвентарь"].append(оружие)
            game.игрок['оружие'] = None
            game.add_to_log(f"Снято {оружие}")
        return

    if hasattr(game, 'equip_armor_rect') and game.equip_armor_rect.collidepoint(pos):
        if game.игрок.get("броня"):
            броня = game.игрок["броня"]
            данные = предметы.предметы.get(броня, {})

            if "сила" in данные:
                game.игрок["сила"] -= данные["сила"]
            if "ловкость" in данные:
                game.игрок["ловкость"] -= данные["ловкость"]
            if "стойкость" in данные:
                game.игрок["стойкость"] -= данные["стойкость"]
            if "интеллект" in данные:
                game.игрок["интеллект"] -= данные["интеллект"]
            if "кулинария" in данные:
                game.игрок["кулинария"] -= данные["кулинария"]
            if "алхимия" in данные:
                game.игрок["алхимия"] -= данные["алхимия"]
            if "кузнечное_дело" in данные:
                game.игрок["кузнечное_дело"] -= данные["кузнечное_дело"]
            if "защита" in данные:
                game.игрок["защита_бонус"] = 0

            game.игрок["инвентарь"].append(броня)
            game.игрок["броня"] = None
            game.inventory.update_max_health()
            game.add_to_log(f"Снята {броня}")
            print(f"✅ Снята {броня}")
        return

    if hasattr(game, 'equip_amulet_rect') and game.equip_amulet_rect.collidepoint(pos):
        if game.игрок.get("амулет"):
            амулет = game.игрок["амулет"]
            game.inventory.add_item(амулет)
            game.игрок["амулет"] = None
            game.add_to_log(f"Снят {амулет}")
            game.inventory.update_amulet_effect()
        return

    if hasattr(game, 'inventory_items'):
        for item in game.inventory_items:
            if len(item) == 3:
                rect, action, data = item
                if rect.collidepoint(pos):
                    if action == "belt":
                        успех = game.add_to_belt(data)
                        if успех:
                            game.inventory.remove_item(data)
                            game.add_to_log(f"{data} помещён на пояс")
                            draw_inventory(game) # перерисовываем
                        else:
                            game.add_to_log("Пояс полон!")
                        return
                    elif action == "belt_remove":
                        slot_index = data
                        пояс = game.игрок.get("пояс", [])
                        if slot_index < len(пояс) and пояс[slot_index] is not None:
                            зелье = пояс[slot_index]
                            пояс[slot_index] = None
                            game.inventory.add_item(зелье)
                            game.add_to_log(f"{зелье} снят с пояса")
                            draw_inventory(game) # перерисовываем
                        return
            else:
                rect, предмет = item
                if rect.collidepoint(pos):
                    успех, сообщение = game.inventory.use_item(предмет)
                    if успех:
                        game.add_to_log(сообщение)
                    else:
                        game.add_to_log(f"{сообщение}")
                    return