# ===== СТАНДАРТНЫЕ БИБЛИОТЕКИ =====
import json
import math
import random
import sys

from ui.battle_ui import draw_battle
from ui.main_menu import show_main_menu
from ui.map_ui import draw_map, handle_map_click

from ui.hud import draw_status, draw_location, draw_actions

from ui.chest_ui import draw_chest, handle_chest_click
from ui.trade_ui import draw_quest_trade_menu, handle_trade_click, draw_trade
from systems.dungeon_controller import DungeonController

from ui.save_menus import show_save_menu, show_load_menu, show_save_menu_for_exit
# ===== СТОРОННИЕ БИБЛИОТЕКИ =====
# noinspection PyUnresolvedReferences
from pyvidplayer2 import Video
from systems.video_manager import VideoManager

from ui.crafting_ui import draw_craft, handle_craft_click

from ui.inventory_ui import draw_inventory, handle_inventory_click
# ===== МУЗЫКА =====
from systems.audio import MusicManager
# ===== КВЕСТЫ =====
from ui.quest_tracker import draw_quest_tracker, draw_daily_quest_tracker
# ===== ИГРОВЫЕ СУЩНОСТИ (entities) =====
from entities import player as игрок
from entities.player import потратить_ресурсы, проверить_голод
from entities import locations as локации
from entities import items as предметы

from ui.skills_menu import draw_skills_menu

# ===== ИГРОВЫЕ СИСТЕМЫ (systems) =====
from systems.battle_system import BattleSystem
from systems.inventory_system import InventorySystem
from systems.quest_system import QuestSystem
from systems import crafting as верстак
from systems import merchant as торговец
from systems import barriers as барьеры
from systems import time_system as время
from systems import exploration

# ===== ЗАГРУЗЧИКИ И СОХРАНЕНИЯ =====
from loaders.skill_loader import SkillLoader
from loaders import save_manager as сохранение
from ui.login_screen import LoginScreen

EMOJI_FONT_PATH = "C:/Windows/Fonts/seguiemj.ttf"
# ===== ИМПОРТ НАСТРОЕК =====
from config import *

# ===== ИНИЦИАЛИЗАЦИЯ =====
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("castle-survival v0.1")
clock = pygame.time.Clock()

# ===== СОЗДАЁМ ШРИФТЫ =====
fonts = get_fonts()
font_tiny = fonts["tiny"]
font_small = fonts["small"]
font_medium = fonts["medium"]
font_large = fonts["large"]
font_emoji = pygame.font.Font(EMOJI_FONT_PATH, 28)


class Game:
    def __init__(self,api=None):
        """Инициализация игры"""
        self.api = api
        self.token = self.api.token if self.api else None  # берём токен из api
        # ========== НАСТРОЙКИ ЭКРАНА ==========
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.fullscreen = False

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.clock = pygame.time.Clock()

        # ========== ШРИФТЫ (прокидываем внутрь класса) ==========
        self.font_tiny = font_tiny
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # ========== ОСНОВНЫЕ ПАРАМЕТРЫ ИГРЫ ==========
        from entities.player import создать_нового_игрока
        self.игрок = создать_нового_игрока()  # 👈 ИЗМЕНЕНО!
        self.текущая_локация = "Убежище"
        self.игра_активна = True
        self.режим = "игра"

        # ===== ФЛАГ ЗАГРУЗКИ ИГРЫ =====  #
        self.игра_загружена = False

        # ==== Добавляется квест ====
        self.quest_system = QuestSystem()

        # ========== ХРАНИЛИЩА ==========
        self.chest_inventory = []

        # ========== ИНТЕРФЕЙС ==========
        self.buttons = []
        self.btn_new = None
        self.btn_load = None
        self.btn_exit = None

        # ========== ЗАГРУЗКА РЕСУРСОВ ==========
        self.close_icon = None
        self.load_close_icon()

        # ========== ЗАГРУЗКА НАВЫКОВ ==========
        self.current_skill_tab = "prof"
        self.skills_data = SkillLoader.load_skills()
        if self.skills_data:
            print(f"✅ Навыки загружены успешно")
            settings = self.skills_data.get("общие_настройки", {})
            print(f"   Очков за уровень: {settings.get('очков_за_уровень', 1)}")
            print(f"   Цена сброса: {settings.get('цена_сброса_навыков', 500)}")

        # ========== ИКОНКИ ПРЕДМЕТОВ ==========
        self.item_icons = {}
        self.load_item_icons()

        # ========== СИСТЕМА ИНВЕНТАРЯ ==========
        self.inventory = InventorySystem(self.игрок, self.item_icons)

        # ===== МУЗЫКА =====
        # Оставляем только словарь с треками.
        # Настройки (громкость, вкл/выкл, текущий плейлист) теперь живет внутри MusicManager.
        музыка_локаций = {
            "Холл": ["assets/music/hall_1.mp3"],
            "Кухня": ["assets/music/kitchen_1.mp3"],
            "Сад": ["assets/music/garden_1.mp3"],
            "Пруд": ["assets/music/pond_1.mp3"],
            "Мастерская": ["assets/music/workshop_1.mp3"],
            "Лестница": ["assets/music/stairs_1.mp3"],
            "Библиотека": ["assets/music/library_1.mp3"],
            "Коридор": ["assets/music/corridor_1.mp3"],
            "Темница": ["assets/music/dungeon_1.mp3"],
            "Главный зал": ["assets/music/great_hall_1.mp3"],
            "Убежище": [
                "assets/music/ubegische_1.mp3",
                "assets/music/ubegische_2.mp3",
            ],
            "Зачарованный лес": ["assets/music/forest_1.mp3"],
            "Древний склеп": ["assets/music/crypt_1.mp3"],
            "бой": ["assets/music/battle_1.mp3"],
            "меню": ["assets/music/menu_1.mp3"],
        }

        # Создаем объект менеджера музыки, передаем ему треки и настройки
        self.music = MusicManager(
            музыка_локаций=музыка_локаций,
            громкость=0.3,
            включена=True
        )

        # ========== СИСТЕМА БОЯ ==========
        self.battle = BattleSystem(self.игрок, self)

        # ========== КОНТРОЛЛЕР ДАНЖЕЙ ==========   #
        self.dungeon = DungeonController(self)

        # ========== ГЛАВНОЕ МЕНЮ ==========
        menu_result = show_main_menu(self)
        print(f"🟢 Результат show_main_menu(): {menu_result}")

        # ===== ЕСЛИ ВЫХОД ИЗ МЕНЮ - ПРЕРЫВАЕМ ИНИЦИАЛИЗАЦИЮ =====
        if menu_result is None or menu_result is False:
            print("🔴 Выход из главного меню, игра завершается")
            self.игра_активна = False
            return  # ← ВАЖНО! ПРЕРЫВАЕМ ВЫПОЛНЕНИЕ __init__

        # ========== ФОНЫ ЛОКАЦИЙ ==========
        self.backgrounds = {}
        self.load_backgrounds()

        # ===== ВИДЕО-ПЕРЕХОДЫ =====
        self.video_manager = VideoManager()

        # ========== ИКОНКИ ДЕЙСТВИЙ ==========
        self.action_icons = {}
        self.load_action_icons()

        # ========== СИСТЕМА КРАФТА ==========
        self.craft_categories = {
            "ОРУЖИЕ": ["лезвие", "призрачный меч"],
            "БРОНЯ": ["кожаная броня", "кольчужная броня"],
            "ЕДА": ["блины", "рыба", "зелье здоровья"],
            "МАТЕРИАЛЫ": ["шестерёнка"]
        }
        self.craft_category = list(self.craft_categories.keys())[0]
        self.craft_scroll = 0

        # ========== ЛОГ СОБЫТИЙ ==========
        self.log_messages = []
        self.max_log_messages = 20

        # ========== ОПИСАНИЕ ЛОКАЦИЙ ==========
        self.description_timer = 0
        self.show_description = True
        self.description_duration = 300

        # ========== СИСТЕМА ОТДЫХА ==========
        self.last_rest_day = None

        # ========== АНИМАЦИЯ ПЕРЕХОДА ==========
        self.transition_alpha = 0
        self.transition_target = 0
        self.transition_active = False
        self.transition_speed = 7
        self.next_location = None

        # ===== ПОСЛЕ ВЫХОДА ИЗ МЕНЮ =====
        if menu_result is not None and menu_result is not False:
            self.игра_загружена = True  # 👈 ДОБАВЬТЕ!

        # ========== ПЕРСОНАЖ ==========
        self.player_size = 200
        self.player_pos = [WIDTH // 5 - self.player_size // 2, HEIGHT // 1.5 - self.player_size // 2]
        self.player_sprite = None
        self.load_player_sprite()


        # ========== ВРАГ ==========
        self.enemy_size = 190
        self.enemy_pos = [WIDTH // 2 - self.enemy_size // 2, 100]
        self.enemy_sprite = None
        self.current_enemy_for_display = None
        #self.load_enemy_sprite()


        # ===== АНИМАЦИЯ НАЧАЛА БОЯ =====
        self.battle_start_animation = False
        self.battle_start_timer = 0
        self.battle_start_alpha = 0
        self.battle_start_scale = 0.5

        # ===== ПАНЕЛЬ ПОЛУЧЕНИЯ ЛУТА =====
        self.loot_panel_active = False
        self.loot_items = []
        self.loot_exp = 0
        self.loot_rare_item = None
        self.loot_animation_progress = 0

        # ======= БОЕВЫЕ ПАРАМЕТРЫ (для совместимости) ========
        self.blocking = False
        self.rage_active = False
        self.enemy_bleed_duration = 0
        self.enemy_bleed_damage = 5
        self.enemy_stunned = False
        self.enemy_weakened_duration = 0
        self.vampirism_active = False
        self.vampirism_duration = 0
        self.revive_used = False

        # ===== ШКАЛА ПРОГРЕССА ОБЫСКА =====
        self.обыск_активен = False
        self.обыск_прогресс = 0
        self.обыск_таймер = 0
        self.обыск_длительность = 60  # 3 секунды при 60 FPS
        self.обыск_x = WIDTH // 2 - 200
        self.обыск_y = HEIGHT // 2 + 100

        # ===== ОТОБРАЖЕНИЕ КВЕСТОВ НА ЭКРАНЕ =====
        self.показывать_квесты = True
        self.квесты_позиция_x = WIDTH - 340
        self.квесты_позиция_y = 80

        self.previous_mode = "игра"


    def show_loot_panel(self, items, exp, rare_item=None):
        """Показывает выезжающую панель с лутом"""
        self.loot_panel_active = True
        self.loot_items = items.copy()
        self.loot_exp = exp
        self.loot_rare_item = rare_item
        self.loot_animation_progress = 0  # ← сбрасываем анимацию
        print(f"📦 Панель лута открыта: {items}, опыт: {exp}")

    def close_loot_panel(self):
        """Закрывает панель лута и добавляет предметы в инвентарь"""
        print(f"\n📦 close_loot_panel вызвана!")
        print(f"   loot_items: {self.loot_items}")
        print(f"   loot_exp: {self.loot_exp}")

        # Добавляем предметы в инвентарь
        for item in self.loot_items:
            self.inventory.add_item(item)
            self.add_to_log(f"Получен: {item}")

        if self.loot_rare_item:
            self.inventory.add_item(self.loot_rare_item)
            self.add_to_log(f"РЕДКИЙ ДРОП: {self.loot_rare_item}!")

        # ВАЖНО: Импортируем глобального игрока и синхронизируем
        from entities.player import игрок as глобальный_игрок, изменить_уровень

        # Синхронизируем локального игрока с глобальным
        # (на случай, если они разошлись)
        глобальный_игрок.update(self.игрок)

        # Добавляем опыт к глобальному игроку
        глобальный_игрок["опыт"] += self.loot_exp
        self.add_to_log(f"+{self.loot_exp} опыта")

        print(f"   📊 Текущий опыт ДО: {глобальный_игрок['опыт'] - self.loot_exp}")
        print(f"   📊 Текущий опыт ПОСЛЕ: {глобальный_игрок['опыт']}")
        print(f"   📊 Порог уровня: {глобальный_игрок['опыта_до_след_уровня']}")

        # Проверяем повышение уровня
        изменить_уровень()

        # СИНХРОНИЗИРУЕМ ОБРАТНО: обновляем локального игрока из глобального
        self.игрок.update(глобальный_игрок)

        print(f"   📊 Уровень после: {self.игрок['уровень']}, опыт: {self.игрок['опыт']}")

        # Закрываем панель
        self.loot_panel_active = False
        self.loot_items = []
        self.loot_exp = 0
        self.loot_rare_item = None
        self.loot_animation_progress = 0

        print(f"   Панель лута закрыта!")
    def draw_loot_panel(self):
        """Рисует выезжающую панель лута в стиле игры"""
        if not self.loot_panel_active:
            return

        # Параметры панели
        panel_width = 320
        panel_height = 250
        panel_y = HEIGHT // 2 - panel_height // 2

        # Анимация выезжания
        if self.loot_animation_progress < 1:
            self.loot_animation_progress += 0.05
            if self.loot_animation_progress > 1:
                self.loot_animation_progress = 1

        current_x = -panel_width + (panel_width * self.loot_animation_progress)
        panel_x = int(current_x)

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # ===== ФОН (как в инвентаре) =====
        # Тёмно-синий фон
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)

        # Золотая рамка
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Внутренняя рамка-пергамент (как в картах боя)
        pygame.draw.rect(self.screen, GOLD, (panel_x + 5, panel_y + 5, panel_width - 10, panel_height - 10), 1)

        # ===== ЗАГОЛОВОК =====
        title = font_medium.render("ПОБЕДА!", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 12))

        # Разделитель (как в инвентаре)
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 15, panel_y + 42),
                         (panel_x + panel_width - 15, panel_y + 42), 2)

        # ===== ОПЫТ =====
        exp_text = font_small.render(f"Опыт: +{self.loot_exp}", True, HEALTH_GREEN)
        self.screen.blit(exp_text, (panel_x + 20, panel_y + 55))

        # ===== ЗАГОЛОВОК ПРЕДМЕТОВ =====
        items_title = font_small.render("ПОЛУЧЕНО:", True, GOLD)
        self.screen.blit(items_title, (panel_x + 20, panel_y + 85))

        # ===== СПИСОК ПРЕДМЕТОВ =====
        y_offset = panel_y + 110
        item_height = 28

        for i, item in enumerate(self.loot_items):
            # Иконка предмета
            if item in self.item_icons:
                icon = self.item_icons[item]
                icon = pygame.transform.scale(icon, (24, 24))
                self.screen.blit(icon, (panel_x + 20, y_offset + i * item_height - 2))
                text_x = panel_x + 50
            else:
                text_x = panel_x + 20

            item_text = font_small.render(f"• {item}", True, WHITE)
            self.screen.blit(item_text, (text_x, y_offset + i * item_height))

        # ===== РЕДКИЙ ПРЕДМЕТ =====
        if self.loot_rare_item:
            rare_y = y_offset + len(self.loot_items) * item_height + 5

            # Разделитель
            pygame.draw.line(self.screen, GOLD,
                             (panel_x + 15, rare_y - 2),
                             (panel_x + panel_width - 15, rare_y - 2), 1)

            rare_title = font_small.render("РЕДКИЙ ДРОП!", True, BLOOD_RED)
            self.screen.blit(rare_title, (panel_x + 100, rare_y))

            if self.loot_rare_item in self.item_icons:
                icon = self.item_icons[self.loot_rare_item]
                icon = pygame.transform.scale(icon, (24, 24))
                self.screen.blit(icon, (panel_x + 20, rare_y + 18))
                text_x = panel_x + 50
            else:
                text_x = panel_x + 20

            rare_text = font_small.render(self.loot_rare_item, True, BLOOD_RED)
            self.screen.blit(rare_text, (text_x, rare_y + 23))

        # ===== КНОПКА "ЗАБРАТЬ" (как в инвентаре) =====
        button_rect = pygame.Rect(panel_x + panel_width // 2 - 70,
                                  panel_y + panel_height - 48,
                                  140, 32)

        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, button_rect)
            button_text = font_small.render("ЗАБРАТЬ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, button_rect)
            pygame.draw.rect(self.screen, GOLD, button_rect, 2)
            button_text = font_small.render("ЗАБРАТЬ", True, WHITE)

        text_x = button_rect.x + button_rect.width // 2 - button_text.get_width() // 2
        text_y = button_rect.y + button_rect.height // 2 - button_text.get_height() // 2
        self.screen.blit(button_text, (text_x, text_y))

        self.loot_button = button_rect

    def draw_item_tooltip(self, item_name, x, y):
        """Рисует всплывающую подсказку с информацией о предмете"""

        # Получаем данные предмета
        item_data = предметы.предметы.get(item_name, {})

        # Собираем информацию о предмете
        info_lines = []

        # Название предмета
        info_lines.append(("=== " + item_name + " ===", GOLD))

        # Тип предмета
        item_type = item_data.get("тип", "неизвестно")
        info_lines.append((f"Тип: {item_type}", WHITE))

        # Характеристики в зависимости от типа
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
            кулинария_бонус = self.игрок.get("кулинария", 0)
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

        # Описание (если есть)
        описание = item_data.get("описание", "")
        if описание:
            # Разбиваем описание на строки
            desc_lines = self._разбить_текст_на_строки(описание, 250, font_small)
            for line in desc_lines[:2]:  # максимум 2 строки описания
                info_lines.append((line, (200, 200, 200)))

        # Цена (если есть)
        цена = item_data.get("цена", 0)
        if цена > 0:
            info_lines.append((f"Цена: {цена} монет", GOLD))

        # Рассчитываем размер подсказки
        line_height = 22
        padding = 10
        max_width = 0

        # Временно рендерим текст для расчёта ширины
        for line, _ in info_lines:
            text_surface = font_small.render(line, True, WHITE)
            max_width = max(max_width, text_surface.get_width())

        tooltip_width = max_width + padding * 2
        tooltip_height = len(info_lines) * line_height + padding * 2

        # Позиция подсказки (сдвигаем, чтобы не выходила за экран)
        tooltip_x = x + 15
        tooltip_y = y - tooltip_height - 10

        # Корректируем, если выходит за левый край
        if tooltip_x + tooltip_width > WIDTH:
            tooltip_x = x - tooltip_width - 15
        # Корректируем, если выходит за верхний край
        if tooltip_y < 0:
            tooltip_y = y + 30

        # Рисуем фон подсказки
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 230), tooltip_rect)
        pygame.draw.rect(self.screen, GOLD, tooltip_rect, 2)

        # Рисуем текст
        text_y = tooltip_y + padding
        for line, color in info_lines:
            text_surface = font_small.render(line, True, color)
            self.screen.blit(text_surface, (tooltip_x + padding, text_y))
            text_y += line_height

    def load_item_icons(self):
        """Загружает иконки для всех предметов"""

        from entities import items as предметы

        # Загружаем только те, для которых есть иконки
        for item_name, path in предметы.ITEMS_WITH_ICONS.items():
            try:
                icon = pygame.image.load(path).convert_alpha()
                icon = pygame.transform.scale(icon, (64, 64))
                self.item_icons[item_name] = icon
            except Exception as e:
                print(f"❌ Не удалось загрузить {item_name}: {e}")
                self.item_icons[item_name] = self.create_placeholder_icon(item_name)

        # Для остальных - заглушки
        for item_name in предметы.предметы.keys():
            if item_name not in self.item_icons:
                self.item_icons[item_name] = self.create_placeholder_icon(item_name)

    def create_placeholder_icon(self, item_name):
        """Создаёт иконку-заглушку для предмета на основе его реального типа"""
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)

        from entities import items as предметы

        # Получаем реальные данные предмета
        item_data = предметы.предметы.get(item_name, {})
        item_type = item_data.get("тип", "неизвестно")

        # Определяем цвет и символ по ТИПУ предмета
        if item_type == "оружие":
            color = (200, 100, 100)  # красный
            symbol = "ОРУЖ"
        elif item_type == "броня":
            color = (100, 100, 200)  # синий
            symbol = "БРОН"
        elif item_type == "еда":
            color = (100, 200, 100)  # зелёный
            symbol = "ЕДА"
        elif item_type == "книга":
            color = (150, 100, 50)  # коричневый
            symbol = "КНИГ"
        elif item_type == "аксессуар" or item_type == "амулет":
            color = (150, 50, 150)  # фиолетовый
            symbol = "АМУЛ"
        elif item_type == "ценность":
            color = (200, 200, 100)  # золотой
            symbol = "ЦЕН"
        elif item_type == "ресурс":
            color = (80, 80, 100)  # серо-синий
            symbol = "РЕС"
        elif item_type == "трофей":
            color = (120, 80, 60)  # коричневый
            symbol = "ТРОФ"
        elif item_type == "ключ":
            color = (180, 150, 50)  # золотистый
            symbol = "КЛЮЧ"
        else:
            color = (150, 150, 150)  # серый
            symbol = "???"

        # Заливка
        pygame.draw.rect(icon, color, (0, 0, 32, 32))
        pygame.draw.rect(icon, (200, 200, 200), (0, 0, 32, 32), 2)

        # Текст
        try:
            font = pygame.font.Font(None, 16)
            text = font.render(symbol, True, (255, 255, 255))
            text_rect = text.get_rect(center=(16, 16))
            icon.blit(text, text_rect)
        except:
            pass

        return icon


    def start_transition(self, new_location):
        """Начинает анимацию перехода к новой локации"""
        if self.transition_active:
            return

        self.transition_active = True
        self.transition_target = 255  # затемняем до чёрного
        self.next_location = new_location
        print(f"🌑 Анимация перехода начата -> {new_location}")

    def update_transition(self):
        """Обновляет анимацию перехода"""
        if not self.transition_active:
            return

        # Плавно меняем прозрачность
        if self.transition_alpha < self.transition_target:
            self.transition_alpha = min(self.transition_alpha + self.transition_speed, self.transition_target)
        elif self.transition_alpha > self.transition_target:
            self.transition_alpha = max(self.transition_alpha - self.transition_speed, self.transition_target)

        # Если достигли полного затемнения
        if self.transition_alpha >= 255 and self.transition_target == 255:
            # Меняем локацию
            self.текущая_локация = self.next_location
            self.show_description = True
            self.description_timer = 0
            время.пройти_время(5)
            print(f"🗺️ Переход в {self.next_location} выполнен")

            # Начинаем светлеть
            self.transition_target = 0

        # Если полностью просветлели
        elif self.transition_alpha <= 0 and self.transition_target == 0:
            self.transition_active = False
            self.next_location = None
            print("✨ Анимация перехода завершена")

    def change_location(self, новая_локация):
        print(f"🔴 change_location вызвана! Новая локация: {новая_локация}")
        # Проверяем, не идет ли уже переход (обращаемся к менеджеру видео)
        if self.video_manager.video_transition_active:
            return

        # Вызываем менеджер видео, передавая ему себя (self), чтобы он имел доступ к музыке и режиму
        self.video_manager.play_transition_video(self, "assets/videos/transition.mp4", новая_локация)

    def toggle_fullscreen(self):
        """Переключение между оконным и полноэкранным режимом"""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            print("🖥️ Полноэкранный режим включен")
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            print("🖥️ Оконный режим включен")


    def load_close_icon(self):
        """Загружает иконку закрытия"""
        try:
            self.close_icon = pygame.image.load("assets/ui/close.png").convert_alpha()
            self.close_icon = pygame.transform.scale(self.close_icon, (40, 40))
            print("✅ Иконка закрытия загружена")
        except Exception as e:
            print(f"❌ Ошибка загрузки иконки закрытия: {e}")
            self.close_icon = None

    def load_action_icons(self):
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
                # Масштабируем до 24x24 для размещения на кнопке
                icon = pygame.transform.scale(icon, (24, 24))
                self.action_icons[key] = icon
            except Exception as e:
                print(f"❌ Ошибка загрузки {key}: {e}")
                self.action_icons[key] = None


    def load_backgrounds(self):
        """Загружает фоны для всех локаций"""

        # Список локаций и соответствующих файлов
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
                self.backgrounds[локация] = bg
            except Exception as e:
                print(f"❌ Не удалось загрузить фон для {локация}: {e}")
                # Если фона нет, создаём запасной цветной фон
                bg = pygame.Surface((WIDTH, HEIGHT))
                # Разные цвета для разных локаций
                colors = {
                    "Холл": DARK_BLUE,
                    "Кухня": DARK_RED,
                    "Сад": (20, 50, 20),
                    "Пруд": (20, 30, 50),
                    "Мастерская": (40, 30, 20),
                    "Лестница": (30, 30, 30),
                    "Библиотека": (40, 20, 20),
                    "Коридор": (25, 20, 20),
                    "Темница": (10, 10, 10),
                    "Главный зал": (50, 30, 30)
                }
                bg.fill(colors.get(локация, BLACK))
                self.backgrounds[локация] = bg

    def apply_class(self, название_класса):
        from systems import classes as классы

        # ===== СБРАСЫВАЕМ ИГРОКА ПЕРЕД ПРИМЕНЕНИЕМ КЛАССА =====
        from entities.player import создать_нового_игрока
        self.игрок = создать_нового_игрока()
        # Обновляем инвентарь и бой с новым игроком
        self.inventory = InventorySystem(self.игрок, self.item_icons)
        self.battle = BattleSystem(self.игрок, self)
        # =====================================================

        данные = классы.классы[название_класса]

        # 1. Класс
        self.игрок["класс"] = название_класса

        # 2. Атрибуты
        for атрибут, значение in данные["начальные_атрибуты"].items():
            self.игрок[атрибут] = значение

        # 3. Умения владения оружием
        for умение, значение in данные["начальные_умения"].items():
            self.игрок[умение] = значение

        # 4. Здоровье от стойкости
        self.игрок["макс_здоровье"] = 10 + self.игрок["стойкость"] * 10
        self.игрок["здоровье"] = self.игрок["макс_здоровье"]

        # 5. Стартовое снаряжение
        if данные["стартовое_оружие"]:
            self.inventory.add_item(данные["стартовое_оружие"])
        if данные["стартовая_броня"]:
            self.inventory.add_item(данные["стартовая_броня"])

        for предмет in данные["стартовые_предметы"]:
            self.inventory.add_item(предмет)

        self.игрок["монета"] = 50

        print(f"\n✅ Ты выбрал путь {название_класса}!")
        print(f"   Атрибуты: Сила={self.игрок['сила']}, Стойкость={self.игрок['стойкость']}")

    def show_class_selection(self):
        """Меню выбора класса с кликами мышью"""
        from systems import classes as классы

        clock = pygame.time.Clock()
        классы_список = ["Воин", "Маг", "Вор"]

        # Сохраняем области клика для каждого класса
        class_rects = []

        while True:
            mouse_pos = pygame.mouse.get_pos()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Проверяем клик по карточкам классов
                    for i, rect in enumerate(class_rects):
                        if rect.collidepoint(mouse_pos):
                            print(f"✅ Выбран класс: {классы_список[i]}")
                            return классы_список[i]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None

            # ОТРИСОВКА
            self.screen.fill(BLACK)

            # Заголовок
            title = font_large.render("ВЫБЕРИ КЛАСС", True, GOLD)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

            # Очищаем список областей клика
            class_rects = []

            # Рисуем карточки классов
            for i, название in enumerate(классы_список):
                x = 200 + i * 300
                y = 150
                width = 250
                height = 420  # ← увеличил высоту для атрибутов

                # Создаём область для клика
                class_rect = pygame.Rect(x, y, width, height)
                class_rects.append(class_rect)

                # Проверяем наведение мыши
                if class_rect.collidepoint(mouse_pos):
                    # Подсветка при наведении
                    pygame.draw.rect(self.screen, GOLD, (x - 5, y - 5, width + 10, height + 10), 4)

                # Фон карточки
                color = классы.классы[название]["цвет"]
                pygame.draw.rect(self.screen, color, (x, y, width, height))
                pygame.draw.rect(self.screen, GOLD, (x, y, width, height), 2)

                # Название
                class_name = font_medium.render(название, True, GOLD)
                self.screen.blit(class_name, (x + width // 2 - class_name.get_width() // 2, y + 15))

                # Описание
                описание = классы.классы[название]["описание"]
                desc_text = font_small.render(описание, True, WHITE)
                self.screen.blit(desc_text, (x + width // 2 - desc_text.get_width() // 2, y + 55))

                # Разделитель
                pygame.draw.line(self.screen, GOLD, (x + 20, y + 85), (x + width - 20, y + 85), 1)

                # АТРИБУТЫ (БЕЗ ПРОВЕРКИ ОСНОВНОГО)
                атрибуты = классы.классы[название]["начальные_атрибуты"]
                attr_y = y + 100
                for атр, знач in атрибуты.items():
                    # Название атрибута
                    атр_текст = font_tiny.render(атр.capitalize() + ":", True, WHITE)
                    self.screen.blit(атр_текст, (x + 30, attr_y))

                    # Значение (все одинаковым цветом)
                    знач_текст = font_tiny.render(f"+{знач}", True, WHITE)
                    self.screen.blit(знач_текст, (x + 120, attr_y))

                    attr_y += 20

                # Стартовое оружие
                оружие = классы.классы[название]["стартовое_оружие"]
                оружие_текст = font_tiny.render(f"{оружие}", True, BLOOD_RED)
                self.screen.blit(оружие_текст, (x + 30, attr_y + 5))

                # Стартовая броня
                броня = классы.классы[название]["стартовая_броня"]
                броня_текст = font_tiny.render(f"{броня}", True, DARK_BLUE)
                self.screen.blit(броня_текст, (x + 30, attr_y + 30))

            # Управление
            instr = font_small.render("Кликни по классу мышкой | ESC - назад", True, WHITE)
            self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 60))

            pygame.display.flip()
            clock.tick(30)

    def handle_quests_click(self, pos):
        """Обрабатывает клики в окне квестов"""

        if hasattr(self, 'quest_back') and self.quest_back.collidepoint(pos):
            # Возвращаемся в меню выбора
            self.режим = "quest_trade_menu"
            return

    def start_trade(self):
        """Начинает торговлю в текущей локации"""
        from systems.merchant import торговцы

        данные_торговца = торговцы.get(self.текущая_локация, {})

        # Проверяем, есть ли у торговца квесты
        if данные_торговца.get("квесты", False):
            # Есть квесты - показываем меню выбора
            self.режим = "quest_trade_menu"
            self.quest_trade_animation_progress = 0
            print("📋 Показано меню выбора: Квесты / Торговля")
            return

        # Нет квестов - сразу торговля
        self.режим = "торговля"
        self.trade_location = self.текущая_локация
        self.trade_mode = "buy"
        self.trade_scroll = 0
        self.trade_animation_progress = 0
        self.current_tip = None

        self.trader_name = данные_торговца.get("имя", "Торговец")
        self.trader_greeting = данные_торговца.get("приветствие", "Добро пожаловать!")

        self.trade_goods = {}
        for предмет, данные in данные_торговца.get("товары", {}).items():
            self.trade_goods[предмет] = {"цена": данные["цена"]}


    def draw_quests(self):
        """Отображает окно квестов"""

        # Анимация появления
        if not hasattr(self, 'quest_animation_progress'):
            self.quest_animation_progress = 0

        if self.quest_animation_progress < 1:
            self.quest_animation_progress += 0.08
            if self.quest_animation_progress > 1:
                self.quest_animation_progress = 1

        # Параметры панели
        panel_width = 600
        panel_height = 500
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        # Затемнение
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Заголовок
        title = font_large.render("КВЕСТЫ", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 20))

        # Информация
        активные = len(self.игрок.get("активные_квесты", []))
        завершенные = len(self.игрок.get("завершенные_квесты", []))
        info_text = font_small.render(f"Активных: {активные}  |  Завершено: {завершенные}", True, WHITE)
        self.screen.blit(info_text, (panel_x + panel_width // 2 - info_text.get_width() // 2, panel_y + 60))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 20, panel_y + 90),
                         (panel_x + panel_width - 20, panel_y + 90), 2)

        # Активные квесты
        y = panel_y + 105
        активные_квесты = self.игрок.get("активные_квесты", [])

        if активные_квесты:
            for квест_id in активные_квесты:
                квест = self.quest_system.получить_квест(квест_id)
                if not квест:
                    continue

                # Название
                name_text = font_medium.render(f"📜 {квест['название']}", True, GOLD)
                self.screen.blit(name_text, (panel_x + 20, y))
                y += 25

                # Описание
                desc_text = font_small.render(квест['описание'], True, WHITE)
                self.screen.blit(desc_text, (panel_x + 30, y))
                y += 22

                # Прогресс
                прогресс_строки = self.quest_system.получить_прогресс_строку(квест_id)
                for строка in прогресс_строки:
                    prog_text = font_tiny.render(f"  • {строка}", True, HEALTH_YELLOW)
                    self.screen.blit(prog_text, (panel_x + 30, y))
                    y += 18

                y += 10
        else:
            empty_text = font_medium.render("Нет активных квестов", True, GRAY)
            self.screen.blit(empty_text, (panel_x + panel_width // 2 - empty_text.get_width() // 2, panel_y + 200))

        # Кнопка "Назад"
        back_rect = pygame.Rect(panel_x + panel_width // 2 - 80, panel_y + panel_height - 50, 160, 40)
        mouse_pos = pygame.mouse.get_pos()

        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, back_rect)
            back_text = font_medium.render("НАЗАД", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, back_rect)
            pygame.draw.rect(self.screen, GOLD, back_rect, 2)
            back_text = font_medium.render("НАЗАД", True, WHITE)

        back_text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
        back_text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
        self.screen.blit(back_text, (back_text_x, back_text_y))

        self.quest_back = back_rect

    def show_quest_trade_menu(self):
        """Показывает меню выбора между квестами и торговлей"""
        self.режим = "quest_trade_menu"
        self.quest_trade_menu_active = True
        self.quest_trade_animation_progress = 0
        print("📋 Показано меню выбора: Квесты / Торговля")

    def handle_quest_trade_click(self, pos):
        """Обрабатывает клики в меню выбора между квестами и торговлей"""
        print(f"🔄 handle_quest_trade_click ВЫЗВАНА! pos={pos}")  # 👈 ДОБАВЬТЕ
        print(f"   Кнопок в self.quest_trade_buttons: {len(self.quest_trade_buttons)}")  # 👈 ДОБАВЬТЕ

        for action, rect in self.quest_trade_buttons:
            print(f"   Проверяем: {action}, rect={rect}")  # 👈 ДОБАВЬТЕ
            if rect.collidepoint(pos):
                print(f"   ✅ КЛИК ПО: {action}")  # 👈 ДОБАВЬТЕ
                if action == "quests":
                    print("📜 Открываем квесты")
                    self.режим = "квесты"
                    self.quest_animation_progress = 0
                    return
                elif action == "trade":
                    print("💰 Начинаем торговлю")
                    from systems.merchant import торговцы
                    данные_торговца = торговцы.get(self.текущая_локация, {})

                    self.режим = "торговля"
                    self.trade_location = self.текущая_локация
                    self.trade_mode = "buy"
                    self.trade_scroll = 0
                    self.trade_animation_progress = 0
                    self.current_tip = None

                    self.trader_name = данные_торговца.get("имя", "Торговец")
                    self.trader_greeting = данные_торговца.get("приветствие", "Добро пожаловать!")

                    self.trade_goods = {}
                    for предмет, данные in данные_торговца.get("товары", {}).items():
                        self.trade_goods[предмет] = {"цена": данные["цена"]}
                    return
                elif action == "back":
                    print("🔙 Возвращаемся в игру")
                    self.режим = "игра"
                    return

        print("   ❌ Ни одна кнопка не совпала!")  # 👈 ДОБАВЬТЕ

    def start_craft(self):
        """Начинает крафт в мастерской"""
        self.режим = "крафт"

        # Получаем рецепты из модуля верстак
        self.craft_recipes = верстак.рецепты.copy()

        # Создаем список рецептов для отображения
        self.craft_items = []
        self.craft_buttons = []


    def learn_skill(self, skill_id):
        print(f"\n📚 LEARN_SKILL вызвана! skill_id: {skill_id}")

        skill = SkillLoader.get_skill_by_id(self.skills_data, skill_id)
        if not skill:
            self.add_to_log(f"❌ Навык {skill_id} не найден!")
            return

        print(f"   Название: {skill.get('название')}")
        print(f"   Тип: {skill.get('тип')}")
        print(f"   Эффект: {skill.get('эффект')}")
        print(f"   Значение: {skill.get('значение')}")

        if skill_id in self.игрок.get("выученные_навыки", []):
            self.add_to_log(f"❌ Уже выучено!")
            return

        if self.игрок.get("очки_навыков", 0) <= 0:
            self.add_to_log(f"❌ Нет очков навыков!")
            return

        if "выученные_навыки" not in self.игрок:
            self.игрок["выученные_навыки"] = []

        self.игрок["выученные_навыки"].append(skill_id)
        self.игрок["очки_навыков"] -= 1
        self.add_to_log(f"✅ Выучен навык: {skill['название']}!")

        # ===== ПРИМЕНЯЕМ ЭФФЕКТ НАВЫКА (ЕСЛИ ПАССИВНЫЙ) =====
        if skill["тип"] == "пассивный":
            print(f"   → Применяем пассивный навык!")

            # ИСПОЛЬЗУЕМ СУЩЕСТВУЮЩУЮ ФУНКЦИЮ из player.py
            from entities.player import игрок as глобальный_игрок, добавить_пассивный_бонус

            # Синхронизация
            глобальный_игрок.update(self.игрок)

            # Применяем эффект
            эффект = skill.get('эффект', '')
            значение = skill.get('значение', 0)

            if эффект:
                добавить_пассивный_бонус(эффект, значение)
                print(f"   ✅ Применён бонус: {эффект} +{значение}")

                # Обновляем здоровье если нужно
                if эффект in ['здоровье', 'hp_bonus', 'стойкость', 'endurance_bonus']:
                    self.inventory.update_max_health()
            else:
                print(f"   ⚠️ У навыка нет эффекта!")

            # Синхронизация обратно
            self.игрок.update(глобальный_игрок)

        else:
            print(f"   → Навык НЕ пассивный (тип: {skill['тип']})")

        # Обновляем интерфейс
        self.draw_status()
        pygame.display.flip()

    def update_max_health(self):
        """Обёртка для вызова метода инвентаря"""
        self.inventory.update_max_health()


    def _create_skill_icon(self, symbol):
        """Создаёт иконку для навыка"""
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)

        # Круглый фон
        pygame.draw.circle(icon, (60, 60, 80), (16, 16), 14)
        pygame.draw.circle(icon, GOLD, (16, 16), 14, 1)

        # Символ
        try:
            font = pygame.font.Font(None, 24)
            text = font.render(symbol, True, GOLD)
            text_rect = text.get_rect(center=(16, 16))
            icon.blit(text, text_rect)
        except:
            pass

        return icon

    def handle_skills_click(self, pos):
        # Переключение вкладок
        if hasattr(self, 'prof_tab_rect') and self.prof_tab_rect.collidepoint(pos):
            self.current_skill_tab = "prof"
            return

        if hasattr(self, 'combat_tab_rect') and self.combat_tab_rect.collidepoint(pos):
            self.current_skill_tab = "combat"
            return

        # Кнопка "Назад"
        if hasattr(self, 'skill_back_button') and self.skill_back_button.collidepoint(pos):
            if hasattr(self, 'previous_mode') and self.previous_mode == "эксплорейшн":
                self.режим = "эксплорейшн"
            else:
                self.режим = "игра"
            return

        # Кнопки прокачки
        if hasattr(self, 'skill_buttons'):
            for item, btn_rect in self.skill_buttons:
                if btn_rect.collidepoint(pos):
                    if self.current_skill_tab == "prof":
                        self.upgrade_skill(item)
                    else:
                        self.learn_skill(item)
                    return

    def handle_click(self, pos):
        """Обработка кликов мыши"""
        if self.режим != "игра":
            return
        if self.обыск_активен:
            return

        локация = локации.локации[self.текущая_локация]

        for action, rect in self.buttons:
            if rect.collidepoint(pos):
                print(f"Кнопка: {action}")

                if action == "й":
                    # Проверяем, можно ли обыскивать эту локацию
                    if локация.get("хаб", False):
                        self.add_to_log("В убежище нечего искать...")
                        break

                    if self.текущая_локация == "Зачарованный лес":
                        self.add_to_log("В лесу нужно нажать 'Исследовать лес'!")
                        break

                        # ===== ТРАТИМ СЫТОСТЬ И ЖАЖДУ (НЕ БЛОКИРУЕМ ОБЫСК) =====
                    успех, сообщение = потратить_ресурсы(self.игрок, сытость_цена=3, жажда_цена=5)
                    self.add_to_log(сообщение)

                    # ===== ПРОВЕРЯЕМ ГОЛОД/ЖАЖДУ =====
                    урон, сообщение_голод = проверить_голод(self.игрок)
                    if урон:
                        self.add_to_log(сообщение_голод)
                        if self.игрок["здоровье"] <= 0:
                            self.игрок_умер()
                            break

                    # ===== ЗАПУСКАЕМ ШКАЛУ ПРОГРЕССА =====
                    self.запустить_шкалу_обыска()
                    self.draw_status()
                    pygame.display.flip()
                    return  # ← ВЫХОДИМ, ЧТОБЫ НЕ ВЫПОЛНЯТЬ ОБЫСК СРАЗУ

                elif action == "ц":
                    self.inventory_animation_progress = 0
                    self.режим = "инвентарь"

                elif action == "к":
                    show_save_menu(self)

                elif action == "у":
                    self.режим = "карта"

                elif action == "т" and локация.get("торговец", False):
                    self.start_trade()

                elif action == "в" and локация.get("верстак", False):
                    self.start_craft()

                elif action == "в_пруд":
                    self.add_to_log("Ты смотришь в тёмную воду...")


                elif action == "с":
                    if self.show_exit_dialog():
                        # Возвращаемся в главное меню
                        self.игра_активна = False
                        # Перезапускаем игру с главного меню
                        self.__init__()
                        return

                elif action == "о":
                    self.skills_animation_progress = 0
                    self.режим = "обучение"

                elif action == "о_лес":
                    # ===== 👇 ПРОВЕРКА СЫТОСТИ И ЖАЖДЫ ДЛЯ ВХОДА В ЛЕС =====
                    успех, сообщение = потратить_ресурсы(self.игрок, сытость_цена=2, жажда_цена=2)
                    if not успех:
                        self.add_to_log(сообщение)
                        break
                    else:
                        self.add_to_log(сообщение)

                    урон, сообщение_голод = игрок.проверить_голод(self.игрок)
                    if урон:
                        self.add_to_log(сообщение_голод)
                        if self.игрок["здоровье"] <= 0:
                            self.игрок_умер()
                            break
                    # =====================================================

                    print("🌳 Вход в Зачарованный лес!")
                    self.текущая_локация = "Зачарованный лес"
                    self.dungeon.init_forest()
                    self.режим = "эксплорейшн"
                    self.exploration_in_battle = False

                elif action == "о_склеп":
                    # ===== 👇 ПРОВЕРКА СЫТОСТИ И ЖАЖДЫ ДЛЯ ВХОДА В СКЛЕП =====

                    успех, сообщение = потратить_ресурсы(self.игрок, сытость_цена=2, жажда_цена=2)
                    if not успех:
                        self.add_to_log(сообщение)
                        break
                    else:
                        self.add_to_log(сообщение)

                    урон, сообщение_голод = игрок.проверить_голод()
                    if урон:
                        self.add_to_log(сообщение_голод)
                        if self.игрок["здоровье"] <= 0:
                            self.игрок_умер()
                            break
                    # =====================================================

                    print("💀 Вход в Древний склеп!")
                    self.текущая_локация = "Древний склеп"
                    self.dungeon.init_crypt()
                    self.режим = "эксплорейшн"
                    self.exploration_in_battle = False

                elif action == "о_хаб":
                    self.rest_in_hub()

                elif action == "я":
                    self.open_chest()

                break

    def show_exit_dialog(self):
        """Показывает диалог выхода с подсветкой кнопок при наведении"""

        # Затемнение фона
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (0, 0))

        # Панель диалога
        panel_width = 320
        panel_height = 280
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Текст вопроса
        question = font_medium.render("СОХРАНИТЬ ИГРУ?", True, GOLD)
        q_x = panel_x + panel_width // 2 - question.get_width() // 2
        self.screen.blit(question, (q_x, panel_y + 30))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 20, panel_y + 70),
                         (panel_x + panel_width - 20, panel_y + 70), 2)

        # Параметры кнопок
        button_width = 260
        button_height = 45
        button_spacing = 15

        start_y = panel_y + 95

        save_rect = pygame.Rect(panel_x + (panel_width - button_width) // 2,
                                start_y, button_width, button_height)
        exit_rect = pygame.Rect(panel_x + (panel_width - button_width) // 2,
                                start_y + button_height + button_spacing,
                                button_width, button_height)
        cancel_rect = pygame.Rect(panel_x + (panel_width - button_width) // 2,
                                  start_y + (button_height + button_spacing) * 2,
                                  button_width, button_height)

        # Отрисовка кнопок
        mouse_pos = pygame.mouse.get_pos()

        # Кнопка "СОХРАНИТЬ"
        if save_rect.collidepoint(mouse_pos):
            # Подсветка при наведении
            pygame.draw.rect(self.screen, GOLD, save_rect)
            save_text = font_medium.render("СОХРАНИТЬ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, save_rect)
            pygame.draw.rect(self.screen, GOLD, save_rect, 2)
            save_text = font_medium.render("СОХРАНИТЬ", True, WHITE)

        text_x = save_rect.x + save_rect.width // 2 - save_text.get_width() // 2
        text_y = save_rect.y + save_rect.height // 2 - save_text.get_height() // 2
        self.screen.blit(save_text, (text_x, text_y))

        # Кнопка "ВЫЙТИ"
        if exit_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, exit_rect)
            exit_text = font_medium.render("ВЫЙТИ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, exit_rect)
            pygame.draw.rect(self.screen, GOLD, exit_rect, 2)
            exit_text = font_medium.render("ВЫЙТИ", True, WHITE)

        text_x = exit_rect.x + exit_rect.width // 2 - exit_text.get_width() // 2
        text_y = exit_rect.y + exit_rect.height // 2 - exit_text.get_height() // 2
        self.screen.blit(exit_text, (text_x, text_y))

        # Кнопка "ОТМЕНА"
        if cancel_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, cancel_rect)
            cancel_text = font_medium.render("ОТМЕНА", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, cancel_rect)
            pygame.draw.rect(self.screen, GOLD, cancel_rect, 2)
            cancel_text = font_medium.render("ОТМЕНА", True, WHITE)

        text_x = cancel_rect.x + cancel_rect.width // 2 - cancel_text.get_width() // 2
        text_y = cancel_rect.y + cancel_rect.height // 2 - cancel_text.get_height() // 2
        self.screen.blit(cancel_text, (text_x, text_y))

        pygame.display.flip()

        # Ожидание выбора
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if save_rect.collidepoint(event.pos):
                            show_save_menu_for_exit(self)
                            return True
                        elif exit_rect.collidepoint(event.pos):
                            return True
                        elif cancel_rect.collidepoint(event.pos):
                            return False
                elif event.type == pygame.MOUSEMOTION:
                    # При движении мыши перерисовываем панель
                    # Рекурсивно вызываем себя для обновления подсветки
                    return self.show_exit_dialog()

            clock.tick(FPS)

        return False

    def rest_in_hub(self):
        """Отдых в убежище — полное восстановление (только 1 раз в день)"""

        # Получаем текущий день
        текущий_день = время.получить_день()

        # Проверяем, отдыхал ли игрок сегодня
        if hasattr(self, 'last_rest_day') and self.last_rest_day == текущий_день:
            self.add_to_log("Ты уже отдыхал сегодня! Отдохнуть можно только раз в день.")
            print("❌ Отдых недоступен - уже отдыхал сегодня")
            return

        # Отдыхаем
        self.игрок["здоровье"] = self.игрок["макс_здоровье"]
        self.inventory.update_max_health()

        if "мана" in self.игрок:
            self.игрок["мана"] = self.игрок["макс_мана"]

        # Запоминаем день отдыха
        self.last_rest_day = текущий_день

        # Проходит время (1 час)
        время.пройти_время(60)

        self.add_to_log("Ты отдохнул в убежище и полностью восстановил силы!")
        print(f"🛌 Игрок отдохнул в убежище. День отдыха: {текущий_день}")

        # ДИАГНОСТИКА
        print("=== ПОСЛЕ ОТДЫХА В ХАБЕ ===")
        print(f"❤️ Здоровье: {self.игрок['здоровье']} / {self.игрок['макс_здоровье']}")
        print(f"💙 Мана:     {self.игрок['мана']} / {self.игрок['макс_мана']}")
        print(f"📅 День отдыха: {self.last_rest_day}")

    def open_chest(self):
        """Открыть сундук — показать окно хранилища"""
        self.режим = "сундук"

        # Если сундук ещё не инициализирован, создаём
        if not hasattr(self, 'chest_inventory'):
            self.chest_inventory = []  # список предметов в сундуке

    def запустить_шкалу_обыска(self):
        """Запускает анимацию шкалы прогресса обыска"""
        self.обыск_активен = True
        self.обыск_прогресс = 0
        self.обыск_таймер = 0
        self.обыск_длительность = 60  # 3 секунды при 60 FPS
        print("🔍 Шкала обыска запущена!")

    def выполнить_обыск(self):
        """Выполняет обыск (вызывается после завершения шкалы)"""
        print("🔍 ВЫПОЛНЯЕМ ОБЫСК")

        from systems import randomizer as рандомайзер
        локация_данные = локации.локации[self.текущая_локация]
        событие = рандомайзер.выбрать_событие(локация_данные)

        if событие == "враг" and локация_данные.get("возможные_враги", []):
            враг = рандомайзер.выбрать_врага(локация_данные["возможные_враги"])
            self.add_to_log(f"Нападает: {враг.replace('_', ' ')}!")
            self.start_battle(враг)

        elif событие == "предмет" and локация_данные.get("возможные_предметы", {}):
            предмет = рандомайзер.выбрать_предмет(локация_данные["возможные_предметы"])
            if предмет:
                self.inventory.add_item(предмет)
                self.add_to_log(f"Ты нашёл: {предмет}!")

                # 👇 Обновляем ежедневные квесты (находка предмета)
                if hasattr(self, 'quest_system') and hasattr(self, 'игрок'):
                    if "ежедневные_квесты" in self.игрок:
                        # Проверяем тип предмета
                        from entities import items as предметы
                        данные = предметы.предметы.get(предмет, {})
                        тип_предмета = данные.get("тип", "")

                        # Если это ресурс - обновляем квест "Собиратель дня"
                        if тип_предмета == "ресурс":
                            завершенные = self.quest_system.обновить_ежедневный_прогресс(
                                self.игрок,
                                "найти",
                                предмет
                            )
                            if завершенные:
                                for квест_id in завершенные:
                                    for q in self.quest_system.ежедневные_квесты:
                                        if q.get("id") == квест_id:
                                            self.add_to_log(f"📅 Ежедневный квест выполнен: {q['название']}")
                                            break
        else:
            self.add_to_log("Здесь ничего нет...")

        время.пройти_время(10)

    def draw_обыск_шкала(self):
        """Рисует шкалу прогресса обыска"""
        if not self.обыск_активен:
            return

        # Параметры шкалы
        ширина = 400
        высота = 30
        x = self.обыск_x
        y = self.обыск_y

        # ===== ЗАТЕМНЕНИЕ ФОНА =====
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        # ===== ФОН ШКАЛЫ =====
        bg_rect = pygame.Rect(x, y, ширина, высота)
        pygame.draw.rect(self.screen, (40, 40, 60), bg_rect)
        pygame.draw.rect(self.screen, GOLD, bg_rect, 2)

        # ===== ЗАПОЛНЕНИЕ ШКАЛЫ =====
        if self.обыск_прогресс > 0:
            заполнение = int(ширина * self.обыск_прогресс)
            fill_rect = pygame.Rect(x + 2, y + 2, заполнение - 4, высота - 4)

            if self.обыск_прогресс < 0.5:
                r = 255
                g = int(255 * (self.обыск_прогресс * 2))
                b = 0
            else:
                r = int(255 * (1 - (self.обыск_прогресс - 0.5) * 2))
                g = 255
                b = 0

            pygame.draw.rect(self.screen, (r, g, b), fill_rect)

        # ===== ТЕКСТ =====
        title_text = font_medium.render("ОБЫСК", True, GOLD)
        title_x = x + ширина // 2 - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, y - 35))

        процент = int(self.обыск_прогресс * 100)
        percent_text = font_small.render(f"{процент}%", True, WHITE)
        percent_x = x + ширина // 2 - percent_text.get_width() // 2
        percent_y = y + высота // 2 - percent_text.get_height() // 2
        self.screen.blit(percent_text, (percent_x, percent_y))

        # Анимированная иконка
        if self.обыск_прогресс < 0.5:
            icon = ""
        elif self.обыск_прогресс < 0.8:
            icon = ""
        else:
            icon = ""

        icon_text = font_medium.render(icon, True, GOLD)
        self.screen.blit(icon_text, (x - 40, y + 2))

        # Свечение
        glow_rect = pygame.Rect(x - 4, y - 4, ширина + 8, высота + 8)
        glow_alpha = int(50 + 100 * abs(pygame.time.get_ticks() % 500 - 250) / 250)
        pygame.draw.rect(self.screen, (GOLD[0], GOLD[1], GOLD[2], glow_alpha), glow_rect, 2)



    def show_save_confirmation(self, slot):
        """Показывает подтверждение сохранения"""
        waiting = True

        while waiting:
            # Затемнение фона
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (0, 0))

            # Панель подтверждения
            panel_width = 400
            panel_height = 200
            panel_x = WIDTH // 2 - panel_width // 2
            panel_y = HEIGHT // 2 - panel_height // 2

            # Фон панели
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
            pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

            # Текст
            title = font_medium.render("ПОДТВЕРЖДЕНИЕ", True, GOLD)
            title_x = panel_x + panel_width // 2 - title.get_width() // 2
            self.screen.blit(title, (title_x, panel_y + 20))

            question = font_small.render(f"Сохранить игру в слот {slot}?", True, WHITE)
            question_x = panel_x + panel_width // 2 - question.get_width() // 2
            self.screen.blit(question, (question_x, panel_y + 70))

            # Кнопки
            yes_rect = pygame.Rect(panel_x + 70, panel_y + 120, 100, 40)
            no_rect = pygame.Rect(panel_x + panel_width - 170, panel_y + 120, 100, 40)

            mouse_pos = pygame.mouse.get_pos()

            # Кнопка ДА
            if yes_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GOLD, yes_rect)
                yes_text = font_medium.render("ДА", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, yes_rect)
                pygame.draw.rect(self.screen, GOLD, yes_rect, 2)
                yes_text = font_medium.render("ДА", True, WHITE)

            text_x = yes_rect.x + yes_rect.width // 2 - yes_text.get_width() // 2
            text_y = yes_rect.y + yes_rect.height // 2 - yes_text.get_height() // 2
            self.screen.blit(yes_text, (text_x, text_y))

            # Кнопка НЕТ
            if no_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GOLD, no_rect)
                no_text = font_medium.render("НЕТ", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, no_rect)
                pygame.draw.rect(self.screen, GOLD, no_rect, 2)
                no_text = font_medium.render("НЕТ", True, WHITE)

            text_x = no_rect.x + no_rect.width // 2 - no_text.get_width() // 2
            text_y = no_rect.y + no_rect.height // 2 - no_text.get_height() // 2
            self.screen.blit(no_text, (text_x, text_y))

            pygame.display.flip()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if yes_rect.collidepoint(event.pos):
                            # Сохраняем в выбранный слот
                            сохранение.сохранить_игру(self.игрок, self.текущая_локация, self.chest_inventory, slot)
                            self.add_to_log(f"Игра сохранена в слот {slot}!")
                            waiting = False
                        elif no_rect.collidepoint(event.pos):
                            waiting = False

            clock.tick(FPS)


    def show_message(self, text, duration=60):
        """Показывает сообщение на экране"""
        message_surface = font_medium.render(text, True, BLOOD_RED)
        message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        self.screen.blit(message_surface, message_rect)
        pygame.display.flip()
        pygame.time.wait(duration * 10)  # duration в кадрах (60 кадров = 1 сек)

    def run(self):
        """Главный игровой цикл"""

        # ===== ЗАГРУЖАЕМ ЕЖЕДНЕВНЫЕ КВЕСТЫ =====  # 👈 ДОБАВЬТЕ ЭТОТ БЛОК
        if hasattr(self, 'quest_system') and hasattr(self, 'игрок'):
            self.quest_system.загрузить_ежедневные_квесты(self.игрок)

        # Для отслеживания смены дня (для системы отдыха)
        предыдущий_день = время.получить_день()

        while self.игра_активна:

            # ========== ПРОВЕРКА СМЕРТИ ==========
            if self.игрок["здоровье"] <= 0:
                self.игрок_умер()
                continue

            # ========== ОБРАБОТКА СОБЫТИЙ ==========
            for event in pygame.event.get():

                # --- Выход из игры ---
                if event.type == pygame.QUIT:
                    self.игра_активна = False

                # --- Клавиатура ---
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

                # --- Клики мыши ---
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()

                        if self.режим == "игра":
                            self.handle_click(mouse_pos)
                            if hasattr(self, 'loot_button') and self.loot_button.collidepoint(mouse_pos):
                                self.close_loot_panel()



                        elif self.режим == "эксплорейшн":
                            # Проверяем клик по кнопке "ЗАБРАТЬ" на панели лута
                            if hasattr(self, 'loot_button') and self.loot_button.collidepoint(mouse_pos):
                                self.close_loot_panel()
                            # Проверяем клик по кнопке выхода из леса
                            if hasattr(self, 'exploration_exit_button') and self.exploration_exit_button.collidepoint(
                                    mouse_pos):
                                print("🚪 Выход из леса")
                                self.режим = "игра"
                                self.текущая_локация = "Сад"
                                self.in_dungeon = False
                                if hasattr(self, 'exploration_zone'):
                                    delattr(self, 'exploration_zone')

                            # Проверяем клики по кнопкам действий
                            for action, rect in self.buttons:
                                if rect.collidepoint(mouse_pos):
                                    print(f"🎯 Нажата кнопка в лесу: {action}")

                                    if action == "ц":  # Инвентарь
                                        print("📦 Открываем инвентарь")
                                        self.inventory_animation_progress = 0
                                        self.режим = "инвентарь"
                                        self.previous_mode = "эксплорейшн"
                                    elif action == "у":  # Карта
                                        print("🗺️ Открываем карту")
                                        self.режим = "карта"
                                        self.previous_mode = "эксплорейшн"
                                    elif action == "о":  # Навыки
                                        print("📚 Открываем навыки")
                                        self.skills_animation_progress = 0
                                        self.режим = "обучение"
                                        self.previous_mode = "эксплорейшн"
                                    elif action == "к":  # Сохранить
                                        print("💾 Сохраняем игру")
                                        show_save_menu(self)
                                    elif action == "с":  # Выход
                                        print("🚪 Выход в главное меню")
                                        if self.show_exit_dialog():
                                            self.игра_активна = False
                                    break


                        elif self.режим == "инвентарь":
                            handle_inventory_click(self, mouse_pos)
                        elif self.режим == "бой":
                            self.handle_battle_click(mouse_pos)
                        elif self.режим == "торговля":
                            handle_trade_click(self, mouse_pos)
                        elif self.режим == "quest_trade_menu":  # 👈 ЭТОЙ СТРОКИ НЕТ!
                            self.handle_quest_trade_click(mouse_pos)
                        elif self.режим == "квесты":  # 👈 ДОБАВЬТЕ ЭТУ СТРОКУ!
                            self.handle_quests_click(mouse_pos)
                        elif self.режим == "крафт":
                            handle_craft_click(self, mouse_pos)
                        elif self.режим == "карта":
                            handle_map_click(self, mouse_pos)
                        elif self.режим == "обучение":
                            self.handle_skills_click(mouse_pos)
                        elif self.режим == "сундук":
                            handle_chest_click(self, mouse_pos)

                # --- Прокрутка колесиком ---
                elif event.type == pygame.MOUSEWHEEL:
                    self._handle_scroll(event.y)

            # ========== СМЕНА ДНЯ (сброс отдыха) ==========
            текущий_день = время.получить_день()
            if текущий_день != предыдущий_день:
                if hasattr(self, 'last_rest_day'):
                    self.last_rest_day = None
                self.add_to_log(f"Наступил новый день! (День {текущий_день})")
                print(f"🌅 Новый день! Отдых снова доступен.")
                предыдущий_день = текущий_день

            # ===== ОБНОВЛЯЕМ ШКАЛУ ОБЫСКА =====
            if self.обыск_активен:
                self.обыск_таймер += 1
                self.обыск_прогресс = self.обыск_таймер / self.обыск_длительность

                if self.обыск_прогресс >= 1:
                    self.обыск_активен = False
                    self.обыск_прогресс = 1
                    self.выполнить_обыск()

            # ===== ОБНОВЛЯЕМ АНИМАЦИЮ ПЕРЕХОДА =====
            self.update_transition()
            self.video_manager.update_transition_video(self)
            self.update_battle_animation()

            # ========== ОТРИСОВКА ==========
            if self.режим == "игра":
                draw_location(self)
                draw_status(self)
                draw_actions(self)
                self.draw_log_panel()
                self.draw_battle_start_animation()
                self.draw_loot_panel()
                draw_quest_tracker(self)
                draw_daily_quest_tracker(self)
                self.draw_обыск_шкала()

            elif self.режим == "инвентарь":
                draw_inventory(self)

            elif self.режим == "обучение":
                draw_skills_menu(self)

            elif self.режим == "бой":
                draw_battle(self)
                self.draw_battle_start_animation()

            elif self.режим == "торговля":
                draw_trade(self)

            elif self.режим == "quest_trade_menu":  # 👈 ДОБАВЬТЕ ЭТУ СТРОКУ!
                draw_quest_trade_menu(self)

            elif self.режим == "квесты":
                self.draw_quests()

            elif self.режим == "крафт":
                draw_craft(self)

            elif self.режим == "карта":
                draw_map(self)

            elif self.режим == "сундук":
                draw_chest(self)

            elif self.режим == "эксплорейшн":
                if hasattr(self, 'exploration_zone'):
                    self.dungeon.handle()
                    self.draw_loot_panel()
                else:
                    print("❌ exploration_zone не существует!")
                    self.режим = "игра"

            # Обновление экрана
            pygame.display.flip()
            clock.tick(FPS)

    def show_exit_confirmation(self):
        """Показывает диалог подтверждения выхода из игры"""

        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Панель диалога
        panel_width = 400
        panel_height = 200
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Текст
        question = font_medium.render("Выйти из игры?", True, GOLD)
        q_x = panel_x + panel_width // 2 - question.get_width() // 2
        self.screen.blit(question, (q_x, panel_y + 30))

        sub_text = font_small.render("Жду тебя снова", True, WHITE)
        sub_x = panel_x + panel_width // 2 - sub_text.get_width() // 2
        self.screen.blit(sub_text, (sub_x, panel_y + 70))

        # Кнопки
        yes_rect = pygame.Rect(panel_x + 50, panel_y + 120, 120, 40)
        no_rect = pygame.Rect(panel_x + panel_width - 170, panel_y + 120, 120, 40)

        mouse_pos = pygame.mouse.get_pos()

        # Кнопка ДА
        if yes_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, yes_rect)
            yes_text = font_medium.render("ДА", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, yes_rect)
            pygame.draw.rect(self.screen, GOLD, yes_rect, 2)
            yes_text = font_medium.render("ДА", True, WHITE)
        self.screen.blit(yes_text, (yes_rect.x + 45, yes_rect.y + 8))

        # Кнопка НЕТ
        if no_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, no_rect)
            no_text = font_medium.render("НЕТ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, no_rect)
            pygame.draw.rect(self.screen, GOLD, no_rect, 2)
            no_text = font_medium.render("НЕТ", True, WHITE)
        self.screen.blit(no_text, (no_rect.x + 40, no_rect.y + 8))

        pygame.display.flip()

        # Ожидание выбора
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if yes_rect.collidepoint(event.pos):
                            return True
                        elif no_rect.collidepoint(event.pos):
                            return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
            clock.tick(FPS)

        return False

    def _handle_scroll(self, y):
        """Обработка прокрутки колесиком мыши (вынесено для читаемости)"""

        # ----- Торговля -----
        if self.режим == "торговля":
            if self.trade_mode == "sell":
                # Подсчёт предметов для продажи
                подсчёт = {}
                for предмет in self.игрок["инвентарь"]:
                    подсчёт[предмет] = подсчёт.get(предмет, 0) + 1

                max_scroll = max(0, len(подсчёт) - 7)

                if y > 0:  # Прокрутка вверх
                    self.trade_scroll = max(0, self.trade_scroll - 1)
                else:  # Прокрутка вниз
                    self.trade_scroll = min(max_scroll, self.trade_scroll + 1)

            elif self.trade_mode == "buy":
                max_scroll = max(0, len(self.trade_goods) - 7)

                if y > 0:
                    self.trade_scroll = max(0, self.trade_scroll - 1)
                else:
                    self.trade_scroll = min(max_scroll, self.trade_scroll + 1)

        # ----- Крафт -----
        elif self.режим == "крафт":
            if hasattr(self, 'craft_scroll'):
                # Получаем рецепты для текущей категории
                рецепты_категории = []
                for recipe_name in self.craft_categories[self.craft_category]:
                    if recipe_name in self.craft_recipes:
                        рецепты_категории.append(recipe_name)

                max_scroll = max(0, len(рецепты_категории) - 7)

                if y > 0:
                    self.craft_scroll = max(0, self.craft_scroll - 1)
                else:
                    self.craft_scroll = min(max_scroll, self.craft_scroll + 1)

    def show_intro(self):
        """Показывает вступительную заставку с историей"""

        # Затемняем экран
        self.screen.fill(BLACK)

        # Разбиваем текст на строки
        intro_text = [
            "Ты родился в маленькой деревне, где каждый день был похож на другой.",
            "Однажды ты решил, что достоин большего. Ты бросил всё и отправился в путь.",
            "Но мир оказался жесток. Тебя гнали из каждого селения.",
            "Ты стал изгоем.",
            "",
            "В тот вечер ты зашёл в таверну, чтобы согреться и забыться.",
            "Карты — твоё последнее утешение. Но удача отвернулась от тебя.",
            "Ты проиграл всё, что имел. А когда денег не осталось,",
            "разъярённые игроки решили отыграться на твоей шкуре.",
            "",
            "Ты бежал в ночь, не разбирая дороги, пока не наткнулся на старый замок.",
            "Дверь со скрипом открылась, и ты скользнул внутрь, захлопнув её за собой...",
            "",
            "Теперь ты здесь. В этом тёмном, забытом месте.",
            "Найди ли ты выход? Или останешься здесь навсегда?"
        ]

        # Параметры отображения
        font_intro = pygame.font.Font(None, 28)
        y_offset = HEIGHT // 2 - 200
        line_height = 35

        # Флаг пропуска анимации
        skip_animation = False
        current_line_index = 0

        # Сначала показываем текст с анимацией, пока не пропустят
        for i, line in enumerate(intro_text):
            if skip_animation:
                break

            if line:
                # Печатаем строку по буквам
                current_text = ""
                for char in line:
                    # Проверяем события во время печати
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                            skip_animation = True
                            break

                    if skip_animation:
                        break

                    current_text += char
                    text_surface = font_intro.render(current_text, True, WHITE)
                    text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset + i * line_height))

                    # Очищаем область под строку (только текущую строку)
                    clear_rect = pygame.Rect(0, text_rect.y - 10, WIDTH, line_height + 20)
                    pygame.draw.rect(self.screen, BLACK, clear_rect)

                    self.screen.blit(text_surface, text_rect)
                    pygame.display.flip()

                    # Задержка
                    clock.tick(30)

                current_line_index = i

                # Пауза после строки (только если не пропущено)
                if not skip_animation:
                    pause_until = pygame.time.get_ticks() + 300
                    while pygame.time.get_ticks() < pause_until:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                return False
                            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                                skip_animation = True
                                break
                        clock.tick(60)
            else:
                # Пустая строка
                current_line_index = i

        # Если пропустили анимацию - показываем весь текст сразу
        if skip_animation:
            # Полностью очищаем экран
            self.screen.fill(BLACK)

            # Рисуем все строки целиком
            for i, line in enumerate(intro_text):
                if line:
                    text_surface = font_intro.render(line, True, WHITE)
                    text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset + i * line_height))
                    self.screen.blit(text_surface, text_rect)

            pygame.display.flip()

            # Небольшая пауза, чтобы игрок увидел текст
            pause_until = pygame.time.get_ticks() + 500
            while pygame.time.get_ticks() < pause_until:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                clock.tick(60)

        # Ждём нажатия любой клавиши или клика
        waiting = True
        skip_text = font_small.render("Нажми любую клавишу или кликни, чтобы продолжить...", True, GRAY)
        skip_rect = skip_text.get_rect(center=(WIDTH // 2, HEIGHT - 30 ))
        self.screen.blit(skip_text, skip_rect)
        pygame.display.flip()

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    break
            clock.tick(FPS)

        return True

    def игрок_умер(self):
        """Обработка смерти игрока"""

        # Показываем сообщение о смерти
        self.screen.fill(BLACK)
        text = font_large.render("ТЫ ПОГИБ В ЗАМКЕ...", True, BLOOD_RED)
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

        # Сообщение о возрождении
        respawn_text = font_medium.render("Возрождение в Убежище через 3 секунды...", True, WHITE)
        self.screen.blit(respawn_text, (WIDTH // 2 - respawn_text.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()
        pygame.time.wait(3000)

        # ===== НЕСОКРУШИМЫЙ (проверяем первым) =====
        if "indestructible" in self.игрок.get("выученные_навыки", []) and not self.revive_used:
            self.revive_used = True
            лечение = int(self.игрок["макс_здоровье"] * 0.2)
            self.игрок["здоровье"] = лечение
            # Возвращаемся в Убежище
            self.текущая_локация = "Убежище"
            self.режим = "игра"
            if hasattr(self, 'battle_log'):
                self.battle_log = []
            self.add_to_log("💪 НЕСОКРУШИМЫЙ! Ты восстал с 20% здоровья!")
            время.пройти_время(60)
            print("💀 Игрок возродился благодаря Несокрушимому")
            return  # не даём умереть по-обычному

        # ===== ОБЫЧНОЕ ВОЗРОЖДЕНИЕ =====
        # 1. Возвращаемся в Холл
        self.текущая_локация = "Убежище"

        # 2. Восстанавливаем здоровье (половину от максимума)
        self.игрок["здоровье"] = self.игрок["макс_здоровье"] // 2
        if self.игрок["здоровье"] < 1:
            self.игрок["здоровье"] = 1
        self.inventory.update_max_health()

        # 3. Сбрасываем режим боя (если был)
        self.режим = "игра"

        # 4. Очищаем лог боя
        if hasattr(self, 'battle_log'):
            self.battle_log = []

        # 5. Добавляем сообщение в лог событий
        self.add_to_log("Ты погиб и возродился в Убежище с половиной здоровья!")

        # 6. Проходит время (1 час)
        время.пройти_время(60)

        print("💀 Игрок возродился в Убежище")

    def fix_armor_value(self):
        """Исправляет неправильное значение брони"""
        print("\n🔧 ПРОВЕРКА И ИСПРАВЛЕНИЕ БРОНИ")

        старое = self.игрок.get("броня")
        print(f"📊 Текущее значение брони: {старое} (тип {type(старое)})")

        # Если броня хранится как число - исправляем
        if isinstance(старое, int):
            print(f"⚠️ Обнаружено ЧИСЛО {старое} вместо названия брони!")

            # Пытаемся определить, какая броня должна быть
            if старое == 6:
                исправленное = "кольчужная броня"
            elif старое == 3:
                исправленное = "кожаная броня"
            else:
                исправленное = None
                print(f"❌ Неизвестное значение брони: {старое}, сбрасываем")

            if исправленное:
                print(f"✅ Исправляем на: {исправленное}")
                self.игрок["броня"] = исправленное
                self.add_to_log(f"🔧 Броня исправлена на {исправленное}")
        else:
            print(f"✅ Значение брони корректное: {старое}")

    def upgrade_skill(self, skill_key):
        """Прокачка профессионального навыка"""

        current_value = self.игрок.get(skill_key, 0)
        max_value = 10

        if current_value >= max_value:
            self.add_to_log("Навык достиг максимума!")
            return False

        if self.игрок.get("очки_умений", 0) <= 0:
            self.add_to_log("Нет очков умений!")
            return False

        self.игрок[skill_key] = current_value + 1
        self.игрок["очки_умений"] -= 1

        self.add_to_log(f"Навык {skill_key} повышен до {self.игрок[skill_key]}!")
        return True

    def craft_item(self, название, рецепт):
        """
        Универсальная функция крафта
        """

        print("\n" + "=" * 40)
        print("КРАФТ ПРЕДМЕТА:", название)
        print("=" * 40)

        print(f"Тип рецепта: {type(рецепт)}")
        print(f"Рецепт: {рецепт}")

        # Определяем тип рецепта
        if isinstance(рецепт, dict) and 'ресурсы' in рецепт:
            # Это словарь с ключом 'ресурсы'
            ресурсы = рецепт['ресурсы']
            количество = рецепт.get('количество', 1)
            print(f"Словарь-рецепт. Ресурсы: {ресурсы}, количество: {количество}")
        elif isinstance(рецепт, list):
            # Это просто список ресурсов
            ресурсы = рецепт
            количество = 1
            print(f"Список ресурсов: {ресурсы}")
        else:
            print(f"Ошибка: непонятный тип рецепта {type(рецепт)}")
            return False

        print(f"\n🎒 Инвентарь ДО: {self.игрок['инвентарь']}")

        # Проверяем наличие ресурсов
        инвентарь_копия = self.игрок["инвентарь"].copy()

        for ресурс in ресурсы:
            if ресурс in инвентарь_копия:
                индекс = инвентарь_копия.index(ресурс)
                инвентарь_копия.pop(индекс)
                print(f"  ✅ Найден {ресурс}")
            else:
                print(f"  ❌ НЕ ХВАТАЕТ {ресурс}!")
                print(f"  Доступные ресурсы: {set(self.игрок['инвентарь'])}")
                return False

        print(f"\n Все ресурсы есть!")

        # Удаляем ресурсы
        for ресурс in ресурсы:
            self.игрок["инвентарь"].remove(ресурс)
            print(f"  🗑️ Удален {ресурс}")

        # Добавляем результат
        for i in range(количество):
            self.игрок["инвентарь"].append(название)
            print(f"  ➕ Добавлен {название} #{i + 1}")

        print(f"\n🎒 Инвентарь ПОСЛЕ: {self.игрок['инвентарь']}")
        print("=" * 40)
        print("✅ КРАФТ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 40)

        self.add_to_log(f"Создан {название} x{количество}")

        return True

    def trade_buy_item(self, предмет, количество):
        """Купить предметы (безлимитная версия)"""
        if предмет not in self.trade_goods:
            return

        данные = self.trade_goods[предмет]
        монеты = self.игрок.get('монета', 0)

        # Просто покупаем сколько просят (без проверки лимитов)
        можно_купить = количество
        общая_цена = данные['цена'] * можно_купить

        # Проверяем только деньги
        if монеты < общая_цена:
            self.add_to_log(f"Нужно {общая_цена} монет!")
            return

        # Покупаем
        self.игрок['монета'] = монеты - общая_цена
        for _ in range(можно_купить):
            self.inventory.add_item(предмет)

        self.add_to_log(f"Куплено {можно_купить} {предмет} за {общая_цена}!")

    def trade_sell_item(self, предмет, количество, цена):
        """Продать предметы"""
        if предмет not in self.игрок["инвентарь"]:
            return

        # Проверяем, сколько есть
        есть = self.игрок["инвентарь"].count(предмет)
        можно_продать = min(есть, количество)

        if можно_продать == 0:
            return

        # Продаём
        for _ in range(можно_продать):
            self.inventory.remove_item(предмет)

        выручка = можно_продать * цена
        self.игрок['монета'] = self.игрок.get('монета', 0) + выручка

        self.add_to_log(f"Продано {можно_продать} {предмет} за {выручка} монет!")
        self.add_to_log(f"Продан {предмет} x{можно_продать}")

    def _draw_trade_sell(self, panel_x, panel_y, panel_width, panel_height):
        """Отрисовка режима продажи с прокруткой"""

        if not self.игрок["инвентарь"]:
            empty_text = font_medium.render("Инвентарь пуст", True, GRAY)
            text_x = panel_x + panel_width // 2 - empty_text.get_width() // 2
            self.screen.blit(empty_text, (text_x, panel_y + 300))
            return

        # Группируем предметы
        подсчёт = {}
        for предмет in self.игрок["инвентарь"]:
            подсчёт[предмет] = подсчёт.get(предмет, 0) + 1

        предметы_список = sorted(list(подсчёт.items()), key=lambda x: x[0])

        # Параметры прокрутки
        if not hasattr(self, 'trade_scroll'):
            self.trade_scroll = 0

        visible_items = 6
        item_height = 55
        start_y = panel_y + 220
        max_scroll = max(0, len(предметы_список) - visible_items)

        # Отображаем предметы
        self.trade_items = []
        start_index = self.trade_scroll
        end_index = min(start_index + visible_items, len(предметы_список))

        for i in range(start_index, end_index):
            предмет, количество = предметы_список[i]
            y = start_y + (i - start_index) * item_height

            # Фон строки
            row_rect = pygame.Rect(panel_x + 50, y, panel_width - 100, item_height - 2)
            if row_rect.collidepoint(pygame.mouse.get_pos()):
                hover_bg = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                hover_bg.fill((GOLD[0], GOLD[1], GOLD[2], 30))
                self.screen.blit(hover_bg, row_rect)

            # Иконка предмета
            if предмет in self.item_icons:
                icon = self.item_icons[предмет]
                icon = pygame.transform.scale(icon, (40, 40))
                self.screen.blit(icon, (panel_x + 60, y + 5))
                name_x = panel_x + 110
            else:
                name_x = panel_x + 70

            # Название
            name_text = font_small.render(предмет, True, WHITE)
            self.screen.blit(name_text, (name_x, y + 15))

            # Количество
            qty_text = font_small.render(f"x{количество}", True, GOLD)
            self.screen.blit(qty_text, (panel_x + 400, y + 18))

            # Цена продажи
            цена_продажи = 1
            if предмет in предметы.предметы:
                цена_покупки = предметы.предметы[предмет].get("цена", 2)
                цена_продажи = max(1, цена_покупки // 2)

            price_text = font_small.render(f"{цена_продажи}", True, GOLD)
            self.screen.blit(price_text, (panel_x + 560, y + 18))

            # Кнопки продажи
            btn1_rect = pygame.Rect(panel_x + 700, y + 10, 45, 30)
            btn_all_rect = pygame.Rect(panel_x + 755, y + 10, 50, 30)

            # Кнопка "1"
            if btn1_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, btn1_rect)
                btn1_text = font_small.render("1", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, btn1_rect)
                pygame.draw.rect(self.screen, GOLD, btn1_rect, 1)
                btn1_text = font_small.render("1", True, WHITE)
            self.screen.blit(btn1_text, (btn1_rect.x + 15, btn1_rect.y + 5))
            self.trade_items.append(("sell_1", предмет, btn1_rect, цена_продажи))

            # Кнопка "ВСЕ"
            if btn_all_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, btn_all_rect)
                btn_all_text = font_small.render("ВСЕ", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, btn_all_rect)
                pygame.draw.rect(self.screen, GOLD, btn_all_rect, 1)
                btn_all_text = font_small.render("ВСЕ", True, WHITE)
            self.screen.blit(btn_all_text, (btn_all_rect.x + 10, btn_all_rect.y + 5))
            self.trade_items.append(("sell_all", предмет, btn_all_rect, цена_продажи, количество))


    def draw_health_bar(self, x, y, width, height, current, maximum):
        """Рисует полоску здоровья"""
        pygame.draw.rect(self.screen, HEALTH_BG, (x, y, width, height))

        percent = current / maximum
        if percent > 0.6:
            color = HEALTH_GREEN
        elif percent > 0.3:
            color = HEALTH_YELLOW
        else:
            color = HEALTH_RED

        bar_width = int(width * percent)
        if bar_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, bar_width, height))

        pygame.draw.rect(self.screen, GOLD, (x, y, width, height), 2)

        health_text = font_small.render(f"{current}/{maximum}", True, WHITE)
        self.screen.blit(health_text, (x + width // 2 - 30, y + 5))

    def draw_mana_bar(self, x, y, width, height, current, maximum):
        """Рисует полоску маны"""
        pygame.draw.rect(self.screen, (40, 40, 60), (x, y, width, height))

        if maximum > 0:
            percent = current / maximum
            bar_width = int(width * percent)
            if bar_width > 0:
                pygame.draw.rect(self.screen, (80, 120, 255), (x, y, bar_width, height))

        pygame.draw.rect(self.screen, GOLD, (x, y, width, height), 2)

        mana_text = font_small.render(f"{current}/{maximum}", True, WHITE)
        self.screen.blit(mana_text, (x + width // 2 - 30, y + 5))

    def handle_battle_click(self, pos):
        if self.battle.battle_ended:
            print("   ⚠️ Бой завершён, клики игнорируются")

            # ===== ПРОВЕРКА НА РЕЗУЛЬТАТ ПОБЕДЫ =====
            if hasattr(self.battle, 'victory_result') and self.battle.victory_result:
                print("   🔥 Обрабатываем результат победы из battle_ended")
                result = self.battle.victory_result
                if isinstance(result, dict) and result.get("victory"):
                    self.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                    self.battle_victory()
                    self.battle.victory_result = None  # Сбрасываем
                    return
            return  # ← Выходим, если бой завершён

        # ===== ПРОВЕРКА КЛИКОВ ПО ПОЯСУ (ТОЛЬКО КОГДА БОЙ АКТИВЕН) =====
        if hasattr(self, 'belt_slots'):
            for slot_index, slot_rect in self.belt_slots:
                if slot_rect.collidepoint(pos):
                    # Используем зелье с пояса
                    успех, сообщение = self.battle.use_belt_potion(slot_index)
                    self.add_to_log(сообщение)

                    if успех:
                        # После использования зелья - ход врага
                        self.battle.enemy_attack()
                        self.enemy_health = self.battle.enemy_health
                        self.battle_log = self.battle.battle_log

                        # Проверяем победу
                        if self.battle.battle_ended and self.battle.victory_result:
                            result = self.battle.victory_result
                            self.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                            self.battle_victory()
                            self.battle.victory_result = None
                    return

        # ===== ОСТАЛЬНЫЕ КНОПКИ =====
        for action, rect in self.battle_buttons:
            if rect.collidepoint(pos):
                if action == "attack":
                    print("⚔️ КЛИК ПО КНОПКЕ АТАКИ")
                    result = self.battle.player_attack()

                    # Синхронизация
                    self.enemy_health = self.battle.enemy_health
                    self.battle_log = self.battle.battle_log
                    print(f"   enemy_health после синхронизации: {self.enemy_health}")

                    if isinstance(result, dict) and result.get("victory"):
                        print("   🏆 Враг убит!")
                        self.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                        self.battle_victory()
                    return

                elif action == "flee":
                    self.battle_flee()
                    return

        # ===== АКТИВНЫЕ НАВЫКИ =====
        if hasattr(self, 'battle_skill_buttons'):
            for skill_id, rect in self.battle_skill_buttons:
                if rect.collidepoint(pos):
                    result = self.battle.use_active_skill(skill_id, self.skills_data, self.add_to_log)

                    self.enemy_health = self.battle.enemy_health
                    self.battle_log = self.battle.battle_log
                    self.blocking = self.battle.blocking

                    if isinstance(result, dict) and result.get("victory"):
                        self.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                        self.battle_victory()
                    return

    def _draw_skill_buttons(self):
        """Рисует панель активных навыков в бою (с SVG иконками)"""
        # Получаем выученные активные навыки
        активные_навыки = []
        for skill_id in self.игрок.get("выученные_навыки", []):
            skill = SkillLoader.get_skill_by_id(self.skills_data, skill_id)
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

        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Заголовок
        title = font_medium.render("⚔️ НАВЫКИ", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 6))

        pygame.draw.line(self.screen, (100, 100, 120), (panel_x + 20, panel_y + 38),
                         (panel_x + panel_width - 20, panel_y + 38), 1)

        self.battle_skill_buttons = []
        mouse_pos = pygame.mouse.get_pos()

        for i, skill in enumerate(активные_навыки[:max_slots]):
            x = panel_x + 15 + i * (slot_size + spacing)
            y = panel_y + 45

            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            shadow_rect = pygame.Rect(x + 2, y + 2, slot_size, slot_size)
            pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect)

            стоимость_маны = skill.get("стоимость_маны", 0)
            маны_хватает = self.игрок.get("мана", 0) >= стоимость_маны

            if маны_хватает:
                for j in range(slot_size):
                    ratio = j / slot_size
                    r = int(20 + 35 * ratio)
                    g = int(40 + 25 * ratio)
                    b = int(80 + 35 * ratio)
                    color = (r, g, b)
                    pygame.draw.line(self.screen, color, (x, y + j), (x + slot_size, y + j))
                pygame.draw.rect(self.screen, GOLD, slot_rect, 2)
            else:
                for j in range(slot_size):
                    ratio = j / slot_size
                    r = int(40 + 20 * ratio)
                    g = int(40 + 20 * ratio)
                    b = int(50 + 20 * ratio)
                    color = (r, g, b)
                    pygame.draw.line(self.screen, color, (x, y + j), (x + slot_size, y + j))
                pygame.draw.rect(self.screen, (80, 80, 80), slot_rect, 2)

            if slot_rect.collidepoint(mouse_pos) and маны_хватает:
                glow_rect = pygame.Rect(x - 3, y - 3, slot_size + 6, slot_size + 6)
                pygame.draw.rect(self.screen, (255, 215, 0, 50), glow_rect, 2)

            # ===== ЗАГРУЖАЕМ SVG ИКОНКУ =====
            skill_type = skill.get("эффект", "damage")
            icon_path = f"assets/skills/{skill_type}.svg"

            try:
                # Пробуем загрузить SVG
                icon = pygame.image.load(icon_path).convert_alpha()
                icon = pygame.transform.scale(icon, (slot_size - 12, slot_size - 12))
            except:
                # Если иконки нет - создаём заглушку
                icon = self._create_skill_icon_1(skill_type)

            self.screen.blit(icon, (x + 6, y + 6))

            # Номер
            num_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
            num_bg.fill((0, 0, 0, 180))
            self.screen.blit(num_bg, (x + 2, y + 2))
            pygame.draw.rect(self.screen, GOLD, (x + 2, y + 2, 20, 20), 1)
            num = font_tiny.render(str(i + 1), True, GOLD if маны_хватает else GRAY)
            self.screen.blit(num, (x + 6, y + 3))

            # Стоимость маны
            if стоимость_маны > 0:
                mana_text = font_tiny.render(f"MP:{стоимость_маны}", True, (100, 200, 255) if маны_хватает else GRAY)
                mana_x = x + slot_size // 2 - mana_text.get_width() // 2
                self.screen.blit(mana_text, (mana_x, y + slot_size - 16))

            # Подсказка
            if slot_rect.collidepoint(mouse_pos):
                tip_text = font_small.render(skill["название"], True, WHITE)
                tip_x = x + slot_size // 2 - tip_text.get_width() // 2
                tip_y = y - 28
                tip_bg = pygame.Surface((tip_text.get_width() + 16, 24), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 220))
                pygame.draw.rect(tip_bg, GOLD, tip_bg.get_rect(), 1)
                self.screen.blit(tip_bg, (tip_x - 8, tip_y - 2))
                self.screen.blit(tip_text, (tip_x, tip_y))

                #if стоимость_маны > 0:
                    #mana_tip = font_tiny.render(f"MP: {стоимость_маны}", True,
                                                #(100, 200, 255) if маны_хватает else GRAY)
                    #mana_tip_x = x + slot_size // 2 - mana_tip.get_width() // 2
                    #self.screen.blit(mana_tip, (mana_tip_x, y - 45))

                if маны_хватает:
                    use_btn = pygame.Rect(x + slot_size - 30, y + slot_size - 26, 26, 22)
                    pygame.draw.rect(self.screen, HEALTH_GREEN, use_btn)
                    pygame.draw.rect(self.screen, GOLD, use_btn, 1)
                    use_text = font_tiny.render("ИСП", True, BLACK)
                    self.screen.blit(use_text, (use_btn.x + 3, use_btn.y + 3))

                self.battle_skill_buttons.append((skill["id"], slot_rect))

            self.battle_skill_buttons.append((skill["id"], slot_rect))

        # Индикатор маны
        #мана_текст = font_tiny.render(f"MP: {self.игрок.get('мана', 0)}/{self.игрок.get('макс_мана', 50)}", True, GOLD)
        #self.screen.blit(мана_текст, (panel_x + 10, panel_y + panel_height - 18))

    def _create_skill_icon_1(self, skill_type):
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

    def battle_flee(self):
        """Побег из боя"""
        успех = self.battle.battle_flee()
        if успех:
            self.режим = "игра"
        self.battle_log = self.battle.battle_log

    # gui_game.py

    def battle_victory(self):
        """Победа в бою — только переключаем режим (панель лута уже показана)"""
        print(f"\n🏆 BATTLE_VICTORY вызвана (GUI)!")

        # ===== ОСТАНАВЛИВАЕМ МУЗЫКУ БОЯ =====
        self.music.остановить_музыку()  # 👈 СНАЧАЛА ОСТАНАВЛИВАЕМ

        # ===== ВОЗВРАЩАЕМ МУЗЫКУ ЛОКАЦИИ =====
        if self.music.есть_музыка(self.текущая_локация):
            self.music.переключить_плейлист(self.текущая_локация, self.игра_загружена)
        else:
            self.music.остановить_музыку()

        # Если бой был в данже, удаляем врага
        if hasattr(self, 'exploration_in_battle') and self.exploration_in_battle:
            if hasattr(self, 'current_enemy'):
                from entities.enemies import ЛЕСНЫЕ_БОССЫ
                if self.current_enemy in ЛЕСНЫЕ_БОССЫ:
                    for i, boss in enumerate(self.exploration_zone.bosses):
                        if boss.boss_name == self.current_enemy:
                            self.exploration_zone.bosses.pop(i)
                            self.add_to_log(f"Ты победил {self.current_enemy.replace('_', ' ')}!")
                            break
                else:
                    for i, mob in enumerate(self.exploration_zone.mobs):
                        if mob.enemy_name == self.current_enemy and mob.is_alive:
                            self.exploration_zone.mobs.pop(i)
                            break

        self.battle_log = []

        # ===== ПЕРЕКЛЮЧАЕМ РЕЖИМ =====
        if hasattr(self, 'exploration_in_battle') and self.exploration_in_battle:
            self.режим = "эксплорейшн"
            self.exploration_in_battle = False
            print("🏰 Возвращаемся в данж")
        elif hasattr(self, 'in_dungeon') and self.in_dungeon:
            self.режим = "эксплорейшн"
            self.in_dungeon = False
            print("🏰 Возвращаемся в данж")
        elif hasattr(self, 'exploration_zone') and self.exploration_zone is not None:
            self.режим = "эксплорейшн"
            print("🏰 Возвращаемся в данж")
        else:
            self.режим = "игра"
            print("🎮 Возвращаемся в игру")

        self.blocking = False
        время.пройти_время(15)

    def add_to_log(self, message):
        """Добавляет сообщение в лог событий"""
        # ===== ПРОВЕРКА: ЕСЛИ log_messages НЕ СУЩЕСТВУЕТ — СОЗДАЁМ =====
        if not hasattr(self, 'log_messages'):
            self.log_messages = []
            self.max_log_messages = 20
        # ==============================================================

        self.log_messages.append(message)
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages.pop(0)
        print(f" Лог: {message}")

    def add_to_belt(self, item):
        """Добавляет предмет на пояс (до 5 слотов)"""
        # Проверяем, что это еда
        from entities import items as предметы
        данные = предметы.предметы.get(item, {})
        if данные.get("тип") != "еда":
            return False

        if "пояс" not in self.игрок:
            self.игрок["пояс"] = []

        пояс = self.игрок["пояс"]

        # Проверяем, есть ли пустой слот
        for i in range(5):
            if i >= len(пояс):
                пояс.append(item)
                return True
            if пояс[i] is None:
                пояс[i] = item
                return True

        return False  # Пояс полон

    def _разбить_текст_на_строки(self, текст, максимальная_ширина, шрифт):
        """
        Разбивает длинный текст на строки, каждая из которых помещается по ширине.
        """
        # Проверяем, помещается ли текст целиком
        if шрифт.size(текст)[0] <= максимальная_ширина:
            return [текст]

        строки = []
        слова = текст.split(' ')
        текущая_строка = ""

        for слово in слова:
            # Пробуем добавить слово
            пробная_строка = текущая_строка + " " + слово if текущая_строка else слово

            if шрифт.size(пробная_строка)[0] <= максимальная_ширина:
                текущая_строка = пробная_строка
            else:
                # Текущая строка заполнена, сохраняем
                if текущая_строка:
                    строки.append(текущая_строка)
                # Начинаем новую строку с этого слова
                текущая_строка = слово

                # Если одно слово не помещается — обрезаем его
                if шрифт.size(текущая_строка)[0] > максимальная_ширина:
                    # Обрезаем слово по буквам
                    while шрифт.size(текущая_строка + "...")[0] > максимальная_ширина and len(текущая_строка) > 0:
                        текущая_строка = текущая_строка[:-1]
                    текущая_строка = текущая_строка + "..."
                    строки.append(текущая_строка)
                    текущая_строка = ""

        # Добавляем последнюю строку
        if текущая_строка:
            строки.append(текущая_строка)

        return строки

    def draw_log_panel(self):
        """Отрисовка панели с логом событий с разбивкой длинного текста"""

        # Параметры панели
        panel_width = 350
        panel_height = 200
        panel_x = 0
        panel_y = 870

        # Полупрозрачный фон
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((26, 26, 46, 180))
        pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Заголовок
        title_text = font_medium.render("СОБЫТИЯ", True, GOLD)
        self.screen.blit(title_text, (panel_x + 10, panel_y + 5))

        # Линия разделителя
        pygame.draw.line(self.screen, GOLD, (panel_x + 10, panel_y + 30),
                         (panel_x + panel_width - 10, panel_y + 30), 1)

        # Максимальная ширина текста
        max_text_width = panel_width - 25  # 275 пикселей

        # Сначала разбиваем ВСЕ сообщения на строки
        все_строки = []
        for msg in self.log_messages:
            строки_сообщения = self._разбить_текст_на_строки(msg, max_text_width, font_small)
            все_строки.append(строки_сообщения)

        # Отображаем строки, начиная с нижней части панели
        line_height = 18
        start_y = panel_y + panel_height - line_height - 5  # от нижнего края

        # Идём снизу вверх
        текущая_y = start_y
        for строки_сообщения in reversed(все_строки):
            # Отображаем строки сообщения снизу вверх
            for строка in reversed(строки_сообщения):
                if текущая_y < panel_y + 35:  # не выше заголовка
                    break
                msg_text = font_small.render(строка, True, WHITE)
                self.screen.blit(msg_text, (panel_x + 15, текущая_y))
                текущая_y -= line_height
            текущая_y -= 2  # небольшой отступ между сообщениями

    def _draw_button(self, rect, text, is_primary):
        """Универсальная отрисовка кнопки"""
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)

        if is_hover:
            pygame.draw.rect(self.screen, GOLD, rect)
            button_text = font_medium.render(text, True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, rect)
            pygame.draw.rect(self.screen, GOLD, rect, 2)
            button_text = font_medium.render(text, True, WHITE)

        text_x = rect.x + rect.width // 2 - button_text.get_width() // 2
        text_y = rect.y + rect.height // 2 - button_text.get_height() // 2
        self.screen.blit(button_text, (text_x, text_y))

    def load_player_sprite(self):
        """Загружает спрайт персонажа"""
        try:
            self.player_sprite = pygame.image.load("assets/player/idle.png").convert_alpha()
            self.player_sprite = pygame.transform.scale(self.player_sprite, (self.player_size, self.player_size))
            print("✅ Спрайт персонажа загружен")
        except:
            print("❌ Не удалось загрузить спрайт, создаю заглушку")
            self.create_player_placeholder()

    def create_player_placeholder(self):
        """Создаёт простой спрайт-заглушку для персонажа"""

        self.player_sprite = pygame.Surface((self.player_size, self.player_size), pygame.SRCALPHA)

        # Тело (синий квадрат) - отступы пропорциональные
        padding = self.player_size // 8  # 8 пикселей для 64px
        body_size = self.player_size - padding * 2

        pygame.draw.rect(self.player_sprite, DARK_BLUE, (padding, padding, body_size, body_size))

        # Глаза
        eye_size = self.player_size // 8
        eye_y = self.player_size // 3
        left_eye_x = self.player_size // 3
        right_eye_x = self.player_size * 2 // 3

        pygame.draw.circle(self.player_sprite, WHITE, (left_eye_x, eye_y), eye_size)
        pygame.draw.circle(self.player_sprite, WHITE, (right_eye_x, eye_y), eye_size)
        pygame.draw.circle(self.player_sprite, BLACK, (left_eye_x, eye_y), eye_size // 2)
        pygame.draw.circle(self.player_sprite, BLACK, (right_eye_x, eye_y), eye_size // 2)

        # Рот (улыбка)
        mouth_y = self.player_size * 2 // 3
        mouth_width = self.player_size // 2
        mouth_height = self.player_size // 4
        pygame.draw.arc(self.player_sprite, WHITE,
                        (self.player_size // 4, mouth_y, mouth_width, mouth_height),
                        0, 3.14, self.player_size // 16)

        # Рамка
        pygame.draw.rect(self.player_sprite, GOLD, (0, 0, self.player_size, self.player_size), 3)

        print(f"🎨 Создан спрайт-заглушка {self.player_size}x{self.player_size}")

    def load_enemy_sprite_by_name(self, enemy_name):
        """Загружает спрайт для конкретного врага"""
        from entities import enemies as враги

        enemy_data = враги.враги.get(enemy_name)
        if not enemy_data:
            print(f"❌ Враг {enemy_name} не найден!")
            return self.create_enemy_placeholder()

        sprite_path = enemy_data.get("спрайт")
        if not sprite_path:
            print(f"⚠️ Для врага {enemy_name} не указан спрайт!")
            return self.create_enemy_placeholder()

        try:
            sprite = pygame.image.load(sprite_path).convert_alpha()
            sprite = pygame.transform.scale(sprite, (self.enemy_size, self.enemy_size))
            print(f"✅ Загружен спрайт для {enemy_name}")
            return sprite
        except Exception as e:
            print(f"❌ Ошибка загрузки спрайта {enemy_name}: {e}")
            return self.create_enemy_placeholder()

    def create_enemy_placeholder(self):
        """Создаёт простой спрайт-заглушку для врага"""
        self.enemy_sprite = pygame.Surface((self.enemy_size, self.enemy_size), pygame.SRCALPHA)

        # Тело (красный квадрат)
        padding = self.enemy_size // 8
        body_size = self.enemy_size - padding * 2
        pygame.draw.rect(self.enemy_sprite, DARK_RED, (padding, padding, body_size, body_size))

        # Глаза (злые)
        eye_size = self.enemy_size // 8
        eye_y = self.enemy_size // 3
        left_eye_x = self.enemy_size // 3
        right_eye_x = self.enemy_size * 2 // 3

        # Белки глаз
        pygame.draw.circle(self.enemy_sprite, WHITE, (left_eye_x, eye_y), eye_size)
        pygame.draw.circle(self.enemy_sprite, WHITE, (right_eye_x, eye_y), eye_size)

        # Зрачки (красные, смотрят на игрока)
        pygame.draw.circle(self.enemy_sprite, BLOOD_RED, (left_eye_x, eye_y), eye_size // 2)
        pygame.draw.circle(self.enemy_sprite, BLOOD_RED, (right_eye_x, eye_y), eye_size // 2)

        # Брови (злые)
        brow_y = eye_y - eye_size // 2
        pygame.draw.line(self.enemy_sprite, BLACK,
                         (left_eye_x - eye_size, brow_y),
                         (left_eye_x + eye_size, brow_y - eye_size // 2), 3)
        pygame.draw.line(self.enemy_sprite, BLACK,
                         (right_eye_x + eye_size, brow_y),
                         (right_eye_x - eye_size, brow_y - eye_size // 2), 3)

        # Рот (злой)
        mouth_y = self.enemy_size * 2 // 3
        mouth_width = self.enemy_size // 2
        mouth_height = self.enemy_size // 4
        pygame.draw.arc(self.enemy_sprite, BLOOD_RED,
                        (self.enemy_size // 4, mouth_y, mouth_width, mouth_height),
                        3.14, 6.28, self.enemy_size // 16)

        # Рамка (красная)
        pygame.draw.rect(self.enemy_sprite, BLOOD_RED, (0, 0, self.enemy_size, self.enemy_size), 3)

        print(f"🎨 Создан спрайт-заглушка врага {self.enemy_size}x{self.enemy_size}")


    def start_battle_animation(self):
        """Запускает анимацию начала боя"""
        self.battle_start_animation = True
        self.battle_start_timer = 45  # длительность анимации в кадрах (0.5 сек при 60 FPS)
        self.battle_start_alpha = 0
        self.battle_start_scale = 0.3
        print("🎬 Анимация начала боя запущена!")

    def update_battle_animation(self):
        """Обновляет анимацию начала боя"""
        if not self.battle_start_animation:
            return

        # Уменьшаем таймер
        self.battle_start_timer -= 1

        # Рассчитываем параметры анимации (более плавно)
        total_frames = 45  # общая длительность
        progress = 1 - (self.battle_start_timer / total_frames)  # от 0 до 1

        if progress < 0.4:
            # Первая фаза (0-40%): нарастание
            phase = progress / 0.4  # от 0 до 1
            self.battle_start_alpha = int(255 * phase)
            self.battle_start_scale = 0.3 + (0.7 * phase)
        elif progress < 0.7:
            # Вторая фаза (40-70%): максимальная интенсивность
            self.battle_start_alpha = 255
            self.battle_start_scale = 1.0
        else:
            # Третья фаза (70-100%): затухание
            phase = (progress - 0.7) / 0.3  # от 0 до 1
            self.battle_start_alpha = int(255 * (1 - phase))
            self.battle_start_scale = 1.0 - (0.2 * phase)

        # Завершаем анимацию
        if self.battle_start_timer <= 0:
            self.battle_start_animation = False
            print("✨ Анимация начала боя завершена!")

    def draw_battle_start_animation(self):
        """Рисует анимацию начала боя"""
        if not self.battle_start_animation:
            return

        # Создаём поверхность для анимации
        animation_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Эффект 1: Вспышка по центру (более плавная)
        flash_radius = int(200 * self.battle_start_scale)  # увеличен максимальный радиус
        flash_center = (WIDTH // 2, HEIGHT // 2)

        # Рисуем несколько кругов для более объёмной вспышки
        for i in range(4):
            radius = flash_radius - i * 25
            if radius > 0:
                alpha = min(200, self.battle_start_alpha // (i + 1))
                color = (255, 215, 0, alpha)
                pygame.draw.circle(animation_surface, color, flash_center, radius)

        # Эффект 2: Текст "БОЙ!" с анимацией (появляется медленнее)
        if self.battle_start_timer > 25:  # показываем дольше
            font_size = int(72 * self.battle_start_scale)
            try:
                battle_font = pygame.font.Font(None, font_size)
            except:
                battle_font = font_large

            # Создаём текст с эффектом свечения
            battle_text = battle_font.render("БОЙ!", True, (255, 215, 0))

            # Несколько теней для эффекта объёма
            for offset in [(3, 3), (2, 2), (1, 1)]:
                shadow_text = battle_font.render("БОЙ!", True, (100, 50, 0))
                shadow_rect = shadow_text.get_rect(center=flash_center)
                shadow_rect.x += offset[0]
                shadow_rect.y += offset[1]
                shadow_rect_alpha = self.battle_start_alpha // 2
                shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
                shadow_surface.blit(shadow_text, (0, 0))
                shadow_surface.set_alpha(shadow_rect_alpha)
                animation_surface.blit(shadow_surface, shadow_rect)

            # Основной текст
            text_rect = battle_text.get_rect(center=flash_center)
            text_surface = pygame.Surface(text_rect.size, pygame.SRCALPHA)
            text_surface.blit(battle_text, (0, 0))
            text_surface.set_alpha(self.battle_start_alpha)
            animation_surface.blit(text_surface, text_rect)

        # Эффект 3: Искры по краям экрана (больше искр, медленнее)
        if self.battle_start_timer > 15 and self.battle_start_alpha > 0:
            spark_count = int(30 * self.battle_start_scale)  # больше искр
            for _ in range(spark_count):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                spark_size = random.randint(2, 6)

                # ИСПРАВЛЕНО: проверяем диапазон для альфы
                if self.battle_start_alpha > 50:
                    spark_alpha = random.randint(50, self.battle_start_alpha)
                elif self.battle_start_alpha > 1:
                    spark_alpha = random.randint(1, self.battle_start_alpha)
                else:
                    spark_alpha = 1

                # Разные цвета искр
                color_choice = random.choice([
                    (255, 215, 0, spark_alpha),  # золотой
                    (255, 180, 0, spark_alpha),  # оранжевый
                    (255, 100, 0, spark_alpha)  # красноватый
                ])
                pygame.draw.circle(animation_surface, color_choice, (x, y), spark_size)

        # Эффект 4: Вращающиеся линии вокруг карт (медленнее)
        if self.battle_start_timer > 20 and self.battle_start_alpha > 0:
            # Медленное вращение
            angle = pygame.time.get_ticks() * 0.005  # было 0.01, теперь медленнее

            # Позиции карт (игрок слева вверху, враг справа внизу)
            card_positions = [
                (80, 80),  # карта игрока
                (WIDTH - 430, HEIGHT - 530)  # карта врага
            ]

            for card in card_positions:
                cx, cy = card[0] + 175, card[1] + 225

                # Больше лучей для эффектности
                for i in range(12):  # было 8, теперь 12
                    rad = angle + (i * 3.14 / 6)  # чаще лучи
                    x1 = cx + int(220 * math.cos(rad)) * self.battle_start_scale
                    y1 = cy + int(220 * math.sin(rad)) * self.battle_start_scale
                    x2 = cx + int(190 * math.cos(rad + 0.6)) * self.battle_start_scale
                    y2 = cy + int(190 * math.sin(rad + 0.6)) * self.battle_start_scale

                    alpha = min(200, int(self.battle_start_alpha / 1.5))
                    line_width = max(1, int(3 * self.battle_start_scale))
                    pygame.draw.line(animation_surface, (255, 215, 0, alpha), (x1, y1), (x2, y2), line_width)

        # Эффект 5: Добавляем парящие частицы (новый эффект)
        if self.battle_start_timer > 10 and self.battle_start_alpha > 50:
            particle_count = int(15 * self.battle_start_scale)
            for _ in range(particle_count):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                size = random.randint(1, 3)

                # ИСПРАВЛЕНО: проверяем диапазон для альфы
                max_alpha = self.battle_start_alpha // 2
                if max_alpha > 30:
                    alpha = random.randint(30, max_alpha)
                elif max_alpha > 1:
                    alpha = random.randint(1, max_alpha)
                else:
                    alpha = 1

                color = (255, 200, 100, alpha)
                pygame.draw.circle(animation_surface, color, (x, y), size)

        # Накладываем анимацию на экран
        self.screen.blit(animation_surface, (0, 0))

    def start_battle(self, враг_имя):
        """Начинает бой с врагом"""
        pygame.event.clear()

        # ===== МУЗЫКА БОЯ =====
        self.music.переключить_плейлист("бой", self.игра_загружена)

        # ===== СБРОС ПАРАМЕТРОВ =====
        self.enemy_bleed_duration = 0
        self.enemy_bleed_damage = 0
        self.enemy_stunned = False
        self.enemy_weakened_duration = 0
        self.blocking = False
        self.enemy_damage_multiplier = 1.0
        self.battle.battle_ended = False  # 👈 ОБЯЗАТЕЛЬНО!
        self.battle.enemy_data = None
        # =============================

        self.add_to_log

        self.enemy_sprite = self.load_enemy_sprite_by_name(враг_имя)

        # Если мы в данже — запоминаем это
        if hasattr(self, 'in_dungeon') and self.in_dungeon:
            self.exploration_in_battle = True
            print("⚔️ Бой в данже!")

        # Запускаем бой через BattleSystem
        battle_data = self.battle.start_battle(враг_имя)

        self.режим = "бой"
        self.current_enemy = battle_data["enemy_name"]
        self.enemy_data = battle_data["enemy_data"]
        self.enemy_health = battle_data["enemy_health"]
        self.battle_log = battle_data["battle_log"]

        # Запускаем анимацию
        self.start_battle_animation()
        pygame.time.wait(200)
        время.пройти_время(2)



    def _пересчитать_пассивные_бонусы(self):
        """
        Пересчитывает все пассивные бонусы при загрузке игры.
        """
        print("\n" + "=" * 50)
        print("🔄 ПЕРЕСЧЁТ ПАССИВНЫХ БОНУСОВ ПРИ ЗАГРУЗКЕ")
        print("=" * 50)

        # Сбрасываем бонусы
        if "пассивные_бонусы" not in self.игрок:
            self.игрок["пассивные_бонусы"] = {}
        else:
            self.игрок["пассивные_бонусы"] = {}

        self.игрок["защита_бонус"] = 0
        self.игрок["counter_chance"] = 0
        self.игрок["revive_hp"] = 0

        # Проходим по всем выученным навыкам
        выученные = self.игрок.get("выученные_навыки", [])
        print(f"📚 Найдено выученных навыков: {len(выученные)}")

        for skill_id in выученные:
            skill = SkillLoader.get_skill_by_id(self.skills_data, skill_id)
            if not skill:
                print(f"   ⚠️ Навык {skill_id} не найден в данных!")
                continue

            # Применяем только пассивные навыки
            if skill.get("тип") == "пассивный":
                эффект = skill.get("эффект")
                значение = skill.get("значение", 0)

                print(f"   🔧 Обработка: {skill.get('название')} (эффект: {эффект}, значение: {значение})")

                if эффект == "hp_bonus":
                    if "пассивные_бонусы" not in self.игрок:
                        self.игрок["пассивные_бонусы"] = {}
                    старое = self.игрок["пассивные_бонусы"].get("hp", 0)
                    self.игрок["пассивные_бонусы"]["hp"] = старое + значение
                    print(f"      ✅ HP бонус: {старое} -> {self.игрок['пассивные_бонусы']['hp']}")

                elif эффект == "armor_bonus":
                    старое = self.игрок.get("защита_бонус", 0)
                    self.игрок["защита_бонус"] = старое + значение
                    print(f"      ✅ Защита бонус: {старое} -> {self.игрок['защита_бонус']}")

                elif эффект == "rage_bonus":
                    print(f"      ✅ Бонус ярости активирован (значение: {значение})")

                elif эффект == "counter_chance":
                    старое = self.игрок.get("counter_chance", 0)
                    self.игрок["counter_chance"] = старое + значение
                    print(f"      ✅ Шанс контратаки: {старое} -> {self.игрок['counter_chance']}%")

                elif эффект == "revive":
                    старое = self.игрок.get("revive_hp", 0)
                    self.игрок["revive_hp"] = старое + значение
                    print(f"      ✅ Возрождение: {старое} -> {self.игрок['revive_hp']}%")

                else:
                    print(f"      ⚠️ Неизвестный эффект: {эффект}")

        print(f"\n📊 ИТОГОВЫЕ БОНУСЫ:")
        print(f"   Пассивные бонусы HP: {self.игрок['пассивные_бонусы'].get('hp', 0)}")
        print(f"   Защита бонус: {self.игрок.get('защита_бонус', 0)}")
        print(f"   Шанс контратаки: {self.игрок.get('counter_chance', 0)}%")
        print(f"   Возрождение: {self.игрок.get('revive_hp', 0)}%")
        print("=" * 50)


if __name__ == "__main__":
    from game_api import GameAPI  # Добавляем импорт

    # Создаём экземпляр API
    api = GameAPI()

    # Показываем окно входа (передаём API)
    login = LoginScreen(api=api)
    token = login.run()

    if token:
        print("✅ Вход выполнен! Запуск игры...")
        # Токен уже сохранён в api через LoginScreen
        game = Game(api=api)  # Передаём API в игру
        game.run()
    else:
        print("❌ Вход не выполнен. Выход.")
        pygame.quit()
        sys.exit()