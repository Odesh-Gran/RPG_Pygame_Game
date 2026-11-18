import pygame
from config import WIDTH, HEIGHT, BLACK, DARK_BLUE, DARK_RED

def load_close_icon(game):
    """Загружает иконку закрытия"""
    try:
        game.close_icon = pygame.image.load("assets/ui/close.png").convert_alpha()
        game.close_icon = pygame.transform.scale(game.close_icon, (40, 40))
        print("✅ Иконка закрытия загружена")
    except Exception as e:
        print(f"❌ Ошибка загрузки иконки закрытия: {e}")
        game.close_icon = None

def load_action_icons(game):
    """Загружает иконки для кнопок действий"""
    icon_files = {
        "search": "assets/ui/buttons/search.png",
        "inventory": "assets/ui/buttons/inventory.png",
        "map": "assets/ui/buttons/map.png",
        "save": "assets/ui/buttons/save.png",
        "skills": "assets/ui/buttons/skills.png",
        "exit": "assets/ui/buttons/exit.png",
        "trade": "assets/ui/buttons/trade.png",
        "craft": "assets/ui/buttons/craft.png",
        "examine": "assets/ui/buttons/examine.png"
    }

    for key, path in icon_files.items():
        try:
            icon = pygame.image.load(path).convert_alpha()
            icon = pygame.transform.scale(icon, (24, 24))
            game.action_icons[key] = icon
        except Exception as e:
            print(f"❌ Ошибка загрузки {key}: {e}")
            game.action_icons[key] = None

def load_backgrounds(game):
    """Загружает фоны для всех локаций"""
    bg_files = {
        "Холл": "assets/backgrounds/hall.png",
        "Кухня": "assets/backgrounds/kitchen.png",
        "Сад": "assets/backgrounds/garden.png",
        "Пруд": "assets/backgrounds/pond.png",
        "Мастерская": "assets/backgrounds/workshop.png",
        "Лестница": "assets/backgrounds/stairs.png",
        "Библиотека": "assets/backgrounds/library.png",
        "Коридор": "assets/backgrounds/corridor.png",
        "Темница": "assets/backgrounds/dungeon.png",
        "Главный зал": "assets/backgrounds/great_hall.png",
        "Убежище": "assets/backgrounds/ubegische.png"
    }

    for локация, path in bg_files.items():
        try:
            bg = pygame.image.load(path).convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            game.backgrounds[локация] = bg
        except Exception as e:
            print(f"❌ Не удалось загрузить фон для {локация}: {e}")
            bg = pygame.Surface((WIDTH, HEIGHT))
            colors = {
                "Холл": DARK_BLUE, "Кухня": DARK_RED, "Сад": (20, 50, 20),
                "Пруд": (20, 30, 50), "Мастерская": (40, 30, 20), "Лестница": (30, 30, 30),
                "Библиотека": (40, 20, 20), "Коридор": (25, 20, 20), "Темница": (10, 10, 10),
                "Главный зал": (50, 30, 30)
            }
            bg.fill(colors.get(локация, BLACK))
            game.backgrounds[локация] = bg

def load_item_icons(game):
    """Загружает иконки для всех предметов"""
    from entities import items as предметы

    for item_name, path in предметы.ITEMS_WITH_ICONS.items():
        try:
            icon = pygame.image.load(path).convert_alpha()
            icon = pygame.transform.scale(icon, (64, 64))
            game.item_icons[item_name] = icon
        except Exception as e:
            print(f"❌ Не удалось загрузить {item_name}: {e}")
            game.item_icons[item_name] = create_placeholder_icon(item_name)

    for item_name in предметы.предметы.keys():
        if item_name not in game.item_icons:
            game.item_icons[item_name] = create_placeholder_icon(item_name)

def create_placeholder_icon(item_name):
    """Создаёт иконку-заглушку для предмета на основе его реального типа"""
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    from entities import items as предметы

    item_data = предметы.предметы.get(item_name, {})
    item_type = item_data.get("тип", "неизвестно")

    if item_type == "оружие":
        color = (200, 100, 100); symbol = "ОРУЖ"
    elif item_type == "броня":
        color = (100, 100, 200); symbol = "БРОН"
    elif item_type == "еда":
        color = (100, 200, 100); symbol = "ЕДА"
    elif item_type == "книга":
        color = (150, 100, 50); symbol = "КНИГ"
    elif item_type == "аксессуар" or item_type == "амулет":
        color = (150, 50, 150); symbol = "АМУЛ"
    elif item_type == "ценность":
        color = (200, 200, 100); symbol = "ЦЕН"
    elif item_type == "ресурс":
        color = (80, 80, 100); symbol = "РЕС"
    elif item_type == "трофей":
        color = (120, 80, 60); symbol = "ТРОФ"
    elif item_type == "ключ":
        color = (180, 150, 50); symbol = "КЛЮЧ"
    else:
        color = (150, 150, 150); symbol = "???"

    pygame.draw.rect(icon, color, (0, 0, 32, 32))
    pygame.draw.rect(icon, (200, 200, 200), (0, 0, 32, 32), 2)

    try:
        font = pygame.font.Font(None, 16)
        text = font.render(symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=(16, 16))
        icon.blit(text, text_rect)
    except:
        pass

    return icon