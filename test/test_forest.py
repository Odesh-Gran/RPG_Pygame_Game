"""
Тест для проверки системы большой локации
"""

import pygame
import sys
import враги
import exploration

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Тест лесной локации")
clock = pygame.time.Clock()
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
RED = (200, 50, 50)
GOLD = (184, 134, 11)

# Шрифты
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 32)


def create_forest_zone():
    """Создаёт тестовую лесную зону"""
    print("\n🌳 СОЗДАНИЕ ЛЕСНОЙ ЗОНЫ")

    # Создаём зону 2000x2000
    zone = exploration.ExplorationZone(2000, 2000, (30, 50, 30))

    # Добавляем препятствия (деревья)
    print("  - Добавляем деревья...")
    tree_positions = [
        (300, 300), (500, 200), (700, 400), (900, 250),
        (1100, 350), (1300, 500), (1500, 300), (1700, 400),
        (400, 600), (600, 700), (800, 550), (1000, 650),
        (1200, 750), (1400, 600), (1600, 700), (1800, 550),
        (250, 1000), (450, 1100), (650, 950), (850, 1050),
        (1050, 1150), (1250, 1000), (1450, 1100), (1650, 950),
        (1850, 1050), (350, 1400), (550, 1300), (750, 1450),
        (950, 1350), (1150, 1400), (1350, 1300), (1550, 1450),
        (1750, 1350), (1950, 1400)
    ]

    for x, y in tree_positions:
        zone.add_obstacle(x, y, 40, 40)

    # Добавляем мобов
    print("  - Добавляем мобов...")

    # Позиции для мобов (разбросаны по карте)
    mob_positions = [
        # Северная часть
        (400, 400), (600, 300), (800, 500), (1000, 400), (1200, 600),
        (1400, 350), (1600, 500), (1800, 400),
        # Центральная часть
        (500, 800), (700, 900), (900, 700), (1100, 850), (1300, 750),
        (1500, 900), (1700, 800), (1900, 700),
        # Южная часть
        (400, 1200), (600, 1300), (800, 1100), (1000, 1250), (1200, 1150),
        (1400, 1300), (1600, 1200), (1800, 1350), (1900, 1250)
    ]

    # Типы мобов (циклически)
    mob_types = ["лесной_гоблин", "лесной_волк", "древний_энт", "лесная_фея"]

    for i, (x, y) in enumerate(mob_positions):
        mob_type = mob_types[i % len(mob_types)]
        level = 1 + (i % 3)  # Уровни 1-3
        mob = exploration.Mob(x, y, mob_type, level)
        zone.add_mob(mob)
        print(f"    Моб {i + 1}: {mob_type} (ур.{level}) на ({x}, {y})")

    # Добавляем босса в центре
    print("  - Добавляем босса в центре...")
    boss = exploration.Boss(200, 1000, "лесной_король")
    zone.add_boss(boss)

    print(f"\n✅ Зона создана!")
    print(f"   - Размер: {zone.width}x{zone.height}")
    print(f"   - Мобов: {len(zone.mobs)}")
    print(f"   - Боссов: {len(zone.bosses)}")
    print(f"   - Препятствий: {len(zone.obstacles)}")

    return zone


def draw_ui(screen, zone, show_help=True):
    """Рисует интерфейс"""
    # Панель информации в левом верхнем углу
    info_panel = pygame.Rect(10, 10, 300, 120)
    pygame.draw.rect(screen, (0, 0, 0, 180), info_panel)
    pygame.draw.rect(screen, GOLD, info_panel, 2)

    # Текст
    texts = [
        f"ПОЗИЦИЯ: ({int(zone.player_x)}, {int(zone.player_y)})",
        f"МОБЫ: {len(zone.mobs)}",
        f"БОСС: {'ЖИВ' if not any(b.defeated for b in zone.bosses) else 'ПОБЕЖДЁН'}",
        f"В БОЮ: {'ДА' if zone.in_battle else 'НЕТ'}"
    ]

    for i, text in enumerate(texts):
        text_surface = font_small.render(text, True, WHITE)
        screen.blit(text_surface, (20, 20 + i * 25))

    # Управление
    if show_help:
        controls = [
            "WASD или СТРЕЛКИ - движение",
            "ESC - выход из теста"
        ]

        for i, text in enumerate(controls):
            text_surface = font_small.render(text, True, (200, 200, 200))
            screen.blit(text_surface, (WIDTH - 300, HEIGHT - 50 + i * 20))


def show_battle_message(screen, enemy_name):
    """Показывает сообщение о начале боя"""
    # Затемнение
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Панель сообщения
    panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 100, 500, 150)
    pygame.draw.rect(screen, (40, 40, 60), panel)
    pygame.draw.rect(screen, RED, panel, 3)

    # Текст
    title = font_medium.render("⚔️ СТОЛКНОВЕНИЕ! ⚔️", True, RED)
    title_x = WIDTH // 2 - title.get_width() // 2
    screen.blit(title, (title_x, HEIGHT // 2 - 60))

    enemy_text = font_medium.render(enemy_name.replace('_', ' ').upper(), True, GOLD)
    enemy_x = WIDTH // 2 - enemy_text.get_width() // 2
    screen.blit(enemy_text, (enemy_x, HEIGHT // 2 - 20))

    hint = font_small.render("Нажмите любую клавишу для продолжения...", True, WHITE)
    hint_x = WIDTH // 2 - hint.get_width() // 2
    screen.blit(hint, (hint_x, HEIGHT // 2 + 40))

    pygame.display.flip()

    # Ждём нажатия
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        clock.tick(FPS)

    return True


def main():
    """Главная функция теста"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ ЛЕСНОЙ ЛОКАЦИИ")
    print("=" * 60)

    # Проверяем наличие врагов
    print("\n📋 ПРОВЕРКА ВРАГОВ:")
    test_enemies = ["лесной_гоблин", "лесной_волк", "древний_энт", "лесная_фея", "лесной_тролль"]

    all_ok = True
    for enemy in test_enemies:
        if enemy in враги.враги:
            data = враги.враги[enemy]
            print(f"  ✅ {enemy}: HP={data['здоровье']}, Сила={data['сила']}, Уровень={data.get('уровень', '?')}")
        else:
            print(f"  ❌ {enemy} НЕ НАЙДЕН!")
            all_ok = False

    # Проверяем боссов
    test_bosses = ["лесной_король", "лесная_ведьма"]
    for boss in test_bosses:
        if boss in враги.враги:
            data = враги.враги[boss]
            print(f"  ✅ {boss}: HP={data['здоровье']}, Сила={data['сила']}")
        else:
            print(f"  ❌ {boss} НЕ НАЙДЕН!")
            all_ok = False

    if not all_ok:
        print("\n❌ ОШИБКА: Некоторые враги не найдены!")
        print("Проверьте файл враги.py")
        return

    # Создаём зону
    print("\n🏞️ СОЗДАНИЕ ЗОНЫ:")
    zone = create_forest_zone()

    # Главный цикл
    print("\n🎮 ЗАПУСК ТЕСТА...")
    print("   Управление: WASD или стрелки")
    print("   Исследуйте лес и встречайте мобов!")
    print("   ESC - выход\n")

    running = True
    battle_started = False
    last_encounter = None

    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Получаем нажатые клавиши
        keys = pygame.key.get_pressed()

        # Обновляем зону
        zone.update(keys)

        # Проверяем столкновения (только если не в бою)
        if not zone.in_battle:
            encounter = zone.check_encounters()
            if encounter and encounter != last_encounter:
                encounter_type, enemy_name, level = encounter

                # Показываем сообщение о бое
                if show_battle_message(screen, enemy_name):
                    print(f"\n⚔️ БОЙ! {enemy_name} (уровень {level})")
                    zone.in_battle = True
                    last_encounter = encounter

                    # Имитация боя (в реальной игре здесь будет боевая система)
                    # Просто показываем сообщение и удаляем моба для теста
                    print(f"   💀 {enemy_name} повержен! (тестовый режим)")

                    # Удаляем моба
                    if encounter_type == "mob":
                        for mob in zone.mobs:
                            if mob.enemy_name == enemy_name and mob.is_alive:
                                # Проверяем близость по координатам
                                dx = abs(mob.x - zone.player_x)
                                dy = abs(mob.y - zone.player_y)
                                if dx < 50 and dy < 50:
                                    zone.mobs.remove(mob)
                                    print(f"   🗡️ Моб {enemy_name} удалён с карты")
                                    break

                    zone.in_battle = False
                    last_encounter = None

        # Отрисовка
        zone.draw(screen)
        draw_ui(screen, zone, show_help=True)

        # Счётчик FPS
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        screen.blit(fps_text, (WIDTH - 80, 10))

        pygame.display.flip()
        clock.tick(FPS)

    print("\n🏁 ТЕСТ ЗАВЕРШЁН")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()