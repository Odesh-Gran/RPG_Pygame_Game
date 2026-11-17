import pygame
from config import *
from loaders import save_manager as сохранение
from ui.save_menus import show_load_menu
from systems import barriers as барьеры
from entities.player import создать_нового_игрока
from systems.inventory_system import InventorySystem
from systems.battle_system import BattleSystem

def show_main_menu(game):
    """Показывает главное меню и возвращает True (игра запущена) или None (выход)"""
    print("🟢 show_main_menu запущена")

    game.music.переключить_плейлист("меню", game.игра_загружена)
    барьеры.сбросить_открытые_барьеры()

    try:
        bg = pygame.image.load("assets/backgrounds/menu_bg.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
        print("✅ Фон загружен")
    except Exception as e:
        print(f"❌ Ошибка загрузки фона: {e}")
        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill((20, 10, 30))

    menu_active = True
    frame_count = 0

    center_x = WIDTH // 2 - -250
    y = 250

    new_rect = pygame.Rect(center_x, y, 300, 60)
    load_rect = pygame.Rect(center_x, y + 80, 300, 60)
    exit_rect = pygame.Rect(center_x, y + 160, 300, 60)

    while menu_active:
        frame_count += 1
        if frame_count % 60 == 0:
            print(f"🔄 Меню активно, кадр {frame_count}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("🟠 Получен сигнал QUIT")
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                print(f"🖱️ Клик в позиции {mouse_pos}")

                if new_rect.collidepoint(mouse_pos):
                    print("🆕 Нажата кнопка НОВАЯ ИГРА")
                    game.music.остановить_музыку()

                    game.игрок = создать_нового_игрока()
                    game.inventory = InventorySystem(game.игрок, game.item_icons)
                    game.battle = BattleSystem(game.игрок, game)
                    game.игра_загружена = True

                    if not game.show_intro():
                        return False

                    выбранный_класс = game.show_class_selection()
                    if выбранный_класс:
                        game.apply_class(выбранный_класс)
                        game.quest_system.добавить_квест(game.игрок, "основной_начало")
                        print("📜 Добавлен стартовый квест (новая игра)")

                        if game.music.есть_музыка(game.текущая_локация):
                            game.music.переключить_плейлист(game.текущая_локация, game.игра_загружена)
                        else:
                            game.music.остановить_музыку()

                        return True
                    else:
                        return False

                elif load_rect.collidepoint(mouse_pos):
                    print("📂 Нажата кнопка ЗАГРУЗИТЬ")
                    saves_info = сохранение.list_saves()
                    if not saves_info:
                        print("❌ Нет сохранённой игры!")
                        game.show_message("Нет сохранений!", duration=60)
                        continue

                    selected_slot = show_load_menu(game)
                    print(f"🔍 selected_slot = {selected_slot}")
                    if selected_slot:
                        print(f"📂 Загружаем слот {selected_slot}")
                        загруженный_игрок, загруженная_локация, chest_inventory = сохранение.загрузить_игру(selected_slot)
                        if загруженный_игрок:
                            game.music.остановить_музыку()

                            game.игрок.update(загруженный_игрок)
                            game.текущая_локация = загруженная_локация
                            game.chest_inventory = chest_inventory
                            game.игра_загружена = True

                            if game.music.есть_музыка(game.текущая_локация):
                                game.music.переключить_плейлист(game.текущая_локация, game.игра_загружена)
                            else:
                                game.music.остановить_музыку()

                            if not game.игрок.get("активные_квесты") and not game.игрок.get("завершенные_квесты"):
                                game.quest_system.добавить_квест(game.игрок, "основной_начало")
                                print("📜 Добавлен стартовый квест (загрузка)")

                            game._пересчитать_пассивные_бонусы()
                            game.inventory.update_max_health()
                            print(f"✅ Загружена игра из слота {selected_slot}")

                            return True
                    continue

                elif exit_rect.collidepoint(mouse_pos):
                    print("🚪 Нажата кнопка ВЫХОД")
                    if game.show_exit_confirmation():
                        print("   ⚠️ Возвращаем None (выход из меню)")
                        return None
                    else:
                        continue

        game.screen.blit(bg, (0, 0))
        pygame.display.flip()
        game.clock.tick(FPS)

    return None