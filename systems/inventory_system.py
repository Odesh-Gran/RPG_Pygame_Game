# systems/inventory_system.py
import pygame
from config import *


class InventorySystem:
    """Управляет инвентарём игрока: добавление, удаление, использование, экипировка"""

    def __init__(self, player, item_icons=None):
        self.player = player
        self.item_icons = item_icons or {}
        self.inventory_items = []  # для хранения кнопок при отрисовке
        self.inventory_back = None
        self.inventory_animation_progress = 0

    def get_inventory_dict(self):
        """Превращает список инвентаря в словарь {предмет: количество}"""
        инвентарь_словарь = {}
        for предмет in self.player["инвентарь"]:
            инвентарь_словарь[предмет] = инвентарь_словарь.get(предмет, 0) + 1
        return инвентарь_словарь

    def add_item(self, item):
        """Добавляет предмет в инвентарь"""
        self.player["инвентарь"].append(item)

    def remove_item(self, item):
        """Удаляет предмет из инвентаря (первое вхождение)"""
        if item in self.player["инвентарь"]:
            self.player["инвентарь"].remove(item)
            return True
        return False

    def count_item(self, item):
        """Возвращает количество предмета в инвентаре"""
        return self.player["инвентарь"].count(item)

    def has_item(self, item, count=1):
        """Проверяет, есть ли предмет в инвентаре (и в нужном количестве)"""
        return self.count_item(item) >= count

    def use_item(self, item):
        """Использовать предмет (еда, книга, броня, оружие, амулет)"""
        import предметы

        if item not in self.player["инвентарь"]:
            return False, "Предмета нет в инвентаре"

        данные = предметы.предметы.get(item, {})
        item_type = данные.get("тип")

        # ===== ЕДА =====
        if item_type == "еда":
            базовое_лечение = данные.get("здоровье", 5)
            кулинария = self.player.get("кулинария", 0)
            лечение = базовое_лечение + кулинария

            # ===== ВОССТАНОВЛЕНИЕ СЫТОСТИ И ЖАЖДЫ =====
            from игрок import восстановить_сытость, восстановить_жажду

            сытость = данные.get("сытость", 0)
            жажда = данные.get("жажда", 0)

            if сытость > 0:
                восстановить_сытость(self.player, сытость)
            if жажда > 0:
                восстановить_жажду(self.player, жажда)

            self.player["здоровье"] = min(
                self.player["здоровье"] + лечение,
                self.player["макс_здоровье"]
            )
            self.remove_item(item)

            # Формируем сообщение
            сообщение = f"+{лечение} здоровья"
            if сытость > 0:
                сообщение += f", +{сытость} сытости"
            if жажда > 0:
                сообщение += f", +{жажда} жажды"

            return True, сообщение

        # ===== БРОНЯ =====
        elif item_type == "броня":
            return self.equip_armor(item)

        # ===== КНИГИ =====
        elif item_type == "книга":
            from игрок import проверить_и_повысить_навык
            навык = данные.get("навык", "кулинария")
            повышение = данные.get("повышение", 5)
            успех, новое_значение, сообщение = проверить_и_повысить_навык(навык, повышение)
            if успех:
                self.remove_item(item)
            return успех, сообщение

        # ===== АМУЛЕТ =====
        elif item_type in ("аксессуар", "амулет"):
            return self.equip_amulet(item)

        # ===== ОРУЖИЕ =====
        elif item_type == "оружие":
            return self.equip_weapon(item)

        else:
            return False, f"Неизвестный тип предмета: {item_type}"

    def equip_weapon(self, item):
        """Экипировать оружие"""
        if self.player["оружие"] is not None:
            старое = self.player["оружие"]
            self.player["инвентарь"].append(старое)

        self.player["оружие"] = item
        self.remove_item(item)
        return True, f"Экипирован {item}"

    def equip_armor(self, item):
        """Надеть броню с учётом всех бонусов"""
        import предметы

        данные = предметы.предметы.get(item, {})
        if данные.get("тип") != "броня":
            return False, "Это не броня"

        if item not in self.player["инвентарь"]:
            return False, "Предмета нет в инвентаре"

        # Снимаем старую броню
        if self.player.get("броня"):
            старая = self.player["броня"]
            старые_данные = предметы.предметы.get(старая, {})
            for attr in ["сила", "ловкость", "стойкость", "интеллект", "кулинария", "алхимия", "кузнечное_дело"]:
                if attr in старые_данные:
                    self.player[attr] = self.player.get(attr, 0) - старые_данные[attr]
            self.player["инвентарь"].append(старая)
            self.player["броня"] = None

        # Надеваем новую
        self.remove_item(item)
        self.player["броня"] = item

        for attr in ["сила", "ловкость", "стойкость", "интеллект", "кулинария", "алхимия", "кузнечное_дело"]:
            if attr in данные:
                self.player[attr] = self.player.get(attr, 0) + данные[attr]

        self.update_max_health()
        защита = данные.get("защита", 0)
        return True, f"Надета {item} (защита +{защита})"

    def equip_amulet(self, item):
        """Надеть амулет"""
        import предметы

        данные = предметы.предметы.get(item, {})
        if данные.get("тип") not in ("аксессуар", "амулет"):
            return False, "Это не амулет"

        if item not in self.player["инвентарь"]:
            return False, "Предмета нет в инвентаре"

        # Снимаем старый
        if self.player.get("амулет"):
            старый = self.player["амулет"]
            self.player["инвентарь"].append(старый)
            self.player["амулет"] = None

        self.remove_item(item)
        self.player["амулет"] = item
        self.update_amulet_effect()
        return True, f"Надет {item}"

    def update_amulet_effect(self):
        """Обновляет эффекты от амулета"""
        амулет = self.player.get("амулет")
        self.player["вампиризм"] = False
        self.player["сила_бонус"] = 0
        self.player["здоровье_бонус"] = 0

        if not амулет:
            self.update_max_health()
            return

        import предметы
        данные = предметы.предметы.get(амулет, {})
        эффект = данные.get("эффект")

        if эффект == "вампиризм":
            self.player["вампиризм"] = True
        elif эффект == "сила":
            self.player["сила_бонус"] = данные.get("сила_бонус", 3)
        elif эффект == "здоровье":
            self.player["здоровье_бонус"] = данные.get("здоровье_бонус", 20)

        self.update_max_health()

    def update_max_health(self):
        """Пересчитывает максимальное здоровье с учётом всех бонусов"""
        print(f"\n🔄 update_max_health вызвана!")  # 👈 ДОБАВЬ

        # Базовое здоровье от стойкости
        общая_стойкость = self.player.get("стойкость", 0) + self.player.get("стойкость_бонус", 0)
        новое_макс = 10 + общая_стойкость * 10
        print(f"   Базовое от стойкости: {новое_макс}")

        # Бонус от амулета на здоровье
        новое_макс += self.player.get("здоровье_бонус", 0)
        print(f"   + бонус амулета: {self.player.get('здоровье_бонус', 0)}")

        # Бонусы от пассивных навыков
        пассивные_бонусы = self.player.get("пассивные_бонусы", {})
        бонус_hp = пассивные_бонусы.get("hp", 0)
        новое_макс += бонус_hp
        print(f"   + бонус пассивных навыков: {бонус_hp}")

        старое_макс = self.player.get("макс_здоровье", новое_макс)
        self.player["макс_здоровье"] = новое_макс

        if self.player["здоровье"] > новое_макс:
            self.player["здоровье"] = новое_макс

        print(f"❤️ Здоровье: {self.player['здоровье']}/{self.player['макс_здоровье']}")