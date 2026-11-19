# ===== СТАНДАРТНЫЕ БИБЛИОТЕКИ =====
import sys
import os

# ===== СТОРОННИЕ БИБЛИОТЕКИ =====
# noinspection PyUnresolvedReferences
from pyvidplayer2 import Video

# ===== КОНФИГУРАЦИЯ =====
from config import *
from game_api import GameAPI


# ===== ИГРОВЫЕ СУЩНОСТИ (entities) =====
from entities import player as игрок
from entities.player import потратить_ресурсы, проверить_голод
from entities import locations as локации
from entities import items as предметы

# ===== ИГРОВЫЕ СИСТЕМЫ (systems) =====
from systems.battle_system import BattleSystem, start_battle_gui, handle_battle_click, battle_flee, battle_victory
from systems.inventory_system import InventorySystem
from systems.quest_system import QuestSystem
from systems import crafting as верстак
from systems import time_system as время
from systems.dungeon_controller import DungeonController
from systems.video_manager import VideoManager
from systems.audio import MusicManager
from systems.skills_system import upgrade_skill, learn_skill
from systems.loot_manager import show_loot_panel, close_loot_panel


# ===== ЗАГРУЗЧИКИ И СОХРАНЕНИЯ =====
from loaders.skill_loader import SkillLoader
from loaders.asset_loader import (
    load_close_icon, load_action_icons, load_backgrounds,
    load_item_icons,
)

# ===== UI: ДИАЛОГИ И ЭКРАНЫ =====
from ui.dialogs.exit_dialog import show_exit_dialog
from ui.login_screen import LoginScreen
from ui.main_menu import show_main_menu

# ===== UI: ПАНЕЛИ И ТРЕКЕРЫ =====
from ui.panels.loot_panel import draw_loot_panel
from ui.panels.search_bar import draw_search_bar
from ui.panels.quests_panel import draw_quests
from ui.quest_tracker import draw_quest_tracker, draw_daily_quest_tracker
from ui.panels.log_panel import draw_log_panel

# ===== UI: ОСНОВНЫЕ ЭКРАНЫ И БОЙ =====
from ui.battle_ui import draw_battle
from ui.battle_intro import update_battle_animation, draw_battle_start_animation
from ui.map_ui import draw_map, handle_map_click
from ui.hud import draw_status, draw_location, draw_actions
from ui.chest_ui import draw_chest, handle_chest_click
from ui.trade_ui import draw_quest_trade_menu, handle_trade_click, draw_trade
from ui.save_menus import show_save_menu
from ui.crafting_ui import draw_craft, handle_craft_click
from ui.inventory_ui import draw_inventory, handle_inventory_click
from ui.skills_menu import draw_skills_menu
from ui.widgets import разбить_текст_на_строки, draw_button

# ===== UI: ВИДЖЕТЫ И СПРАЙТЫ =====
from ui.widgets import разбить_текст_на_строки
from ui.sprites import load_player_sprite

# ===== КОНСТАНТЫ =====
EMOJI_FONT_PATH = "C:/Windows/Fonts/seguiemj.ttf"

# ===== ИНИЦИАЛИЗАЦИЯ =====
# ВАЖНО: окно здесь НЕ создаём!
# Окно логина создаст LoginScreen, окно игры — Game.__init__.
pygame.init()
pygame.mixer.init()

# ===== СОЗДАЁМ ШРИФТЫ =====
fonts = get_fonts()
font_tiny = fonts["tiny"]
font_small = fonts["small"]
font_medium = fonts["medium"]
font_large = fonts["large"]
font_emoji = pygame.font.Font(EMOJI_FONT_PATH, 28)

class Game:
    def __init__(self, api=None):
        """Инициализация игры"""
        # ========== API И АВТОРИЗАЦИЯ ==========
        self.api = api
        self.token = self.api.token if self.api else None

        # ========== НАСТРОЙКИ ЭКРАНА ==========
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.fullscreen = True
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),
            pygame.FULLSCREEN | pygame.SCALED
        )
        pygame.display.set_caption("castle-survival v0.1")
        try:
            icon = pygame.image.load("assets/icon.png").convert_alpha()
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить иконку: {e}")
        self.clock = pygame.time.Clock()

        # ========== ШРИФТЫ ==========
        self.font_tiny = font_tiny
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large

        # ========== ОСНОВНЫЕ ПАРАМЕТРЫ ИГРЫ ==========
        from entities.player import создать_нового_игрока
        self.игрок = создать_нового_игрока()
        self.текущая_локация = "Убежище"
        self.игра_активна = True
        self.режим = "игра"
        self.игра_загружена = False
        self.previous_mode = "игра"

        # ========== ИГРОВЫЕ СИСТЕМЫ ==========
        self.quest_system = QuestSystem()
        self.battle = BattleSystem(self.игрок, self)
        self.dungeon = DungeonController(self)

        # ========== ХРАНИЛИЩА И ИНТЕРФЕЙС ==========
        self.chest_inventory = []
        self.buttons = []
        self.btn_new = None
        self.btn_load = None
        self.btn_exit = None

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
        load_item_icons(self)
        self.inventory = InventorySystem(self.игрок, self.item_icons)

        # ========== ЗАГРУЗКА РЕСУРСОВ ==========
        self.close_icon = None
        load_close_icon(self)

        # ========== МУЗЫКА ==========
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
        self.music = MusicManager(
            музыка_локаций=музыка_локаций,
            громкость=0.3,
            включена=True
        )
        self.logout_requested = False
        # ========== ГЛАВНОЕ МЕНЮ ==========
        menu_result = show_main_menu(self)
        print(f"🟢 Результат show_main_menu(): {menu_result}")

        # Пользователь вышел из аккаунта
        if menu_result == "logout":
            print("🔓 Запрошен выход из аккаунта")
            self.игра_активна = False
            self.logout_requested = True
            return

        if menu_result is None or menu_result is False:
            print("🔴 Выход из главного меню, игра завершается")
            self.игра_активна = False
            return

        self.игра_загружена = True

        # ========== ФОНЫ И ВИДЕО ==========
        self.backgrounds = {}
        load_backgrounds(self)
        self.video_manager = VideoManager()

        # ========== ИКОНКИ ДЕЙСТВИЙ ==========
        self.action_icons = {}
        load_action_icons(self)

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

        # ========== ПЕРСОНАЖ ==========
        self.player_size = 200
        self.player_pos = [WIDTH // 5 - self.player_size // 2, HEIGHT // 1.5 - self.player_size // 2]
        self.player_sprite = None
        load_player_sprite(self)

        # ========== ВРАГ ==========
        self.enemy_size = 190
        self.enemy_pos = [WIDTH // 2 - self.enemy_size // 2, 100]
        self.enemy_sprite = None
        self.current_enemy_for_display = None

        # ========== АНИМАЦИЯ НАЧАЛА БОЯ ==========
        self.battle_start_animation = False
        self.battle_start_timer = 0
        self.battle_start_alpha = 0
        self.battle_start_scale = 0.5

        # ========== ПАНЕЛЬ ЛУТА ==========
        self.loot_panel_active = False
        self.loot_items = []
        self.loot_exp = 0
        self.loot_rare_item = None
        self.loot_animation_progress = 0

        # ========== БОЕВЫЕ ПАРАМЕТРЫ (для совместимости) ==========
        self.blocking = False
        self.rage_active = False
        self.enemy_bleed_duration = 0
        self.enemy_bleed_damage = 5
        self.enemy_stunned = False
        self.enemy_weakened_duration = 0
        self.vampirism_active = False
        self.vampirism_duration = 0
        self.revive_used = False

        # ========== ШКАЛА ОБЫСКА ==========
        self.обыск_активен = False
        self.обыск_прогресс = 0
        self.обыск_таймер = 0
        self.обыск_длительность = 60
        self.обыск_x = WIDTH // 2 - 200
        self.обыск_y = HEIGHT // 2 + 100

        # ========== ОТОБРАЖЕНИЕ КВЕСТОВ ==========
        self.показывать_квесты = True
        self.квесты_позиция_x = WIDTH - 340
        self.квесты_позиция_y = 80

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
            self.screen = pygame.display.set_mode(
                (self.WIDTH, self.HEIGHT),
                pygame.FULLSCREEN | pygame.SCALED
            )
            print("🖥️ Полноэкранный режим включен")
        else:
            self.screen = pygame.display.set_mode(
                (self.WIDTH, self.HEIGHT)
            )
            print("🖥️ Оконный режим включен")

        # Возвращаем заголовок и иконку после пересоздания окна
        pygame.display.set_caption("castle-survival v0.1")
        try:
            icon = pygame.image.load("assets/icon.png").convert_alpha()
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить иконку: {e}")

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
                        upgrade_skill(self, item)
                    else:
                        learn_skill(self, item)
                    return

    def handle_click(self, pos):
        """Обработка кликов мыши в режиме 'игра'"""
        if self.режим != "игра":
            return
        if self.обыск_активен:
            return

        локация = локации.локации[self.текущая_локация]

        for action, rect in self.buttons:
            if not rect.collidepoint(pos):
                continue

            print(f"Кнопка: {action}")

            # ============================================================
            # 1. ОБЫСК (кнопка "й")
            # ============================================================
            if action == "й":
                if локация.get("хаб", False):
                    self.add_to_log("В убежище нечего искать...")
                    break

                if self.текущая_локация == "Зачарованный лес":
                    self.add_to_log("В лесу нужно нажать 'Исследовать лес'!")
                    break

                # Тратим сытость и жажду
                успех, сообщение = потратить_ресурсы(self.игрок, сытость_цена=3, жажда_цена=5)
                self.add_to_log(сообщение)

                # Проверяем голод/жажду
                урон, сообщение_голод = проверить_голод(self.игрок)
                if урон:
                    self.add_to_log(сообщение_голод)
                    if self.игрок["здоровье"] <= 0:
                        self.игрок_умер()
                        break

                # Запускаем шкалу прогресса
                self.запустить_шкалу_обыска()
                draw_status(self)
                pygame.display.flip()
                return

            # ============================================================
            # 2. ИНВЕНТАРЬ (кнопка "ц")
            # ============================================================
            elif action == "ц":
                self.inventory_animation_progress = 0
                self.режим = "инвентарь"

            # ============================================================
            # 3. СОХРАНЕНИЕ (кнопка "к")
            # ============================================================
            elif action == "к":
                show_save_menu(self)

            # ============================================================
            # 4. КАРТА (кнопка "у")
            # ============================================================
            elif action == "у":
                self.режим = "карта"

            # ============================================================
            # 5. ТОРГОВЛЯ (кнопка "т")
            # ============================================================
            elif action == "т" and локация.get("торговец", False):
                self.start_trade()

            # ============================================================
            # 6. КРАФТ (кнопка "в")
            # ============================================================
            elif action == "в" and локация.get("верстак", False):
                self.start_craft()

            # ============================================================
            # 7. ОСМОТР ПРУДА (кнопка "в_пруд")
            # ============================================================
            elif action == "в_пруд":
                self.add_to_log("Ты смотришь в тёмную воду...")

            # ============================================================
            # 8. ВЫХОД (кнопка "с")
            # ============================================================
            elif action == "с":
                if show_exit_dialog(self):
                    self.игра_активна = False
                    self.__init__()
                    return

            # ============================================================
            # 9. НАВЫКИ (кнопка "о")
            # ============================================================
            elif action == "о":
                self.skills_animation_progress = 0
                self.режим = "обучение"

            # ============================================================
            # 10. ВХОД В ЗАЧАРОВАННЫЙ ЛЕС (кнопка "о_лес")
            # ============================================================
            elif action == "о_лес":
                # Тратим сытость и жажду
                успех, сообщение = потратить_ресурсы(self.игрок, сытость_цена=2, жажда_цена=2)
                if not успех:
                    self.add_to_log(сообщение)
                    break
                self.add_to_log(сообщение)

                # Проверяем голод/жажду
                урон, сообщение_голод = игрок.проверить_голод(self.игрок)
                if урон:
                    self.add_to_log(сообщение_голод)
                    if self.игрок["здоровье"] <= 0:
                        self.игрок_умер()
                        break

                print("🌳 Вход в Зачарованный лес!")
                self.текущая_локация = "Зачарованный лес"
                self.dungeon.init_forest()
                self.режим = "эксплорейшн"
                self.exploration_in_battle = False

            # ============================================================
            # 11. ВХОД В ДРЕВНИЙ СКЛЕП (кнопка "о_склеп")
            # ============================================================
            elif action == "о_склеп":
                # Тратим сытость и жажду
                успех, сообщение = потратить_ресурсы(self.игрок, сытость_цена=2, жажда_цена=2)
                if not успех:
                    self.add_to_log(сообщение)
                    break
                self.add_to_log(сообщение)

                # Проверяем голод/жажду
                урон, сообщение_голод = игрок.проверить_голод()
                if урон:
                    self.add_to_log(сообщение_голод)
                    if self.игрок["здоровье"] <= 0:
                        self.игрок_умер()
                        break

                print("💀 Вход в Древний склеп!")
                self.текущая_локация = "Древний склеп"
                self.dungeon.init_crypt()
                self.режим = "эксплорейшн"
                self.exploration_in_battle = False

            # ============================================================
            # 12. ОТДЫХ В ХАБЕ (кнопка "о_хаб")
            # ============================================================
            elif action == "о_хаб":
                self.rest_in_hub()

            # ============================================================
            # 13. СУНДУК (кнопка "я")
            # ============================================================
            elif action == "я":
                self.open_chest()

            break

    def rest_in_hub(self):
        текущий_день = время.получить_день()
        if hasattr(self, 'last_rest_day') and self.last_rest_day == текущий_день:
            self.add_to_log("Ты уже отдыхал сегодня! Отдохнуть можно только раз в день.")
            print("❌ Отдых недоступен - уже отдыхал сегодня")
            return

        self.игрок["здоровье"] = self.игрок["макс_здоровье"]
        self.inventory.update_max_health()
        if "мана" in self.игрок:
            self.игрок["мана"] = self.игрок["макс_мана"]

        self.last_rest_day = текущий_день
        время.пройти_время(300)
        self.add_to_log("Ты отдохнул в убежище и полностью восстановил силы!")
        print(f"🛌 Игрок отдохнул в убежище. День отдыха: {текущий_день}")

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
            start_battle_gui(self, враг)

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

                        # 👇 ОТЛАДКА
                        print(f"   🔍 Найден предмет: {предмет}")
                        print(f"   🔍 Тип предмета: '{тип_предмета}'")
                        print(f"   🔍 'ежедневные_квесты' в игроке: {'ежедневные_квесты' in self.игрок}")
                        if "ежедневные_квесты" in self.игрок:
                            print(f"   🔍 Список ежедневных квестов: {self.игрок['ежедневные_квесты']}")

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

    def run(self):
        """Главный игровой цикл"""

        # ===== ЗАГРУЖАЕМ ЕЖЕДНЕВНЫЕ КВЕСТЫ =====
        if hasattr(self, 'quest_system') and hasattr(self, 'игрок'):
            self.quest_system.загрузить_ежедневные_квесты(self.игрок)

        предыдущий_день = время.получить_день()

        while self.игра_активна:

            # ============================================================
            # 1. ПРОВЕРКА СМЕРТИ
            # ============================================================
            if self.игрок["здоровье"] <= 0:
                self.игрок_умер()
                continue

            # ============================================================
            # 2. ОБРАБОТКА СОБЫТИЙ
            # ============================================================
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

                        # Режим "игра"
                        if self.режим == "игра":
                            self.handle_click(mouse_pos)
                            if hasattr(self, 'loot_button') and self.loot_button.collidepoint(mouse_pos):
                                close_loot_panel(self)

                        # Режим "эксплорейшн" (исследование данжей)
                        elif self.режим == "эксплорейшн":
                            # Кнопка "ЗАБРАТЬ" на панели лута
                            if hasattr(self, 'loot_button') and self.loot_button.collidepoint(mouse_pos):
                                close_loot_panel(self)

                            # Кнопка выхода из леса
                            if hasattr(self, 'exploration_exit_button') and self.exploration_exit_button.collidepoint(
                                    mouse_pos):
                                print("🚪 Выход из леса")
                                self.режим = "игра"
                                self.текущая_локация = "Сад"
                                self.in_dungeon = False
                                if hasattr(self, 'exploration_zone'):
                                    delattr(self, 'exploration_zone')

                            # Кнопки действий (инвентарь, карта, навыки, сохранить, выход)
                            for action, rect in self.buttons:
                                if rect.collidepoint(mouse_pos):
                                    print(f"🎯 Нажата кнопка в лесу: {action}")

                                    if action == "ц":
                                        print("📦 Открываем инвентарь")
                                        self.inventory_animation_progress = 0
                                        self.режим = "инвентарь"
                                        self.previous_mode = "эксплорейшн"
                                    elif action == "у":
                                        print("🗺️ Открываем карту")
                                        self.режим = "карта"
                                        self.previous_mode = "эксплорейшн"
                                    elif action == "о":
                                        print("📚 Открываем навыки")
                                        self.skills_animation_progress = 0
                                        self.режим = "обучение"
                                        self.previous_mode = "эксплорейшн"
                                    elif action == "к":
                                        print("💾 Сохраняем игру")
                                        show_save_menu(self)
                                    elif action == "с":
                                        print("🚪 Выход в главное меню")
                                        if show_exit_dialog(self):
                                            self.игра_активна = False
                                    break

                        # Остальные режимы (инвентарь, бой, торговля, карта и т.д.)
                        elif self.режим == "инвентарь":
                            handle_inventory_click(self, mouse_pos)
                        elif self.режим == "бой":
                            handle_battle_click(self, mouse_pos)
                        elif self.режим == "торговля":
                            handle_trade_click(self, mouse_pos)
                        elif self.режим == "quest_trade_menu":
                            self.handle_quest_trade_click(mouse_pos)
                        elif self.режим == "квесты":
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

            # ============================================================
            # 3. СМЕНА ДНЯ (сброс отдыха и обновление квестов)
            # ============================================================
            текущий_день = время.получить_день()
            if текущий_день != предыдущий_день:
                if hasattr(self, 'last_rest_day'):
                    self.last_rest_day = None
                self.add_to_log(f"Наступил новый день! (День {текущий_день})")
                print(f"🌅 Новый день! Отдых снова доступен.")
                self.quest_system.загрузить_ежедневные_квесты(self.игрок)
                print("📅 Ежедневные квесты обновлены!")
                предыдущий_день = текущий_день

            # ============================================================
            # 4. ОБНОВЛЕНИЕ ШКАЛЫ ОБЫСКА
            # ============================================================
            if self.обыск_активен:
                self.обыск_таймер += 1
                self.обыск_прогресс = self.обыск_таймер / self.обыск_длительность
                if self.обыск_прогресс >= 1:
                    self.обыск_активен = False
                    self.обыск_прогресс = 1
                    self.выполнить_обыск()

            # ============================================================
            # 5. ОБНОВЛЕНИЕ АНИМАЦИЙ
            # ============================================================
            self.update_transition()
            self.video_manager.update_transition_video(self)
            update_battle_animation(self)

            # ============================================================
            # 6. ОТРИСОВКА (в зависимости от режима)
            # ============================================================
            if self.режим == "игра":
                draw_location(self)
                draw_status(self)
                draw_actions(self)
                draw_log_panel(self)
                draw_battle_start_animation(self)
                draw_loot_panel(self)
                draw_quest_tracker(self)
                draw_daily_quest_tracker(self)
                draw_search_bar(self)

            elif self.режим == "инвентарь":
                draw_inventory(self)

            elif self.режим == "обучение":
                draw_skills_menu(self)

            elif self.режим == "бой":
                draw_battle(self)
                draw_battle_start_animation(self)

            elif self.режим == "торговля":
                draw_trade(self)

            elif self.режим == "quest_trade_menu":
                draw_quest_trade_menu(self)

            elif self.режим == "квесты":
                draw_quests(self)

            elif self.режим == "крафт":
                draw_craft(self)

            elif self.режим == "карта":
                draw_map(self)

            elif self.режим == "сундук":
                draw_chest(self)

            elif self.режим == "эксплорейшн":
                if hasattr(self, 'exploration_zone'):
                    self.dungeon.handle()
                    draw_loot_panel(self)
                else:
                    print("❌ exploration_zone не существует!")
                    self.режим = "игра"

            # ============================================================
            # 7. ОБНОВЛЕНИЕ ЭКРАНА
            # ============================================================
            pygame.display.flip()
            self.clock.tick(FPS)

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
    api = GameAPI()

    while True:
        token = None

        # ===== 1. Автологин по сохранённому токену =====
        saved_token = api.load_token()
        if saved_token:
            print("🔑 Найден сохранённый токен, проверяем на сервере...")
            if api.verify_token(saved_token):
                token = saved_token
                print("✅ Токен действителен — вход без пароля")
            else:
                print("⚠️ Токен недействителен, потребуется вход")
                try:
                    os.remove(api.token_file)
                except OSError:
                    pass
                api.token = None
        else:
            print("🔐 Сохранённого токена нет")

        # ===== 2. Окно логина, если токена нет =====
        if not token:
            login = LoginScreen(api=api)
            token = login.run()

        if not token:
            print("❌ Вход не выполнен. Выход.")
            pygame.quit()
            sys.exit()

        # ===== 3. Запуск игры =====
        print("✅ Вход выполнен! Запуск игры...")
        game = Game(api=api)
        game.run()

        # ===== 4. Проверяем, не запрошен ли logout =====
        if getattr(game, "logout_requested", False):
            print("🔓 Выход из аккаунта — возвращаемся к логину")
            pygame.display.quit()
            continue   # цикл заново → покажет LoginScreen
        else:
            break      # обычный выход

    pygame.quit()
    sys.exit()