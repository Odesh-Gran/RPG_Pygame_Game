import pygame
from config import *

def draw_skills_menu(game):
    """Меню навыков с вертикальными вкладками слева"""

    # Анимация появления
    if not hasattr(game, 'skills_animation_progress'):
        game.skills_animation_progress = 0

    if game.skills_animation_progress < 1:
        game.skills_animation_progress += 0.08
        if game.skills_animation_progress > 1:
            game.skills_animation_progress = 1

    # Параметры панели
    panel_width = 900
    panel_height = 600
    start_y = -panel_height
    current_y = start_y + (panel_height * game.skills_animation_progress)
    panel_y = int(current_y)

    # Сдвигаем панель вправо, чтобы освободить место для вкладок
    panel_x = WIDTH // 2 - panel_width // 2

    # Фон с затемнением
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    game.screen.blit(overlay, (0, 0))

    # Основная панель с градиентом
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    for i in range(panel_height):
        ratio = i / panel_height
        r = int(26 + 20 * ratio)
        g = int(26 + 10 * ratio)
        b = int(46 + 30 * ratio)
        color = (r, g, b)
        pygame.draw.line(game.screen, color,
                         (panel_x, panel_y + i),
                         (panel_x + panel_width, panel_y + i))

    # Золотая рамка
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    # Уголки
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

    # ===== ВЕРТИКАЛЬНЫЕ ВКЛАДКИ СЛЕВА =====
    tab_width = 120
    tab_height = 55
    tab_spacing = 5
    start_x = panel_x - tab_width - 10
    start_y = panel_y + 60

    tabs = [
        {"id": "prof", "label": "ПРОФЕССИИ", "icon": ""},
        {"id": "combat", "label": "БОЕВЫЕ", "icon": ""}
    ]

    mouse_pos = pygame.mouse.get_pos()
    game.prof_tab_rect = None
    game.combat_tab_rect = None

    # Рисуем вертикальные вкладки
    for i, tab in enumerate(tabs):
        y = start_y + i * (tab_height + tab_spacing)
        tab_rect = pygame.Rect(start_x, y, tab_width, tab_height)

        # Сохраняем ссылки для кликов
        if tab["id"] == "prof":
            game.prof_tab_rect = tab_rect
        else:
            game.combat_tab_rect = tab_rect

        # Определяем, активна ли вкладка
        is_active = (game.current_skill_tab == tab["id"])
        is_hover = tab_rect.collidepoint(mouse_pos)

        # Фон вкладки
        if is_active:
            # Активная вкладка - золотая
            pygame.draw.rect(game.screen, GOLD, tab_rect)
            # Соединительная линия с панелью
            pygame.draw.rect(game.screen, GOLD, (tab_rect.right, tab_rect.y, 5, tab_height))
            text_color = BLACK
        elif is_hover:
            # Подсветка при наведении
            pygame.draw.rect(game.screen, (60, 60, 80), tab_rect)
            pygame.draw.rect(game.screen, GOLD, tab_rect, 2)
            text_color = GOLD
        else:
            # Обычная вкладка
            pygame.draw.rect(game.screen, DARK_RED, tab_rect)
            pygame.draw.rect(game.screen, GOLD, tab_rect, 2)
            text_color = WHITE

        # Иконка
        icon_text = game.font_medium.render(tab["icon"], True, text_color)
        game.screen.blit(icon_text, (tab_rect.x + 8, tab_rect.y + 8))

        # Текст (вертикально, в две строки)
        label_lines = tab["label"].split()
        if len(label_lines) > 1:
            for j, line in enumerate(label_lines):
                label_text = game.font_small.render(line, True, text_color)
                label_x = tab_rect.x + tab_width // 2 - label_text.get_width() // 2
                label_y = tab_rect.y + 30 + j * 18
                game.screen.blit(label_text, (label_x, label_y))
        else:
            label_text = game.font_small.render(tab["label"], True, text_color)
            label_x = tab_rect.x + tab_width // 2 - label_text.get_width() // 2
            label_y = tab_rect.y + tab_height // 2 - label_text.get_height() // 2 + 5
            game.screen.blit(label_text, (label_x, label_y))

    # Заголовок (меняется от вкладки)
    if game.current_skill_tab == "prof":
        title_text = "ПРОФЕССИОНАЛЬНЫЕ НАВЫКИ"
    else:
        title_text = "БОЕВЫЕ НАВЫКИ"

    title = game.font_large.render(title_text, True, GOLD)
    title_shadow = game.font_large.render(title_text, True, (80, 60, 30))
    title_x = panel_x + panel_width // 2 - title.get_width() // 2
    game.screen.blit(title_shadow, (title_x + 3, panel_y + 23))
    game.screen.blit(title, (title_x, panel_y + 20))

    # Декоративные линии под заголовком
    line_y = panel_y + 70
    for i in range(3):
        alpha = 100 - i * 30
        line_width = panel_width - 100 - i * 20
        line_x = panel_x + 50 + i * 10
        pygame.draw.line(game.screen, (GOLD[0], GOLD[1], GOLD[2], alpha),
                         (line_x, line_y + i),
                         (line_x + line_width, line_y + i), 2)

    # Очки умений (для профессий)
    points_prof = game.игрок.get('очки_умений', 0)
    if points_prof > 0:
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        pulse_alpha = int(100 + 155 * pulse)
        prof_color = (255, 215, 0, pulse_alpha)
    else:
        prof_color = GOLD

    # Очки навыков (для боевых)
    points_combat = game.игрок.get('очки_навыков', 0)
    if points_combat > 0:
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        pulse_alpha = int(100 + 155 * pulse)
        combat_color = (255, 215, 0, pulse_alpha)
    else:
        combat_color = GOLD

    # Текст очков умений
    prof_text = game.font_medium.render(f"ОЧКИ УМЕНИЙ: {points_prof}", True, prof_color)
    prof_x = panel_x + panel_width // 2 - prof_text.get_width() // 2
    game.screen.blit(prof_text, (prof_x, panel_y + 85))

    # Текст очков навыков
    combat_text = game.font_medium.render(f"ОЧКИ НАВЫКОВ: {points_combat}", True, combat_color)
    combat_x = panel_x + panel_width // 2 - combat_text.get_width() // 2
    game.screen.blit(combat_text, (combat_x, panel_y + 115))

    # ===== БЛОК ХАРАКТЕРИСТИК - ТОЛЬКО ДЛЯ ПРОФЕССИОНАЛЬНЫХ НАВЫКОВ =====
    if game.current_skill_tab == "prof":
        stats_y = panel_y + 160
        stats_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
        stats_bg.fill((0, 0, 0, 100))
        game.screen.blit(stats_bg, (panel_x + 30, stats_y))
        pygame.draw.rect(game.screen, GOLD, (panel_x + 30, stats_y, 400, 100), 1)

        stats_title = game.font_small.render("ХАРАКТЕРИСТИКИ", True, GOLD)
        game.screen.blit(stats_title, (panel_x + 40, stats_y + 8))

        stats_list = [
            ("СИЛА", game.игрок['сила'], f"+{game.игрок['сила'] // 2} урона"),
            ("ЛОВКОСТЬ", game.игрок['ловкость'],
             f"+{game.игрок['ловкость'] // 2}% крита, +{game.игрок['ловкость'] // 4}% уклонения"),
            ("СТОЙКОСТЬ", game.игрок['стойкость'], f"+{game.игрок['стойкость'] * 10} здоровья"),
            ("ИНТЕЛЛЕКТ", game.игрок['интеллект'], f"+{game.игрок['интеллект']} магии")
        ]

        for i, (name, value, bonus) in enumerate(stats_list):
            y = stats_y + 30 + i * 18
            name_text = game.font_tiny.render(name, True, WHITE)
            game.screen.blit(name_text, (panel_x + 45, y))
            value_text = game.font_tiny.render(str(value), True, GOLD)
            game.screen.blit(value_text, (panel_x + 130, y))

            bar_width = 120
            bar_height = 4
            bar_x = panel_x + 170
            bar_y = y + 6
            pygame.draw.rect(game.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            fill_width = int(bar_width * (value / 20))
            pygame.draw.rect(game.screen, GOLD, (bar_x, bar_y, fill_width, bar_height))

            bonus_text = game.font_tiny.render(bonus, True, HEALTH_GREEN)
            game.screen.blit(bonus_text, (panel_x + 300, y))

    # ===== РАЗДЕЛИТЕЛЬ ПОСЛЕ ЗАГОЛОВКА =====
    line_y_after_header = panel_y + 155 if game.current_skill_tab == "prof" else panel_y + 140
    pygame.draw.line(game.screen, GOLD,
                     (panel_x + 30, line_y_after_header),
                     (panel_x + panel_width - 30, line_y_after_header), 2)

    # ===== СОДЕРЖИМОЕ =====
    game.skill_buttons = []

    if game.current_skill_tab == "prof":
        # ===== ПРОФЕССИОНАЛЬНЫЕ НАВЫКИ =====
        skills = [
            {"name": "КУЛИНАРИЯ", "key": "кулинария", "desc": "Увеличивает лечение от еды на +{value}",
             "color": HEALTH_GREEN},
            {"name": "АЛХИМИЯ", "key": "алхимия", "desc": "Увеличивает эффект зелий на +{value}%",
             "color": HEALTH_GREEN},
            {"name": "КУЗНЕЧНОЕ ДЕЛО", "key": "кузнечное_дело", "desc": "Позволяет улучшать оружие и броню",
             "color": GOLD}
        ]

        skills_y = panel_y + 280
        skills_bg = pygame.Surface((840, 280), pygame.SRCALPHA)
        skills_bg.fill((0, 0, 0, 80))
        game.screen.blit(skills_bg, (panel_x + 30, skills_y - 10))

        for i, skill in enumerate(skills):
            value = game.игрок.get(skill["key"], 0)
            max_value = 10

            if "кулинария" in skill["key"]:
                desc = skill["desc"].replace("{value}", str(value))
            elif "алхимия" in skill["key"]:
                desc = skill["desc"].replace("{value}", str(value * 5))
            else:
                desc = skill["desc"]

            skill_rect = pygame.Rect(panel_x + 50, skills_y + i * 90, 800, 80)

            if skill_rect.collidepoint(mouse_pos):
                hover_bg = pygame.Surface((skill_rect.width, skill_rect.height), pygame.SRCALPHA)
                hover_bg.fill((GOLD[0], GOLD[1], GOLD[2], 30))
                game.screen.blit(hover_bg, skill_rect)

            pygame.draw.rect(game.screen, (80, 80, 100), skill_rect, 1)

            # Иконка (увеличенная)
            icon_surf = game._create_skill_icon("")
            icon_surf = pygame.transform.scale(icon_surf, (48, 48))
            game.screen.blit(icon_surf, (skill_rect.x + 15, skill_rect.y + 16))

            # Название
            name_text = game.font_medium.render(skill["name"], True, skill["color"])
            game.screen.blit(name_text, (skill_rect.x + 75, skill_rect.y + 15))

            # Уровень
            level_text = game.font_small.render(f"Уровень {value}/{max_value}", True, WHITE)
            game.screen.blit(level_text, (skill_rect.x + 75, skill_rect.y + 42))

            # Полоса прогресса
            bar_width = 200
            bar_height = 8
            bar_x = skill_rect.x + 280
            bar_y = skill_rect.y + 28
            pygame.draw.rect(game.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            fill_width = int(bar_width * (value / max_value))
            pygame.draw.rect(game.screen, skill["color"], (bar_x, bar_y, fill_width, bar_height))

            # Описание
            desc_text = game.font_small.render(desc, True, GRAY)
            game.screen.blit(desc_text, (skill_rect.x + 500, skill_rect.y + 28))

            # Кнопка "+"
            if points_prof > 0 and value < max_value:
                plus_rect = pygame.Rect(skill_rect.x + skill_rect.width - 55, skill_rect.y + 22, 40, 35)

                if plus_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(game.screen, GOLD, plus_rect)
                    plus_text = game.font_large.render("+", True, BLACK)
                else:
                    pygame.draw.rect(game.screen, DARK_RED, plus_rect)
                    pygame.draw.rect(game.screen, GOLD, plus_rect, 2)
                    plus_text = game.font_large.render("+", True, WHITE)

                game.screen.blit(plus_text, (plus_rect.x + 8, plus_rect.y - 2))
                game.skill_buttons.append((skill["key"], plus_rect))

    else:
        # ===== БОЕВЫЕ НАВЫКИ ИЗ JSON - 3 ВЕТКИ =====
        if not hasattr(game, 'skills_data') or not game.skills_data:
            no_data_text = game.font_small.render("Навыки не загружены!", True, HEALTH_RED)
            game.screen.blit(no_data_text, (panel_x + panel_width // 2 - 100, panel_y + 350))
        else:
            # Получаем первые 3 ветки
            ветки = list(game.skills_data["ветки"].keys())[:3]
            колонка_ширина = panel_width // 3 - 40
            колонка_x = [panel_x + 30, panel_x + колонка_ширина + 50, panel_x + колонка_ширина * 2 + 70]

            skills_y = panel_y + 180
            skills_bg = pygame.Surface((840, 360), pygame.SRCALPHA)
            skills_bg.fill((0, 0, 0, 80))
            game.screen.blit(skills_bg, (panel_x + 30, skills_y - 10))

            # Отображаем 3 ветки
            for idx, название_ветки in enumerate(ветки):
                if idx >= 3:
                    break

                branch_title = game.font_small.render(название_ветки, True, GOLD)
                game.screen.blit(branch_title, (колонка_x[idx] + 20, skills_y - 5))

                навыки_ветки = game.skills_data["ветки"][название_ветки]["навыки"]
                y_offset = skills_y + 25

                for skill in навыки_ветки:
                    skill_id = skill["id"]
                    skill_name = skill["название"]
                    skill_type = skill["тип"]
                    skill_cost = skill.get("стоимость_маны", 0)
                    skill_desc = skill.get("описание", "")

                    if skill_type == "активный":
                        name_color = BLOOD_RED
                        type_text = f"АКТ {skill_cost} ман"
                    else:
                        name_color = HEALTH_GREEN
                        type_text = "ПАС"

                    row_rect = pygame.Rect(колонка_x[idx] + 40, y_offset, колонка_ширина - 20, 52)

                    if row_rect.collidepoint(mouse_pos):
                        hover_bg = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                        hover_bg.fill((GOLD[0], GOLD[1], GOLD[2], 30))
                        game.screen.blit(hover_bg, row_rect)

                    pygame.draw.rect(game.screen, (80, 80, 100), row_rect, 1)

                    # Иконка
                    icon_surf = game._create_skill_icon("")
                    icon_surf = pygame.transform.scale(icon_surf, (24, 24))
                    game.screen.blit(icon_surf, (колонка_x[idx] + 18, y_offset + 12))

                    # Название
                    name_text = game.font_tiny.render(skill_name, True, name_color)
                    game.screen.blit(name_text, (колонка_x[idx] + 48, y_offset + 4))

                    # Тип
                    type_surface = game.font_tiny.render(type_text, True, WHITE)
                    game.screen.blit(type_surface, (колонка_x[idx] + 48, y_offset + 20))

                    # Описание
                    if len(skill_desc) > 14:
                        skill_desc = skill_desc[:12] + "..."
                    desc_text = game.font_tiny.render(skill_desc, True, GRAY)
                    game.screen.blit(desc_text, (колонка_x[idx] + 48, y_offset + 34))

                    # Кнопка "ВЫУЧИТЬ"
                    is_learned = skill_id in game.игрок.get("выученные_навыки", [])

                    if not is_learned and points_combat > 0:
                        btn_rect = pygame.Rect(колонка_x[idx] + колонка_ширина - 50, y_offset + 16, 55, 24)

                        if btn_rect.collidepoint(mouse_pos):
                            pygame.draw.rect(game.screen, GOLD, btn_rect)
                            btn_text = game.font_tiny.render("ВЫУЧИТЬ", True, BLACK)
                        else:
                            pygame.draw.rect(game.screen, DARK_RED, btn_rect)
                            pygame.draw.rect(game.screen, GOLD, btn_rect, 1)
                            btn_text = game.font_tiny.render("ВЫУЧИТЬ", True, WHITE)

                        game.screen.blit(btn_text, (btn_rect.x + 4, btn_rect.y + 5))
                        game.skill_buttons.append((skill_id, btn_rect))
                    elif is_learned:
                        learned_text = game.font_tiny.render("ВЫУЧЕНО", True, HEALTH_GREEN)
                        game.screen.blit(learned_text, (колонка_x[idx] + колонка_ширина - 65, y_offset + 14))

                    y_offset += 56

    # Кнопка "Назад"
    back_rect = pygame.Rect(panel_x + panel_width // 2 - 80, panel_y + panel_height - 45, 160, 40)

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

    game.skill_back_button = back_rect