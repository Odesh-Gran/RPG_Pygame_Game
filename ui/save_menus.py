import pygame
import sys
from config import *
from loaders import save_manager as сохранение
from entities import items as предметы # если вдруг понадобится
import json

def show_save_menu(game):
    """Показывает меню выбора слота для сохранения (вертикальное расположение с прокруткой)"""
    # ===== СИНХРОНИЗИРУЕМ ИГРОКА ПЕРЕД СОХРАНЕНИЕМ =====
    if "пассивные_бонусы" not in game.игрок:
        game.игрок["пассивные_бонусы"] = {}
        print("🔧 Добавлено поле 'пассивные_бонусы' перед сохранением")
    if "выученные_навыки" not in game.игрок:
        game.игрок["выученные_навыки"] = []
    if "очки_навыков" not in game.игрок:
        game.игрок["очки_навыков"] = 0
    if "очки_умений" not in game.игрок:
        game.игрок["очки_умений"] = 0
    if "сила_бонус" not in game.игрок:
        game.игрок["сила_бонус"] = 0
    if "здоровье_бонус" not in game.игрок:
        game.игрок["здоровье_бонус"] = 0
    if "стойкость_бонус" not in game.игрок:
        game.игрок["стойкость_бонус"] = 0
    if "защита_бонус" not in game.игрок:
        game.игрок["защита_бонус"] = 0
    if "вампиризм" not in game.игрок:
        game.игрок["вампиризм"] = False
    if "амулет" not in game.игрок:
        game.игрок["амулет"] = None

    saves_info = сохранение.list_saves()

    scroll_offset = 0
    visible_slots = 4
    total_slots = 5
    waiting = True
    selected_slot = None

    while waiting:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        game.screen.blit(s, (0, 0))

        title = game.font_large.render("СОХРАНЕНИЕ ИГРЫ", True, GOLD)
        title_shadow = game.font_large.render("СОХРАНЕНИЕ ИГРЫ", True, (80, 60, 30))
        title_x = WIDTH // 2 - title.get_width() // 2
        game.screen.blit(title_shadow, (title_x + 3, 63))
        game.screen.blit(title, (title_x, 60))

        subtitle = game.font_medium.render("Выберите слот для сохранения:", True, WHITE)
        sub_x = WIDTH // 2 - subtitle.get_width() // 2
        game.screen.blit(subtitle, (sub_x, 120))

        slot_buttons = []
        slot_width = 500
        slot_height = 110
        spacing = 15
        start_x = WIDTH // 2 - slot_width // 2
        start_y = 170

        max_scroll = max(0, total_slots - visible_slots)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        start_slot = scroll_offset
        end_slot = min(start_slot + visible_slots, total_slots)

        for i in range(start_slot, end_slot):
            slot = i + 1
            y = start_y + (i - start_slot) * (slot_height + spacing)

            slot_rect = pygame.Rect(start_x, y, slot_width, slot_height)

            save_info = None
            for info in saves_info:
                if info["slot"] == slot:
                    save_info = info
                    break

            if save_info:
                pygame.draw.rect(game.screen, DARK_BLUE, slot_rect)
                pygame.draw.rect(game.screen, GOLD, slot_rect, 2)

                slot_text = game.font_medium.render(f"СЛОТ {slot}", True, GOLD)
                game.screen.blit(slot_text, (start_x + 20, y + 12))

                line1 = f"{save_info['class']} | Уровень {save_info['level']}"
                line1_text = game.font_small.render(line1, True, WHITE)
                line1_x = start_x + slot_width // 2 - line1_text.get_width() // 2
                game.screen.blit(line1_text, (line1_x, y + 28))

                line2 = f"{save_info['time']} | День {save_info['day']}"
                line2_text = game.font_small.render(line2, True, WHITE)
                line2_x = start_x + slot_width // 2 - line2_text.get_width() // 2
                game.screen.blit(line2_text, (line2_x, y + 53))

                line3 = f"{save_info['location']}"
                line3_text = game.font_small.render(line3, True, WHITE)
                line3_x = start_x + slot_width // 2 - line3_text.get_width() // 2
                game.screen.blit(line3_text, (line3_x, y + 78))

                try:
                    with open(f"save_{slot}.json", 'r', encoding='utf-8') as f:
                        данные = json.load(f)
                        игрок_из_сейва = данные.get("игрок", {})
                        if "пассивные_бонусы" not in игрок_из_сейва:
                            old_text = game.font_tiny.render("⚠️ СТАРАЯ ВЕРСИЯ", True, HEALTH_YELLOW)
                            game.screen.blit(old_text, (start_x + slot_width - 130, y + 15))
                except:
                    pass
            else:
                pygame.draw.rect(game.screen, DARK_RED, slot_rect)
                pygame.draw.rect(game.screen, GOLD, slot_rect, 2)

                slot_text = game.font_medium.render(f"СЛОТ {slot}", True, GOLD)
                game.screen.blit(slot_text, (start_x + 20, y + 42))
                empty_text = game.font_medium.render("ПУСТО", True, GRAY)
                game.screen.blit(empty_text, (start_x + slot_width // 2 - empty_text.get_width() // 2, y + 62))

            slot_buttons.append((slot, slot_rect))

            if slot_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(game.screen, GOLD, slot_rect, 3)

        if total_slots > visible_slots:
            scroll_bar_x = start_x + slot_width + 15
            scroll_bar_y = start_y
            scroll_bar_height = visible_slots * (slot_height + spacing)
            scroll_bar_width = 8

            scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
            pygame.draw.rect(game.screen, (40, 40, 40), scroll_bg_rect)
            pygame.draw.rect(game.screen, GOLD, scroll_bg_rect, 1)

            scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
            scroll_thumb_height = max(40, scroll_bar_height // total_slots)
            scroll_thumb_y = scroll_bar_y + scroll_ratio * (scroll_bar_height - scroll_thumb_height)

            scroll_thumb_rect = pygame.Rect(scroll_bar_x, scroll_thumb_y, scroll_bar_width, scroll_thumb_height)
            pygame.draw.rect(game.screen, GOLD, scroll_thumb_rect)

        back_rect = pygame.Rect(WIDTH // 2 - 100, start_y + visible_slots * (slot_height + spacing) + 0, 200, 45)
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

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for slot, rect in slot_buttons:
                        if rect.collidepoint(event.pos):
                            selected_slot = slot
                            waiting = False
                            break

                    if back_rect.collidepoint(event.pos):
                        return
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    scroll_offset -= 1
                else:
                    scroll_offset += 1
                scroll_offset = max(0, min(scroll_offset, max_scroll))

        game.clock.tick(FPS)

    if selected_slot:
        game.show_save_confirmation(selected_slot)


def show_load_menu(game):
    """Показывает меню выбора слота для загрузки (только непустые слоты)"""
    print("📋 show_load_menu вызвана")
    saves_info = сохранение.list_saves()

    if not saves_info:
        print("   ❌ Нет сохранений!")
        game.show_message("Нет сохранений!", duration=60)
        return None

    scroll_offset = 0
    visible_slots = 4
    total_slots = 5
    waiting = True
    selected_slot = None

    while waiting:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        game.screen.blit(s, (0, 0))

        title = game.font_large.render("ЗАГРУЗКА ИГРЫ", True, GOLD)
        title_shadow = game.font_large.render("ЗАГРУЗКА ИГРЫ", True, (80, 60, 30))
        title_x = WIDTH // 2 - title.get_width() // 2
        game.screen.blit(title_shadow, (title_x + 3, 63))
        game.screen.blit(title, (title_x, 60))

        subtitle = game.font_medium.render("Выберите слот для загрузки:", True, WHITE)
        sub_x = WIDTH // 2 - subtitle.get_width() // 2
        game.screen.blit(subtitle, (sub_x, 120))

        slot_buttons = []
        slot_width = 500
        slot_height = 110
        spacing = 15
        start_x = WIDTH // 2 - slot_width // 2
        start_y = 170

        max_scroll = max(0, total_slots - visible_slots)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        start_slot = scroll_offset
        end_slot = min(start_slot + visible_slots, total_slots)

        for i in range(start_slot, end_slot):
            slot = i + 1
            y = start_y + (i - start_slot) * (slot_height + spacing)

            slot_rect = pygame.Rect(start_x, y, slot_width, slot_height)

            save_info = None
            for info in saves_info:
                if info["slot"] == slot:
                    save_info = info
                    break

            if save_info:
                pygame.draw.rect(game.screen, DARK_BLUE, slot_rect)
                pygame.draw.rect(game.screen, GOLD, slot_rect, 2)

                slot_text = game.font_medium.render(f"СЛОТ {slot}", True, GOLD)
                game.screen.blit(slot_text, (start_x + 20, y + 12))

                line1 = f"{save_info['class']} | Уровень {save_info['level']}"
                line1_text = game.font_small.render(line1, True, WHITE)
                line1_x = start_x + slot_width // 2 - line1_text.get_width() // 2
                game.screen.blit(line1_text, (line1_x, y + 28))

                line2 = f"{save_info['time']} | День {save_info['day']}"
                line2_text = game.font_small.render(line2, True, WHITE)
                line2_x = start_x + slot_width // 2 - line2_text.get_width() // 2
                game.screen.blit(line2_text, (line2_x, y + 53))

                line3 = f"{save_info['location']}"
                line3_text = game.font_small.render(line3, True, WHITE)
                line3_x = start_x + slot_width // 2 - line3_text.get_width() // 2
                game.screen.blit(line3_text, (line3_x, y + 78))

                slot_buttons.append((slot, slot_rect))

                if slot_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(game.screen, GOLD, slot_rect, 3)
            else:
                pygame.draw.rect(game.screen, (40, 40, 40), slot_rect)
                pygame.draw.rect(game.screen, GRAY, slot_rect, 2)
                slot_text = game.font_medium.render(f"СЛОТ {slot}", True, GRAY)
                game.screen.blit(slot_text, (start_x + 20, y + 42))
                empty_text = game.font_medium.render("ПУСТО", True, GRAY)
                game.screen.blit(empty_text, (start_x + slot_width // 2 - empty_text.get_width() // 2, y + 62))

        if total_slots > visible_slots:
            scroll_bar_x = start_x + slot_width + 15
            scroll_bar_y = start_y
            scroll_bar_height = visible_slots * (slot_height + spacing)
            scroll_bar_width = 8

            scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
            pygame.draw.rect(game.screen, (40, 40, 40), scroll_bg_rect)
            pygame.draw.rect(game.screen, GOLD, scroll_bg_rect, 1)

            scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
            scroll_thumb_height = max(40, scroll_bar_height // total_slots)
            scroll_thumb_y = scroll_bar_y + scroll_ratio * (scroll_bar_height - scroll_thumb_height)

            scroll_thumb_rect = pygame.Rect(scroll_bar_x, scroll_thumb_y, scroll_bar_width, scroll_thumb_height)
            pygame.draw.rect(game.screen, GOLD, scroll_thumb_rect)

        back_rect = pygame.Rect(WIDTH // 2 - 100, start_y + visible_slots * (slot_height + spacing) + 0, 200, 45)
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

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("   🟠 Получен QUIT, возвращаем None")
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for slot, rect in slot_buttons:
                        if rect.collidepoint(event.pos):
                            selected_slot = slot
                            print(f"   ✅ Выбран слот {selected_slot}")
                            waiting = False
                            break

                    if back_rect.collidepoint(event.pos):
                        print("   🔙 Нажата кнопка НАЗАД, возвращаем None")
                        return None
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    scroll_offset -= 1
                else:
                    scroll_offset += 1
                scroll_offset = max(0, min(scroll_offset, max_scroll))

        game.clock.tick(FPS)

    print(f"📋 show_load_menu возвращает: {selected_slot}")
    return selected_slot


def show_save_menu_for_exit(game):
    """Меню выбора слота для сохранения перед выходом"""
    saves_info = сохранение.list_saves()

    scroll_offset = 0
    visible_slots = 4
    total_slots = 5

    waiting = True

    while waiting:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        game.screen.blit(s, (0, 0))

        title = game.font_large.render("СОХРАНЕНИЕ", True, GOLD)
        title_x = WIDTH // 2 - title.get_width() // 2
        game.screen.blit(title, (title_x, 60))

        subtitle = game.font_medium.render("Выберите слот для сохранения:", True, WHITE)
        sub_x = WIDTH // 2 - subtitle.get_width() // 2
        game.screen.blit(subtitle, (sub_x, 120))

        slot_buttons = []
        slot_width = 500
        slot_height = 110
        spacing = 15
        start_x = WIDTH // 2 - slot_width // 2
        start_y = 170

        max_scroll = max(0, total_slots - visible_slots)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        start_slot = scroll_offset
        end_slot = min(start_slot + visible_slots, total_slots)

        for i in range(start_slot, end_slot):
            slot = i + 1
            y = start_y + (i - start_slot) * (slot_height + spacing)

            slot_rect = pygame.Rect(start_x, y, slot_width, slot_height)

            save_info = None
            for info in saves_info:
                if info["slot"] == slot:
                    save_info = info
                    break

            if save_info:
                pygame.draw.rect(game.screen, DARK_BLUE, slot_rect)
                pygame.draw.rect(game.screen, GOLD, slot_rect, 2)

                slot_text = game.font_medium.render(f"СЛОТ {slot}", True, GOLD)
                game.screen.blit(slot_text, (start_x + 20, y + 12))

                line1 = f"{save_info['class']} | Уровень {save_info['level']}"
                line1_text = game.font_small.render(line1, True, WHITE)
                line1_x = start_x + slot_width // 2 - line1_text.get_width() // 2
                game.screen.blit(line1_text, (line1_x, y + 28))

                line2 = f"{save_info['time']} | День {save_info['day']}"
                line2_text = game.font_small.render(line2, True, WHITE)
                line2_x = start_x + slot_width // 2 - line2_text.get_width() // 2
                game.screen.blit(line2_text, (line2_x, y + 53))

                line3 = f"{save_info['location']}"
                line3_text = game.font_small.render(line3, True, WHITE)
                line3_x = start_x + slot_width // 2 - line3_text.get_width() // 2
                game.screen.blit(line3_text, (line3_x, y + 78))
            else:
                pygame.draw.rect(game.screen, DARK_RED, slot_rect)
                pygame.draw.rect(game.screen, GOLD, slot_rect, 2)

                slot_text = game.font_medium.render(f"СЛОТ {slot}", True, GOLD)
                game.screen.blit(slot_text, (start_x + 20, y + 42))
                empty_text = game.font_medium.render("ПУСТО", True, GRAY)
                game.screen.blit(empty_text, (start_x + slot_width // 2 - empty_text.get_width() // 2, y + 62))

            slot_buttons.append((slot, slot_rect))

            if save_info and slot_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(game.screen, GOLD, slot_rect, 3)

        if total_slots > visible_slots:
            scroll_bar_x = start_x + slot_width + 15
            scroll_bar_y = start_y
            scroll_bar_height = visible_slots * (slot_height + spacing)
            scroll_bar_width = 8

            scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
            pygame.draw.rect(game.screen, (40, 40, 40), scroll_bg_rect)
            pygame.draw.rect(game.screen, GOLD, scroll_bg_rect, 1)

            scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
            scroll_thumb_height = max(40, scroll_bar_height // total_slots)
            scroll_thumb_y = scroll_bar_y + scroll_ratio * (scroll_bar_height - scroll_thumb_height)

            scroll_thumb_rect = pygame.Rect(scroll_bar_x, scroll_thumb_y, scroll_bar_width, scroll_thumb_height)
            pygame.draw.rect(game.screen, GOLD, scroll_thumb_rect)

        back_rect = pygame.Rect(WIDTH // 2 - 100, start_y + visible_slots * (slot_height + spacing) + 20, 200, 45)
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

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for slot, rect in slot_buttons:
                        if rect.collidepoint(event.pos):
                            сохранение.сохранить_игру(game.игрок, game.текущая_локация, game.chest_inventory, slot)
                            game.add_to_log(f"Игра сохранена в слот {slot}!")
                            waiting = False
                            return

                    if back_rect.collidepoint(event.pos):
                        waiting = False
                        return
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    scroll_offset -= 1
                else:
                    scroll_offset += 1
                scroll_offset = max(0, min(scroll_offset, max_scroll))

        game.clock.tick(FPS)