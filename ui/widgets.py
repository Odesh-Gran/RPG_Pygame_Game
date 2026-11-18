import pygame
from config import WIDTH, HEIGHT, GOLD, WHITE, BLOOD_RED, HEALTH_GREEN, HEALTH_BG, HEALTH_YELLOW, HEALTH_RED

def draw_item_tooltip(game, item_name, x, y):
    """Рисует всплывающую подсказку с информацией о предмете"""

    from entities import items as предметы
    item_data = предметы.предметы.get(item_name, {})

    info_lines = []

    info_lines.append(("=== " + item_name + " ===", GOLD))

    item_type = item_data.get("тип", "неизвестно")
    info_lines.append((f"Тип: {item_type}", WHITE))

    if item_type == "оружие":
        урон = item_data.get("урон", 0)
        тип_оружия = item_data.get("тип_оружия", "одноручное")
        требование = item_data.get("требуемый_навык", 0)

        info_lines.append((f"Урон: +{урон}", BLOOD_RED))
        info_lines.append((f"Тип оружия: {тип_оружия}", WHITE))
        if требование > 0:
            info_lines.append((f"Требует навык: {требование}", GOLD))

    elif item_type == "броня":
        защита = item_data.get("защита", 0)
        info_lines.append((f"Защита: +{защита}", HEALTH_GREEN))

    elif item_type == "еда":
        лечение = item_data.get("здоровье", 5)
        кулинария_бонус = game.игрок.get("кулинария", 0)
        итоговое_лечение = лечение + кулинария_бонус

        info_lines.append((f"Восстанавливает: {лечение} HP", HEALTH_GREEN))
        if кулинария_бонус > 0:
            info_lines.append((f"Бонус кулинарии: +{кулинария_бонус} HP", GOLD))
            info_lines.append((f"Итого: +{итоговое_лечение} HP", HEALTH_GREEN))

    elif item_type == "книга":
        навык = item_data.get("навык", "кулинария")
        повышение = item_data.get("повышение", 5)
        info_lines.append((f"Увеличивает {навык} на {повышение}", GOLD))

    elif item_type == "аксессуар" or item_type == "амулет":
        эффект = item_data.get("эффект", "неизвестный")
        if эффект == "вампиризм":
            info_lines.append((f"Эффект: Вампиризм (лечение от урона)", BLOOD_RED))
        elif эффект == "сила":
            бонус = item_data.get("сила_бонус", 3)
            info_lines.append((f"Эффект: Сила +{бонус}", BLOOD_RED))
        elif эффект == "здоровье":
            бонус = item_data.get("здоровье_бонус", 20)
            info_lines.append((f"Эффект: Здоровье +{бонус}", HEALTH_GREEN))
        else:
            info_lines.append((f"Эффект: {эффект}", GOLD))

    # Описание (если есть) - теперь используем функцию напрямую
    описание = item_data.get("описание", "")
    if описание:
        desc_lines = разбить_текст_на_строки(описание, 250, game.font_small)
        for line in desc_lines[:2]:  # максимум 2 строки описания
            info_lines.append((line, (200, 200, 200)))

    цена = item_data.get("цена", 0)
    if цена > 0:
        info_lines.append((f"Цена: {цена} монет", GOLD))

    line_height = 22
    padding = 10
    max_width = 0

    for line, _ in info_lines:
        text_surface = game.font_small.render(line, True, WHITE)
        max_width = max(max_width, text_surface.get_width())

    tooltip_width = max_width + padding * 2
    tooltip_height = len(info_lines) * line_height + padding * 2

    tooltip_x = x + 15
    tooltip_y = y - tooltip_height - 10

    if tooltip_x + tooltip_width > WIDTH:
        tooltip_x = x - tooltip_width - 15
    if tooltip_y < 0:
        tooltip_y = y + 30

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(game.screen, (0, 0, 0, 230), tooltip_rect)
    pygame.draw.rect(game.screen, GOLD, tooltip_rect, 2)

    text_y = tooltip_y + padding
    for line, color in info_lines:
        text_surface = game.font_small.render(line, True, color)
        game.screen.blit(text_surface, (tooltip_x + padding, text_y))
        text_y += line_height


def draw_health_bar(game, x, y, width, height, current, maximum):
    """Рисует полоску здоровья"""
    pygame.draw.rect(game.screen, HEALTH_BG, (x, y, width, height))

    percent = current / maximum if maximum > 0 else 0
    if percent > 0.6:
        color = HEALTH_GREEN
    elif percent > 0.3:
        color = HEALTH_YELLOW
    else:
        color = HEALTH_RED

    bar_width = int(width * percent)
    if bar_width > 0:
        pygame.draw.rect(game.screen, color, (x, y, bar_width, height))

    pygame.draw.rect(game.screen, GOLD, (x, y, width, height), 2)

    health_text = game.font_small.render(f"{current}/{maximum}", True, WHITE)
    game.screen.blit(health_text, (x + width // 2 - 30, y + 5))


def draw_mana_bar(game, x, y, width, height, current, maximum):
    """Рисует полоску маны"""
    pygame.draw.rect(game.screen, (40, 40, 60), (x, y, width, height))

    if maximum > 0:
        percent = current / maximum
        bar_width = int(width * percent)
        if bar_width > 0:
            pygame.draw.rect(game.screen, (80, 120, 255), (x, y, bar_width, height))

    pygame.draw.rect(game.screen, GOLD, (x, y, width, height), 2)

    mana_text = game.font_small.render(f"{current}/{maximum}", True, WHITE)
    game.screen.blit(mana_text, (x + width // 2 - 30, y + 5))


def show_message(game, text, duration=60):
    """Показывает сообщение на экране"""
    message_surface = game.font_medium.render(text, True, BLOOD_RED)
    message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    game.screen.blit(message_surface, message_rect)
    pygame.display.flip()
    pygame.time.wait(duration * 10)


def разбить_текст_на_строки(text, max_width, font):
    """Разбивает текст на строки, чтобы каждая помещалась в max_width"""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines