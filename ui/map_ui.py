import pygame
from config import *
from entities import locations as локации
from systems import barriers as барьеры

def draw_map(game):
    """Отрисовка карты с кликабельными локациями и учётом барьеров"""
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 10))
    game.screen.blit(s, (0, 0))

    game.map_rects = {
        "Холл": pygame.Rect(390, 90, 120, 80),
        "Кухня": pygame.Rect(625, 70, 140, 65),
        "Коридор": pygame.Rect(190, 75, 60, 95),
        "Лестница": pygame.Rect(388, 223, 90, 78),
        "Сад": pygame.Rect(635, 168, 60, 130),
        "Пруд": pygame.Rect(830, 183, 94, 100),
        "Темница": pygame.Rect(62, 260, 148, 65),
        "Библиотека": pygame.Rect(355, 371, 140, 73),
        "Мастерская": pygame.Rect(653, 370, 177, 80),
        "Главный зал": pygame.Rect(43, 80, 70, 110),
        "Убежище": pygame.Rect(527, 212, 70, 80)
    }

    try:
        map_img = pygame.image.load("assets/ui/map.png").convert_alpha()
        map_img = pygame.transform.scale(map_img, (1000, 600))
        game.screen.blit(map_img, (WIDTH // 2 - 500, HEIGHT // 2 - 300))
    except Exception as e:
        print(f"❌ Ошибка загрузки карты: {e}")
        text = game.font_medium.render("Карта не найдена", True, GOLD)
        game.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    инвентарь_словарь = {}
    for предмет in game.игрок["инвентарь"]:
        инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

    game.доступные_локации = {}
    game.заблокированные_локации = {}

    for название, rect in game.map_rects.items():
        доступна, причина, подсказка = барьеры.проверить_доступность_локации(
            название, инвентарь_словарь
        )

        if доступна:
            game.доступные_локации[название] = rect
        else:
            game.заблокированные_локации[название] = {
                "rect": rect,
                "причина": причина,
                "подсказка": подсказка
            }

    map_x = WIDTH // 2 - 500
    map_y = HEIGHT // 2 - 300

    for название, данные in game.заблокированные_локации.items():
        rect = данные["rect"]
        world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)

        s_block = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s_block.fill((0, 0, 0, 150))
        game.screen.blit(s_block, (world_rect.x, world_rect.y))

        lock_text = game.font_small.render("Х", True, GOLD)
        game.screen.blit(lock_text, (world_rect.x + rect.width // 2 - 10, world_rect.y + rect.height // 2 - 10))

    if game.текущая_локация in game.map_rects:
        rect = game.map_rects[game.текущая_локация]
        highlight_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
        pygame.draw.rect(game.screen, GOLD, highlight_rect, 3)

        here_text = game.font_small.render("ТЫ", True, GOLD)
        game.screen.blit(here_text, (map_x + rect.x + 35, map_y + rect.y - 15))

    mouse_pos = pygame.mouse.get_pos()
    game.map_hover_location = None
    game.map_hover_blocked = False
    game.map_hover_reason = None

    for название, rect in game.доступные_локации.items():
        world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
        if world_rect.collidepoint(mouse_pos):
            pygame.draw.rect(game.screen, GOLD, world_rect, 2)
            game.map_hover_location = название
            game.map_hover_blocked = False

    for название, данные in game.заблокированные_локации.items():
        rect = данные["rect"]
        world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
        if world_rect.collidepoint(mouse_pos):
            pygame.draw.rect(game.screen, BLOOD_RED, world_rect, 2)
            game.map_hover_location = название
            game.map_hover_blocked = True
            game.map_hover_reason = данные["причина"]
            game.map_hover_hint = данные["подсказка"]

    if hasattr(game, 'map_hover_location') and game.map_hover_location:
        tip_x = mouse_pos[0] + 15
        tip_y = mouse_pos[1] + 15

        локация_данные = локации.локации.get(game.map_hover_location, {})
        уровень = локация_данные.get("уровень", "?")
        сложность = локация_данные.get("сложность", "")

        if сложность == "легко":
            цвет_сложности = HEALTH_GREEN
            звезды = "[1/5]"
        elif сложность == "средне":
            цвет_сложности = HEALTH_YELLOW
            звезды = "[3/5]"
        elif сложность == "сложно":
            цвет_сложности = HEALTH_RED
            звезды = "[5/5]"
        else:
            цвет_сложности = WHITE
            звезды = "[?]"

        if game.map_hover_blocked:
            tip_width = 300
            tip_height = 80
            tip_bg = pygame.Surface((tip_width, tip_height), pygame.SRCALPHA)
            tip_bg.fill((0, 0, 0, 200))
            game.screen.blit(tip_bg, (tip_x, tip_y))

            tip_text = game.font_small.render(f"[ЗАКРЫТО] {game.map_hover_location}", True, BLOOD_RED)
            game.screen.blit(tip_text, (tip_x + 10, tip_y + 5))

            reason_text = game.font_small.render(game.map_hover_reason[:40], True, WHITE)
            game.screen.blit(reason_text, (tip_x + 10, tip_y + 30))

            hint_text = game.font_small.render(f"[СОВЕТ] {game.map_hover_hint}", True, GOLD)
            game.screen.blit(hint_text, (tip_x + 10, tip_y + 55))
        else:
            tip_width = 220
            tip_height = 95
            tip_bg = pygame.Surface((tip_width, tip_height), pygame.SRCALPHA)
            tip_bg.fill((0, 0, 0, 200))
            game.screen.blit(tip_bg, (tip_x, tip_y))

            name_text = game.font_small.render(f"[ЛОКАЦИЯ] {game.map_hover_location}", True, GOLD)
            game.screen.blit(name_text, (tip_x + 10, tip_y + 5))

            level_text = game.font_small.render(f"[УРОВЕНЬ] {уровень}", True, WHITE)
            game.screen.blit(level_text, (tip_x + 10, tip_y + 30))

            сложность_текст = game.font_small.render(f"[СЛОЖНОСТЬ] {звезды}", True, цвет_сложности)
            game.screen.blit(сложность_текст, (tip_x + 10, tip_y + 55))

            if уровень != "?" and уровень > game.игрок["уровень"] + 2:
                warning = game.font_small.render("[ОПАСНО]", True, HEALTH_RED)
                game.screen.blit(warning, (tip_x + 10, tip_y + 75))
            elif уровень != "?" and уровень < game.игрок["уровень"] - 2:
                easy = game.font_small.render("[БЕЗОПАСНО]", True, HEALTH_GREEN)
                game.screen.blit(easy, (tip_x + 10, tip_y + 75))

    close_rect = pygame.Rect(WIDTH // 2 + 425, HEIGHT // 2 - 280, 40, 40)
    if game.close_icon:
        game.screen.blit(game.close_icon, (close_rect.x, close_rect.y))
    game.map_close_button = close_rect


def handle_map_click(game, pos):
    """Обработка кликов на карте с учётом барьеров"""
    if hasattr(game, 'map_close_button') and game.map_close_button.collidepoint(pos):
        if hasattr(game, 'previous_mode') and game.previous_mode == "эксплорейшн":
            game.режим = "эксплорейшн"
        else:
            game.режим = "игра"
        return

    map_x = WIDTH // 2 - 500
    map_y = HEIGHT // 2 - 300

    инвентарь_словарь = {}
    for предмет in game.игрок["инвентарь"]:
        инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

    for название, rect in game.map_rects.items():
        world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
        if world_rect.collidepoint(pos):

            print(f"\n🎯 КЛИК ПО ЛОКАЦИИ: {название}")
            print(f"📍 Текущая локация: {game.текущая_локация}")
            print(f"📦 Инвентарь: {инвентарь_словарь}")

            доступна, причина, подсказка = барьеры.проверить_доступность_локации(
                название, инвентарь_словарь
            )

            print(f"🔍 Доступна: {доступна}")
            if not доступна:
                print(f"   ❌ Причина: {причина}")
                print(f"   💡 Подсказка: {подсказка}")

            if доступна:
                if барьеры.is_barrier_open(название):
                    print(f"✅ Барьер для {название} УЖЕ ОТКРЫТ, переходим")
                    game.change_location(название)
                    return

                барьер_найден = False
                for локация_источник, барьеры_локации in барьеры.барьеры.items():
                    for барьер_ключ, барьер in барьеры_локации.items():
                        if барьер["локация_назначения"] == название:
                            барьер_найден = True
                            print(f"🔑 НАЙДЕН БАРЬЕР: {локация_источник} -> {барьер_ключ}")
                            print(f"   Требуется: {барьер['требуется']} x{барьер.get('требуется_количество', 1)}")

                            успех, сообщение, новый_инвентарь = барьеры.открыть_локацию_через_барьер(
                                game.текущая_локация, название, инвентарь_словарь
                            )

                            if успех:
                                print(f"✅ БАРЬЕР ОТКРЫТ! {сообщение}")

                                game.игрок["инвентарь"] = []
                                for предмет, колво in новый_инвентарь.items():
                                    game.игрок["инвентарь"].extend([предмет] * колво)

                                инвентарь_словарь = {}
                                for предмет in game.игрок["инвентарь"]:
                                    инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

                                game.add_to_log(сообщение)
                                барьеры.открытые_барьеры.add(название)
                                print(f"🔓 Барьер {название} открыт и сохранён!")

                                game.change_location(название)
                                return
                            else:
                                print(f"❌ НЕ УДАЛОСЬ ОТКРЫТЬ: {сообщение}")
                                game.add_to_log(сообщение)
                                return

                if not барьер_найден:
                    print(f"🚪 Нет барьера для {название}, просто переходим")
                    game.change_location(название)
                    return

            else:
                print(f"❌ Локация {название} НЕДОСТУПНА")
                game.add_to_log(причина)
                if подсказка:
                    game.add_to_log(подсказка)
                return

    return