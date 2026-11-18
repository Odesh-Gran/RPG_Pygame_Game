import pygame
from config import *
from entities import items as предметы
from ui.widgets import draw_health_bar, draw_mana_bar
from ui.widgets import разбить_текст_на_строки
from loaders.skill_loader import SkillLoader

def draw_battle(game):
    """Экран боя в стиле настольной игры"""
    try:
        table_bg = pygame.image.load("assets/backgrounds/battle_table.png").convert()
        table_bg = pygame.transform.scale(table_bg, (WIDTH, HEIGHT))
        game.screen.blit(table_bg, (0, 0))
    except Exception as e:
        print(f"❌ Не удалось загрузить фон стола: {e}")
        TABLE_COLOR = (70, 50, 35)
        LINE_COLOR = (90, 70, 55)
        game.screen.fill(TABLE_COLOR)
        for x in range(0, WIDTH, 50):
            pygame.draw.line(game.screen, LINE_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(game.screen, LINE_COLOR, (0, y), (WIDTH, y), 1)

    _draw_player_card(game)
    _draw_enemy_card(game)
    _draw_battle_log(game)
    _draw_action_panel(game)
    _draw_belt_panel(game)
    draw_skill_buttons(game) # Оставляем в Game, если там логика


def _draw_player_card(game):
    card_width = 350
    card_height = 460
    card_x = 80
    card_y = 80

    _draw_card_background(game, card_x, card_y, card_width, card_height)
    _draw_card_title(game, card_x, card_y, card_width, "ТЫ")

    sprite_x = card_x + card_width // 2 - game.player_size // 2
    sprite_y = card_y + 80
    _draw_player_sprite(game, sprite_x, sprite_y)

    health_bar_y = sprite_y + game.player_size + 20
    draw_health_bar(
        game,
        card_x + 30, health_bar_y, card_width - 60, 22,
        game.игрок['здоровье'], game.игрок['макс_здоровье']
    )

    mana_bar_y = health_bar_y + 32
    draw_mana_bar(
        game,
        card_x + 30, mana_bar_y, card_width - 60, 22,
        game.игрок.get('мана', 0), game.игрок.get('макс_мана', 50)
    )

    _draw_player_equipment(game, card_x, mana_bar_y + 28)


def _draw_enemy_card(game):
    card_width = 350
    card_height = 450
    card_x = WIDTH - card_width - 80
    card_y = HEIGHT - card_height - 80

    _draw_card_background(game, card_x, card_y, card_width, card_height)

    enemy_name = game.current_enemy.replace('_', ' ').upper()
    _draw_card_title(game, card_x, card_y, card_width, enemy_name)

    sprite_x = card_x + card_width // 2 - game.enemy_size // 2
    sprite_y = card_y + 80
    _draw_enemy_sprite(game, sprite_x, sprite_y)

    health_bar_y = sprite_y + game.enemy_size + 20
    draw_health_bar(
        game,
        card_x + 30, health_bar_y, card_width - 60, 25,
        game.enemy_health, game.enemy_data["здоровье"]
    )

    stats_y = health_bar_y + 40
    _draw_enemy_stats(game, card_x, stats_y)
    _draw_enemy_description(game, card_x, card_y, card_height, stats_y + 120)


def _draw_card_background(game, x, y, width, height):
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(game.screen, DARK_BLUE, card_rect)
    pygame.draw.rect(game.screen, GOLD, card_rect, 4)
    pygame.draw.rect(game.screen, GOLD, (x + 10, y + 10, width - 20, height - 20), 2)


def _draw_card_title(game, x, y, width, title_text):
    title = game.font_medium.render(title_text, True, GOLD)
    title_x = x + width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, y + 20))
    pygame.draw.line(game.screen, GOLD, (x + 30, y + 55), (x + width - 30, y + 55), 2)


def _draw_player_sprite(game, x, y):
    if game.player_sprite:
        game.screen.blit(game.player_sprite, (x, y))
    else:
        pygame.draw.rect(game.screen, DARK_BLUE, (x, y, game.player_size, game.player_size))
        pygame.draw.rect(game.screen, GOLD, (x, y, game.player_size, game.player_size), 2)


def _draw_enemy_sprite(game, x, y):
    if game.enemy_sprite:
        game.screen.blit(game.enemy_sprite, (x, y))
    else:
        pygame.draw.rect(game.screen, DARK_RED, (x, y, game.enemy_size, game.enemy_size))
        pygame.draw.rect(game.screen, GOLD, (x, y, game.enemy_size, game.enemy_size), 2)


def _draw_player_equipment(game, card_x, health_bar_y):
    if game.игрок['оружие']:
        weapon_text = game.font_small.render(f"{game.игрок['оружие']}", True, BLOOD_RED)
        game.screen.blit(weapon_text, (card_x + 20, health_bar_y + 35))

    if game.игрок.get("броня") and isinstance(game.игрок["броня"], str):
        armor_data = предметы.предметы.get(game.игрок["броня"], {})
        armor_def = armor_data.get("защита", 0)
        armor_text = game.font_small.render(f"{game.игрок['броня']} (+{armor_def})", True, HEALTH_GREEN)
        game.screen.blit(armor_text, (card_x + 20, health_bar_y + 55))


def _draw_enemy_stats(game, card_x, stats_y):
    if "сила" in game.enemy_data:
        power_text = game.font_small.render(f"СИЛА: {game.enemy_data['сила']}", True, BLOOD_RED)
        game.screen.blit(power_text, (card_x + 20, stats_y))

    if "награда" in game.enemy_data:
        награда = game.enemy_data["награда"]
        if isinstance(награда, (list, tuple)):
            reward_item = награда[0] if len(награда) > 0 else "ничего"
            reward_exp = награда[1] if len(награда) > 1 else 0
            reward_text = game.font_small.render(f"НАГРАДА: {reward_item} (+{reward_exp} опыта)", True, GOLD)
            game.screen.blit(reward_text, (card_x + 20, stats_y + 25))
            if len(награда) > 2:
                extra_items = ", ".join(str(x) for x in награда[2:])
                extra_text = game.font_tiny.render(f"ДОП.: {extra_items}", True, HEALTH_YELLOW)
                game.screen.blit(extra_text, (card_x + 20, stats_y + 45))
        else:
            reward_text = game.font_small.render(f"НАГРАДА: {награда}", True, GOLD)
            game.screen.blit(reward_text, (card_x + 20, stats_y + 25))

    редкий_дроп = game.enemy_data.get("редкий_дроп", [])
    шанс_редкого = game.enemy_data.get("шанс_редкого_дропа", 0)
    if шанс_редкого == 0 and "особенности" in game.enemy_data:
        шанс_редкого = game.enemy_data["особенности"].get("шанс_редкого_дропа", 0)

    if редкий_дроп:
        редкие_предметы = ", ".join(редкий_дроп)
        if шанс_редкого > 0:
            редкий_текст = game.font_tiny.render(f"РЕДКИЙ ДРОП: {редкие_предметы} ({шанс_редкого}%)", True, BLOOD_RED)
        else:
            редкий_текст = game.font_tiny.render(f"РЕДКИЙ ДРОП: {редкие_предметы}", True, BLOOD_RED)

        y_offset = stats_y + 68 if (
                    "награда" in game.enemy_data and isinstance(game.enemy_data["награда"], (list, tuple)) and len(
                game.enemy_data["награда"]) > 2) else stats_y + 48
        game.screen.blit(редкий_текст, (card_x + 20, y_offset))


def _draw_enemy_description(game, card_x, card_y, card_height, desc_start_y):
    enemy_description = game.enemy_data.get("описание", "Таинственное создание, полное тёмной энергии.")
    desc_lines = разбить_текст_на_строки(enemy_description, 290, game.font_small)[:4]

    if not desc_lines:
        return

    max_desc_y = card_y + card_height - 40
    if desc_start_y + len(desc_lines) * 18 > max_desc_y:
        max_lines = (max_desc_y - desc_start_y) // 18
        desc_lines = desc_lines[:max_lines]

    if not desc_lines:
        return

    desc_bg_height = len(desc_lines) * 18 + 10
    desc_bg_rect = pygame.Rect(card_x + 20, desc_start_y - 5, 310, desc_bg_height)
    pygame.draw.rect(game.screen, (0, 0, 0, 150), desc_bg_rect)
    pygame.draw.rect(game.screen, GOLD, desc_bg_rect, 1)

    for i, line in enumerate(desc_lines):
        desc_text = game.font_small.render(line, True, (220, 220, 200))
        text_x = card_x + 175 - desc_text.get_width() // 2
        game.screen.blit(desc_text, (text_x, desc_start_y + i * 18))


def _draw_battle_log(game):
    log_width = 250
    log_height = 150
    log_x = WIDTH // 2 - log_width // 2
    log_y = HEIGHT - 300

    log_surface = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
    log_surface.fill((0, 0, 0, 180))
    pygame.draw.rect(log_surface, GOLD, log_surface.get_rect(), 2)
    game.screen.blit(log_surface, (log_x, log_y))

    current_round = game.battle.round_number if hasattr(game.battle, 'round_number') else 0
    title_text = f"ХОД БОЯ (Раунд {current_round})"
    log_title = game.font_small.render(title_text, True, GOLD)
    title_x = log_x + log_width // 2 - log_title.get_width() // 2
    game.screen.blit(log_title, (title_x, log_y + 5))

    pygame.draw.line(game.screen, GOLD, (log_x + 10, log_y + 25), (log_x + log_width - 10, log_y + 25), 1)

    text_start_y = log_y + 32
    max_lines = 8
    messages = game.battle_log[-max_lines:] if game.battle_log else []

    for i, msg in enumerate(messages):
        if "РАУНД" in msg:
            color = GOLD
        elif "=" * 5 in msg:
            color = (100, 100, 100)
        elif "КРИТИЧЕСКИЙ" in msg:
            color = (255, 215, 0)
        elif "урон" in msg.lower() or "Получено" in msg:
            color = BLOOD_RED
        elif "Вампиризм" in msg:
            color = HEALTH_GREEN
        elif "КОНТРАТАКА" in msg:
            color = (255, 150, 50)
        elif "Нападает" in msg:
            color = GOLD
        else:
            color = WHITE

        log_text = game.font_small.render(msg, True, color)
        text_x = log_x + log_width // 2 - log_text.get_width() // 2
        game.screen.blit(log_text, (text_x, text_start_y + i * 18))


def _draw_belt_panel(game):
    пояс = game.игрок.get("пояс", [])
    slot_size = 64
    spacing = 10
    panel_width = 5 * (slot_size + spacing) + spacing + 20
    panel_height = slot_size + 60

    panel_x = WIDTH - panel_width - 1450
    panel_y = HEIGHT - 230

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill((20, 20, 40, 200))
    pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)

    corner_size = 10
    corners = [(2, 2), (panel_width - corner_size - 2, 2), (2, panel_height - corner_size - 2),
               (panel_width - corner_size - 2, panel_height - corner_size - 2)]
    for cx, cy in corners:
        pygame.draw.rect(panel_surface, GOLD, (cx, cy, corner_size, corner_size), 2)

    game.screen.blit(panel_surface, (panel_x, panel_y))

    title = game.font_medium.render("ПОЯС", True, GOLD)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 6))

    pygame.draw.line(game.screen, (100, 100, 120), (panel_x + 20, panel_y + 38),
                     (panel_x + panel_width - 20, panel_y + 38), 1)
    pygame.draw.line(game.screen, GOLD, (panel_x + 15, panel_y + 35), (panel_x + panel_width - 15, panel_y + 35), 1)

    game.belt_slots = []
    mouse_pos = pygame.mouse.get_pos()

    for i in range(5):
        x = panel_x + 15 + i * (slot_size + spacing)
        y = panel_y + 45
        slot_rect = pygame.Rect(x, y, slot_size, slot_size)

        pygame.draw.rect(game.screen, (0, 0, 0, 80), pygame.Rect(x + 2, y + 2, slot_size, slot_size))

        if i < len(пояс) and пояс[i] is not None:
            for j in range(slot_size):
                ratio = j / slot_size
                r = int(20 + 35 * ratio)
                g = int(40 + 25 * ratio)
                b = int(80 + 35 * ratio)
                color = (r, g, b)
                pygame.draw.line(game.screen, color, (x, y + j), (x + slot_size, y + j))

            pygame.draw.rect(game.screen, GOLD, slot_rect, 2)

            if slot_rect.collidepoint(mouse_pos):
                glow_rect = pygame.Rect(x - 3, y - 3, slot_size + 6, slot_size + 6)
                pygame.draw.rect(game.screen, (255, 215, 0, 50), glow_rect, 2)

            item = пояс[i]
            if item in game.item_icons:
                icon = game.item_icons[item]
                icon = pygame.transform.scale(icon, (slot_size - 12, slot_size - 12))
                game.screen.blit(icon, (x + 6, y + 6))
            else:
                name = game.font_tiny.render(item[:8], True, WHITE)
                game.screen.blit(name, (x + 5, y + slot_size // 2 - 5))

            num_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
            num_bg.fill((0, 0, 0, 180))
            game.screen.blit(num_bg, (x + 2, y + 2))
            pygame.draw.rect(game.screen, GOLD, (x + 2, y + 2, 20, 20), 1)
            num = game.font_tiny.render(str(i + 1), True, GOLD)
            game.screen.blit(num, (x + 6, y + 3))

            if slot_rect.collidepoint(mouse_pos):
                pygame.draw.rect(game.screen, (255, 215, 0, 80), slot_rect, 3)
                tip_text = game.font_small.render(f"{item}", True, WHITE)
                tip_x = x + slot_size // 2 - tip_text.get_width() // 2
                tip_y = y - 28
                tip_bg = pygame.Surface((tip_text.get_width() + 16, 24), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 220))
                pygame.draw.rect(tip_bg, GOLD, tip_bg.get_rect(), 1)
                game.screen.blit(tip_bg, (tip_x - 8, tip_y - 2))
                game.screen.blit(tip_text, (tip_x, tip_y))

                use_btn = pygame.Rect(x + slot_size - 30, y + slot_size - 26, 26, 22)
                pygame.draw.rect(game.screen, HEALTH_GREEN, use_btn)
                pygame.draw.rect(game.screen, GOLD, use_btn, 1)
                use_text = game.font_tiny.render("ИСП", True, BLACK)
                game.screen.blit(use_text, (use_btn.x + 3, use_btn.y + 3))
                game.belt_slots.append((i, use_btn))

            game.belt_slots.append((i, slot_rect))

        else:
            pygame.draw.rect(game.screen, (30, 30, 45), slot_rect)
            pygame.draw.rect(game.screen, (60, 60, 80), slot_rect, 2)

            num_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
            num_bg.fill((0, 0, 0, 150))
            game.screen.blit(num_bg, (x + 2, y + 2))
            num = game.font_tiny.render(str(i + 1), True, (60, 60, 80))
            game.screen.blit(num, (x + 6, y + 3))

            empty_icon = game.font_tiny.render("∅", True, (40, 40, 60))
            game.screen.blit(empty_icon, (x + slot_size // 2 - 8, y + slot_size // 2 - 10))

            if slot_rect.collidepoint(mouse_pos):
                tip_text = game.font_tiny.render("Пустой слот", True, GRAY)
                tip_x = x + slot_size // 2 - tip_text.get_width() // 2
                tip_y = y - 20
                tip_bg = pygame.Surface((tip_text.get_width() + 10, 18), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 200))
                game.screen.blit(tip_bg, (tip_x - 5, tip_y - 2))
                game.screen.blit(tip_text, (tip_x, tip_y))


def _draw_action_panel(game):
    panel_width = 400
    panel_height = 80
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT - 160

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    game.battle_buttons = []
    mouse_pos = pygame.mouse.get_pos()

    # ===== Кнопка АТАКА =====
    attack_rect = pygame.Rect(panel_x + 50, panel_y + 15, 120, 50)
    if attack_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, attack_rect)
        attack_text = game.font_medium.render("АТАКА", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, attack_rect)
        pygame.draw.rect(game.screen, GOLD, attack_rect, 2)
        attack_text = game.font_medium.render("АТАКА", True, WHITE)

    text_x = attack_rect.x + attack_rect.width // 2 - attack_text.get_width() // 2
    text_y = attack_rect.y + attack_rect.height // 2 - attack_text.get_height() // 2
    game.screen.blit(attack_text, (text_x, text_y))
    game.battle_buttons.append(("attack", attack_rect))

    # ===== Кнопка ПОБЕГ =====
    flee_rect = pygame.Rect(panel_x + panel_width - 170, panel_y + 15, 120, 50)
    if flee_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, flee_rect)
        flee_text = game.font_medium.render("ПОБЕГ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, flee_rect)
        pygame.draw.rect(game.screen, GOLD, flee_rect, 2)
        flee_text = game.font_medium.render("ПОБЕГ", True, WHITE)

    text_x = flee_rect.x + flee_rect.width // 2 - flee_text.get_width() // 2
    text_y = flee_rect.y + flee_rect.height // 2 - flee_text.get_height() // 2
    game.screen.blit(flee_text, (text_x, text_y))
    game.battle_buttons.append(("flee", flee_rect))

def draw_skill_buttons(game):
    """Рисует панель активных навыков в бою"""
    # Получаем выученные активные навыки
    активные_навыки = []
    for skill_id in game.игрок.get("выученные_навыки", []):
        skill = SkillLoader.get_skill_by_id(game.skills_data, skill_id)
        if skill and skill.get("тип") == "активный":
            активные_навыки.append(skill)

    if not активные_навыки:
        return

    # Параметры панели
    slot_size = 64
    spacing = 10
    max_slots = 4
    panel_width = max_slots * (slot_size + spacing) + spacing + 20
    panel_height = slot_size + 60

    # Позиция - слева внизу
    panel_x = 30
    panel_y = HEIGHT - 500

    # Фон панели
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill((20, 20, 40, 200))
    pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)

    corner_size = 10
    corners = [(2, 2), (panel_width - corner_size - 2, 2), (2, panel_height - corner_size - 2),
               (panel_width - corner_size - 2, panel_height - corner_size - 2)]
    for cx, cy in corners:
        pygame.draw.rect(panel_surface, GOLD, (cx, cy, corner_size, corner_size), 2)

    game.screen.blit(panel_surface, (panel_x, panel_y))

    # Заголовок
    title = game.font_medium.render("⚔️ НАВЫКИ", True, GOLD)
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title, (title_x, panel_y + 6))

    pygame.draw.line(game.screen, (100, 100, 120), (panel_x + 20, panel_y + 38),
                     (panel_x + panel_width - 20, panel_y + 38), 1)

    game.battle_skill_buttons = []
    mouse_pos = pygame.mouse.get_pos()

    for i, skill in enumerate(активные_навыки[:max_slots]):
        x = panel_x + 15 + i * (slot_size + spacing)
        y = panel_y + 45

        slot_rect = pygame.Rect(x, y, slot_size, slot_size)
        shadow_rect = pygame.Rect(x + 2, y + 2, slot_size, slot_size)
        pygame.draw.rect(game.screen, (0, 0, 0, 80), shadow_rect)

        стоимость_маны = skill.get("стоимость_маны", 0)
        маны_хватает = game.игрок.get("мана", 0) >= стоимость_маны

        if маны_хватает:
            for j in range(slot_size):
                ratio = j / slot_size
                r = int(20 + 35 * ratio)
                g = int(40 + 25 * ratio)
                b = int(80 + 35 * ratio)
                color = (r, g, b)
                pygame.draw.line(game.screen, color, (x, y + j), (x + slot_size, y + j))
            pygame.draw.rect(game.screen, GOLD, slot_rect, 2)
        else:
            for j in range(slot_size):
                ratio = j / slot_size
                r = int(40 + 20 * ratio)
                g = int(40 + 20 * ratio)
                b = int(50 + 20 * ratio)
                color = (r, g, b)
                pygame.draw.line(game.screen, color, (x, y + j), (x + slot_size, y + j))
            pygame.draw.rect(game.screen, (80, 80, 80), slot_rect, 2)

        if slot_rect.collidepoint(mouse_pos) and маны_хватает:
            glow_rect = pygame.Rect(x - 3, y - 3, slot_size + 6, slot_size + 6)
            pygame.draw.rect(game.screen, (255, 215, 0, 50), glow_rect, 2)

        # ===== ЗАГРУЖАЕМ SVG ИКОНКУ =====
        skill_type = skill.get("эффект", "damage")
        icon_path = f"assets/skills/{skill_type}.svg"

        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            icon = pygame.transform.scale(icon, (slot_size - 12, slot_size - 12))
        except:
            icon = _create_skill_icon_1(skill_type)

        game.screen.blit(icon, (x + 6, y + 6))

        # Номер
        num_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
        num_bg.fill((0, 0, 0, 180))
        game.screen.blit(num_bg, (x + 2, y + 2))
        pygame.draw.rect(game.screen, GOLD, (x + 2, y + 2, 20, 20), 1)
        num = game.font_tiny.render(str(i + 1), True, GOLD if маны_хватает else GRAY)
        game.screen.blit(num, (x + 6, y + 3))

        # Стоимость маны
        if стоимость_маны > 0:
            mana_text = game.font_tiny.render(f"MP:{стоимость_маны}", True, (100, 200, 255) if маны_хватает else GRAY)
            mana_x = x + slot_size // 2 - mana_text.get_width() // 2
            game.screen.blit(mana_text, (mana_x, y + slot_size - 16))

        # Подсказка
        if slot_rect.collidepoint(mouse_pos):
            tip_text = game.font_small.render(skill["название"], True, WHITE)
            tip_x = x + slot_size // 2 - tip_text.get_width() // 2
            tip_y = y - 28
            tip_bg = pygame.Surface((tip_text.get_width() + 16, 24), pygame.SRCALPHA)
            tip_bg.fill((0, 0, 0, 220))
            pygame.draw.rect(tip_bg, GOLD, tip_bg.get_rect(), 1)
            game.screen.blit(tip_bg, (tip_x - 8, tip_y - 2))
            game.screen.blit(tip_text, (tip_x, tip_y))

            if маны_хватает:
                use_btn = pygame.Rect(x + slot_size - 30, y + slot_size - 26, 26, 22)
                pygame.draw.rect(game.screen, HEALTH_GREEN, use_btn)
                pygame.draw.rect(game.screen, GOLD, use_btn, 1)
                use_text = game.font_tiny.render("ИСП", True, BLACK)
                game.screen.blit(use_text, (use_btn.x + 3, use_btn.y + 3))

        game.battle_skill_buttons.append((skill["id"], slot_rect))


def _create_skill_icon_1(skill_type):
    """Создаёт заглушку для иконки навыка"""
    icon = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(icon, (30, 30, 50), (20, 20), 18)
    pygame.draw.circle(icon, GOLD, (20, 20), 18, 1)

    colors = {
        "damage": (255, 80, 80),
        "shield": (80, 80, 255),
        "lifesteal": (255, 50, 150),
        "stun": (255, 200, 50),
        "weaken": (50, 200, 255),
        "bleed": (200, 50, 50),
        "rage": (255, 100, 0)
    }
    color = colors.get(skill_type, (150, 150, 150))

    pygame.draw.circle(icon, color, (20, 20), 12)
    pygame.draw.circle(icon, (255, 255, 255), (20, 20), 12, 1)

    return icon