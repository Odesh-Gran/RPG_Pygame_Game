import json
import math
import random
import sys
# noinspection PyUnresolvedReferences
from pyvidplayer2 import Video
import exploration
import барьеры
import верстак
import время
import локации
import предметы
import сохранение
import торговец
from skill_loader import SkillLoader
from systems.battle_system import BattleSystem
from systems.inventory_system import InventorySystem
import игрок
from игрок import потратить_ресурсы, проверить_голод
from systems.quest_system import QuestSystem

EMOJI_FONT_PATH = "C:/Windows/Fonts/seguiemj.ttf"
# ===== ИМПОРТ НАСТРОЕК =====
from config import *

# ===== ИНИЦИАЛИЗАЦИЯ =====
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Убежище в замке")
clock = pygame.time.Clock()

# ===== СОЗДАЁМ ШРИФТЫ =====
fonts = get_fonts()
font_tiny = fonts["tiny"]
font_small = fonts["small"]
font_medium = fonts["medium"]
font_large = fonts["large"]
font_emoji = pygame.font.Font(EMOJI_FONT_PATH, 28)


class Game:
    def __init__(self):
        """Инициализация игры"""

        # ========== НАСТРОЙКИ ЭКРАНА ==========
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.fullscreen = False

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Убежище в замке")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        # ========== ОСНОВНЫЕ ПАРАМЕТРЫ ИГРЫ ==========
        from игрок import создать_нового_игрока
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
        self.музыка_включена = True
        self.текущая_музыка = None
        self.громкость = 0.3
        self.текущий_плейлист = []
        self.индекс_в_плейлисте = 0

        # МУЗЫКА ДЛЯ ЛОКАЦИЙ
        self.музыка_локаций = {
            "Холл": [
                "assets/music/hall_1.mp3",
            ],
            "Кухня": [
                "assets/music/kitchen_1.mp3",
            ],
            "Сад": [
                "assets/music/garden_1.mp3",
            ],
            "Пруд": [
                "assets/music/pond_1.mp3",
            ],
            "Мастерская": [
                "assets/music/workshop_1.mp3",
            ],
            "Лестница": [
                "assets/music/stairs_1.mp3",
            ],
            "Библиотека": [
                "assets/music/library_1.mp3",
            ],
            "Коридор": [
                "assets/music/corridor_1.mp3",
            ],
            "Темница": [
                "assets/music/dungeon_1.mp3",
            ],
            "Главный зал": [
                "assets/music/great_hall_1.mp3",
            ],
            "Убежище": [
                "assets/music/ubegische_1.mp3",
                "assets/music/ubegische_2.mp3",
            ],
            "Зачарованный лес": [
                "assets/music/forest_1.mp3",
            ],
            "Древний склеп": [
                "assets/music/crypt_1.mp3",
            ],
            "бой": [
                "assets/music/battle_1.mp3",
            ],
            "меню": [
                "assets/music/menu_1.mp3",
            ],
        }

        # ========== СИСТЕМА БОЯ ==========
        self.battle = BattleSystem(self.игрок, self)

        # ========== ГЛАВНОЕ МЕНЮ ==========
        menu_result = self.show_main_menu()
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
        self.transition_video = None
        self.next_location = None
        self.video_transition_active = False

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
        from игрок import игрок as глобальный_игрок, изменить_уровень

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

        import предметы

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

        import предметы

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
        if self.video_transition_active:
            return

        self.play_transition_video("assets/videos/transition.mp4", новая_локация)

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
        import классы

        # ===== СБРАСЫВАЕМ ИГРОКА ПЕРЕД ПРИМЕНЕНИЕМ КЛАССА =====
        from игрок import создать_нового_игрока
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
        import классы

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
        from торговец import торговцы

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

    def draw_quest_trade_menu(self):
        """Рисует меню выбора: Квесты или Торговля"""

        # Анимация появления
        if not hasattr(self, 'quest_trade_animation_progress'):
            self.quest_trade_animation_progress = 0

        if self.quest_trade_animation_progress < 1:
            self.quest_trade_animation_progress += 0.08
            if self.quest_trade_animation_progress > 1:
                self.quest_trade_animation_progress = 1

        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Параметры панели
        panel_width = 500
        panel_height = 350
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Заголовок
        title = font_large.render("СТРАННИК", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 25))

        # Приветствие
        greeting = font_small.render('"Чем могу помочь?"', True, (200, 200, 180))
        greeting_x = panel_x + panel_width // 2 - greeting.get_width() // 2
        self.screen.blit(greeting, (greeting_x, panel_y + 75))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 30, panel_y + 110),
                         (panel_x + panel_width - 30, panel_y + 110), 2)

        mouse_pos = pygame.mouse.get_pos()

        # ===== КНОПКА "КВЕСТЫ" =====
        quest_rect = pygame.Rect(panel_x + 60, panel_y + 135, 380, 60)
        if quest_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, quest_rect)
            quest_text = font_medium.render("📜 КВЕСТЫ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, quest_rect)
            pygame.draw.rect(self.screen, GOLD, quest_rect, 2)
            quest_text = font_medium.render("📜 КВЕСТЫ", True, WHITE)

        quest_text_x = quest_rect.x + quest_rect.width // 2 - quest_text.get_width() // 2
        quest_text_y = quest_rect.y + quest_rect.height // 2 - quest_text.get_height() // 2
        self.screen.blit(quest_text, (quest_text_x, quest_text_y))
        self.quest_trade_buttons = [("quests", quest_rect)]

        # ===== КНОПКА "ТОРГОВЛЯ" =====
        trade_rect = pygame.Rect(panel_x + 60, panel_y + 215, 380, 60)
        if trade_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, trade_rect)
            trade_text = font_medium.render("💰 ТОРГОВЛЯ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, trade_rect)
            pygame.draw.rect(self.screen, GOLD, trade_rect, 2)
            trade_text = font_medium.render("💰 ТОРГОВЛЯ", True, WHITE)

        trade_text_x = trade_rect.x + trade_rect.width // 2 - trade_text.get_width() // 2
        trade_text_y = trade_rect.y + trade_rect.height // 2 - trade_text.get_height() // 2
        self.screen.blit(trade_text, (trade_text_x, trade_text_y))
        self.quest_trade_buttons.append(("trade", trade_rect))

        # ===== КНОПКА "НАЗАД" =====
        back_rect = pygame.Rect(panel_x + panel_width // 2 - 70, panel_y + panel_height - 50, 140, 35)
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
        self.quest_trade_buttons.append(("back", back_rect))

        self.quest_trade_back = back_rect

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
                    from торговец import торговцы
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

    def draw_status(self):
        """Отрисовка красивого статус-бара"""

        # ===== ПАРАМЕТРЫ ПАНЕЛИ =====
        panel_x = 380
        panel_y = HEIGHT - 180
        panel_width = 450
        panel_height = 180

        # ===== ФОН С ГРАДИЕНТОМ =====
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        for i in range(panel_height):
            ratio = i / panel_height
            r = int(15 + 20 * ratio)
            g = int(15 + 15 * ratio)
            b = int(30 + 30 * ratio)
            color = (r, g, b, 220)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

        pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)

        corner_size = 10
        corners = [(2, 2), (panel_width - corner_size - 2, 2), (2, panel_height - corner_size - 2),
                   (panel_width - corner_size - 2, panel_height - corner_size - 2)]
        for cx, cy in corners:
            pygame.draw.rect(panel_surface, GOLD, (cx, cy, corner_size, corner_size), 2)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        # ===== ЗАГОЛОВОК =====
        title = font_medium.render("ГЕРОЙ", True, GOLD)
        self.screen.blit(title, (panel_x + 15, panel_y + 8))

        # ===== ИМЯ И КЛАСС =====
        name_text = font_small.render(f"{self.игрок['имя']} | {self.игрок['класс'] or 'Без класса'}", True, WHITE)
        self.screen.blit(name_text, (panel_x + 15, panel_y + 35))

        # ===== ВРЕМЯ (СПРАВА ВВЕРХУ) =====
        import время
        время_строка = время.показать_время()
        день = время.получить_день()

        # Определяем цвет в зависимости от времени суток
        час = время.получить_час()
        if 6 <= час < 12:
            цвет_времени = (255, 200, 100)  # Утро - золотистый
            иконка = ""
        elif 12 <= час < 18:
            цвет_времени = (255, 255, 200)  # День - светло-жёлтый
            иконка = ""
        elif 18 <= час < 22:
            цвет_времени = (255, 150, 50)  # Вечер - оранжевый
            иконка = ""
        else:
            цвет_времени = (100, 150, 255)  # Ночь - голубой
            иконка = ""

        время_текст = font_small.render(f"{иконка} {время_строка} | День {день}", True, цвет_времени)
        время_x = panel_x + panel_width - время_текст.get_width() - 15
        self.screen.blit(время_текст, (время_x, panel_y + 10))

        # ===== ЛЕВАЯ ЧАСТЬ: ЗДОРОВЬЕ И МАНА =====
        left_x = panel_x + 15
        left_width = 175

        # Здоровье
        hp_y = panel_y + 60
        hp_text = font_small.render("HP", True, HEALTH_GREEN)
        self.screen.blit(hp_text, (left_x, hp_y))

        hp_bar_x = left_x + 35
        hp_bar_y = hp_y + 2
        hp_bar_width = left_width - 35
        hp_bar_height = 18

        pygame.draw.rect(self.screen, (40, 40, 50), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(self.screen, (60, 60, 80), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 1)

        # Защита от деления на ноль
        if self.игрок['макс_здоровье'] <= 0:
            self.игрок['макс_здоровье'] = 100

        hp_percent = self.игрок['здоровье'] / self.игрок['макс_здоровье']

        if hp_percent > 0.6:
            hp_color = HEALTH_GREEN
        elif hp_percent > 0.3:
            hp_color = HEALTH_YELLOW
        else:
            hp_color = HEALTH_RED

        hp_fill = int(hp_bar_width * hp_percent)
        if hp_fill > 0:
            pygame.draw.rect(self.screen, hp_color, (hp_bar_x + 1, hp_bar_y + 1, hp_fill - 2, hp_bar_height - 2))

        hp_value = font_small.render(f"{self.игрок['здоровье']}/{self.игрок['макс_здоровье']}", True, WHITE)
        hp_value_x = hp_bar_x + hp_bar_width // 2 - hp_value.get_width() // 2
        self.screen.blit(hp_value, (hp_value_x, hp_bar_y + 2))

        # Мана
        mana_y = hp_y + hp_bar_height + 8
        mana_text = font_small.render("MP", True, (120, 180, 255))
        self.screen.blit(mana_text, (left_x, mana_y))

        mana_bar_x = hp_bar_x
        mana_bar_y = mana_y + 2
        mana_bar_width = hp_bar_width
        mana_bar_height = 18

        pygame.draw.rect(self.screen, (40, 40, 50), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
        pygame.draw.rect(self.screen, (60, 60, 80), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 1)

        if self.игрок.get('макс_мана', 50) > 0:
            mana_percent = self.игрок.get('мана', 0) / self.игрок.get('макс_мана', 50)
            mana_fill = int(mana_bar_width * mana_percent)
            if mana_fill > 0:
                pygame.draw.rect(self.screen, (80, 150, 255),
                                 (mana_bar_x + 1, mana_bar_y + 1, mana_fill - 2, mana_bar_height - 2))

        mana_value = font_small.render(f"{self.игрок.get('мана', 0)}/{self.игрок.get('макс_мана', 50)}", True, WHITE)
        mana_value_x = mana_bar_x + mana_bar_width // 2 - mana_value.get_width() // 2
        self.screen.blit(mana_value, (mana_value_x, mana_bar_y + 2))

        # ===== ПРАВАЯ ЧАСТЬ: СЫТОСТЬ И ЖАЖДА =====
        right_x = panel_x + panel_width - 190
        right_width = 155

        hunger_y = panel_y + 60
        hunger_text = font_small.render("Голод", True, (200, 180, 150))
        self.screen.blit(hunger_text, (right_x - 1, hunger_y))

        hunger_bar_x = right_x + 55
        hunger_bar_y = hunger_y + 2
        hunger_bar_width = right_width - 55
        hunger_bar_height = 18

        pygame.draw.rect(self.screen, (40, 40, 50), (hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height))
        pygame.draw.rect(self.screen, (60, 60, 80), (hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height),
                         1)

        сытость = self.игрок.get("сытость", 100)
        hunger_fill = int(hunger_bar_width * (сытость / 100))

        if сытость > 70:
            hunger_color = HEALTH_GREEN
        elif сытость > 40:
            hunger_color = HEALTH_YELLOW
        else:
            hunger_color = HEALTH_RED

        if hunger_fill > 0:
            pygame.draw.rect(self.screen, hunger_color,
                             (hunger_bar_x + 1, hunger_bar_y + 1, hunger_fill - 2, hunger_bar_height - 2))

        hunger_value = font_small.render(f"{сытость}%", True, WHITE)
        hunger_value_x = hunger_bar_x + hunger_bar_width // 2 - hunger_value.get_width() // 2
        self.screen.blit(hunger_value, (hunger_value_x, hunger_bar_y + 2))

        # Жажда
        thirst_y = hunger_y + hunger_bar_height + 8
        thirst_text = font_small.render("Жажда", True, (100, 200, 255))
        self.screen.blit(thirst_text, (right_x - 10, thirst_y))

        thirst_bar_x = hunger_bar_x
        thirst_bar_y = thirst_y + 2
        thirst_bar_width = hunger_bar_width
        thirst_bar_height = 18

        pygame.draw.rect(self.screen, (40, 40, 50), (thirst_bar_x, thirst_bar_y, thirst_bar_width, thirst_bar_height))
        pygame.draw.rect(self.screen, (60, 60, 80), (thirst_bar_x, thirst_bar_y, thirst_bar_width, thirst_bar_height),
                         1)

        жажда = self.игрок.get("жажда", 100)
        thirst_fill = int(thirst_bar_width * (жажда / 100))

        if жажда > 70:
            thirst_color = (100, 200, 255)
        elif жажда > 40:
            thirst_color = HEALTH_YELLOW
        else:
            thirst_color = HEALTH_RED

        if thirst_fill > 0:
            pygame.draw.rect(self.screen, thirst_color,
                             (thirst_bar_x + 1, thirst_bar_y + 1, thirst_fill - 2, thirst_bar_height - 2))

        thirst_value = font_small.render(f"{жажда}%", True, WHITE)
        thirst_value_x = thirst_bar_x + thirst_bar_width // 2 - thirst_value.get_width() // 2
        self.screen.blit(thirst_value, (thirst_value_x, thirst_bar_y + 2))

        # ===== УРОВЕНЬ И ОПЫТ (ВНИЗУ) =====
        bottom_y = max(mana_y + mana_bar_height + 8, thirst_y + thirst_bar_height + 8) + 8
        level_text = font_small.render(f"LVL {self.игрок['уровень']}", True, GOLD)
        self.screen.blit(level_text, (left_x, bottom_y))

        exp_bar_x = left_x + 60
        exp_bar_y = bottom_y + 2
        exp_bar_width = panel_width - 80 - 170
        exp_bar_height = 16

        pygame.draw.rect(self.screen, (40, 40, 50), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height))
        pygame.draw.rect(self.screen, (60, 60, 80), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height), 1)

        if self.игрок['опыта_до_след_уровня'] > 0:
            exp_percent = self.игрок['опыт'] / self.игрок['опыта_до_след_уровня']
            exp_fill = int(exp_bar_width * exp_percent)
            if exp_fill > 0:
                for i in range(exp_fill):
                    ratio = i / exp_fill
                    r = int(150 + 105 * ratio)
                    g = int(50 + 165 * ratio)
                    b = int(200 - 100 * ratio)
                    pygame.draw.line(self.screen, (r, g, b), (exp_bar_x + 1 + i, exp_bar_y + 1),
                                     (exp_bar_x + 1 + i, exp_bar_y + exp_bar_height - 1))

        exp_value = font_small.render(f"{self.игрок['опыт']}/{self.игрок['опыта_до_след_уровня']}", True, WHITE)
        exp_value_x = exp_bar_x + exp_bar_width // 2 - exp_value.get_width() // 2
        self.screen.blit(exp_value, (exp_value_x, exp_bar_y + 2))

        # ===== МОНЕТЫ =====
        coins_text = font_small.render(f"Gold: {self.игрок.get('монета', 0)}", True, GOLD)
        coins_x = panel_x + panel_width - coins_text.get_width() - 15
        self.screen.blit(coins_text, (coins_x, bottom_y))

    def draw_location(self):
        """Отрисовка описания локации с фоном"""

        # ===== ЕСЛИ ИДЁТ ВИДЕО-ПЕРЕХОД — НЕ РИСУЕМ ЛОКАЦИЮ =====
        if self.режим == "видео_переход":
            # Видео отрисовывается в update_transition_video()
            return
        # ======================================================

        # Рисуем фон, если есть
        if self.текущая_локация in self.backgrounds:
            self.screen.blit(self.backgrounds[self.текущая_локация], (0, 0))
        else:
            self.screen.fill(BLACK)

        # Затемнение для читаемости текста
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        # Название локации (ВСЕГДА ВИДНО)
        title_text = font_large.render(self.текущая_локация, True, GOLD)
        self.screen.blit(title_text, (5, 5))

        # ОПИСАНИЕ С ТАЙМЕРОМ
        if self.show_description:
            локация = локации.локации[self.текущая_локация]
            lines = локация["описание"].split('\n')
            y = 40
            for line in lines:
                if line:
                    desc_text = font_small.render(line.strip(), True, WHITE)
                    self.screen.blit(desc_text, (15, y))
                    y += 25

            # Увеличиваем таймер
            self.description_timer += 1
            if self.description_timer >= self.description_duration:
                self.show_description = False
                self.description_timer = 0
                print("⏰ Описание скрыто")  # для отладки

        # ===== ОТРИСОВКА ПЕРСОНАЖА (ПОВЕРХ ВСЕГО) =====
        # self.draw_player()

            # ===== АНИМАЦИЯ ПЕРЕХОДА (РИСУЕМ ПОВЕРХ ВСЕГО) =====
        if self.transition_active and self.transition_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.transition_alpha)))
            self.screen.blit(overlay, (0, 0))

    def draw_actions(self):
        """Отрисовка горизонтальной панели действий с иконками"""

        локация = локации.локации[self.текущая_локация]

        # Очищаем список кнопок
        self.buttons = []

        # Параметры панели
        icon_size = 64
        icon_spacing = 10
        panel_padding = 15

        # Собираем все иконки в список
        icon_list = []

        # ===== ДЛЯ ЛЕСА - ТОЛЬКО НУЖНЫЕ КНОПКИ =====
        if self.текущая_локация == "Зачарованный лес":
            # В лесу только: Инвентарь, Навыки, Выход
            icon_list.append(("ц", "inventory", "Инвентарь"))
            icon_list.append(("о", "skills", "Навыки"))
            icon_list.append(("с", "exit", "Выход"))

        else:
            # ===== ДЛЯ ОБЫЧНЫХ ЛОКАЦИЙ =====
            # Кнопка обыска (не для хаба)
            if not локация.get("хаб", False):
                icon_list.append(("й", "search", "Обыск"))

            icon_list.append(("ц", "inventory", "Инвентарь"))
            icon_list.append(("у", "map", "Карта"))
            icon_list.append(("о", "skills", "Навыки"))

            # Кнопки для хаба
            if локация.get("хаб", False):
                icon_list.append(("о_хаб", "rest", "Отдохнуть"))
                icon_list.append(("я", "chest", "Сундук"))

            # Дополнительные иконки
            if локация.get("торговец", False):
                icon_list.append(("т", "trade", "Торговец"))
            if локация.get("верстак", False):
                icon_list.append(("в", "craft", "Верстак"))
            if self.текущая_локация == "Пруд":
                icon_list.append(("в_пруд", "examine", "Осмотреть"))

            # Кнопка для входа в лес (если это обычная локация, а не лес)
            if self.текущая_локация != "Зачарованный лес" and локации.локации.get("Зачарованный лес"):
                # Можно добавить, но не обязательно
                pass

            # ===== КНОПКИ ДЛЯ ВХОДА В ДАНЖИ =====
            if self.текущая_локация == "Сад":
                icon_list.append(("о_лес", "explore", "Исследовать лес"))

            if self.текущая_локация == "Темница":
                icon_list.append(("о_склеп", "explore", "Войти в склеп"))

            # Кнопки сохранения и выхода
            icon_list.append(("к", "save", "Сохранить"))
            icon_list.append(("с", "exit", "Выход"))

        # ===== ВЫХОД ВСЕГДА В КОНЦЕ (уже добавлен выше) =====
        # Для леса мы уже добавили "с" в список выше

        # Рассчитываем размер панели
        panel_width = len(icon_list) * (icon_size + icon_spacing) + panel_padding
        panel_height = icon_size + panel_padding * 2

        # Позиция панели (внизу по центру)
        panel_x = (WIDTH - panel_width) // 1
        panel_y = HEIGHT - panel_height - 0

        # Рисуем фон панели
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((26, 26, 46, 180))
        pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Рисуем иконки в ряд
        start_x = panel_x + panel_padding

        for i, (action, icon_key, tooltip) in enumerate(icon_list):
            x = start_x + i * (icon_size + icon_spacing)
            y = panel_y + panel_padding

            icon_rect = pygame.Rect(x, y, icon_size, icon_size)
            is_hover = icon_rect.collidepoint(pygame.mouse.get_pos())

            # Фон иконки
            if is_hover:
                pygame.draw.rect(self.screen, GOLD, icon_rect)
                # Подсказка
                tooltip_text = font_small.render(tooltip, True, WHITE)
                tooltip_x = x + icon_size // 2 - tooltip_text.get_width() // 2
                tooltip_y = y - 25
                tip_bg = pygame.Surface((tooltip_text.get_width() + 10, 25), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 200))
                self.screen.blit(tip_bg, (tooltip_x - 5, tooltip_y - 5))
                self.screen.blit(tooltip_text, (tooltip_x, tooltip_y))
            else:
                pygame.draw.rect(self.screen, DARK_RED, icon_rect)
                pygame.draw.rect(self.screen, GOLD, icon_rect, 2)

            # Иконка
            if icon_key in self.action_icons and self.action_icons[icon_key]:
                icon = self.action_icons[icon_key]
                icon = pygame.transform.scale(icon, (icon_size - 8, icon_size - 8))
                self.screen.blit(icon, (x + 4, y + 4))

            self.buttons.append((action, icon_rect))

    def draw_skills_menu(self):
        """Меню навыков с вертикальными вкладками слева"""

        # Анимация появления
        if not hasattr(self, 'skills_animation_progress'):
            self.skills_animation_progress = 0

        if self.skills_animation_progress < 1:
            self.skills_animation_progress += 0.08
            if self.skills_animation_progress > 1:
                self.skills_animation_progress = 1

        # Параметры панели
        panel_width = 900
        panel_height = 600
        start_y = -panel_height
        current_y = start_y + (panel_height * self.skills_animation_progress)
        panel_y = int(current_y)

        # Сдвигаем панель вправо, чтобы освободить место для вкладок
        panel_x = WIDTH // 2 - panel_width // 2

        # Фон с затемнением
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Основная панель с градиентом
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        for i in range(panel_height):
            ratio = i / panel_height
            r = int(26 + 20 * ratio)
            g = int(26 + 10 * ratio)
            b = int(46 + 30 * ratio)
            color = (r, g, b)
            pygame.draw.line(self.screen, color,
                             (panel_x, panel_y + i),
                             (panel_x + panel_width, panel_y + i))

        # Золотая рамка
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Уголки
        corner_size = 20
        corners = [
            (panel_x, panel_y),
            (panel_x + panel_width - corner_size, panel_y),
            (panel_x, panel_y + panel_height - corner_size),
            (panel_x + panel_width - corner_size, panel_y + panel_height - corner_size)
        ]
        for cx, cy in corners:
            pygame.draw.rect(self.screen, GOLD, (cx, cy, corner_size, corner_size), 2)
            pygame.draw.line(self.screen, GOLD, (cx + 5, cy + 5), (cx + corner_size - 5, cy + corner_size - 5), 1)
            pygame.draw.line(self.screen, GOLD, (cx + corner_size - 5, cy + 5), (cx + 5, cy + corner_size - 5), 1)

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
        self.prof_tab_rect = None
        self.combat_tab_rect = None

        # Рисуем вертикальные вкладки
        for i, tab in enumerate(tabs):
            y = start_y + i * (tab_height + tab_spacing)
            tab_rect = pygame.Rect(start_x, y, tab_width, tab_height)

            # Сохраняем ссылки для кликов
            if tab["id"] == "prof":
                self.prof_tab_rect = tab_rect
            else:
                self.combat_tab_rect = tab_rect

            # Определяем, активна ли вкладка
            is_active = (self.current_skill_tab == tab["id"])
            is_hover = tab_rect.collidepoint(mouse_pos)

            # Фон вкладки
            if is_active:
                # Активная вкладка - золотая
                pygame.draw.rect(self.screen, GOLD, tab_rect)
                # Соединительная линия с панелью
                pygame.draw.rect(self.screen, GOLD, (tab_rect.right, tab_rect.y, 5, tab_height))
                text_color = BLACK
            elif is_hover:
                # Подсветка при наведении
                pygame.draw.rect(self.screen, (60, 60, 80), tab_rect)
                pygame.draw.rect(self.screen, GOLD, tab_rect, 2)
                text_color = GOLD
            else:
                # Обычная вкладка
                pygame.draw.rect(self.screen, DARK_RED, tab_rect)
                pygame.draw.rect(self.screen, GOLD, tab_rect, 2)
                text_color = WHITE

            # Иконка
            icon_text = font_medium.render(tab["icon"], True, text_color)
            self.screen.blit(icon_text, (tab_rect.x + 8, tab_rect.y + 8))

            # Текст (вертикально, в две строки)
            label_lines = tab["label"].split()
            if len(label_lines) > 1:
                for j, line in enumerate(label_lines):
                    label_text = font_small.render(line, True, text_color)
                    label_x = tab_rect.x + tab_width // 2 - label_text.get_width() // 2
                    label_y = tab_rect.y + 30 + j * 18
                    self.screen.blit(label_text, (label_x, label_y))
            else:
                label_text = font_small.render(tab["label"], True, text_color)
                label_x = tab_rect.x + tab_width // 2 - label_text.get_width() // 2
                label_y = tab_rect.y + tab_height // 2 - label_text.get_height() // 2 + 5
                self.screen.blit(label_text, (label_x, label_y))

        # Заголовок (меняется от вкладки)
        if self.current_skill_tab == "prof":
            title_text = "ПРОФЕССИОНАЛЬНЫЕ НАВЫКИ"
        else:
            title_text = "БОЕВЫЕ НАВЫКИ"

        title = font_large.render(title_text, True, GOLD)
        title_shadow = font_large.render(title_text, True, (80, 60, 30))
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title_shadow, (title_x + 3, panel_y + 23))
        self.screen.blit(title, (title_x, panel_y + 20))

        # Декоративные линии под заголовком
        line_y = panel_y + 70
        for i in range(3):
            alpha = 100 - i * 30
            line_width = panel_width - 100 - i * 20
            line_x = panel_x + 50 + i * 10
            pygame.draw.line(self.screen, (GOLD[0], GOLD[1], GOLD[2], alpha),
                             (line_x, line_y + i),
                             (line_x + line_width, line_y + i), 2)

        # Очки умений (для профессий)
        points_prof = self.игрок.get('очки_умений', 0)
        if points_prof > 0:
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            pulse_alpha = int(100 + 155 * pulse)
            prof_color = (255, 215, 0, pulse_alpha)
        else:
            prof_color = GOLD

        # Очки навыков (для боевых)
        points_combat = self.игрок.get('очки_навыков', 0)
        if points_combat > 0:
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            pulse_alpha = int(100 + 155 * pulse)
            combat_color = (255, 215, 0, pulse_alpha)
        else:
            combat_color = GOLD

        # Текст очков умений
        prof_text = font_medium.render(f"ОЧКИ УМЕНИЙ: {points_prof}", True, prof_color)
        prof_x = panel_x + panel_width // 2 - prof_text.get_width() // 2
        self.screen.blit(prof_text, (prof_x, panel_y + 85))

        # Текст очков навыков
        combat_text = font_medium.render(f"ОЧКИ НАВЫКОВ: {points_combat}", True, combat_color)
        combat_x = panel_x + panel_width // 2 - combat_text.get_width() // 2
        self.screen.blit(combat_text, (combat_x, panel_y + 115))

        # ===== БЛОК ХАРАКТЕРИСТИК - ТОЛЬКО ДЛЯ ПРОФЕССИОНАЛЬНЫХ НАВЫКОВ =====
        if self.current_skill_tab == "prof":
            stats_y = panel_y + 160
            stats_bg = pygame.Surface((400, 100), pygame.SRCALPHA)
            stats_bg.fill((0, 0, 0, 100))
            self.screen.blit(stats_bg, (panel_x + 30, stats_y))
            pygame.draw.rect(self.screen, GOLD, (panel_x + 30, stats_y, 400, 100), 1)

            stats_title = font_small.render("ХАРАКТЕРИСТИКИ", True, GOLD)
            self.screen.blit(stats_title, (panel_x + 40, stats_y + 8))

            stats_list = [
                ("СИЛА", self.игрок['сила'], f"+{self.игрок['сила'] // 2} урона"),
                ("ЛОВКОСТЬ", self.игрок['ловкость'],
                 f"+{self.игрок['ловкость'] // 2}% крита, +{self.игрок['ловкость'] // 4}% уклонения"),
                ("СТОЙКОСТЬ", self.игрок['стойкость'], f"+{self.игрок['стойкость'] * 10} здоровья"),
                ("ИНТЕЛЛЕКТ", self.игрок['интеллект'], f"+{self.игрок['интеллект']} магии")
            ]

            for i, (name, value, bonus) in enumerate(stats_list):
                y = stats_y + 30 + i * 18
                name_text = font_tiny.render(name, True, WHITE)
                self.screen.blit(name_text, (panel_x + 45, y))
                value_text = font_tiny.render(str(value), True, GOLD)
                self.screen.blit(value_text, (panel_x + 130, y))

                bar_width = 120
                bar_height = 4
                bar_x = panel_x + 170
                bar_y = y + 6
                pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
                fill_width = int(bar_width * (value / 20))
                pygame.draw.rect(self.screen, GOLD, (bar_x, bar_y, fill_width, bar_height))

                bonus_text = font_tiny.render(bonus, True, HEALTH_GREEN)
                self.screen.blit(bonus_text, (panel_x + 300, y))

        # ===== РАЗДЕЛИТЕЛЬ ПОСЛЕ ЗАГОЛОВКА =====
        # Убираем старые вкладки, теперь разделитель просто под заголовком
        line_y_after_header = panel_y + 155 if self.current_skill_tab == "prof" else panel_y + 140
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 30, line_y_after_header),
                         (panel_x + panel_width - 30, line_y_after_header), 2)

        # ===== СОДЕРЖИМОЕ =====
        self.skill_buttons = []

        if self.current_skill_tab == "prof":
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
            self.screen.blit(skills_bg, (panel_x + 30, skills_y - 10))

            for i, skill in enumerate(skills):
                value = self.игрок.get(skill["key"], 0)
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
                    self.screen.blit(hover_bg, skill_rect)

                pygame.draw.rect(self.screen, (80, 80, 100), skill_rect, 1)

                # Иконка (увеличенная)
                icon_surf = self._create_skill_icon("")
                icon_surf = pygame.transform.scale(icon_surf, (48, 48))
                self.screen.blit(icon_surf, (skill_rect.x + 15, skill_rect.y + 16))

                # Название
                name_text = font_medium.render(skill["name"], True, skill["color"])
                self.screen.blit(name_text, (skill_rect.x + 75, skill_rect.y + 15))

                # Уровень
                level_text = font_small.render(f"Уровень {value}/{max_value}", True, WHITE)
                self.screen.blit(level_text, (skill_rect.x + 75, skill_rect.y + 42))

                # Полоса прогресса
                bar_width = 200
                bar_height = 8
                bar_x = skill_rect.x + 280
                bar_y = skill_rect.y + 28
                pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
                fill_width = int(bar_width * (value / max_value))
                pygame.draw.rect(self.screen, skill["color"], (bar_x, bar_y, fill_width, bar_height))

                # Описание
                desc_text = font_small.render(desc, True, GRAY)
                self.screen.blit(desc_text, (skill_rect.x + 500, skill_rect.y + 28))

                # Кнопка "+"
                if points_prof > 0 and value < max_value:
                    plus_rect = pygame.Rect(skill_rect.x + skill_rect.width - 55, skill_rect.y + 22, 40, 35)

                    if plus_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(self.screen, GOLD, plus_rect)
                        plus_text = font_large.render("+", True, BLACK)
                    else:
                        pygame.draw.rect(self.screen, DARK_RED, plus_rect)
                        pygame.draw.rect(self.screen, GOLD, plus_rect, 2)
                        plus_text = font_large.render("+", True, WHITE)

                    self.screen.blit(plus_text, (plus_rect.x + 8, plus_rect.y - 2))
                    self.skill_buttons.append((skill["key"], plus_rect))

        else:
            # ===== БОЕВЫЕ НАВЫКИ ИЗ JSON - 3 ВЕТКИ =====
            if not hasattr(self, 'skills_data') or not self.skills_data:
                no_data_text = font_small.render("Навыки не загружены!", True, HEALTH_RED)
                self.screen.blit(no_data_text, (panel_x + panel_width // 2 - 100, panel_y + 350))
            else:
                # Получаем первые 3 ветки
                ветки = list(self.skills_data["ветки"].keys())[:3]
                колонка_ширина = panel_width // 3 - 40
                колонка_x = [panel_x + 30, panel_x + колонка_ширина + 50, panel_x + колонка_ширина * 2 + 70]

                skills_y = panel_y + 180
                skills_bg = pygame.Surface((840, 360), pygame.SRCALPHA)
                skills_bg.fill((0, 0, 0, 80))
                self.screen.blit(skills_bg, (panel_x + 30, skills_y - 10))

                # Отображаем 3 ветки
                for idx, название_ветки in enumerate(ветки):
                    if idx >= 3:
                        break

                    branch_title = font_small.render(название_ветки, True, GOLD)
                    self.screen.blit(branch_title, (колонка_x[idx] + 20, skills_y - 5))

                    навыки_ветки = self.skills_data["ветки"][название_ветки]["навыки"]
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
                            self.screen.blit(hover_bg, row_rect)

                        pygame.draw.rect(self.screen, (80, 80, 100), row_rect, 1)

                        # Иконка
                        icon_surf = self._create_skill_icon("")
                        icon_surf = pygame.transform.scale(icon_surf, (24, 24))
                        self.screen.blit(icon_surf, (колонка_x[idx] + 18, y_offset + 12))

                        # Название
                        name_text = font_tiny.render(skill_name, True, name_color)
                        self.screen.blit(name_text, (колонка_x[idx] + 48, y_offset + 4))

                        # Тип
                        type_surface = font_tiny.render(type_text, True, WHITE)
                        self.screen.blit(type_surface, (колонка_x[idx] + 48, y_offset + 20))

                        # Описание
                        if len(skill_desc) > 14:
                            skill_desc = skill_desc[:12] + "..."
                        desc_text = font_tiny.render(skill_desc, True, GRAY)
                        self.screen.blit(desc_text, (колонка_x[idx] + 48, y_offset + 34))

                        # Кнопка "ВЫУЧИТЬ"
                        is_learned = skill_id in self.игрок.get("выученные_навыки", [])

                        if not is_learned and points_combat > 0:
                            btn_rect = pygame.Rect(колонка_x[idx] + колонка_ширина - 50, y_offset + 16, 55, 24)

                            if btn_rect.collidepoint(mouse_pos):
                                pygame.draw.rect(self.screen, GOLD, btn_rect)
                                btn_text = font_tiny.render("ВЫУЧИТЬ", True, BLACK)
                            else:
                                pygame.draw.rect(self.screen, DARK_RED, btn_rect)
                                pygame.draw.rect(self.screen, GOLD, btn_rect, 1)
                                btn_text = font_tiny.render("ВЫУЧИТЬ", True, WHITE)

                            self.screen.blit(btn_text, (btn_rect.x + 4, btn_rect.y + 5))
                            self.skill_buttons.append((skill_id, btn_rect))
                        elif is_learned:
                            learned_text = font_tiny.render("ВЫУЧЕНО", True, HEALTH_GREEN)
                            self.screen.blit(learned_text, (колонка_x[idx] + колонка_ширина - 65, y_offset + 14))

                        y_offset += 56

        # Кнопка "Назад"
        back_rect = pygame.Rect(panel_x + panel_width // 2 - 80, panel_y + panel_height - 45, 160, 40)

        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, back_rect)
            back_text = font_medium.render("НАЗАД", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, back_rect)
            pygame.draw.rect(self.screen, GOLD, back_rect, 2)
            back_text = font_medium.render("НАЗАД", True, WHITE)

        text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
        text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))

        self.skill_back_button = back_rect

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

            # ИСПОЛЬЗУЕМ СУЩЕСТВУЮЩУЮ ФУНКЦИЮ из игрок.py
            from игрок import игрок as глобальный_игрок, добавить_пассивный_бонус

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
                    self.show_save_menu()

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

                    урон, сообщение_голод = игрок.проверить_голод()
                    if урон:
                        self.add_to_log(сообщение_голод)
                        if self.игрок["здоровье"] <= 0:
                            self.игрок_умер()
                            break
                    # =====================================================

                    print("🌳 Вход в Зачарованный лес!")
                    self.текущая_локация = "Зачарованный лес"
                    self.init_forest_exploration()
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
                    self.init_crypt_exploration()
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
                            self.show_save_menu_for_exit()
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

    def show_save_menu_for_exit(self):
        """Меню выбора слота для сохранения перед выходом"""

        saves_info = сохранение.list_saves()

        # Параметры прокрутки
        scroll_offset = 0
        visible_slots = 4
        total_slots = 5

        waiting = True
        selected_slot = None

        while waiting:
            # Затемнение фона
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (0, 0))

            # Заголовок
            title = font_large.render("СОХРАНЕНИЕ", True, GOLD)
            title_x = WIDTH // 2 - title.get_width() // 2
            self.screen.blit(title, (title_x, 60))

            subtitle = font_medium.render("Выберите слот для сохранения:", True, WHITE)
            sub_x = WIDTH // 2 - subtitle.get_width() // 2
            self.screen.blit(subtitle, (sub_x, 120))

            # Слоты
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
                    pygame.draw.rect(self.screen, DARK_BLUE, slot_rect)
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 2)

                    slot_text = font_medium.render(f"СЛОТ {slot}", True, GOLD)
                    self.screen.blit(slot_text, (start_x + 20, y + 12))

                    line1 = f"{save_info['class']} | Уровень {save_info['level']}"
                    line1_text = font_small.render(line1, True, WHITE)
                    line1_x = start_x + slot_width // 2 - line1_text.get_width() // 2
                    self.screen.blit(line1_text, (line1_x, y + 28))

                    line2 = f"{save_info['time']} | День {save_info['day']}"
                    line2_text = font_small.render(line2, True, WHITE)
                    line2_x = start_x + slot_width // 2 - line2_text.get_width() // 2
                    self.screen.blit(line2_text, (line2_x, y + 53))

                    line3 = f"{save_info['location']}"
                    line3_text = font_small.render(line3, True, WHITE)
                    line3_x = start_x + slot_width // 2 - line3_text.get_width() // 2
                    self.screen.blit(line3_text, (line3_x, y + 78))
                else:
                    pygame.draw.rect(self.screen, DARK_RED, slot_rect)
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 2)

                    slot_text = font_medium.render(f"СЛОТ {slot}", True, GOLD)
                    self.screen.blit(slot_text, (start_x + 20, y + 42))
                    empty_text = font_medium.render("ПУСТО", True, GRAY)
                    self.screen.blit(empty_text, (start_x + slot_width // 2 - empty_text.get_width() // 2, y + 62))

                slot_buttons.append((slot, slot_rect))

                if save_info and slot_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 3)

            # Ползунок прокрутки
            if total_slots > visible_slots:
                scroll_bar_x = start_x + slot_width + 15
                scroll_bar_y = start_y
                scroll_bar_height = visible_slots * (slot_height + spacing)
                scroll_bar_width = 8

                scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
                pygame.draw.rect(self.screen, (40, 40, 40), scroll_bg_rect)
                pygame.draw.rect(self.screen, GOLD, scroll_bg_rect, 1)

                scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
                scroll_thumb_height = max(40, scroll_bar_height // total_slots)
                scroll_thumb_y = scroll_bar_y + scroll_ratio * (scroll_bar_height - scroll_thumb_height)

                scroll_thumb_rect = pygame.Rect(scroll_bar_x, scroll_thumb_y, scroll_bar_width, scroll_thumb_height)
                pygame.draw.rect(self.screen, GOLD, scroll_thumb_rect)

            # Кнопка "Назад"
            back_rect = pygame.Rect(WIDTH // 2 - 100, start_y + visible_slots * (slot_height + spacing) + 20, 200, 45)
            mouse_pos = pygame.mouse.get_pos()

            if back_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GOLD, back_rect)
                back_text = font_medium.render("НАЗАД", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, back_rect)
                pygame.draw.rect(self.screen, GOLD, back_rect, 2)
                back_text = font_medium.render("НАЗАД", True, WHITE)

            text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
            text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
            self.screen.blit(back_text, (text_x, text_y))

            pygame.display.flip()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for slot, rect in slot_buttons:
                            if rect.collidepoint(event.pos):
                                # Сохраняем в выбранный слот
                                сохранение.сохранить_игру(self.игрок, self.текущая_локация, self.chest_inventory, slot)
                                self.add_to_log(f"Игра сохранена в слот {slot}!")
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

            clock.tick(FPS)

    def show_save_menu(self):
        """Показывает меню выбора слота для сохранения (вертикальное расположение с прокруткой)"""

        # ===== СИНХРОНИЗИРУЕМ ИГРОКА ПЕРЕД СОХРАНЕНИЕМ =====
        # Убеждаемся, что у игрока есть все нужные поля
        if "пассивные_бонусы" not in self.игрок:
            self.игрок["пассивные_бонусы"] = {}
            print("🔧 Добавлено поле 'пассивные_бонусы' перед сохранением")

        if "выученные_навыки" not in self.игрок:
            self.игрок["выученные_навыки"] = []
            print("🔧 Добавлено поле 'выученные_навыки' перед сохранением")

        if "очки_навыков" not in self.игрок:
            self.игрок["очки_навыков"] = 0
            print("🔧 Добавлено поле 'очки_навыков' перед сохранением")

        if "очки_умений" not in self.игрок:
            self.игрок["очки_умений"] = 0
            print("🔧 Добавлено поле 'очки_умений' перед сохранением")

        if "сила_бонус" not in self.игрок:
            self.игрок["сила_бонус"] = 0
            print("🔧 Добавлено поле 'сила_бонус' перед сохранением")

        if "здоровье_бонус" not in self.игрок:
            self.игрок["здоровье_бонус"] = 0
            print("🔧 Добавлено поле 'здоровье_бонус' перед сохранением")

        if "стойкость_бонус" not in self.игрок:
            self.игрок["стойкость_бонус"] = 0
            print("🔧 Добавлено поле 'стойкость_бонус' перед сохранением")

        if "защита_бонус" not in self.игрок:
            self.игрок["защита_бонус"] = 0
            print("🔧 Добавлено поле 'защита_бонус' перед сохранением")

        if "вампиризм" not in self.игрок:
            self.игрок["вампиризм"] = False
            print("🔧 Добавлено поле 'вампиризм' перед сохранением")

        if "амулет" not in self.игрок:
            self.игрок["амулет"] = None
            print("🔧 Добавлено поле 'амулет' перед сохранением")
        # =====================================================

        # Получаем список существующих сохранений
        saves_info = сохранение.list_saves()

        # Параметры прокрутки
        scroll_offset = 0
        visible_slots = 4
        total_slots = 5

        waiting = True
        selected_slot = None

        while waiting:
            # Затемнение фона
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (0, 0))

            # Заголовок
            title = font_large.render("СОХРАНЕНИЕ ИГРЫ", True, GOLD)
            title_shadow = font_large.render("СОХРАНЕНИЕ ИГРЫ", True, (80, 60, 30))
            title_x = WIDTH // 2 - title.get_width() // 2
            self.screen.blit(title_shadow, (title_x + 3, 63))
            self.screen.blit(title, (title_x, 60))

            # Подзаголовок
            subtitle = font_medium.render("Выберите слот для сохранения:", True, WHITE)
            sub_x = WIDTH // 2 - subtitle.get_width() // 2
            self.screen.blit(subtitle, (sub_x, 120))

            # ===== ВЕРТИКАЛЬНОЕ РАСПОЛОЖЕНИЕ СЛОТОВ С ПРОКРУТКОЙ =====
            slot_buttons = []
            slot_width = 500
            slot_height = 110
            spacing = 15
            start_x = WIDTH // 2 - slot_width // 2
            start_y = 170

            # Ограничиваем прокрутку
            max_scroll = max(0, total_slots - visible_slots)
            scroll_offset = max(0, min(scroll_offset, max_scroll))

            # Отображаем только видимые слоты
            start_slot = scroll_offset
            end_slot = min(start_slot + visible_slots, total_slots)

            for i in range(start_slot, end_slot):
                slot = i + 1
                y = start_y + (i - start_slot) * (slot_height + spacing)

                slot_rect = pygame.Rect(start_x, y, slot_width, slot_height)

                # Проверяем, есть ли сохранение в этом слоте
                save_info = None
                for info in saves_info:
                    if info["slot"] == slot:
                        save_info = info
                        break

                # Фон слота
                if save_info:
                    # Есть сохранение - тёмно-синий фон
                    pygame.draw.rect(self.screen, DARK_BLUE, slot_rect)
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 2)

                    # Номер слота (слева)
                    slot_text = font_medium.render(f"СЛОТ {slot}", True, GOLD)
                    self.screen.blit(slot_text, (start_x + 20, y + 12))

                    # Информация о сохранении (по центру, 3 строки)
                    line1 = f"{save_info['class']} | Уровень {save_info['level']}"
                    line1_text = font_small.render(line1, True, WHITE)
                    line1_x = start_x + slot_width // 2 - line1_text.get_width() // 2
                    self.screen.blit(line1_text, (line1_x, y + 28))

                    line2 = f"{save_info['time']} | День {save_info['day']}"
                    line2_text = font_small.render(line2, True, WHITE)
                    line2_x = start_x + slot_width // 2 - line2_text.get_width() // 2
                    self.screen.blit(line2_text, (line2_x, y + 53))

                    line3 = f"{save_info['location']}"
                    line3_text = font_small.render(line3, True, WHITE)
                    line3_x = start_x + slot_width // 2 - line3_text.get_width() // 2
                    self.screen.blit(line3_text, (line3_x, y + 78))

                    # ===== ДОБАВЛЯЕМ ИНДИКАТОР СТАРОЙ ВЕРСИИ =====
                    # Проверяем, есть ли в сохранении пассивные бонусы
                    try:
                        with open(f"save_{slot}.json", 'r', encoding='utf-8') as f:
                            данные = json.load(f)
                            игрок_из_сейва = данные.get("игрок", {})
                            if "пассивные_бонусы" not in игрок_из_сейва:
                                old_text = font_tiny.render("⚠️ СТАРАЯ ВЕРСИЯ", True, HEALTH_YELLOW)
                                self.screen.blit(old_text, (start_x + slot_width - 130, y + 15))
                    except:
                        pass

                else:
                    # Пустой слот - тёмно-красный фон
                    pygame.draw.rect(self.screen, DARK_RED, slot_rect)
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 2)

                    slot_text = font_medium.render(f"СЛОТ {slot}", True, GOLD)
                    self.screen.blit(slot_text, (start_x + 20, y + 42))
                    empty_text = font_medium.render("ПУСТО", True, GRAY)
                    self.screen.blit(empty_text, (start_x + slot_width // 2 - empty_text.get_width() // 2, y + 62))

                slot_buttons.append((slot, slot_rect))

                # Эффект при наведении
                if slot_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 3)

            # ===== ПОЛЗУНОК ПРОКРУТКИ =====
            if total_slots > visible_slots:
                scroll_bar_x = start_x + slot_width + 15
                scroll_bar_y = start_y
                scroll_bar_height = visible_slots * (slot_height + spacing)
                scroll_bar_width = 8

                scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
                pygame.draw.rect(self.screen, (40, 40, 40), scroll_bg_rect)
                pygame.draw.rect(self.screen, GOLD, scroll_bg_rect, 1)

                scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
                scroll_thumb_height = max(40, scroll_bar_height // total_slots)
                scroll_thumb_y = scroll_bar_y + scroll_ratio * (scroll_bar_height - scroll_thumb_height)

                scroll_thumb_rect = pygame.Rect(scroll_bar_x, scroll_thumb_y, scroll_bar_width, scroll_thumb_height)
                pygame.draw.rect(self.screen, GOLD, scroll_thumb_rect)

            # Кнопка "Назад"
            back_rect = pygame.Rect(WIDTH // 2 - 100, start_y + visible_slots * (slot_height + spacing) + 0, 200, 45)
            mouse_pos = pygame.mouse.get_pos()

            if back_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GOLD, back_rect)
                back_text = font_medium.render("НАЗАД", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, back_rect)
                pygame.draw.rect(self.screen, GOLD, back_rect, 2)
                back_text = font_medium.render("НАЗАД", True, WHITE)

            text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
            text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
            self.screen.blit(back_text, (text_x, text_y))

            pygame.display.flip()

            # ===== ОБРАБОТКА СОБЫТИЙ =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Проверяем клик по слотам
                        for slot, rect in slot_buttons:
                            if rect.collidepoint(event.pos):
                                selected_slot = slot
                                waiting = False
                                break

                        # Проверяем клик по кнопке "Назад"
                        if back_rect.collidepoint(event.pos):
                            return
                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        scroll_offset -= 1
                    else:
                        scroll_offset += 1
                    scroll_offset = max(0, min(scroll_offset, max_scroll))

            clock.tick(FPS)

        # Если выбран слот - показываем подтверждение
        if selected_slot:
            self.show_save_confirmation(selected_slot)

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

    def draw_chest(self):
        """Отрисовка окна сундука для хранения предметов"""

        # ===== ПРОВЕРКА: если сундук ещё не создан, создаём =====
        if not hasattr(self, 'chest_inventory'):
            self.chest_inventory = []

        # Затемняем фон
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (0, 0))

        # Рамка окна
        chest_rect = pygame.Rect(150, 60, 980, 600)
        pygame.draw.rect(self.screen, DARK_BLUE, chest_rect)
        pygame.draw.rect(self.screen, GOLD, chest_rect, 3)

        # Заголовок
        title = font_large.render("СУНДУК", True, GOLD)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # Левая колонка — инвентарь игрока
        inv_title = font_medium.render("ИНВЕНТАРЬ", True, GOLD)
        self.screen.blit(inv_title, (200, 130))

        # Правая колонка — сундук
        chest_title = font_medium.render("СУНДУК", True, GOLD)
        self.screen.blit(chest_title, (700, 130))

        # Подсчёт предметов
        инвентарь_словарь = {}
        for предмет in self.игрок["инвентарь"]:
            инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

        сундук_словарь = {}
        for предмет in self.chest_inventory:
            сундук_словарь[предмет] = сундук_словарь.get(предмет, 0) + 1

        # Отображаем предметы инвентаря (слева)
        y = 170
        self.chest_inventory_items = []  # для кликов

        for предмет, количество in инвентарь_словарь.items():
            # Название
            name_text = font_small.render(предмет, True, WHITE)
            self.screen.blit(name_text, (200, y))

            # Количество
            count_text = font_small.render(f"x{количество}", True, GOLD)
            self.screen.blit(count_text, (350, y))

            # Кнопка "В сундук"
            btn_rect = pygame.Rect(450, y - 3, 80, 25)
            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, btn_rect)
                btn_text = font_small.render(">", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, btn_rect)
                pygame.draw.rect(self.screen, GOLD, btn_rect, 1)
                btn_text = font_small.render(">", True, WHITE)
            self.screen.blit(btn_text, (btn_rect.x + 30, btn_rect.y + 3))

            self.chest_inventory_items.append(("to_chest", предмет, btn_rect))
            y += 35

        # Отображаем предметы сундука (справа)
        y = 170
        for предмет, количество in сундук_словарь.items():
            # Название
            name_text = font_small.render(предмет, True, WHITE)
            self.screen.blit(name_text, (700, y))

            # Количество
            count_text = font_small.render(f"x{количество}", True, GOLD)
            self.screen.blit(count_text, (850, y))

            # Кнопка "В инвентарь"
            btn_rect = pygame.Rect(950, y - 3, 80, 25)
            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, btn_rect)
                btn_text = font_small.render("<", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, btn_rect)
                pygame.draw.rect(self.screen, GOLD, btn_rect, 1)
                btn_text = font_small.render("<", True, WHITE)
            self.screen.blit(btn_text, (btn_rect.x + 30, btn_rect.y + 3))

            self.chest_inventory_items.append(("to_inventory", предмет, btn_rect))
            y += 35

        # Кнопка "Назад"
        back_rect = pygame.Rect(WIDTH // 2 - 100, 620, 200, 50)
        pygame.draw.rect(self.screen, DARK_RED, back_rect)
        pygame.draw.rect(self.screen, GOLD, back_rect, 2)
        back_text = font_medium.render("НАЗАД", True, WHITE)
        self.screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 635))
        self.chest_back = back_rect

    def handle_chest_click(self, pos):
        """Обработка кликов в окне сундука"""

        if not hasattr(self, 'chest_inventory'):
            self.chest_inventory = []

        # Кнопка "Назад"
        if hasattr(self, 'chest_back') and self.chest_back.collidepoint(pos):
            self.режим = "игра"
            return

        # Перемещение предметов
        if hasattr(self, 'chest_inventory_items'):
            for action, предмет, rect in self.chest_inventory_items:
                if rect.collidepoint(pos):
                    if action == "to_chest":
                        # Перемещаем из инвентаря в сундук
                        if self.inventory.has_item(предмет):
                            self.inventory.remove_item(предмет)
                            self.chest_inventory.append(предмет)
                            self.add_to_log(f"📦 {предмет} перемещён в сундук")

                    elif action == "to_inventory":
                        # Перемещаем из сундука в инвентарь
                        if предмет in self.chest_inventory:
                            self.chest_inventory.remove(предмет)
                            self.inventory.add_item(предмет)
                            self.add_to_log(f"📦 {предмет} взят из сундука")

                    return

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

        import рандомайзер
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
                        import предметы
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

    def show_main_menu(self):
        """Показывает главное меню (только фон, кнопки невидимы но активны)"""
        print("🟢 show_main_menu запущена")

        # ===== МУЗЫКА МЕНЮ =====
        self.переключить_плейлист("меню")

        # Сбрасываем открытые барьеры
        барьеры.сбросить_открытые_барьеры()

        # ===== ЗАГРУЖАЕМ ФОН =====
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

        # ===== ПОЗИЦИИ КНОПОК (невидимые, но активные) =====
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

                    # ===== КНОПКИ РАБОТАЮТ ПО СВОИМ ПОЗИЦИЯМ (НЕВИДИМЫЕ) =====
                    if new_rect.collidepoint(mouse_pos):
                        print("🆕 Нажата кнопка НОВАЯ ИГРА")

                        # 👇 ОСТАНАВЛИВАЕМ МУЗЫКУ МЕНЮ
                        self.остановить_музыку()

                        from игрок import создать_нового_игрока
                        self.игрок = создать_нового_игрока()
                        self.inventory = InventorySystem(self.игрок, self.item_icons)
                        self.battle = BattleSystem(self.игрок, self)

                        # ===== МАРКЕР, ЧТО ИГРА ЗАГРУЖЕНА =====  # 👈 ДОБАВЬТЕ!
                        self.игра_загружена = True


                        if not self.show_intro():
                            return False

                        выбранный_класс = self.show_class_selection()
                        if выбранный_класс:
                            self.apply_class(выбранный_класс)

                            # ===== ДОБАВЛЯЕМ СТАРТОВЫЙ КВЕСТ ДЛЯ НОВОЙ ИГРЫ =====
                            self.quest_system.добавить_квест(self.игрок, "основной_начало")
                            print("📜 Добавлен стартовый квест (новая игра)")

                            # ===== ВКЛЮЧАЕМ МУЗЫКУ ДЛЯ НАЧАЛЬНОЙ ЛОКАЦИИ =====
                            if self.есть_музыка(self.текущая_локация):
                                self.переключить_плейлист(self.текущая_локация)
                            else:
                                self.остановить_музыку()

                            # 👇 ВЫХОДИМ ИЗ МЕНЮ (МУЗЫКА УЖЕ ОСТАНОВЛЕНА)
                            return True
                        else:
                            return False

                    elif load_rect.collidepoint(mouse_pos):
                        print("📂 Нажата кнопка ЗАГРУЗИТЬ")
                        saves_info = сохранение.list_saves()
                        if not saves_info:
                            print("❌ Нет сохранённой игры!")
                            self.show_message("Нет сохранений!", duration=60)
                            continue

                        selected_slot = self.show_load_menu()
                        print(f"🔍 selected_slot = {selected_slot}")
                        if selected_slot:
                            print(f"📂 Загружаем слот {selected_slot}")
                            загруженный_игрок, загруженная_локация, chest_inventory = сохранение.загрузить_игру(
                                selected_slot)
                            if загруженный_игрок:
                                # 👇 ОСТАНАВЛИВАЕМ МУЗЫКУ МЕНЮ
                                self.остановить_музыку()

                                self.игрок.update(загруженный_игрок)
                                self.текущая_локация = загруженная_локация
                                self.chest_inventory = chest_inventory

                                # ===== МАРКЕР, ЧТО ИГРА ЗАГРУЖЕНА =====
                                self.игра_загружена = True

                                # ===== ВКЛЮЧАЕМ МУЗЫКУ ДЛЯ ТЕКУЩЕЙ ЛОКАЦИИ =====
                                if self.есть_музыка(self.текущая_локация):
                                    self.переключить_плейлист(self.текущая_локация)
                                else:
                                    self.остановить_музыку()

                                # ===== ПРОВЕРЯЕМ КВЕСТЫ ПРИ ЗАГРУЗКЕ =====
                                if not self.игрок.get("активные_квесты") and not self.игрок.get("завершенные_квесты"):
                                    self.quest_system.добавить_квест(self.игрок, "основной_начало")
                                    print("📜 Добавлен стартовый квест (загрузка)")

                                self._пересчитать_пассивные_бонусы()
                                self.inventory.update_max_health()
                                print(f"✅ Загружена игра из слота {selected_slot}")

                                # 👇 ВЫХОДИМ ИЗ МЕНЮ (МУЗЫКА УЖЕ ОСТАНОВЛЕНА)
                                return True
                        continue

                    elif exit_rect.collidepoint(mouse_pos):
                        print("🚪 Нажата кнопка ВЫХОД")
                        if self.show_exit_confirmation():
                            print("   ⚠️ Возвращаем None (выход из меню)")
                            return None
                        else:
                            continue

            # ===== ОТРИСОВКА (ТОЛЬКО ФОН) =====
            self.screen.blit(bg, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)

        return None

    def show_load_menu(self):
        """Показывает меню выбора слота для загрузки (только непустые слоты)"""
        print("📋 show_load_menu вызвана")

        saves_info = сохранение.list_saves()

        if not saves_info:
            print("   ❌ Нет сохранений!")
            self.show_message("Нет сохранений!", duration=60)
            return None  # 👈 ВОЗВРАЩАЕМ None, НЕ True!

        scroll_offset = 0
        visible_slots = 4
        total_slots = 5

        waiting = True
        selected_slot = None

        while waiting:
            # Затемнение фона
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (0, 0))

            # Заголовок
            title = font_large.render("ЗАГРУЗКА ИГРЫ", True, GOLD)
            title_shadow = font_large.render("ЗАГРУЗКА ИГРЫ", True, (80, 60, 30))
            title_x = WIDTH // 2 - title.get_width() // 2
            self.screen.blit(title_shadow, (title_x + 3, 63))
            self.screen.blit(title, (title_x, 60))

            subtitle = font_medium.render("Выберите слот для загрузки:", True, WHITE)
            sub_x = WIDTH // 2 - subtitle.get_width() // 2
            self.screen.blit(subtitle, (sub_x, 120))

            # ===== ВЕРТИКАЛЬНОЕ РАСПОЛОЖЕНИЕ СЛОТОВ =====
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

                # Проверяем, есть ли сохранение в этом слоте
                save_info = None
                for info in saves_info:
                    if info["slot"] == slot:
                        save_info = info
                        break

                if save_info:
                    # ЕСТЬ СОХРАНЕНИЕ - активный слот
                    pygame.draw.rect(self.screen, DARK_BLUE, slot_rect)
                    pygame.draw.rect(self.screen, GOLD, slot_rect, 2)

                    slot_text = font_medium.render(f"СЛОТ {slot}", True, GOLD)
                    self.screen.blit(slot_text, (start_x + 20, y + 12))

                    line1 = f"{save_info['class']} | Уровень {save_info['level']}"
                    line1_text = font_small.render(line1, True, WHITE)
                    line1_x = start_x + slot_width // 2 - line1_text.get_width() // 2
                    self.screen.blit(line1_text, (line1_x, y + 28))

                    line2 = f"{save_info['time']} | День {save_info['day']}"
                    line2_text = font_small.render(line2, True, WHITE)
                    line2_x = start_x + slot_width // 2 - line2_text.get_width() // 2
                    self.screen.blit(line2_text, (line2_x, y + 53))

                    line3 = f"{save_info['location']}"
                    line3_text = font_small.render(line3, True, WHITE)
                    line3_x = start_x + slot_width // 2 - line3_text.get_width() // 2
                    self.screen.blit(line3_text, (line3_x, y + 78))

                    slot_buttons.append((slot, slot_rect))

                    if slot_rect.collidepoint(pygame.mouse.get_pos()):
                        pygame.draw.rect(self.screen, GOLD, slot_rect, 3)
                else:
                    # ПУСТОЙ СЛОТ - неактивный
                    pygame.draw.rect(self.screen, (40, 40, 40), slot_rect)
                    pygame.draw.rect(self.screen, GRAY, slot_rect, 2)
                    slot_text = font_medium.render(f"СЛОТ {slot}", True, GRAY)
                    self.screen.blit(slot_text, (start_x + 20, y + 42))
                    empty_text = font_medium.render("ПУСТО", True, GRAY)
                    self.screen.blit(empty_text, (start_x + slot_width // 2 - empty_text.get_width() // 2, y + 62))

            # Ползунок прокрутки
            if total_slots > visible_slots:
                scroll_bar_x = start_x + slot_width + 15
                scroll_bar_y = start_y
                scroll_bar_height = visible_slots * (slot_height + spacing)
                scroll_bar_width = 8

                scroll_bg_rect = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)
                pygame.draw.rect(self.screen, (40, 40, 40), scroll_bg_rect)
                pygame.draw.rect(self.screen, GOLD, scroll_bg_rect, 1)

                scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
                scroll_thumb_height = max(40, scroll_bar_height // total_slots)
                scroll_thumb_y = scroll_bar_y + scroll_ratio * (scroll_bar_height - scroll_thumb_height)

                scroll_thumb_rect = pygame.Rect(scroll_bar_x, scroll_thumb_y, scroll_bar_width, scroll_thumb_height)
                pygame.draw.rect(self.screen, GOLD, scroll_thumb_rect)

            # Кнопка "Назад"
            back_rect = pygame.Rect(WIDTH // 2 - 100, start_y + visible_slots * (slot_height + spacing) + 0, 200, 45)
            mouse_pos = pygame.mouse.get_pos()

            if back_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GOLD, back_rect)
                back_text = font_medium.render("НАЗАД", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, back_rect)
                pygame.draw.rect(self.screen, GOLD, back_rect, 2)
                back_text = font_medium.render("НАЗАД", True, WHITE)

            text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
            text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
            self.screen.blit(back_text, (text_x, text_y))

            pygame.display.flip()

            # ===== ОБРАБОТКА СОБЫТИЙ =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("   🟠 Получен QUIT, возвращаем None")
                    return None  # 👈 ВОЗВРАЩАЕМ None, НЕ True!

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Проверяем клик по слотам
                        for slot, rect in slot_buttons:
                            if rect.collidepoint(event.pos):
                                selected_slot = slot
                                print(f"   ✅ Выбран слот {selected_slot}")
                                waiting = False
                                break

                        # Проверяем клик по кнопке "Назад"
                        if back_rect.collidepoint(event.pos):
                            print("   🔙 Нажата кнопка НАЗАД, возвращаем None")
                            return None  # 👈 ВОЗВРАЩАЕМ None, НЕ True!

                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        scroll_offset -= 1
                    else:
                        scroll_offset += 1
                    scroll_offset = max(0, min(scroll_offset, max_scroll))

            clock.tick(FPS)

        # ===== ВЫХОД ИЗ ЦИКЛА =====
        print(f"📋 show_load_menu возвращает: {selected_slot}")
        return selected_slot  # 👈 ВОЗВРАЩАЕМ ЧИСЛО ИЛИ None

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
                                        self.show_save_menu()
                                    elif action == "с":  # Выход
                                        print("🚪 Выход в главное меню")
                                        if self.show_exit_dialog():
                                            self.игра_активна = False
                                    break

                        elif self.режим == "инвентарь":
                            self.handle_inventory_click(mouse_pos)
                        elif self.режим == "бой":
                            self.handle_battle_click(mouse_pos)
                        elif self.режим == "торговля":
                            self.handle_trade_click(mouse_pos)
                        elif self.режим == "quest_trade_menu":  # 👈 ЭТОЙ СТРОКИ НЕТ!
                            self.handle_quest_trade_click(mouse_pos)
                        elif self.режим == "квесты":  # 👈 ДОБАВЬТЕ ЭТУ СТРОКУ!
                            self.handle_quests_click(mouse_pos)
                        elif self.режим == "крафт":
                            self.handle_craft_click(mouse_pos)
                        elif self.режим == "карта":
                            self.handle_map_click(mouse_pos)
                        elif self.режим == "обучение":
                            self.handle_skills_click(mouse_pos)
                        elif self.режим == "сундук":
                            self.handle_chest_click(mouse_pos)

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
            self.update_transition_video()
            self.update_battle_animation()



            # ========== ОТРИСОВКА ==========
            if self.режим == "игра":
                self.draw_location()
                self.draw_status()
                self.draw_actions()
                self.draw_log_panel()
                self.draw_battle_start_animation()
                self.draw_loot_panel()
                self.draw_quest_tracker()
                self.draw_daily_quest_tracker()
                self.draw_обыск_шкала()

            elif self.режим == "инвентарь":
                self.draw_inventory()

            elif self.режим == "обучение":
                self.draw_skills_menu()

            elif self.режим == "бой":
                self.draw_battle()
                self.draw_battle_start_animation()

            elif self.режим == "торговля":
                self.draw_trade()

            elif self.режим == "quest_trade_menu":  # 👈 ДОБАВЬТЕ ЭТУ СТРОКУ!
                self.draw_quest_trade_menu()

            elif self.режим == "квесты":
                self.draw_quests()

            elif self.режим == "крафт":
                self.draw_craft()

            elif self.режим == "карта":
                self.draw_map()

            elif self.режим == "сундук":
                self.draw_chest()

            elif self.режим == "эксплорейшн":
                if hasattr(self, 'exploration_zone'):
                    self.handle_exploration()
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

    def draw_inventory(self):
        """Инвентарь с анимацией в стиле игры"""

        # Анимация появления
        if not hasattr(self, 'inventory_animation_progress'):
            self.inventory_animation_progress = 0

        if self.inventory_animation_progress < 1:
            self.inventory_animation_progress += 0.08
            if self.inventory_animation_progress > 1:
                self.inventory_animation_progress = 1

        # ===== ПОЗИЦИЯ МЫШИ =====
        mouse_pos = pygame.mouse.get_pos()  # ← ДОБАВИЛ!

        # Параметры панели с анимацией
        panel_width = 1300
        panel_height = 620
        start_y = -panel_height
        current_y = start_y + (panel_height * self.inventory_animation_progress)
        panel_y = int(current_y)
        panel_x = WIDTH // 2 - panel_width // 2

        # Основная панель с градиентом (как в торговле)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # ===== ГРАДИЕНТНЫЙ ФОН (КАК В ТОРГОВЛЕ) =====
        for i in range(panel_height):
            ratio = i / panel_height
            r = int(26 + 15 * ratio)
            g = int(26 + 10 * ratio)
            b = int(46 + 20 * ratio)
            color = (r, g, b)
            pygame.draw.line(self.screen, color,
                             (panel_x, panel_y + i),
                             (panel_x + panel_width, panel_y + i))

        # Золотая рамка с декоративными углами
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Декоративные уголки
        corner_size = 20
        corners = [
            (panel_x, panel_y),
            (panel_x + panel_width - corner_size, panel_y),
            (panel_x, panel_y + panel_height - corner_size),
            (panel_x + panel_width - corner_size, panel_y + panel_height - corner_size)
        ]
        for cx, cy in corners:
            pygame.draw.rect(self.screen, GOLD, (cx, cy, corner_size, corner_size), 2)
            pygame.draw.line(self.screen, GOLD, (cx + 5, cy + 5), (cx + corner_size - 5, cy + corner_size - 5), 1)
            pygame.draw.line(self.screen, GOLD, (cx + corner_size - 5, cy + 5), (cx + 5, cy + corner_size - 5), 1)

        # Заголовок с тенью
        title = font_large.render("ИНВЕНТАРЬ", True, GOLD)
        title_shadow = font_large.render("ИНВЕНТАРЬ", True, (80, 60, 30))
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title_shadow, (title_x + 3, panel_y + 23))
        self.screen.blit(title, (title_x, panel_y + 20))

        # Декоративная линия под заголовком
        line_y = panel_y + 70
        for i in range(2):
            line_width = panel_width - 150 - i * 20
            line_x = panel_x + 75 + i * 10
            pygame.draw.line(self.screen, (GOLD[0], GOLD[1], GOLD[2], 100 - i * 30),
                             (line_x, line_y + i),
                             (line_x + line_width, line_y + i), 2)

        # ===== ЛЕВАЯ ПАНЕЛЬ - ЭКИПИРОВКА =====
        equip_panel_x = panel_x + 30
        equip_panel_y = panel_y + 95
        equip_panel_width = 280
        equip_panel_height = 480

        # Фон панели экипировки
        pygame.draw.rect(self.screen, (26, 26, 46),
                         (equip_panel_x, equip_panel_y, equip_panel_width, equip_panel_height))
        pygame.draw.rect(self.screen, GOLD, (equip_panel_x, equip_panel_y, equip_panel_width, equip_panel_height), 1)

        # Заголовок экипировки
        equip_title = font_medium.render("ЭКИПИРОВКА", True, GOLD)
        equip_title_x = equip_panel_x + equip_panel_width // 2 - equip_title.get_width() // 2
        self.screen.blit(equip_title, (equip_title_x, equip_panel_y + 10))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (equip_panel_x + 15, equip_panel_y + 40),
                         (equip_panel_x + equip_panel_width - 15, equip_panel_y + 40), 1)

        # ===== РЯД 1: ОРУЖИЕ И БРОНЯ =====
        cell_size = 80
        spacing = 30
        start_x = equip_panel_x + 30
        row1_y = equip_panel_y + 55

        # Ячейка оружия
        weapon_rect = pygame.Rect(start_x, row1_y, cell_size, cell_size)
        pygame.draw.rect(self.screen, DARK_RED, weapon_rect)
        pygame.draw.rect(self.screen, GOLD, weapon_rect, 2)

        if self.игрок['оружие']:
            if self.игрок['оружие'] in self.item_icons:
                icon = self.item_icons[self.игрок['оружие']]
                icon = pygame.transform.scale(icon, (64, 64))
                icon_x = start_x + (cell_size - 64) // 2
                icon_y = row1_y + (cell_size - 64) // 2
                self.screen.blit(icon, (icon_x, icon_y))
            else:
                weapon_name = font_small.render(self.игрок['оружие'], True, WHITE)
                if len(self.игрок['оружие']) > 12:
                    weapon_name = font_small.render(self.игрок['оружие'][:10] + "...", True, WHITE)
                text_x = start_x + (cell_size - weapon_name.get_width()) // 2
                text_y = row1_y + cell_size // 2 - 10
                self.screen.blit(weapon_name, (text_x, text_y))

                if self.игрок['оружие'] in предметы.предметы:
                    урон = предметы.предметы[self.игрок['оружие']].get("урон", 0)
                    dmg_text = font_tiny.render(f"+{урон}", True, BLOOD_RED)
                    self.screen.blit(dmg_text, (start_x + 5, row1_y + cell_size - 20))
        else:
            empty_text = font_small.render("ПУСТО", True, GRAY)
            text_x = start_x + (cell_size - empty_text.get_width()) // 2
            text_y = row1_y + cell_size // 2 - 5
            self.screen.blit(empty_text, (text_x, text_y))

        weapon_label = font_tiny.render("ОРУЖИЕ", True, GOLD)
        self.screen.blit(weapon_label, (start_x + cell_size // 2 - weapon_label.get_width() // 2,
                                        row1_y + cell_size + 5))
        self.equip_weapon_rect = weapon_rect

        # Ячейка брони
        armor_x = start_x + cell_size + spacing
        armor_rect = pygame.Rect(armor_x, row1_y, cell_size, cell_size)
        pygame.draw.rect(self.screen, DARK_RED, armor_rect)
        pygame.draw.rect(self.screen, GOLD, armor_rect, 2)


        if self.игрок.get("броня"):
            if self.игрок["броня"] in self.item_icons:
                icon = self.item_icons[self.игрок["броня"]]
                icon = pygame.transform.scale(icon, (64, 64))
                icon_x = armor_x + (cell_size - 64) // 2
                icon_y = row1_y + (cell_size - 64) // 2
                self.screen.blit(icon, (icon_x, icon_y))
            else:
                armor_name = font_small.render(self.игрок["броня"], True, WHITE)
                if len(self.игрок["броня"]) > 12:
                    armor_name = font_small.render(self.игрок["броня"][:10] + "...", True, WHITE)
                text_x = armor_x + (cell_size - armor_name.get_width()) // 2
                text_y = row1_y + cell_size // 2 - 10
                self.screen.blit(armor_name, (text_x, text_y))

                if self.игрок["броня"] in предметы.предметы:
                    защита = предметы.предметы[self.игрок["броня"]].get("защита", 0)
                    def_text = font_tiny.render(f"+{защита}", True, HEALTH_GREEN)
                    self.screen.blit(def_text, (armor_x + 5, row1_y + cell_size - 20))
        else:
            empty_text = font_small.render("ПУСТО", True, GRAY)
            text_x = armor_x + (cell_size - empty_text.get_width()) // 2
            text_y = row1_y + cell_size // 2 - 5
            self.screen.blit(empty_text, (text_x, text_y))

        armor_label = font_tiny.render("БРОНЯ", True, GOLD)
        self.screen.blit(armor_label,
                         (armor_x + cell_size // 2 - armor_label.get_width() // 2, row1_y + cell_size + 5))
        self.equip_armor_rect = armor_rect

        # ===== РЯД 2: АМУЛЕТ =====
        row2_y = row1_y + cell_size + 40
        amulet_rect = pygame.Rect(start_x, row2_y, cell_size, cell_size)
        pygame.draw.rect(self.screen, DARK_RED, amulet_rect)
        pygame.draw.rect(self.screen, GOLD, amulet_rect, 2)


        if self.игрок.get("амулет"):
            if self.игрок["амулет"] in self.item_icons:
                icon = self.item_icons[self.игрок["амулет"]]
                icon = pygame.transform.scale(icon, (64, 64))
                icon_x = start_x + (cell_size - 64) // 2
                icon_y = row2_y + (cell_size - 64) // 2
                self.screen.blit(icon, (icon_x, icon_y))
            else:
                amulet_name = font_small.render(self.игрок["амулет"], True, WHITE)
                if len(self.игрок["амулет"]) > 12:
                    amulet_name = font_small.render(self.игрок["амулет"][:10] + "...", True, WHITE)
                text_x = start_x + (cell_size - amulet_name.get_width()) // 2
                text_y = row2_y + cell_size // 2 - 10
                self.screen.blit(amulet_name, (text_x, text_y))
        else:
            empty_text = font_small.render("ПУСТО", True, GRAY)
            text_x = start_x + (cell_size - empty_text.get_width()) // 2
            text_y = row2_y + cell_size // 2 - 5
            self.screen.blit(empty_text, (text_x, text_y))

        amulet_label = font_tiny.render("АМУЛЕТ", True, GOLD)
        self.screen.blit(amulet_label,
                         (start_x + cell_size // 2 - amulet_label.get_width() // 2, row2_y + cell_size + 5))
        self.equip_amulet_rect = amulet_rect

        # ===== ХАРАКТЕРИСТИКИ С ЗДОРОВЬЕМ И МАНОЙ =====
        stats_y = row2_y + cell_size + 30
        stats_title = font_small.render("СОСТОЯНИЕ", True, GOLD)
        self.screen.blit(stats_title, (equip_panel_x + equip_panel_width // 2 - stats_title.get_width() // 2, stats_y))

        # Здоровье
        health_text = font_small.render(f"Здоровье: {self.игрок['здоровье']}/{self.игрок['макс_здоровье']}", True,
                                        HEALTH_GREEN)
        self.screen.blit(health_text, (equip_panel_x + 20, stats_y + 25))

        # Мана
        mana_current = self.игрок.get('мана', 0)
        mana_max = self.игрок.get('макс_мана', 50)
        mana_text = font_small.render(f"Мана: {mana_current}/{mana_max}", True, (120, 180, 255))
        self.screen.blit(mana_text, (equip_panel_x + 20, stats_y + 45))

        # Остальные характеристики
        stats_title2 = font_small.render("ХАРАКТЕРИСТИКИ", True, GOLD)
        self.screen.blit(stats_title2,
                         (equip_panel_x + equip_panel_width // 2 - stats_title2.get_width() // 2, stats_y + 70))

        сила = self.игрок.get('сила', 0) + self.игрок.get('сила_бонус', 0)
        стойкость = self.игрок.get('стойкость', 0)
        ловкость = self.игрок.get('ловкость', 0)
        интеллект = self.игрок.get('интеллект', 0)
        кулинария = self.игрок.get('кулинария', 0)

        stats = [
            f"Сила: {сила}",
            f"Стойкость: {стойкость}",
            f"Ловкость: {ловкость}",
            f"Интеллект: {интеллект}",
            f"Кулинария: {кулинария}"
        ]

        if self.игрок.get('сила_бонус', 0) > 0:
            stats[0] = f"Сила: {сила} (+{self.игрок['сила_бонус']})"

        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, WHITE)
            self.screen.blit(stat_text, (equip_panel_x + 20, stats_y + 95 + i * 20))

        # ===== ПРАВАЯ ПАНЕЛЬ - ИНВЕНТАРЬ =====
        inv_panel_x = equip_panel_x + equip_panel_width + 0
        inv_panel_y = equip_panel_y
        inv_panel_width = panel_width - (equip_panel_x + equip_panel_width + 20) - 30
        inv_panel_height = equip_panel_height

        pygame.draw.rect(self.screen, (26, 26, 46), (inv_panel_x, inv_panel_y, inv_panel_width, inv_panel_height))
        pygame.draw.rect(self.screen, GOLD, (inv_panel_x, inv_panel_y, inv_panel_width, inv_panel_height), 1)

        inv_title = font_medium.render("ИНВЕНТАРЬ", True, GOLD)
        inv_title_x = inv_panel_x + inv_panel_width // 2 - inv_title.get_width() // 2
        self.screen.blit(inv_title, (inv_title_x, inv_panel_y + 10))

        pygame.draw.line(self.screen, GOLD,
                         (inv_panel_x + 15, inv_panel_y + 40),
                         (inv_panel_x + inv_panel_width - 15, inv_panel_y + 40), 1)

        # ===== ЯЧЕЙКИ ИНВЕНТАРЯ =====
        cell_size_inv = 70
        cols = (inv_panel_width - 50) // (cell_size_inv + 10)
        rows = 5
        spacing_inv = 10

        start_x_inv = inv_panel_x + 25
        start_y_inv = inv_panel_y + 55

        # Группируем предметы
        предметы_игрока = self.игрок["инвентарь"]
        подсчёт = {}
        for предмет in предметы_игрока:
            подсчёт[предмет] = подсчёт.get(предмет, 0) + 1

        уникальные_предметы = sorted(list(подсчёт.keys()))
        self.inventory_items = []

        icon_size_inv = 48
        hovered_item = None
        mouse_pos = pygame.mouse.get_pos()
        hover_pos = None

        for row in range(rows):
            for col in range(cols):
                x = start_x_inv + col * (cell_size_inv + spacing_inv)
                y = start_y_inv + row * (cell_size_inv + spacing_inv)

                cell_rect = pygame.Rect(x, y, cell_size_inv, cell_size_inv)

                pygame.draw.rect(self.screen, DARK_RED, cell_rect)
                pygame.draw.rect(self.screen, GOLD, cell_rect, 2)

                index = row * cols + col
                if index < len(уникальные_предметы):
                    предмет = уникальные_предметы[index]
                    количество = подсчёт[предмет]

                    if предмет in self.item_icons:
                        icon = self.item_icons[предмет]
                        icon = pygame.transform.scale(icon, (icon_size_inv, icon_size_inv))
                        icon_x = x + (cell_size_inv - icon_size_inv) // 2
                        icon_y = y + (cell_size_inv - icon_size_inv) // 2 - 5
                        self.screen.blit(icon, (icon_x, icon_y))
                    else:
                        короткое_название = предмет[:8] + ".." if len(предмет) > 8 else предмет
                        item_text = font_tiny.render(короткое_название, True, WHITE)
                        text_x = x + (cell_size_inv - item_text.get_width()) // 2
                        text_y = y + cell_size_inv // 2 - 5
                        self.screen.blit(item_text, (text_x, text_y))

                    if количество > 1:
                        count_text = font_tiny.render(f"x{количество}", True, GOLD)
                        count_x = x + cell_size_inv - count_text.get_width() - 3
                        count_y = y + cell_size_inv - count_text.get_height() - 2
                        self.screen.blit(count_text, (count_x, count_y))

                    # ===== 👇 КНОПКА "НА ПОЯС" ДЛЯ ЗЕЛИЙ (ВНУТРИ ЦИКЛА - ПРАВИЛЬНО!) =====
                    данные = предметы.предметы.get(предмет, {})
                    if данные.get("тип") == "еда":
                        belt_btn = pygame.Rect(x + cell_size_inv - 50, y + cell_size_inv - 28, 24, 24)
                        if belt_btn.collidepoint(mouse_pos):
                            pygame.draw.rect(self.screen, GOLD, belt_btn)
                            btn_text = font_tiny.render("П", True, BLACK)
                        else:
                            pygame.draw.rect(self.screen, DARK_RED, belt_btn)
                            pygame.draw.rect(self.screen, GOLD, belt_btn, 1)
                            btn_text = font_tiny.render("П", True, WHITE)
                        self.screen.blit(btn_text, (belt_btn.x + 4, belt_btn.y + 2))
                        self.inventory_items.append((belt_btn, "belt", предмет))

                    # Сохраняем ячейку для клика
                    self.inventory_items.append((cell_rect, предмет))

        # ===== 👇 КОНЕЦ ЦИКЛА! ПАНЕЛЬ ПОЯСА (ТОЛЬКО ОДИН РАЗ, ПОСЛЕ ЦИКЛА!) =====
        # ===== ПАНЕЛЬ ПОЯСА (СПРАВА ОТ ИНВЕНТАРЯ, ВЕРТИКАЛЬНО) =====
        # 👇 ИЗМЕНЯЕМ ПОЗИЦИЮ - ПОДНИМАЕМ ВВЕРХ И СДВИГАЕМ ВПРАВО
        belt_panel_x = inv_panel_x + inv_panel_width  # Справа от инвентаря
        belt_panel_y = panel_y + 95  # На уровне экипировки
        belt_panel_width = 85  # Чуть уже
        belt_panel_height = equip_panel_height  # Та же высота

        # Фон панели пояса
        pygame.draw.rect(self.screen, (26, 26, 46),
                         (belt_panel_x, belt_panel_y, belt_panel_width, belt_panel_height))
        pygame.draw.rect(self.screen, GOLD,
                         (belt_panel_x, belt_panel_y, belt_panel_width, belt_panel_height), 2)

        # Заголовок
        belt_title = font_small.render("ПОЯС", True, GOLD)
        title_x = belt_panel_x + belt_panel_width // 2 - belt_title.get_width() // 2
        self.screen.blit(belt_title, (title_x, belt_panel_y + 10))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (belt_panel_x + 10, belt_panel_y + 40),
                         (belt_panel_x + belt_panel_width - 10, belt_panel_y + 40), 1)

        пояс = self.игрок.get("пояс", [])
        belt_slot_size = 60  # Чуть меньше
        belt_spacing = 8
        start_y = belt_panel_y + 55
        start_x = belt_panel_x + (belt_panel_width - belt_slot_size) // 2

        for i in range(5):
            y = start_y + i * (belt_slot_size + belt_spacing)
            x = start_x

            belt_rect = pygame.Rect(x, y, belt_slot_size, belt_slot_size)

            shadow_rect = pygame.Rect(x + 2, y + 2, belt_slot_size, belt_slot_size)
            pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect)

            if i < len(пояс) and пояс[i] is not None:
                # Есть зелье на поясе
                for j in range(belt_slot_size):
                    ratio = j / belt_slot_size
                    r = int(20 + 30 * ratio)
                    g = int(40 + 20 * ratio)
                    b = int(80 + 30 * ratio)
                    color = (r, g, b)
                    pygame.draw.line(self.screen, color, (x, y + j), (x + belt_slot_size, y + j))

                pygame.draw.rect(self.screen, GOLD, belt_rect, 2)

                item = пояс[i]
                if item in self.item_icons:
                    icon = self.item_icons[item]
                    icon = pygame.transform.scale(icon, (belt_slot_size - 12, belt_slot_size - 12))
                    self.screen.blit(icon, (x + 6, y + 6))
                else:
                    name = font_tiny.render(item[:8], True, WHITE)
                    self.screen.blit(name, (x + 5, y + belt_slot_size // 2 - 5))

                num_bg = pygame.Surface((18, 18), pygame.SRCALPHA)
                num_bg.fill((0, 0, 0, 180))
                self.screen.blit(num_bg, (x + 2, y + 2))
                num = font_tiny.render(str(i + 1), True, GOLD)
                self.screen.blit(num, (x + 5, y + 2))

                remove_btn = pygame.Rect(x + belt_slot_size - 22, y + belt_slot_size - 22, 18, 18)
                if remove_btn.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, BLOOD_RED, remove_btn)
                    btn_text = font_tiny.render("В", True, WHITE)
                    pygame.draw.rect(self.screen, GOLD, remove_btn, 1)
                else:
                    pygame.draw.rect(self.screen, (100, 0, 0, 150), remove_btn)
                    pygame.draw.rect(self.screen, GOLD, remove_btn, 1)
                    btn_text = font_tiny.render("В", True, WHITE)
                self.screen.blit(btn_text, (remove_btn.x + 3, remove_btn.y + 1))

                self.inventory_items.append((remove_btn, "belt_remove", i))

                if belt_rect.collidepoint(mouse_pos):
                    tip_text = font_tiny.render(f"{item}", True, WHITE)
                    tip_x = x + belt_slot_size // 2 - tip_text.get_width() // 2
                    tip_y = y - 20
                    tip_bg = pygame.Surface((tip_text.get_width() + 10, 18), pygame.SRCALPHA)
                    tip_bg.fill((0, 0, 0, 200))
                    self.screen.blit(tip_bg, (tip_x - 5, tip_y - 2))
                    self.screen.blit(tip_text, (tip_x, tip_y))

            else:
                # Пустой слот
                pygame.draw.rect(self.screen, (30, 30, 40), belt_rect)
                pygame.draw.rect(self.screen, (80, 80, 90), belt_rect, 2)

                num_bg = pygame.Surface((18, 18), pygame.SRCALPHA)
                num_bg.fill((0, 0, 0, 150))
                self.screen.blit(num_bg, (x + 2, y + 2))
                num = font_tiny.render(str(i + 1), True, (60, 60, 70))
                self.screen.blit(num, (x + 5, y + 2))

                empty = font_tiny.render("пусто", True, (60, 60, 70))
                self.screen.blit(empty, (x + belt_slot_size // 2 - empty.get_width() // 2, y + belt_slot_size // 2 - 5))


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

        text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
        text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))

        self.inventory_back = back_rect

        hovered_item = None
        hover_pos = None

        # 1. Проверяем ячейки экипировки
        if weapon_rect.collidepoint(mouse_pos) and self.игрок['оружие']:
            hovered_item = self.игрок['оружие']
            hover_pos = (weapon_rect.centerx + 20, weapon_rect.centery)
        elif armor_rect.collidepoint(mouse_pos) and self.игрок.get("броня"):
            hovered_item = self.игрок["броня"]
            hover_pos = (armor_rect.centerx + 20, armor_rect.centery)
        elif amulet_rect.collidepoint(mouse_pos) and self.игрок.get("амулет"):
            hovered_item = self.игрок["амулет"]
            hover_pos = (amulet_rect.centerx + 20, amulet_rect.centery)
        else:
            # 2. Проверяем ячейки инвентаря (только те, где 2 элемента - rect и предмет)
            for item in self.inventory_items:
                if len(item) == 2:  # только ячейки, не кнопки "belt"
                    cell_rect, item_name = item
                    if cell_rect.collidepoint(mouse_pos):
                        hovered_item = item_name
                        hover_pos = (cell_rect.centerx + 20, cell_rect.centery)
                        break

        # 3. Рисуем подсказку ПОВЕРХ всего
        if hovered_item and hover_pos:
            self.draw_item_tooltip(hovered_item, hover_pos[0], hover_pos[1])

    def handle_inventory_click(self, pos):
        # Кнопка "Назад"
        if hasattr(self, 'inventory_back') and self.inventory_back.collidepoint(pos):
            if hasattr(self, 'previous_mode') and self.previous_mode == "эксплорейшн":
                self.режим = "эксплорейшн"
                self.previous_mode = None
            else:
                self.режим = "игра"
            return

        # ===== КЛИК ПО ЯЧЕЙКЕ ОРУЖИЯ =====
        if hasattr(self, 'equip_weapon_rect') and self.equip_weapon_rect.collidepoint(pos):
            if self.игрок['оружие']:
                оружие = self.игрок['оружие']
                self.игрок["инвентарь"].append(оружие)
                self.игрок['оружие'] = None
                self.add_to_log(f"Снято {оружие}")
            return

        # ===== КЛИК ПО ЯЧЕЙКЕ БРОНИ =====
        if hasattr(self, 'equip_armor_rect') and self.equip_armor_rect.collidepoint(pos):
            if self.игрок.get("броня"):
                броня = self.игрок["броня"]
                данные = предметы.предметы.get(броня, {})

                if "сила" in данные:
                    self.игрок["сила"] -= данные["сила"]
                if "ловкость" in данные:
                    self.игрок["ловкость"] -= данные["ловкость"]
                if "стойкость" in данные:
                    self.игрок["стойкость"] -= данные["стойкость"]
                if "интеллект" in данные:
                    self.игрок["интеллект"] -= данные["интеллект"]
                if "кулинария" in данные:
                    self.игрок["кулинария"] -= данные["кулинария"]
                if "алхимия" in данные:
                    self.игрок["алхимия"] -= данные["алхимия"]
                if "кузнечное_дело" in данные:
                    self.игрок["кузнечное_дело"] -= данные["кузнечное_дело"]
                if "защита" in данные:
                    self.игрок["защита_бонус"] = 0

                self.игрок["инвентарь"].append(броня)
                self.игрок["броня"] = None
                self.inventory.update_max_health()
                self.add_to_log(f"Снята {броня}")
                print(f"✅ Снята {броня}")
            return

        # ===== КЛИК ПО ЯЧЕЙКЕ АМУЛЕТА =====
        if hasattr(self, 'equip_amulet_rect') and self.equip_amulet_rect.collidepoint(pos):
            if self.игрок.get("амулет"):
                амулет = self.игрок["амулет"]
                self.inventory.add_item(амулет)
                self.игрок["амулет"] = None
                self.add_to_log(f"Снят {амулет}")
                self.inventory.update_amulet_effect()
            return

        # ===== КЛИК ПО ЯЧЕЙКАМ ИНВЕНТАРЯ (ОДИН ЦИКЛ!) =====
        if hasattr(self, 'inventory_items'):
            for item in self.inventory_items:
                if len(item) == 3:
                    # Формат: (rect, action, data)
                    rect, action, data = item
                    if rect.collidepoint(pos):
                        if action == "belt":
                            # Кладём на пояс
                            успех = self.add_to_belt(data)
                            if успех:
                                self.inventory.remove_item(data)
                                self.add_to_log(f"{data} помещён на пояс")
                                self.draw_inventory()
                            else:
                                self.add_to_log("Пояс полон!")
                            return
                        elif action == "belt_remove":
                            # Снимаем с пояса
                            slot_index = data
                            пояс = self.игрок.get("пояс", [])
                            if slot_index < len(пояс) and пояс[slot_index] is not None:
                                зелье = пояс[slot_index]
                                пояс[slot_index] = None
                                self.inventory.add_item(зелье)
                                self.add_to_log(f"{зелье} снят с пояса")
                                self.draw_inventory()
                            return
                else:
                    # Формат: (rect, предмет) - обычная ячейка
                    rect, предмет = item
                    if rect.collidepoint(pos):
                        успех, сообщение = self.inventory.use_item(предмет)
                        if успех:
                            self.add_to_log(сообщение)
                        else:
                            self.add_to_log(f"{сообщение}")
                        return

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

    def draw_trade(self):
        """Отрисовка окна торговца с анимацией"""

        # Анимация появления
        if not hasattr(self, 'trade_animation_progress'):
            self.trade_animation_progress = 0

        if self.trade_animation_progress < 1:
            self.trade_animation_progress += 0.08
            if self.trade_animation_progress > 1:
                self.trade_animation_progress = 1

        # Параметры панели с анимацией
        panel_width = 900
        panel_height = 620
        start_x = -panel_width
        current_x = start_x + (panel_width * self.trade_animation_progress)
        panel_x = int(current_x)
        panel_y = 50

        # Фон с затемнением
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 10))
        self.screen.blit(overlay, (0, 0))

        # Основная панель с градиентом
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Градиентный фон
        for i in range(panel_height):
            ratio = i / panel_height
            r = int(26 + 15 * ratio)
            g = int(26 + 10 * ratio)
            b = int(46 + 20 * ratio)
            color = (r, g, b)
            pygame.draw.line(self.screen, color,
                             (panel_x, panel_y + i),
                             (panel_x + panel_width, panel_y + i))

        # Золотая рамка с декоративными углами
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Декоративные уголки
        corner_size = 20
        corners = [
            (panel_x, panel_y),
            (panel_x + panel_width - corner_size, panel_y),
            (panel_x, panel_y + panel_height - corner_size),
            (panel_x + panel_width - corner_size, panel_y + panel_height - corner_size)
        ]
        for cx, cy in corners:
            pygame.draw.rect(self.screen, GOLD, (cx, cy, corner_size, corner_size), 2)
            pygame.draw.line(self.screen, GOLD, (cx + 5, cy + 5), (cx + corner_size - 5, cy + corner_size - 5), 1)
            pygame.draw.line(self.screen, GOLD, (cx + corner_size - 5, cy + 5), (cx + 5, cy + corner_size - 5), 1)

        # Заголовок с именем торговца
        title = font_large.render(self.trader_name, True, GOLD)
        title_shadow = font_large.render(self.trader_name, True, (80, 60, 30))
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title_shadow, (title_x + 3, panel_y + 23))
        self.screen.blit(title, (title_x, panel_y + 20))

        # Приветствие
        greeting = font_small.render(f"\"{self.trader_greeting}\"", True, (200, 200, 180))
        greeting_x = panel_x + panel_width // 2 - greeting.get_width() // 2
        self.screen.blit(greeting, (greeting_x, panel_y + 70))

        # Декоративная линия
        line_y = panel_y + 105
        for i in range(2):
            line_width = panel_width - 150 - i * 20
            line_x = panel_x + 75 + i * 10
            pygame.draw.line(self.screen, (GOLD[0], GOLD[1], GOLD[2], 100 - i * 30),
                             (line_x, line_y + i),
                             (line_x + line_width, line_y + i), 2)

        # ===== БЛОК С МОНЕТАМИ =====
        coins_text = font_medium.render(f"Монеты: {self.игрок.get('монета', 0)}", True, GOLD)
        self.screen.blit(coins_text, (panel_x + 30, panel_y + 125))

        # ===== СОЗДАЁМ СПИСОК КНОПОК =====
        self.trade_buttons = []

        # Кнопки переключения режимов
        buy_rect = pygame.Rect(panel_x + panel_width - 280, panel_y + 120, 120, 40)
        sell_rect = pygame.Rect(panel_x + panel_width - 150, panel_y + 120, 120, 40)

        mouse_pos = pygame.mouse.get_pos()

        # Кнопка "КУПИТЬ"
        if buy_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, buy_rect)
            buy_text = font_medium.render("КУПИТЬ", True, BLACK)
            glow_rect = pygame.Rect(buy_rect.x - 3, buy_rect.y - 3, buy_rect.width + 6, buy_rect.height + 6)
            pygame.draw.rect(self.screen, (255, 215, 0, 100), glow_rect, 2)
        else:
            if self.trade_mode == "buy":
                pygame.draw.rect(self.screen, GOLD, buy_rect)
                buy_text = font_medium.render("КУПИТЬ", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, buy_rect)
                pygame.draw.rect(self.screen, GOLD, buy_rect, 2)
                buy_text = font_medium.render("КУПИТЬ", True, WHITE)

        text_x = buy_rect.x + buy_rect.width // 2 - buy_text.get_width() // 2
        text_y = buy_rect.y + buy_rect.height // 2 - buy_text.get_height() // 2
        self.screen.blit(buy_text, (text_x, text_y))

        # Кнопка "ПРОДАТЬ"
        if sell_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, sell_rect)
            sell_text = font_medium.render("ПРОДАТЬ", True, BLACK)
            glow_rect = pygame.Rect(sell_rect.x - 3, sell_rect.y - 3, sell_rect.width + 6, sell_rect.height + 6)
            pygame.draw.rect(self.screen, (255, 215, 0, 100), glow_rect, 2)
        else:
            if self.trade_mode == "sell":
                pygame.draw.rect(self.screen, GOLD, sell_rect)
                sell_text = font_medium.render("ПРОДАТЬ", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, sell_rect)
                pygame.draw.rect(self.screen, GOLD, sell_rect, 2)
                sell_text = font_medium.render("ПРОДАТЬ", True, WHITE)

        text_x = sell_rect.x + sell_rect.width // 2 - sell_text.get_width() // 2
        text_y = sell_rect.y + sell_rect.height // 2 - sell_text.get_height() // 2
        self.screen.blit(sell_text, (text_x, text_y))

        self.trade_buttons.append(("buy_mode", buy_rect))
        self.trade_buttons.append(("sell_mode", sell_rect))

        # ===== ПАНЕЛЬ СОВЕТОВ (под монетами, слева) =====
        self._draw_trade_tips(panel_x, panel_y, panel_width, panel_height)

        # Заголовки колонок
        headers = ["ПРЕДМЕТ", "ХАРАКТЕРИСТИКИ", "ЦЕНА", "ДЕЙСТВИЕ"]
        header_x = [panel_x + 80, panel_x + 280, panel_x + 550, panel_x + 700]

        for i, header in enumerate(headers):
            header_text = font_small.render(header, True, GOLD)
            self.screen.blit(header_text, (header_x[i], panel_y + 175))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 50, panel_y + 205),
                         (panel_x + panel_width - 50, panel_y + 205), 2)

        # Отображаем соответствующий режим
        if self.trade_mode == "buy":
            self._draw_trade_buy(panel_x, panel_y, panel_width, panel_height)
        else:
            self._draw_trade_sell(panel_x, panel_y, panel_width, panel_height)

        # Кнопка "Назад"
        back_rect = pygame.Rect(panel_x + panel_width // 2 - 80, panel_y + panel_height - 60, 160, 40)

        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, back_rect)
            back_text = font_medium.render("НАЗАД", True, BLACK)
            arrow_text = font_medium.render("", True, BLACK)
            self.screen.blit(arrow_text, (back_rect.x + 20, back_rect.y + 8))
        else:
            pygame.draw.rect(self.screen, DARK_RED, back_rect)
            pygame.draw.rect(self.screen, GOLD, back_rect, 2)
            back_text = font_medium.render("НАЗАД", True, WHITE)
            arrow_text = font_medium.render("", True, WHITE)
            self.screen.blit(arrow_text, (back_rect.x + 20, back_rect.y + 8))

        text_x = back_rect.x + back_rect.width // 2 - back_text.get_width() // 2
        text_y = back_rect.y + back_rect.height // 2 - back_text.get_height() // 2
        self.screen.blit(back_text, (text_x, text_y))

        self.trade_buttons.append(("back", back_rect))

    def _draw_trade_buy(self, panel_x, panel_y, panel_width, panel_height):
        """Отрисовка режима покупки"""

        # Сортировка товаров
        товары_список = sorted(self.trade_goods.items(), key=lambda x: x[0])

        # Параметры прокрутки
        if not hasattr(self, 'trade_scroll'):
            self.trade_scroll = 0

        visible_items = 6
        item_height = 55
        start_y = panel_y + 220
        max_scroll = max(0, len(товары_список) - visible_items)

        # Кнопки прокрутки
        if len(товары_список) > visible_items:
            # Стрелка вверх
            up_rect = pygame.Rect(panel_x + panel_width - 60, start_y, 40, 30)
            if up_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, up_rect)
                up_text = font_medium.render("", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, up_rect)
                pygame.draw.rect(self.screen, GOLD, up_rect, 1)
                up_text = font_medium.render("", True, WHITE)
            self.screen.blit(up_text, (up_rect.x + 12, up_rect.y + 3))
            self.trade_buttons.append(("scroll_up", up_rect))

            # Стрелка вниз
            down_rect = pygame.Rect(panel_x + panel_width - 60, start_y + visible_items * item_height, 40, 30)
            if down_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, down_rect)
                down_text = font_medium.render("", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, down_rect)
                pygame.draw.rect(self.screen, GOLD, down_rect, 1)
                down_text = font_medium.render("", True, WHITE)
            self.screen.blit(down_text, (down_rect.x + 12, down_rect.y + 3))
            self.trade_buttons.append(("scroll_down", down_rect))

        # Отображаем товары
        self.trade_items = []
        start_index = self.trade_scroll
        end_index = min(start_index + visible_items, len(товары_список))

        for i in range(start_index, end_index):
            предмет, данные = товары_список[i]
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

            # Характеристики
            item_data = предметы.предметы.get(предмет, {})
            item_type = item_data.get("тип", "")

            if item_type == "оружие":
                stats = f"Урон: +{item_data.get('урон', 0)}"
            elif item_type == "броня":
                stats = f"Защита: +{item_data.get('защита', 0)}"
            elif item_type == "еда":
                stats = f"Восст.: {item_data.get('здоровье', 0)} HP"
            else:
                stats = item_type.capitalize()

            stats_text = font_tiny.render(stats, True, (180, 180, 160))
            self.screen.blit(stats_text, (name_x, y + 35))

            # Цена
            price_text = font_small.render(f"{данные['цена']}", True, GOLD)
            self.screen.blit(price_text, (panel_x + 560, y + 18))

            # Кнопки покупки
            btn1_rect = pygame.Rect(panel_x + 700, y + 10, 45, 30)
            btn5_rect = pygame.Rect(panel_x + 755, y + 10, 45, 30)

            # Кнопка x1
            if btn1_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, btn1_rect)
                btn1_text = font_small.render("x1", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, btn1_rect)
                pygame.draw.rect(self.screen, GOLD, btn1_rect, 1)
                btn1_text = font_small.render("x1", True, WHITE)
            self.screen.blit(btn1_text, (btn1_rect.x + 12, btn1_rect.y + 5))
            self.trade_items.append(("buy_1", предмет, btn1_rect))

            # Кнопка x5
            if btn5_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, btn5_rect)
                btn5_text = font_small.render("x5", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, btn5_rect)
                pygame.draw.rect(self.screen, GOLD, btn5_rect, 1)
                btn5_text = font_small.render("x5", True, WHITE)
            self.screen.blit(btn5_text, (btn5_rect.x + 12, btn5_rect.y + 5))
            self.trade_items.append(("buy_5", предмет, btn5_rect))

    def _draw_trade_tips(self, panel_x, panel_y, panel_width, panel_height):
        """Рисует панель советов торговца (под монетами, слева)"""

        торговец_данные = торговец.торговцы.get(self.trade_location, {})
        советы = торговец_данные.get("советы", [])

        if not советы:
            return

        # Выбираем совет
        if not hasattr(self, 'current_tip') or self.current_tip is None:
            self.current_tip = random.choice(советы)

        # Позиция панели советов (ПОД монетами, слева)
        tips_width = 300
        tips_height = 100
        tips_x = panel_x + 925  # на одном уровне с монетами
        tips_y = panel_y + 510  # под монетами (было 125 у монет + 40 отступ)

        # Фон панели советов
        tips_rect = pygame.Rect(tips_x, tips_y, tips_width, tips_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), tips_rect)
        pygame.draw.rect(self.screen, GOLD, tips_rect, 2)

        # Заголовок
        tips_title = font_small.render("СОВЕТ ТОРГОВЦА", True, GOLD)
        self.screen.blit(tips_title, (tips_x + 10, tips_y + 8))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (tips_x + 10, tips_y + 32),
                         (tips_x + tips_width - 10, tips_y + 32), 1)

        # ===== РАЗБИВАЕМ ТЕКСТ НА СТРОКИ =====
        совет = self.current_tip
        max_width = tips_width - 25  # отступы слева и справа

        # Разбиваем текст на строки
        строки = self._разбить_текст_на_строки(совет, max_width, font_small)

        # Ограничиваем количество строк (максимум 2)
        строки = строки[:2]

        # Отображаем строки
        y_offset = tips_y + 38
        for i, строка in enumerate(строки):
            tip_text = font_small.render(f"\"{строка}\"", True, (220, 220, 200))
            self.screen.blit(tip_text, (tips_x + 10, y_offset + i * 18))

        # Кнопка "ЕЩЁ" (в правом нижнем углу)
        if len(советы) > 1:
            tip_button_rect = pygame.Rect(tips_x + tips_width - 55, tips_y + tips_height - 22, 45, 18)
            if tip_button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, tip_button_rect)
                tip_button_text = font_tiny.render("ЕЩЁ", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, tip_button_rect)
                pygame.draw.rect(self.screen, GOLD, tip_button_rect, 1)
                tip_button_text = font_tiny.render("ЕЩЁ", True, WHITE)
            self.screen.blit(tip_button_text, (tip_button_rect.x + 12, tip_button_rect.y + 3))
            self.trade_buttons.append(("ask_tip", tip_button_rect))

    def handle_trade_click(self, pos):
        """Обработка кликов в окне торговца"""

        if not hasattr(self, 'trade_buttons'):
            return

        # Инициализируем trade_scroll, если его нет
        if not hasattr(self, 'trade_scroll'):
            self.trade_scroll = 0

        for action, *data in self.trade_buttons:
            if action == "back" and data[0].collidepoint(pos):
                self.режим = "игра"
                if hasattr(self, 'trade_buttons'):
                    delattr(self, 'trade_buttons')
                if hasattr(self, 'trade_scroll'):
                    delattr(self, 'trade_scroll')
                return

            elif action == "buy_mode" and data[0].collidepoint(pos):
                self.trade_mode = "buy"
                self.trade_scroll = 0
                return

            elif action == "sell_mode" and data[0].collidepoint(pos):
                self.trade_mode = "sell"
                self.trade_scroll = 0
                return

            elif action == "ask_tip" and data[0].collidepoint(pos):
                # Меняем совет на новый случайный
                import торговец
                import random
                торговец_данные = торговец.торговцы.get(self.trade_location, {})
                советы = торговец_данные.get("советы", [])
                if советы:
                    if len(советы) > 1:
                        новый_совет = random.choice(советы)
                        if hasattr(self, 'current_tip') and self.current_tip == новый_совет:
                            другие_советы = [с for с in советы if с != self.current_tip]
                            if другие_советы:
                                новый_совет = random.choice(другие_советы)
                        self.current_tip = новый_совет
                    else:
                        self.current_tip = советы[0]
                    self.add_to_log(f" {self.trader_name} дал новый совет")
                return

        # Обработка покупки/продажи
        if hasattr(self, 'trade_items'):
            for item_data in self.trade_items:
                if item_data[0] == "buy_1":
                    action, предмет, rect = item_data
                    if rect.collidepoint(pos):
                        self.trade_buy_item(предмет, 1)
                        return

                elif item_data[0] == "buy_5":  # ← новая кнопка
                    action, предмет, rect = item_data
                    if rect.collidepoint(pos):
                        self.trade_buy_item(предмет, 5)
                        return

                elif item_data[0] == "sell_1":
                    action, предмет, rect, цена = item_data
                    if rect.collidepoint(pos):
                        self.trade_sell_item(предмет, 1, цена)
                        return

                elif item_data[0] == "sell_all":
                    action, предмет, rect, цена, количество = item_data
                    if rect.collidepoint(pos):
                        self.trade_sell_item(предмет, количество, цена)
                        return

    def handle_craft_click(self, pos):
        """Обработка кликов в верстаке"""

        # Кнопка "Назад"
        for action, rect in self.craft_buttons:
            if action == "back" and rect.collidepoint(pos):
                self.режим = "игра"
                return
            elif action == "scroll_up" and rect.collidepoint(pos):
                self.craft_scroll = max(0, self.craft_scroll - 1)
                return
            elif action == "scroll_down" and rect.collidepoint(pos):
                # Получаем рецепты для текущей категории
                рецепты_категории = []
                for recipe_name in self.craft_categories[self.craft_category]:
                    if recipe_name in self.craft_recipes:
                        рецепты_категории.append(recipe_name)

                max_scroll = len(рецепты_категории) - 7
                self.craft_scroll = min(max_scroll, self.craft_scroll + 1)
                return

        # Переключение категорий
        if hasattr(self, 'category_buttons'):
            for category, rect in self.category_buttons:
                if rect.collidepoint(pos):
                    self.craft_category = category
                    self.craft_scroll = 0
                    return

        # Кнопки создания предметов
        for название, рецепт, btn_rect in self.craft_items:
            if btn_rect.collidepoint(pos):
                self.craft_item(название, рецепт)
                return

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

    def draw_craft(self):
        """Отрисовка окна верстака с категориями и прокруткой"""

        self.craft_buttons = []
        self.craft_items = []

        # Категории рецептов
        categories = {
            "ОРУЖИЕ": ["лезвие", "призрачный меч"],
            "БРОНЯ": ["кожаная броня", "кольчужная броня"],
            "ЕДА": ["блины", "рыба", "зелье здоровья"],
            "МАТЕРИАЛЫ": ["шестерёнка"]
        }

        # Если нет выбранной категории, выбираем первую
        if not hasattr(self, 'craft_category'):
            self.craft_category = list(categories.keys())[0]

        # Параметры прокрутки
        if not hasattr(self, 'craft_scroll'):
            self.craft_scroll = 0

        # Затемняем фон
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (0, 0))

        # Рамка окна
        craft_rect = pygame.Rect(100, 50, 1080, 650)
        pygame.draw.rect(self.screen, DARK_BLUE, craft_rect)
        pygame.draw.rect(self.screen, GOLD, craft_rect, 3)

        # Заголовок
        title = font_large.render("ВЕРСТАК", True, GOLD)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        # Ресурсы игрока
        y_res = 120
        ресурсы_текст = font_medium.render("ТВОИ РЕСУРСЫ:", True, GOLD)
        self.screen.blit(ресурсы_текст, (120, y_res))

        # Подсчёт ресурсов
        ресурсы = {}
        for предмет in self.игрок["инвентарь"]:
            if предмет in предметы.предметы and предметы.предметы[предмет]["тип"] == "ресурс":
                ресурсы[предмет] = ресурсы.get(предмет, 0) + 1

        # Отображаем ресурсы
        if ресурсы:
            ресурсы_список = []
            for предмет, количество in ресурсы.items():
                ресурсы_список.append(f"{предмет} x{количество}")
            ресурсы_строка = " | ".join(ресурсы_список)

            if len(ресурсы_строка) > 80:
                ресурсы_строка = ресурсы_строка[:80] + "..."

            res_display = font_small.render(ресурсы_строка, True, WHITE)
            self.screen.blit(res_display, (120, y_res + 25))
        else:
            res_display = font_small.render("Нет ресурсов", True, GRAY)
            self.screen.blit(res_display, (120, y_res + 25))

        # Разделитель
        pygame.draw.line(self.screen, GOLD, (120, 180), (1060, 180), 2)

        # ===== КАТЕГОРИИ =====
        cat_x = 120
        cat_y = 190
        cat_spacing = 120

        self.category_buttons = []
        for i, category in enumerate(categories.keys()):
            cat_rect = pygame.Rect(cat_x + i * cat_spacing, cat_y, 110, 30)

            # Подсветка выбранной категории
            if category == self.craft_category:
                pygame.draw.rect(self.screen, GOLD, cat_rect)
                cat_text = font_small.render(category, True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, cat_rect)
                pygame.draw.rect(self.screen, GOLD, cat_rect, 2)
                cat_text = font_small.render(category, True, WHITE)

            self.screen.blit(cat_text, (cat_rect.x + 5, cat_rect.y + 5))
            self.category_buttons.append((category, cat_rect))

        # ===== СПИСОК РЕЦЕПТОВ С ПРОКРУТКОЙ =====
        # Заголовки колонок
        name_header = font_small.render("РЕЦЕПТ", True, GOLD)
        resources_header = font_small.render("НУЖНО", True, GOLD)

        self.screen.blit(name_header, (120, 230))
        self.screen.blit(resources_header, (450, 230))

        # Получаем рецепты для выбранной категории
        category_recipes = []
        for recipe_name in categories[self.craft_category]:
            if recipe_name in self.craft_recipes:
                category_recipes.append((recipe_name, self.craft_recipes[recipe_name]))

        # Параметры отображения
        y_start = 260
        item_height = 45
        visible_items = 7  # Сколько рецептов видно одновременно

        # Кнопки прокрутки
        if len(category_recipes) > visible_items:
            # Стрелка вверх
            up_rect = pygame.Rect(1000, 230, 30, 30)
            if up_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, up_rect)
                up_text = font_medium.render("▲", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, up_rect)
                pygame.draw.rect(self.screen, GOLD, up_rect, 2)
                up_text = font_medium.render("▲", True, WHITE)
            self.screen.blit(up_text, (1005, 235))
            self.craft_buttons.append(("scroll_up", up_rect))

            # Стрелка вниз
            down_rect = pygame.Rect(1000, 570, 30, 30)
            if down_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, GOLD, down_rect)
                down_text = font_medium.render("▼", True, BLACK)
            else:
                pygame.draw.rect(self.screen, DARK_RED, down_rect)
                pygame.draw.rect(self.screen, GOLD, down_rect, 2)
                down_text = font_medium.render("▼", True, WHITE)
            self.screen.blit(down_text, (1005, 575))
            self.craft_buttons.append(("scroll_down", down_rect))

        # Отображаем видимые рецепты
        start_index = self.craft_scroll
        end_index = min(start_index + visible_items, len(category_recipes))

        y = y_start
        for i in range(start_index, end_index):
            название, рецепт = category_recipes[i]

            # Группируем одинаковые ресурсы
            нужные_ресурсы = {}
            for ресурс in рецепт["ресурсы"]:
                нужные_ресурсы[ресурс] = нужные_ресурсы.get(ресурс, 0) + 1

            # Проверяем, есть ли все ресурсы
            есть_все = True
            for ресурс, нужно in нужные_ресурсы.items():
                if ресурсы.get(ресурс, 0) < нужно:
                    есть_все = False
                    break

            # Подсветка при наведении
            item_rect = pygame.Rect(120, y - 3, 800, 35)
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, DARK_RED, item_rect)

            # Название рецепта
            name_text = font_small.render(название, True, WHITE)
            self.screen.blit(name_text, (120, y))

            # Нужные ресурсы (группированные)
            ресурсы_текст = []
            for ресурс, нужно in нужные_ресурсы.items():
                if нужно > 1:
                    ресурсы_текст.append(f"{ресурс} x{нужно}")
                else:
                    ресурсы_текст.append(ресурс)

            res_text = font_small.render(", ".join(ресурсы_текст), True, WHITE)
            self.screen.blit(res_text, (450, y + 2))

            # Индикатор наличия ресурсов
            if есть_все:
                indicator = "+"
            else:
                indicator = "-"
            ind_text = font_small.render(indicator, True, WHITE)
            self.screen.blit(ind_text, (920, y))

            # Кнопка создания (только если есть ресурсы)
            if есть_все:
                btn_rect = pygame.Rect(960, y - 3, 100, 30)
                if btn_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, GOLD, btn_rect)
                    btn_text = font_small.render("СОЗДАТЬ", True, BLACK)
                else:
                    pygame.draw.rect(self.screen, DARK_RED, btn_rect)
                    pygame.draw.rect(self.screen, GOLD, btn_rect, 1)
                    btn_text = font_small.render("СОЗДАТЬ", True, WHITE)
                self.screen.blit(btn_text, (btn_rect.x + 10, btn_rect.y + 5))
                self.craft_items.append((название, рецепт, btn_rect))

            y += item_height

        # Кнопка "Назад"
        back_rect = pygame.Rect(WIDTH // 2 - 100, 620, 200, 50)
        pygame.draw.rect(self.screen, DARK_RED, back_rect)
        pygame.draw.rect(self.screen, GOLD, back_rect, 2)
        back_text = font_medium.render("НАЗАД", True, WHITE)
        self.screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 635))
        self.craft_buttons.append(("back", back_rect))



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
        self.остановить_музыку()  # 👈 СНАЧАЛА ОСТАНАВЛИВАЕМ

        # ===== ВОЗВРАЩАЕМ МУЗЫКУ ЛОКАЦИИ =====
        if self.есть_музыка(self.текущая_локация):
            self.переключить_плейлист(self.текущая_локация)
        else:
            self.остановить_музыку()

        # Если бой был в данже, удаляем врага
        if hasattr(self, 'exploration_in_battle') and self.exploration_in_battle:
            if hasattr(self, 'current_enemy'):
                from враги import ЛЕСНЫЕ_БОССЫ
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

    def draw_map(self):
        """Отрисовка карты с кликабельными локациями и учётом барьеров"""

        # Лёгкое затемнение (прозрачное)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 10))  # 80 - лёгкое затемнение (рекомендую 80 вместо 180)
        self.screen.blit(s, (0, 0))

        # Координаты кликабельных областей для каждой локации
        self.map_rects = {
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

        # Загружаем карту
        try:
            map_img = pygame.image.load("assets/ui/map.png").convert_alpha()
            map_img = pygame.transform.scale(map_img, (1000, 600))
            self.screen.blit(map_img, (WIDTH // 2 - 500, HEIGHT // 2 - 300))
        except Exception as e:
            print(f"❌ Ошибка загрузки карты: {e}")
            text = font_medium.render("Карта не найдена", True, GOLD)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        # Создаём словарь инвентаря для проверки барьеров
        инвентарь_словарь = {}
        for предмет in self.игрок["инвентарь"]:
            инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

        # Проверяем доступность каждой локации
        self.доступные_локации = {}
        self.заблокированные_локации = {}

        for название, rect in self.map_rects.items():
            доступна, причина, подсказка = барьеры.проверить_доступность_локации(
                название, инвентарь_словарь
            )

            if доступна:
                self.доступные_локации[название] = rect
            else:
                self.заблокированные_локации[название] = {
                    "rect": rect,
                    "причина": причина,
                    "подсказка": подсказка
                }

        # Рисуем блокировки поверх карты
        map_x = WIDTH // 2 - 500
        map_y = HEIGHT // 2 - 300

        for название, данные in self.заблокированные_локации.items():
            rect = данные["rect"]
            world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)

            # Затемняем заблокированную локацию
            s_block = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s_block.fill((0, 0, 0, 150))
            self.screen.blit(s_block, (world_rect.x, world_rect.y))

            # Рисуем замок
            lock_text = font_small.render("Х", True, GOLD)
            self.screen.blit(lock_text, (world_rect.x + rect.width // 2 - 10, world_rect.y + rect.height // 2 - 10))

        # Подсвечиваем текущую локацию
        if self.текущая_локация in self.map_rects:
            rect = self.map_rects[self.текущая_локация]
            highlight_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
            pygame.draw.rect(self.screen, GOLD, highlight_rect, 3)

            # Добавляем текст "ВЫ ЗДЕСЬ"
            here_text = font_small.render("ТЫ", True, GOLD)
            self.screen.blit(here_text, (map_x + rect.x + 35, map_y + rect.y - 15))

        # Подсветка при наведении и показ подсказок
        mouse_pos = pygame.mouse.get_pos()
        self.map_hover_location = None
        self.map_hover_blocked = False
        self.map_hover_reason = None

        for название, rect in self.доступные_локации.items():
            world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
            if world_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GOLD, world_rect, 2)
                self.map_hover_location = название
                self.map_hover_blocked = False

        for название, данные in self.заблокированные_локации.items():
            rect = данные["rect"]
            world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
            if world_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BLOOD_RED, world_rect, 2)
                self.map_hover_location = название
                self.map_hover_blocked = True
                self.map_hover_reason = данные["причина"]
                self.map_hover_hint = данные["подсказка"]

        if hasattr(self, 'map_hover_location') and self.map_hover_location:
            tip_x = mouse_pos[0] + 15
            tip_y = mouse_pos[1] + 15

            # Получаем данные локации
            локация_данные = локации.локации.get(self.map_hover_location, {})
            уровень = локация_данные.get("уровень", "?")
            сложность = локация_данные.get("сложность", "")

            # Определяем цвет и звёзды сложности
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

            if self.map_hover_blocked:
                # Заблокированная локация - ДОБАВЛЯЕМ ФОН
                tip_width = 300
                tip_height = 80
                tip_bg = pygame.Surface((tip_width, tip_height), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 200))
                self.screen.blit(tip_bg, (tip_x, tip_y))

                tip_text = font_small.render(f"[ЗАКРЫТО] {self.map_hover_location}", True, BLOOD_RED)
                self.screen.blit(tip_text, (tip_x + 10, tip_y + 5))

                reason_text = font_small.render(self.map_hover_reason[:40], True, WHITE)
                self.screen.blit(reason_text, (tip_x + 10, tip_y + 30))

                hint_text = font_small.render(f"[СОВЕТ] {self.map_hover_hint}", True, GOLD)
                self.screen.blit(hint_text, (tip_x + 10, tip_y + 55))
            else:
                # Доступная локация
                tip_width = 220
                tip_height = 95

                # Фон подсказки
                tip_bg = pygame.Surface((tip_width, tip_height), pygame.SRCALPHA)
                tip_bg.fill((0, 0, 0, 200))
                self.screen.blit(tip_bg, (tip_x, tip_y))

                # Название
                name_text = font_small.render(f"[ЛОКАЦИЯ] {self.map_hover_location}", True, GOLD)
                self.screen.blit(name_text, (tip_x + 10, tip_y + 5))

                # Уровень
                level_text = font_small.render(f"[УРОВЕНЬ] {уровень}", True, WHITE)
                self.screen.blit(level_text, (tip_x + 10, tip_y + 30))

                # Сложность
                сложность_текст = font_small.render(f"[СЛОЖНОСТЬ] {звезды}", True, цвет_сложности)
                self.screen.blit(сложность_текст, (tip_x + 10, tip_y + 55))

                # Предупреждение если уровень выше
                if уровень != "?" and уровень > self.игрок["уровень"] + 2:
                    warning = font_small.render("[ОПАСНО]", True, HEALTH_RED)
                    self.screen.blit(warning, (tip_x + 10, tip_y + 75))
                elif уровень != "?" and уровень < self.игрок["уровень"] - 2:
                    easy = font_small.render("[БЕЗОПАСНО]", True, HEALTH_GREEN)
                    self.screen.blit(easy, (tip_x + 10, tip_y + 75))

        # Кнопка закрытия
        close_rect = pygame.Rect(WIDTH // 2 + 425, HEIGHT // 2 - 280, 40, 40)
        if self.close_icon:
            self.screen.blit(self.close_icon, (close_rect.x, close_rect.y))
        self.map_close_button = close_rect

    def handle_map_click(self, pos):
        """Обработка кликов на карте с учётом барьеров"""

        # Кнопка закрытия
        if hasattr(self, 'map_close_button') and self.map_close_button.collidepoint(pos):
            if hasattr(self, 'previous_mode') and self.previous_mode == "эксплорейшн":
                self.режим = "эксплорейшн"
            else:
                self.режим = "игра"
            return

        map_x = WIDTH // 2 - 500
        map_y = HEIGHT // 2 - 300

        # Создаём словарь инвентаря
        инвентарь_словарь = {}
        for предмет in self.игрок["инвентарь"]:
            инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

        # Проверяем клики по ВСЕМ локациям
        for название, rect in self.map_rects.items():
            world_rect = pygame.Rect(map_x + rect.x, map_y + rect.y, rect.width, rect.height)
            if world_rect.collidepoint(pos):

                print(f"\n🎯 КЛИК ПО ЛОКАЦИИ: {название}")
                print(f"📍 Текущая локация: {self.текущая_локация}")
                print(f"📦 Инвентарь: {инвентарь_словарь}")

                # Проверяем доступность
                доступна, причина, подсказка = барьеры.проверить_доступность_локации(
                    название, инвентарь_словарь
                )

                print(f"🔍 Доступна: {доступна}")
                if not доступна:
                    print(f"   ❌ Причина: {причина}")
                    print(f"   💡 Подсказка: {подсказка}")

                if доступна:
                    # ===== ПРОВЕРЯЕМ, ОТКРЫТ ЛИ УЖЕ БАРЬЕР =====
                    if барьеры.is_barrier_open(название):
                        print(f"✅ Барьер для {название} УЖЕ ОТКРЫТ, переходим")
                        self.change_location(название)
                        # ❌ УБИРАЕМ self.режим = "игра"
                        return

                    # ===== ИЩЕМ БАРЬЕР =====
                    барьер_найден = False
                    for локация_источник, барьеры_локации in барьеры.барьеры.items():
                        for барьер_ключ, барьер in барьеры_локации.items():
                            if барьер["локация_назначения"] == название:
                                барьер_найден = True
                                print(f"🔑 НАЙДЕН БАРЬЕР: {локация_источник} -> {барьер_ключ}")
                                print(f"   Требуется: {барьер['требуется']} x{барьер.get('требуется_количество', 1)}")

                                # Открываем барьер
                                успех, сообщение, новый_инвентарь = барьеры.открыть_локацию_через_барьер(
                                    self.текущая_локация, название, инвентарь_словарь
                                )

                                if успех:
                                    print(f"✅ БАРЬЕР ОТКРЫТ! {сообщение}")

                                    self.игрок["инвентарь"] = []
                                    for предмет, колво in новый_инвентарь.items():
                                        self.игрок["инвентарь"].extend([предмет] * колво)

                                    инвентарь_словарь = {}
                                    for предмет in self.игрок["инвентарь"]:
                                        инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1

                                    self.add_to_log(сообщение)
                                    барьеры.открытые_барьеры.add(название)
                                    print(f"🔓 Барьер {название} открыт и сохранён!")

                                    self.change_location(название)
                                    # ❌ УБИРАЕМ self.режим = "игра"
                                    return
                                else:
                                    print(f"❌ НЕ УДАЛОСЬ ОТКРЫТЬ: {сообщение}")
                                    self.add_to_log(сообщение)
                                    return

                    # ===== ЕСЛИ БАРЬЕР НЕ НАЙДЕН =====
                    if not барьер_найден:
                        print(f"🚪 Нет барьера для {название}, просто переходим")
                        self.change_location(название)
                        # ❌ УБИРАЕМ self.режим = "игра"
                        return

                else:
                    print(f"❌ Локация {название} НЕДОСТУПНА")
                    self.add_to_log(причина)
                    if подсказка:
                        self.add_to_log(подсказка)
                    return

        return

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
        import предметы
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

    def draw_battle(self):
        """Экран боя в стиле настольной игры"""

        # ===== 1. ОТРИСОВКА ФОНА СТОЛА =====
        try:
            # Загружаем фон стола
            table_bg = pygame.image.load("assets/backgrounds/battle_table.png").convert()
            table_bg = pygame.transform.scale(table_bg, (WIDTH, HEIGHT))
            self.screen.blit(table_bg, (0, 0))
        except Exception as e:
            # Если файла нет - используем запасной вариант (цветной фон)
            print(f"❌ Не удалось загрузить фон стола: {e}")
            TABLE_COLOR = (70, 50, 35)
            LINE_COLOR = (90, 70, 55)
            self.screen.fill(TABLE_COLOR)
            # Вертикальные линии
            for x in range(0, WIDTH, 50):
                pygame.draw.line(self.screen, LINE_COLOR, (x, 0), (x, HEIGHT), 1)
            # Горизонтальные линии
            for y in range(0, HEIGHT, 50):
                pygame.draw.line(self.screen, LINE_COLOR, (0, y), (WIDTH, y), 1)

        # ===== 2. ОТРИСОВКА КАРТ =====
        self._draw_player_card()
        self._draw_enemy_card()
        # ===== 3. ОТРИСОВКА ЛОГА БОЯ =====
        self._draw_battle_log()
        # ===== 4. ОТРИСОВКА ПАНЕЛИ ДЕЙСТВИЙ =====
        self._draw_action_panel()
        # ===== 5. ОТРИСОВКА ПОЯСА С ЗЕЛЬЯМИ =====
        self._draw_belt_panel()  # 👈 ДОБАВЛЯЕМ
        # ===== 6. ОТРИСОВКА КНОПОК НАВЫКОВ =====
        self._draw_skill_buttons()



    def _draw_player_card(self):
        """Рисует карту игрока (слева)"""
        card_width = 350
        card_height = 460
        card_x = 80
        card_y = 80

        # Фон и рамка карты
        self._draw_card_background(card_x, card_y, card_width, card_height)

        # Название "ТЫ"
        self._draw_card_title(card_x, card_y, card_width, "ТЫ")

        # Спрайт игрока
        sprite_x = card_x + card_width // 2 - self.player_size // 2
        sprite_y = card_y + 80
        self._draw_player_sprite(sprite_x, sprite_y)

        # Полоска здоровья
        health_bar_y = sprite_y + self.player_size + 20
        self.draw_health_bar(
            card_x + 30, health_bar_y, card_width - 60, 22,
            self.игрок['здоровье'], self.игрок['макс_здоровье']
        )

        # Полоска маны (такая же как здоровье)
        mana_bar_y = health_bar_y + 32
        self.draw_mana_bar(
            card_x + 30, mana_bar_y, card_width - 60, 22,
            self.игрок.get('мана', 0), self.игрок.get('макс_мана', 50)
        )

        # Экипировка
        self._draw_player_equipment(card_x, mana_bar_y + 28)

    def _draw_enemy_card(self):
        """Рисует карту врага (справа)"""
        card_width = 350
        card_height = 450
        card_x = WIDTH - card_width - 80
        card_y = HEIGHT - card_height - 80

        # Фон и рамка карты
        self._draw_card_background(card_x, card_y, card_width, card_height)

        # Название врага
        enemy_name = self.current_enemy.replace('_', ' ').upper()
        self._draw_card_title(card_x, card_y, card_width, enemy_name)

        # Спрайт врага
        sprite_x = card_x + card_width // 2 - self.enemy_size // 2
        sprite_y = card_y + 80
        self._draw_enemy_sprite(sprite_x, sprite_y)

        # Полоска здоровья
        health_bar_y = sprite_y + self.enemy_size + 20
        self.draw_health_bar(
            card_x + 30, health_bar_y, card_width - 60, 25,
            self.enemy_health, self.enemy_data["здоровье"]
        )

        # Характеристики врага
        stats_y = health_bar_y + 40
        self._draw_enemy_stats(card_x, stats_y)

        # Описание врага (в самом низу)
        self._draw_enemy_description(card_x, card_y, card_height, stats_y + 120)

    def _draw_card_background(self, x, y, width, height):
        """Рисует фон карты с рамкой"""
        # Основной фон
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, DARK_BLUE, card_rect)
        pygame.draw.rect(self.screen, GOLD, card_rect, 4)

        # Внутренняя рамка-пергамент
        pygame.draw.rect(self.screen, GOLD, (x + 10, y + 10, width - 20, height - 20), 2)

    def _draw_card_title(self, x, y, width, title_text):
        """Рисует заголовок карты"""
        title = font_medium.render(title_text, True, GOLD)
        title_x = x + width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, y + 20))

        # Разделитель под заголовком
        pygame.draw.line(self.screen, GOLD,
                         (x + 30, y + 55),
                         (x + width - 30, y + 55), 2)

    def _draw_player_sprite(self, x, y):
        """Рисует спрайт игрока"""
        if self.player_sprite:
            self.screen.blit(self.player_sprite, (x, y))
        else:
            # Заглушка
            pygame.draw.rect(self.screen, DARK_BLUE, (x, y, self.player_size, self.player_size))
            pygame.draw.rect(self.screen, GOLD, (x, y, self.player_size, self.player_size), 2)

    def _draw_enemy_sprite(self, x, y):
        """Рисует спрайт врага"""
        if self.enemy_sprite:
            self.screen.blit(self.enemy_sprite, (x, y))
        else:
            # Заглушка
            pygame.draw.rect(self.screen, DARK_RED, (x, y, self.enemy_size, self.enemy_size))
            pygame.draw.rect(self.screen, GOLD, (x, y, self.enemy_size, self.enemy_size), 2)

    def _draw_player_equipment(self, card_x, health_bar_y):
        """Рисует экипировку игрока"""
        # Оружие
        if self.игрок['оружие']:
            weapon_text = font_small.render(f"{self.игрок['оружие']}", True, BLOOD_RED)
            self.screen.blit(weapon_text, (card_x + 20, health_bar_y + 35))

        # Броня
        if self.игрок.get("броня") and isinstance(self.игрок["броня"], str):
            armor_data = предметы.предметы.get(self.игрок["броня"], {})
            armor_def = armor_data.get("защита", 0)
            armor_text = font_small.render(f"{self.игрок['броня']} (+{armor_def})", True, HEALTH_GREEN)
            self.screen.blit(armor_text, (card_x + 20, health_bar_y + 55))

    def _draw_enemy_stats(self, card_x, stats_y):
        """Рисует характеристики врага"""

        # ===== СИЛА =====
        if "сила" in self.enemy_data:
            power_text = font_small.render(f"СИЛА: {self.enemy_data['сила']}", True, BLOOD_RED)
            self.screen.blit(power_text, (card_x + 20, stats_y))

        # ===== ОБЫЧНЫЙ ДРОП (РАБОТАЕТ С ЛЮБЫМ КОЛИЧЕСТВОМ) =====
        if "награда" in self.enemy_data:
            награда = self.enemy_data["награда"]

            # Если это список или кортеж
            if isinstance(награда, (list, tuple)):
                # Первый элемент - всегда предмет
                reward_item = награда[0] if len(награда) > 0 else "ничего"
                # Второй элемент - опыт (если есть)
                reward_exp = награда[1] if len(награда) > 1 else 0

                reward_text = font_small.render(f"НАГРАДА: {reward_item} (+{reward_exp} опыта)", True, GOLD)
                self.screen.blit(reward_text, (card_x + 20, stats_y + 25))

                # Если есть третий элемент и больше - показываем дополнительно
                if len(награда) > 2:
                    extra_items = ", ".join(str(x) for x in награда[2:])
                    extra_text = font_tiny.render(f"ДОП.: {extra_items}", True, HEALTH_YELLOW)
                    self.screen.blit(extra_text, (card_x + 20, stats_y + 45))
            else:
                # Если награда - просто строка
                reward_text = font_small.render(f"НАГРАДА: {награда}", True, GOLD)
                self.screen.blit(reward_text, (card_x + 20, stats_y + 25))

        # ===== РЕДКИЙ ДРОП =====
        редкий_дроп = self.enemy_data.get("редкий_дроп", [])

        # Ищем шанс: сначала на верхнем уровне, потом внутри "особенности"
        шанс_редкого = self.enemy_data.get("шанс_редкого_дропа", 0)
        if шанс_редкого == 0 and "особенности" in self.enemy_data:
            шанс_редкого = self.enemy_data["особенности"].get("шанс_редкого_дропа", 0)

        # Рисуем, только если есть редкий дроп
        if редкий_дроп:
            редкие_предметы = ", ".join(редкий_дроп)

            if шанс_редкого > 0:
                редкий_текст = font_tiny.render(
                    f"РЕДКИЙ ДРОП: {редкие_предметы} ({шанс_редкого}%)",
                    True, BLOOD_RED
                )
            else:
                редкий_текст = font_tiny.render(
                    f"РЕДКИЙ ДРОП: {редкие_предметы}",
                    True, BLOOD_RED
                )

            # Смещаем вниз, если есть дополнительная информация
            if "награда" in self.enemy_data and isinstance(self.enemy_data["награда"], (list, tuple)) and len(
                    self.enemy_data["награда"]) > 2:
                self.screen.blit(редкий_текст, (card_x + 20, stats_y + 68))
            else:
                self.screen.blit(редкий_текст, (card_x + 20, stats_y + 48))

    def _draw_enemy_description(self, card_x, card_y, card_height, desc_start_y):
        """Рисует описание врага в нижней части карты"""
        enemy_description = self.enemy_data.get("описание", "Таинственное создание, полное тёмной энергии.")

        # Разбиваем описание на строки
        desc_lines = self._разбить_текст_на_строки(enemy_description, 290, font_small)
        desc_lines = desc_lines[:4]  # Максимум 4 строки

        if not desc_lines:
            return

        # Проверяем, не вылезает ли за границы
        max_desc_y = card_y + card_height - 40
        if desc_start_y + len(desc_lines) * 18 > max_desc_y:
            max_lines = (max_desc_y - desc_start_y) // 18
            desc_lines = desc_lines[:max_lines]

        if not desc_lines:
            return

        # Фон для описания
        desc_bg_height = len(desc_lines) * 18 + 10
        desc_bg_rect = pygame.Rect(card_x + 20, desc_start_y - 5, 310, desc_bg_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), desc_bg_rect)
        pygame.draw.rect(self.screen, GOLD, desc_bg_rect, 1)

        # Отображаем текст описания
        for i, line in enumerate(desc_lines):
            desc_text = font_small.render(line, True, (220, 220, 200))
            text_x = card_x + 175 - desc_text.get_width() // 2
            self.screen.blit(desc_text, (text_x, desc_start_y + i * 18))

    def _draw_battle_log(self):
        """Рисует лог боя"""
        log_width = 250
        log_height = 150
        log_x = WIDTH // 2 - log_width // 2
        log_y = HEIGHT - 300

        # ===== ФОН =====
        log_surface = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
        log_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(log_surface, GOLD, log_surface.get_rect(), 2)
        self.screen.blit(log_surface, (log_x, log_y))

        # ===== ЗАГОЛОВОК =====
        current_round = self.battle.round_number if hasattr(self.battle, 'round_number') else 0
        title_text = f"ХОД БОЯ (Раунд {current_round})"
        log_title = font_small.render(title_text, True, GOLD)
        title_x = log_x + log_width // 2 - log_title.get_width() // 2
        self.screen.blit(log_title, (title_x, log_y + 5))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (log_x + 10, log_y + 25),
                         (log_x + log_width - 10, log_y + 25), 1)

        # ===== ПОКАЗЫВАЕМ СООБЩЕНИЯ =====
        text_start_y = log_y + 32
        max_lines = 8

        messages = self.battle_log[-max_lines:] if self.battle_log else []

        for i, msg in enumerate(messages):
            # Определяем цвет
            if "РАУНД" in msg:
                color = GOLD
            elif "=" * 5 in msg:  # Разделитель
                color = (100, 100, 100)  # Серый
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

            log_text = font_small.render(msg, True, color)
            text_x = log_x + log_width // 2 - log_text.get_width() // 2
            self.screen.blit(log_text, (text_x, text_start_y + i * 18))

    def _draw_belt_panel(self):
        """Рисует панель пояса с зельями в бою"""
        пояс = self.игрок.get("пояс", [])

        # Параметры панели
        slot_size = 64
        spacing = 10
        panel_width = 5 * (slot_size + spacing) + spacing + 20
        panel_height = slot_size + 60

        # Позиция - справа внизу, над панелью действий
        panel_x = WIDTH - panel_width - 1450
        panel_y = HEIGHT - 230

        # Фон панели с градиентом
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Тёмный фон с прозрачностью
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 20, 40, 200))

        # Рамка с золотым свечением
        pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 2)

        # Декоративные уголки
        corner_size = 10
        corners = [
            (2, 2),
            (panel_width - corner_size - 2, 2),
            (2, panel_height - corner_size - 2),
            (panel_width - corner_size - 2, panel_height - corner_size - 2)
        ]
        for cx, cy in corners:
            pygame.draw.rect(panel_surface, GOLD, (cx, cy, corner_size, corner_size), 2)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Заголовок с иконкой
        title = font_medium.render("ПОЯС", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 6))

        # Тонкая линия под заголовком
        pygame.draw.line(self.screen, (100, 100, 120),
                         (panel_x + 20, panel_y + 38),
                         (panel_x + panel_width - 20, panel_y + 38), 1)

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 15, panel_y + 35),
                         (panel_x + panel_width - 15, panel_y + 35), 1)

        self.belt_slots = []
        mouse_pos = pygame.mouse.get_pos()

        for i in range(5):
            x = panel_x + 15 + i * (slot_size + spacing)
            y = panel_y + 45

            slot_rect = pygame.Rect(x, y, slot_size, slot_size)

            # Тень слота
            shadow_rect = pygame.Rect(x + 2, y + 2, slot_size, slot_size)
            pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect)

            if i < len(пояс) and пояс[i] is not None:
                # Есть зелье - градиентный фон
                for j in range(slot_size):
                    ratio = j / slot_size
                    r = int(20 + 35 * ratio)
                    g = int(40 + 25 * ratio)
                    b = int(80 + 35 * ratio)
                    color = (r, g, b)
                    pygame.draw.line(self.screen, color,
                                     (x, y + j),
                                     (x + slot_size, y + j))

                pygame.draw.rect(self.screen, GOLD, slot_rect, 2)

                # Свечение при наведении
                if slot_rect.collidepoint(mouse_pos):
                    glow_rect = pygame.Rect(x - 3, y - 3, slot_size + 6, slot_size + 6)
                    pygame.draw.rect(self.screen, (255, 215, 0, 50), glow_rect, 2)

                # Иконка зелья
                item = пояс[i]
                if item in self.item_icons:
                    icon = self.item_icons[item]
                    icon = pygame.transform.scale(icon, (slot_size - 12, slot_size - 12))
                    self.screen.blit(icon, (x + 6, y + 6))
                else:
                    name = font_tiny.render(item[:8], True, WHITE)
                    self.screen.blit(name, (x + 5, y + slot_size // 2 - 5))

                # Номер слота (стильный)
                num_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
                num_bg.fill((0, 0, 0, 180))
                self.screen.blit(num_bg, (x + 2, y + 2))
                pygame.draw.rect(self.screen, GOLD, (x + 2, y + 2, 20, 20), 1)
                num = font_tiny.render(str(i + 1), True, GOLD)
                self.screen.blit(num, (x + 6, y + 3))

                # Кнопка использования (появляется при наведении)
                if slot_rect.collidepoint(mouse_pos):
                    # Подсветка слота
                    pygame.draw.rect(self.screen, (255, 215, 0, 80), slot_rect, 3)

                    # Подсказка
                    tip_text = font_small.render(f"{item}", True, WHITE)
                    tip_x = x + slot_size // 2 - tip_text.get_width() // 2
                    tip_y = y - 28
                    tip_bg = pygame.Surface((tip_text.get_width() + 16, 24), pygame.SRCALPHA)
                    tip_bg.fill((0, 0, 0, 220))
                    pygame.draw.rect(tip_bg, GOLD, tip_bg.get_rect(), 1)
                    self.screen.blit(tip_bg, (tip_x - 8, tip_y - 2))
                    self.screen.blit(tip_text, (tip_x, tip_y))

                    # Кнопка "ИСП"
                    use_btn = pygame.Rect(x + slot_size - 30, y + slot_size - 26, 26, 22)
                    pygame.draw.rect(self.screen, HEALTH_GREEN, use_btn)
                    pygame.draw.rect(self.screen, GOLD, use_btn, 1)
                    use_text = font_tiny.render("ИСП", True, BLACK)
                    self.screen.blit(use_text, (use_btn.x + 3, use_btn.y + 3))
                    self.belt_slots.append((i, use_btn))

                self.belt_slots.append((i, slot_rect))

            else:
                # Пустой слот
                pygame.draw.rect(self.screen, (30, 30, 45), slot_rect)
                pygame.draw.rect(self.screen, (60, 60, 80), slot_rect, 2)

                # Номер слота
                num_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
                num_bg.fill((0, 0, 0, 150))
                self.screen.blit(num_bg, (x + 2, y + 2))
                num = font_tiny.render(str(i + 1), True, (60, 60, 80))
                self.screen.blit(num, (x + 6, y + 3))

                # Иконка "пусто"
                empty_icon = font_tiny.render("∅", True, (40, 40, 60))
                self.screen.blit(empty_icon, (x + slot_size // 2 - 8, y + slot_size // 2 - 10))

                # При наведении на пустой слот
                if slot_rect.collidepoint(mouse_pos):
                    tip_text = font_tiny.render("Пустой слот", True, GRAY)
                    tip_x = x + slot_size // 2 - tip_text.get_width() // 2
                    tip_y = y - 20
                    tip_bg = pygame.Surface((tip_text.get_width() + 10, 18), pygame.SRCALPHA)
                    tip_bg.fill((0, 0, 0, 200))
                    self.screen.blit(tip_bg, (tip_x - 5, tip_y - 2))
                    self.screen.blit(tip_text, (tip_x, tip_y))



    def _draw_action_panel(self):
        """Рисует панель действий с кнопками"""
        panel_width = 400
        panel_height = 80
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT - 160

        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3)

        # Кнопки
        self.battle_buttons = []

        # Кнопка атаки
        attack_rect = pygame.Rect(panel_x + 50, panel_y + 15, 120, 50)
        self._draw_button(attack_rect, "АТАКА", True)
        self.battle_buttons.append(("attack", attack_rect))

        # Кнопка побега
        flee_rect = pygame.Rect(panel_x + panel_width - 170, panel_y + 15, 120, 50)
        self._draw_button(flee_rect, "ПОБЕГ", False)
        self.battle_buttons.append(("flee", flee_rect))

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
        import враги

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
        self.переключить_плейлист("бой")

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

    def init_forest_exploration(self):
        """Инициализирует коридорный данж - Зачарованный лес"""
        print("\n" + "=" * 50)
        print("🏰 ИНИЦИАЛИЗАЦИЯ КОРИДОРНОГО ДАНЖА - ЗАЧАРОВАННЫЙ ЛЕС")
        print("=" * 50)

        collision_map_path = "assets/dungeon/forest_collision.png"
        visual_map_path = "assets/dungeon/forest_visual.png"

        self.exploration_zone = exploration.ExplorationZone(
            2016, 3024,
            collision_map_path=collision_map_path,
            visual_map_path=visual_map_path
        )

        self.exploration_zone.load_enemies_from_map("forest")

        self.exploration_in_battle = False
        self.in_dungeon = True  # 👈 ДОБАВЛЯЕМ!

        print("\n" + "=" * 50)
        print(f"✅ КОРИДОРНЫЙ ДАНЖ ИНИЦИАЛИЗИРОВАН!")
        print(f"   - Мобов: {len(self.exploration_zone.mobs)}")
        print(f"   - Боссов: {len(self.exploration_zone.bosses)}")
        print("=" * 50)

    def init_crypt_exploration(self):
        """Инициализирует данж - Древний склеп"""
        print("\n" + "=" * 50)
        print("💀 ИНИЦИАЛИЗАЦИЯ ДРЕВНЕГО СКЛЕПА")
        print("=" * 50)

        collision_map_path = "assets/dungeon/crypt_collision.png"
        visual_map_path = "assets/dungeon/crypt_visual.png"

        self.exploration_zone = exploration.ExplorationZone(
            2016, 3024,
            collision_map_path=collision_map_path,
            visual_map_path=visual_map_path
        )

        self.exploration_zone.load_enemies_from_map("crypt")

        self.exploration_in_battle = False
        self.in_dungeon = True  # 👈 ДОБАВЛЯЕМ!

        print("\n" + "=" * 50)
        print(f"✅ СКЛЕП ИНИЦИАЛИЗИРОВАН!")
        print(f"   - Мобов: {len(self.exploration_zone.mobs)}")
        print(f"   - Боссов: {len(self.exploration_zone.bosses)}")
        print("=" * 50)

    def handle_exploration(self):
        """Обрабатывает исследование большой локации"""
        if self.режим != "эксплорейшн":
            return

        if not hasattr(self, 'exploration_zone'):
            print("❌ ОШИБКА: exploration_zone не создан!")
            self.режим = "игра"
            self.in_dungeon = False  # 👈 ДОБАВЛЯЕМ
            return

        # Получаем нажатые клавиши
        keys = pygame.key.get_pressed()

        # Обновляем зону
        self.exploration_zone.update(keys)

        # Проверяем столкновения (только если не в бою)
        if not hasattr(self, 'exploration_in_battle') or not self.exploration_in_battle:
            encounter = self.exploration_zone.check_encounters()
            if encounter:
                encounter_type, enemy_name, level = encounter
                print(f"⚔️ Столкновение с {enemy_name}!")

                from враги import ЛЕСНЫЕ_БОССЫ

                if encounter_type == "boss" or enemy_name in ЛЕСНЫЕ_БОССЫ:
                    self.start_boss_battle(enemy_name)
                else:
                    self.start_battle(enemy_name)

                self.режим = "бой"
                self.exploration_in_battle = True
                return

        # Отрисовка зоны
        self.exploration_zone.draw(self.screen)

        # Рисуем статус-бар (здоровье, опыт, уровень)
        self.draw_status()

        # Рисуем панель действий (кнопки)
        self.draw_actions()

        # Рисуем лог событий
        self.draw_log_panel()

        # Рисуем интерфейс экспедиции
        self.draw_exploration_ui()

        # Кнопка выхода (оставляем на всякий случай)
        exit_button = pygame.Rect(10, 10, 100, 40)
        mouse_pos = pygame.mouse.get_pos()

        if exit_button.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GOLD, exit_button)
            exit_text = font_medium.render("ВЫЙТИ", True, BLACK)
        else:
            pygame.draw.rect(self.screen, DARK_RED, exit_button)
            pygame.draw.rect(self.screen, GOLD, exit_button, 2)
            exit_text = font_medium.render("ВЫЙТИ", True, WHITE)

        self.screen.blit(exit_text, (exit_button.x + 15, exit_button.y + 8))
        self.exploration_exit_button = exit_button

        # ===== ПРОВЕРКА КЛИКА ПО КНОПКЕ ВЫХОДА =====
        # Этот код уже есть в run(), но для надёжности добавим сюда
        # Если клик по exit_button — выходим из данжа

    def draw_exploration_ui(self):
        """Рисует интерфейс для экспедиции"""
        # Панель информации в левом верхнем углу
        info_panel = pygame.Rect(10, 60, 250, 100)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_panel)
        pygame.draw.rect(self.screen, GOLD, info_panel, 2)

        # Текст
        texts = [
            f"Позиция: ({int(self.exploration_zone.player_x)}, {int(self.exploration_zone.player_y)})",
            f"Мобы: {len([m for m in self.exploration_zone.mobs if m.is_alive])}",
            f"Босс: {'Жив' if not any(b.defeated for b in self.exploration_zone.bosses) else 'Побеждён'}"
        ]

        for i, text in enumerate(texts):
            text_surface = font_small.render(text, True, (200, 200, 200))
            self.screen.blit(text_surface, (20, 70 + i * 25))

        # Управление
        controls = [
            "WASD/Стрелки - движение",
            "Выйти - кнопка в левом верхнем углу"
        ]

        for i, text in enumerate(controls):
            text_surface = font_tiny.render(text, True, (150, 150, 150))
            self.screen.blit(text_surface, (20, HEIGHT - 40 + i * 15))

    def start_boss_battle(self, boss_name):
        """Начинает битву с боссом"""
        from враги import получить_босса

        # ===== СБРОС ПАРАМЕТРОВ =====
        self.battle.battle_ended = False  # 👈 ОБЯЗАТЕЛЬНО!
        self.battle.enemy_data = None
        self.enemy_bleed_duration = 0
        self.enemy_bleed_damage = 0
        self.enemy_stunned = False
        self.enemy_weakened_duration = 0
        self.blocking = False
        self.enemy_damage_multiplier = 1.0
        # =============================

        self.режим = "бой"
        self.current_enemy = boss_name
        self.enemy_data = получить_босса(boss_name).copy()
        self.enemy_health = self.enemy_data["здоровье"]
        self.battle_log = [f"👑 ПЕРЕД ТОБОЙ {boss_name.replace('_', ' ').upper()}!"]
        self.is_boss_battle = True

        # ===== ДОБАВЛЯЕМ ДАННЫЕ В BATTLE SYSTEM =====
        self.battle.current_enemy = boss_name
        self.battle.enemy_data = self.enemy_data
        self.battle.enemy_health = self.enemy_health
        self.battle.battle_log = self.battle_log
        # =============================================

        self.start_battle_animation()
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

    def play_transition_video(self, video_path, target_location):
        try:
            print(f"🎬 play_transition_video: {video_path} -> {target_location}")
            # ===== ОСТАНАВЛИВАЕМ МУЗЫКУ ПЕРЕД ВИДЕО =====
            self.остановить_музыку()  # 👈 ДОБАВЬТЕ!

            print(f"🎬 Загрузка видео: {video_path}")
            self.transition_video = Video(video_path)
            self.transition_video.play()
            self.next_location = target_location
            self.video_transition_active = True
            self.режим = "видео_переход"
            print(f"▶️ Видео воспроизводится, переход к {target_location}")
            print(f"📍 РЕЖИМ УСТАНОВЛЕН: {self.режим}")
        except Exception as e:
            print(f"❌ Ошибка загрузки видео: {e}")
            self.текущая_локация = target_location
            self.show_description = True
            self.description_timer = 0
            self.режим = "игра"

            # ===== ЕСЛИ ВИДЕО НЕ ЗАГРУЗИЛОСЬ - ВКЛЮЧАЕМ МУЗЫКУ СРАЗУ =====
            if self.текущая_локация != "меню" and self.есть_музыка(self.текущая_локация):
                self.переключить_плейлист(self.текущая_локация)
            else:
                self.остановить_музыку()

    def update_transition_video(self):
        """Обновляет состояние видео-перехода"""

        if self.режим != "видео_переход":
            return

        if self.transition_video is None:
            self.режим = "игра"
            return

        if not self.transition_video.active:
            print("🎬 ВИДЕО ЗАВЕРШЕНО! Обновляем квесты...")  # 👈 ДОБАВЬ

            # Завершаем переход
            self.текущая_локация = self.next_location
            self.show_description = True
            self.description_timer = 0
            время.пройти_время(5)
            self.transition_video.close()
            self.transition_video = None
            self.video_transition_active = False
            self.режим = "игра"

            # Обновляем ежедневные квесты (посещение локации)
            print(f"   📍 Текущая локация: {self.текущая_локация}")  # 👈 ДОБАВЬ
            if hasattr(self, 'quest_system') and hasattr(self, 'игрок'):
                if "ежедневные_квесты" in self.игрок:
                    print(f"   🔄 ВЫЗЫВАЕМ обновить_ежедневный_прогресс(посетить, {self.текущая_локация})")  # 👈 ДОБАВЬ
                    завершенные = self.quest_system.обновить_ежедневный_прогресс(
                        self.игрок,
                        "посетить",
                        self.текущая_локация
                    )
                    print(f"   📊 Результат: {завершенные}")  # 👈 ДОБАВЬ
                    if завершенные:
                        for квест_id in завершенные:
                            for q in self.quest_system.ежедневные_квесты:
                                if q.get("id") == квест_id:
                                    self.add_to_log(f"📅 Ежедневный квест выполнен: {q['название']}")
                                    break

                else:
                    print("   ❌ Нет ежедневные_квесты в игроке!")  # 👈 ДОБАВЬ
            else:
                print("   ❌ Нет quest_system или игрока!")  # 👈 ДОБАВЬ

            # Включаем музыку
            if self.текущая_локация != "меню" and self.есть_музыка(self.текущая_локация):
                self.переключить_плейлист(self.текущая_локация)
            else:
                self.остановить_музыку()

            print(f"🗺️ Видео-переход завершён: {self.текущая_локация}")
            return

        try:
            self.transition_video.draw(self.screen, (0, 0), force_draw=True)
        except Exception as e:
            print(f"⚠️ Ошибка отрисовки видео: {e}")

    def загрузить_музыку(self, файл):
        """Загружает и воспроизводит музыку"""
        if not self.музыка_включена:
            return

        import os
        if not os.path.exists(файл):  # 👈 ПРОВЕРКА
            print(f"⚠️ Файл не найден: {файл}")
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(файл)
            pygame.mixer.music.set_volume(self.громкость)
            pygame.mixer.music.play(-1)
            self.текущая_музыка = файл
            print(f"🎵 Музыка: {файл.split('/')[-1]}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки музыки: {e}")

    def переключить_плейлист(self, локация):
        """Переключает на новый плейлист локации"""

        # ===== НЕ ВКЛЮЧАЕМ МУЗЫКУ МЕНЮ ПОСЛЕ ЗАГРУЗКИ ИГРЫ =====
        if локация == "меню" and self.игра_загружена:
            return

        if not self.есть_музыка(локация):
            return

        плейлист = self.музыка_локаций[локация]
        import random
        self.текущий_плейлист = плейлист.copy()
        random.shuffle(self.текущий_плейлист)
        self.индекс_в_плейлисте = 0
        self.играть_следующий_трек()

    def играть_следующий_трек(self):
        """Играет следующий трек из плейлиста"""
        if not self.текущий_плейлист:
            return

        import os

        while self.индекс_в_плейлисте < len(self.текущий_плейлист):
            файл = self.текущий_плейлист[self.индекс_в_плейлисте]
            if os.path.exists(файл):
                self.загрузить_музыку(файл)
                self.индекс_в_плейлисте += 1
                return
            else:
                print(f"⚠️ Пропускаем: {файл}")
                self.индекс_в_плейлисте += 1

        # Все файлы в плейлисте не найдены
        if self.индекс_в_плейлисте >= len(self.текущий_плейлист):
            import random
            random.shuffle(self.текущий_плейлист)
            self.индекс_в_плейлисте = 0
            self.играть_следующий_трек()

    def переключить_музыку(self):
        """Включает/выключает музыку"""
        self.музыка_включена = not self.музыка_включена
        if self.музыка_включена:
            pygame.mixer.music.unpause()
            print("🎵 Музыка включена")
        else:
            pygame.mixer.music.pause()
            print("🔇 Музыка выключена")

    def остановить_музыку(self):
        """Останавливает музыку"""
        try:
            pygame.mixer.music.stop()
            self.текущая_музыка = None
            print("🔇 Музыка остановлена")
        except Exception as e:
            print(f"⚠️ Ошибка остановки музыки: {e}")

    def есть_музыка(self, локация):
        """Проверяет, есть ли музыка для локации"""
        if локация not in self.музыка_локаций:
            return False

        плейлист = self.музыка_локаций[локация]
        if not плейлист:
            return False

        import os
        for файл in плейлист:
            if os.path.exists(файл):
                return True
        return False

    def draw_quest_tracker(self):
        """Отображает активные квесты на экране"""
        if not self.показывать_квесты:
            return

        if self.режим == "бой":
            return

        активные_квесты = self.игрок.get("активные_квесты", [])
        if not активные_квесты:
            return

        # ===== ПАРАМЕТРЫ =====
        panel_width = 320
        panel_height = 30 + len(активные_квесты) * 75  # 👈 больше места
        panel_x = self.квесты_позиция_x
        panel_y = self.квесты_позиция_y

        if panel_height > 400:
            panel_height = 400

        # ===== ФОН =====
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        for i in range(panel_height):
            ratio = i / panel_height
            r = int(10 + 15 * ratio)
            g = int(10 + 10 * ratio)
            b = int(20 + 20 * ratio)
            color = (r, g, b, 200)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

        pygame.draw.rect(panel_surface, GOLD, panel_surface.get_rect(), 1)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # ===== ЗАГОЛОВОК =====
        title = font_medium.render("КВЕСТЫ", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 6))

        # Разделитель
        pygame.draw.line(self.screen, GOLD,
                         (panel_x + 10, panel_y + 28),
                         (panel_x + panel_width - 10, panel_y + 28), 1)

        # ===== КВЕСТЫ =====
        y = panel_y + 34
        max_quests = min(len(активные_квесты), 5)  # 👈 5 квестов вместо 6 (больше места)

        for i, квест_id in enumerate(активные_квесты[:max_quests]):
            квест = self.quest_system.получить_квест(квест_id)
            if not квест:
                continue

            # ===== НАЗВАНИЕ =====
            name = квест.get("название", "???")
            name_text = font_small.render(name, True, (255, 215, 0))
            self.screen.blit(name_text, (panel_x + 12, y))
            y += 18

            # ===== ОПИСАНИЕ (НОВОЕ!) =====
            description = квест.get("описание", "")
            # Разбиваем описание на строки
            desc_lines = self._разбить_текст_на_строки(description, panel_width - 30, font_small)
            desc_lines = desc_lines[:2]  # максимум 2 строки

            for line in desc_lines:
                desc_text = font_small.render(line, True, (180, 180, 180))
                self.screen.blit(desc_text, (panel_x + 14, y))
                y += 16

            # ===== ПРОГРЕСС =====
            прогресс_строки = self.quest_system.получить_прогресс_строку(квест_id)
            прогресс_строки = self.quest_system.получить_прогресс_строку(квест_id, self.игрок)
            if прогресс_строки:
                prog_text = font_small.render(прогресс_строки[0][:35], True, (200, 200, 200))
                self.screen.blit(prog_text, (panel_x + 14, y))
                y += 16
            else:
                status_text = font_small.render("В процессе...", True, (150, 150, 150))
                self.screen.blit(status_text, (panel_x + 14, y))
                y += 16

            # Разделитель
            if i < len(активные_квесты[:max_quests]) - 1:
                pygame.draw.line(self.screen, (80, 80, 100),
                                 (panel_x + 12, y),
                                 (panel_x + panel_width - 12, y), 1)
                y += 6

        # Если квестов больше 5
        if len(активные_квесты) > 5:
            more_text = font_small.render(f"... и ещё {len(активные_квесты) - 5}", True, GRAY)
            self.screen.blit(more_text, (panel_x + 12, y + 4))

    def draw_daily_quest_tracker(self):
        """Отображает ежедневные квесты на экране (отдельная панель)"""


        # Проверяем, есть ли ежедневные квесты
        if not hasattr(self, 'quest_system'):
            print("   ❌ Нет quest_system!")
            return

        if not hasattr(self.quest_system, 'ежедневные_квесты'):
            print("   ❌ Нет ежедневные_квесты в quest_system!")
            return

        # Проверяем, что у игрока есть поля для ежедневных квестов
        if "ежедневные_квесты" not in self.игрок:
            print("   ⚠️ Нет ежедневные_квесты в игроке! Создаём...")
            self.игрок["ежедневные_квесты"] = []
            self.игрок["ежедневные_квесты_прогресс"] = {}
            self.игрок["ежедневные_квесты_дата"] = ""

        # Если у игрока нет квестов - загружаем
        if not self.игрок["ежедневные_квесты"]:
            print("   ⚠️ Нет активных квестов! Загружаем...")
            self.quest_system.загрузить_ежедневные_квесты(self.игрок)

        активные = self.игрок.get("ежедневные_квесты", [])

        # Проверяем, какие из них ещё не завершены
        активные_незавершенные = []
        for квест_ид in активные:
            if not self.quest_system.проверить_ежедневный_квест(квест_ид, self.игрок):
                # Находим данные квеста
                for квест in self.quest_system.ежедневные_квесты:
                    if квест.get("id") == квест_ид:
                        активные_незавершенные.append(квест)
                        break

        if not активные_незавершенные:
            print("   ❌ Нет активных ежедневных квестов!")
            return

        # ===== ПАРАМЕТРЫ ПАНЕЛИ =====
        panel_width = 280
        panel_height = 30 + len(активные_незавершенные) * 80
        panel_x = WIDTH - panel_width - 20
        panel_y = 200

        if panel_height > 380:
            panel_height = 380

        # ===== ФОН ПАНЕЛИ =====
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        for i in range(panel_height):
            ratio = i / panel_height
            r = int(10 + 15 * ratio)
            g = int(30 + 20 * ratio)
            b = int(10 + 10 * ratio)
            color = (r, g, b, 200)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

        pygame.draw.rect(panel_surface, HEALTH_GREEN, panel_surface.get_rect(), 2)

        corner_size = 8
        corners = [(2, 2), (panel_width - corner_size - 2, 2),
                   (2, panel_height - corner_size - 2), (panel_width - corner_size - 2, panel_height - corner_size - 2)]
        for cx, cy in corners:
            pygame.draw.rect(panel_surface, HEALTH_GREEN, (cx, cy, corner_size, corner_size), 2)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        # ===== ЗАГОЛОВОК =====
        title = font_medium.render("ЕЖЕДНЕВНЫЕ", True, HEALTH_GREEN)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, panel_y + 6))

        pygame.draw.line(self.screen, HEALTH_GREEN,
                         (panel_x + 10, panel_y + 30),
                         (panel_x + panel_width - 10, panel_y + 30), 1)

        # ===== ОТОБРАЖАЕМ КВЕСТЫ =====
        y = panel_y + 36
        max_quests = min(len(активные_незавершенные), 4)

        for i in range(max_quests):
            квест = активные_незавершенные[i]
            квест_ид = квест.get("id")

            if not квест_ид:
                continue

            # Название
            name = квест.get("название", "???")
            name_text = font_small.render(name, True, HEALTH_GREEN)
            self.screen.blit(name_text, (panel_x + 12, y))
            y += 18

            # 👇 ИСПРАВЛЕНО: берём прогресс ИЗ ИГРОКА
            прогресс = self.игрок.get("ежедневные_квесты_прогресс", {}).get(квест_ид, {})
            текущее = прогресс.get("текущее", 0)  # 👈 ВАЖНО!
            цель = квест.get("цели", {}).get("количество", 1)

            тип = квест.get("тип", "убить")
            if тип == "убить":
                прог_текст = f"Убито: {текущее}/{цель}"
            elif тип == "найти":
                прог_текст = f"Найдено: {текущее}/{цель}"
            elif тип == "посетить":
                прог_текст = f"Посещено: {текущее}/{цель}"
            elif тип == "крафт":
                прог_текст = f"Создано: {текущее}/{цель}"
            elif тип == "монеты":
                прог_текст = f"Монет: {текущее}/{цель}"
            else:
                прог_текст = f"Прогресс: {текущее}/{цель}"

            prog_text = font_small.render(прог_текст, True, (200, 200, 200))
            self.screen.blit(prog_text, (panel_x + 14, y))
            y += 16

            # Полоса прогресса
            bar_width = panel_width - 30
            bar_height = 6
            bar_x = panel_x + 14
            bar_y = y

            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

            if цель > 0:
                fill_width = int(bar_width * (текущее / цель))
                fill_width = min(fill_width, bar_width)
                if fill_width > 0:
                    for j in range(fill_width):
                        ratio = j / bar_width
                        r = int(200 + 55 * ratio)
                        g = int(200 - 55 * ratio)
                        color = (r, g, 0)
                        pygame.draw.line(self.screen, color,
                                         (bar_x + j, bar_y + 1),
                                         (bar_x + j, bar_y + bar_height - 1))

            pygame.draw.rect(self.screen, HEALTH_GREEN, (bar_x, bar_y, bar_width, bar_height), 1)
            y += 14

            # Награда
            награда = квест.get("награда", {})
            награда_текст = []
            if награда.get("опыт"):
                награда_текст.append(f"+{награда['опыт']} опыта")
            if награда.get("монеты"):
                награда_текст.append(f"{награда['монеты']} монет")

            if награда_текст:
                reward_text = font_tiny.render(" " + " ".join(награда_текст), True, GOLD)
                self.screen.blit(reward_text, (panel_x + 14, y))
                y += 16

            if i < max_quests - 1:
                pygame.draw.line(self.screen, (40, 60, 40),
                                 (panel_x + 12, y),
                                 (panel_x + panel_width - 12, y), 1)
                y += 4

        if len(активные_незавершенные) > 4:
            more_text = font_tiny.render(f"... и ещё {len(активные_незавершенные) - 4}", True, GRAY)
            self.screen.blit(more_text, (panel_x + 12, y + 4))



if __name__ == "__main__":
    game = Game()
    game.run()