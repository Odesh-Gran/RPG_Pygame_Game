# systems/battle_system.py
import random
import pygame
from entities import enemies as враги
from entities import items as предметы
from systems import time_system as время
from ui.sprites import load_enemy_sprite_by_name
from ui.battle_intro import start_battle_animation


class BattleSystem:
    """Управляет боем: атаки, навыки, победа/поражение"""

    def __init__(self, player, game=None):
        self.player = player
        self.game = game

        # Параметры боя
        self.enemy_data = None
        self.enemy_health = 0
        self.current_enemy = None
        self.battle_log = []
        self.round_number = 0
        self.round_started = False
        self.is_boss_battle = False
        self.exploration_in_battle = False
        self.exploration_zone = None

        # Боевые флаги
        self.blocking = False
        self.rage_active = False
        self.enemy_bleed_duration = 0
        self.enemy_bleed_damage = 5
        self.enemy_stunned = False
        self.enemy_weakened_duration = 0
        self.vampirism_active = False
        self.vampirism_duration = 0
        self.revive_used = False
        self.enemy_damage_multiplier = 1.0

        # Кнопки для интерфейса
        self.battle_buttons = []
        self.battle_skill_buttons = []

        # ===== ФЛАГ ЗАВЕРШЕНИЯ БОЯ =====
        self.battle_ended = False
        self.victory_result = None

    def start_battle(self, enemy_name):
        """Начинает бой с врагом"""
        print(f"\n⚔️ START_BATTLE: {enemy_name}")

        # ===== СБРОС ВСЕХ ПАРАМЕТРОВ =====
        self.battle_ended = False
        self.victory_result = None
        self.enemy_bleed_duration = 0
        self.enemy_bleed_damage = 0
        self.enemy_stunned = False
        self.enemy_weakened_duration = 0
        self.blocking = False
        self.enemy_damage_multiplier = 1.0
        self.enemy_data = None  # ← ОЧИЩАЕМ ЗДЕСЬ!
        self.enemy_health = 0
        self.battle_log = []
        self.round_number = 0
        # =================================

        self.current_enemy = enemy_name
        self.enemy_data = враги.враги[enemy_name].copy()  # ← УСТАНАВЛИВАЕМ ЗАНОВО
        self.enemy_health = self.enemy_data["здоровье"]

        self.battle_log = [f"Нападает - {enemy_name.replace('_', ' ')}!"]

        return {
            "enemy_name": enemy_name,
            "enemy_data": self.enemy_data,
            "enemy_health": self.enemy_health,
            "battle_log": self.battle_log
        }

    def _check_armor(self):
        """Проверяет броню перед боем"""
        print("\n" + "=" * 40)
        print("🛡️ ПРОВЕРКА БРОНИ ПЕРЕД БОЕМ")
        print("=" * 40)

        броня = self.player.get("броня")
        print(f"📦 Значение: {броня}")
        print(f"📦 Тип: {type(броня)}")

        if isinstance(броня, str):
            данные = предметы.предметы.get(броня, {})
            защита = данные.get("защита", 0)
            print(f"✅ Броня надета: {броня} (защита {защита})")
        elif броня is None:
            print("❌ Броня не надета")
        else:
            print(f"⚠️ НЕПРАВИЛЬНЫЙ ТИП! Ожидалась строка или None, получено {type(броня)}")
            if self.game and hasattr(self.game, 'fix_armor_value'):
                self.game.fix_armor_value()

        print("=" * 40)

    # systems/battle_system.py

    def player_attack(self):
        """Атака игрока — новый раунд"""

        # ===== НОВЫЙ РАУНД: ОЧИЩАЕМ ВСЁ =====
        self.round_number += 1
        self.battle_log = []  # ← ПОЛНОСТЬЮ ОЧИЩАЕМ!

        if self.battle_ended:
            return True

        # ===== РАСЧЁТ УРОНА =====
        твой_урон = self.calculate_damage(1.0)

        # ===== КРИТИЧЕСКИЙ УДАР =====
        шанс_крита = 5 + (self.player["ловкость"] // 2)
        is_crit = random.randint(1, 100) <= шанс_крита

        if is_crit:
            твой_урон = int(твой_урон * 1.5)
            self.battle_log.append(f"КРИТИЧЕСКИЙ УДАР! {твой_урон} урона!")
        else:
            self.battle_log.append(f"Ты нанёс {твой_урон} урона!")

        self.enemy_health -= твой_урон

        if self.enemy_health <= 0:
            result = self.get_victory_result()
            self.battle_ended = True
            self.victory_result = result
            return result

        # ===== ВАМПИРИЗМ =====
        if self.player.get("вампиризм", False):
            лечение = твой_урон // 3
            if лечение > 0:
                self.player["здоровье"] = min(
                    self.player["здоровье"] + лечение,
                    self.player["макс_здоровье"]
                )
                self.battle_log.append(f"Вампиризм: +{лечение} здоровья!")

        # ===== РАЗДЕЛИТЕЛЬ =====
        self.battle_log.append("=" * 26)

        # ===== ХОД ВРАГА =====
        self.enemy_attack()
        return True

    def enemy_attack(self):
        """Атака врага"""

        if self.battle_ended:
            return

        if self.enemy_health <= 0:
            return self.get_victory_result()

        # ===== ОГЛУШЕНИЕ =====
        if self.enemy_stunned:
            self.battle_log.append("Враг оглушён и пропускает ход!")
            self.enemy_stunned = False
            return

        # ===== КРОВОТЕЧЕНИЕ =====
        if self.enemy_bleed_duration > 0:
            self.enemy_health -= self.enemy_bleed_damage
            self.battle_log.append(f"Кровотечение: {self.enemy_bleed_damage} урона!")
            self.enemy_bleed_duration -= 1

            if self.enemy_health <= 0:
                return self.get_victory_result()

        # ===== БЛОК =====
        if self.blocking:
            self.battle_log.append("Ты заблокировал атаку!")
            self.blocking = False
            return

        # ===== УРОН ВРАГА =====
        сила_врага = self.enemy_data["сила"]
        базовый_урон_врага = random.randint(3, сила_врага)
        бонус_сложности = self.player["уровень"] // 3
        урон_врага = базовый_урон_врага + бонус_сложности

        # Защита
        защита_брони = 0
        if self.player.get("броня") and isinstance(self.player["броня"], str):
            данные_брони = предметы.предметы.get(self.player["броня"], {})
            защита_брони = данные_брони.get("защита", 0)
        защита_брони += self.player.get("защита_бонус", 0)

        # Уклонение
        шанс_уклонения = self.player["ловкость"] // 4
        if random.randint(1, 100) <= шанс_уклонения:
            self.battle_log.append("Ты уклонился от атаки!")
            return

        # Ослабление
        if self.enemy_weakened_duration > 0:
            урон_врага = int(урон_врага * self.enemy_damage_multiplier)
            self.enemy_weakened_duration -= 1

        урон_после_брони = max(1, урон_врага - защита_брони)
        self.player["здоровье"] -= урон_после_брони
        self.battle_log.append(f"Получено {урон_после_брони} урона")

        # ===== КОНТРАТАКА =====
        if "counterattack" in self.player.get("выученные_навыки", []):
            if random.randint(1, 100) <= 25:
                урон_контры = self.calculate_damage(0.8)
                self.enemy_health -= урон_контры
                self.battle_log.append(f"КОНТРАТАКА! {урон_контры} урона врагу!")

                if self.enemy_health <= 0:
                    self.victory_result = self.get_victory_result()
                    self.battle_ended = True
                    return self.victory_result

        # ===== СМЕРТЬ ИГРОКА =====
        if self.player["здоровье"] <= 0:
            if self.game:
                self.game.игрок_умер()
            else:
                self.player["здоровье"] = 1

    def calculate_damage(self, множитель=1.0, потерянное_здоровье=0):
        """Рассчитывает урон атаки"""
        # Базовый урон от оружия
        базовый_урон = 2
        if self.player['оружие']:
            оружие = self.player['оружие']
            базовый_урон = предметы.предметы[оружие].get("урон", 2)

        # Бонус от силы
        бонус_силы = self.player["сила"] // 2
        бонус_уровня = self.player["уровень"] // 2

        итоговый_урон = (базовый_урон + бонус_силы + бонус_уровня) * множитель

        # Ярость
        if "rage" in self.player.get("выученные_навыки", []):
            if потерянное_здоровье > 0:
                макс_здоровье = self.player["макс_здоровье"]
                процент_потери = потерянное_здоровье / макс_здоровье
                бонус_ярости = 1 + (процент_потери * 0.1)
                итоговый_урон = int(итоговый_урон * бонус_ярости)

        # Случайное отклонение
        вариация = random.uniform(0.8, 1.2)
        return max(1, int(итоговый_урон * вариация))

    def use_active_skill(self, skill_id, skills_data, add_to_log=None):
        """Применяет активный навык в бою"""

        # ===== НОВЫЙ РАУНД: ОЧИЩАЕМ ВСЁ =====
        self.round_number += 1
        self.battle_log = []  # ← ПОЛНОСТЬЮ ОЧИЩАЕМ!

        from loaders.skill_loader import SkillLoader

        skill = SkillLoader.get_skill_by_id(skills_data, skill_id)
        if not skill:
            if add_to_log:
                add_to_log(f"Навык {skill_id} не найден!")
            return False

        # Проверка маны
        стоимость_маны = skill.get("стоимость_маны", 0)
        if self.player.get("мана", 0) < стоимость_маны:
            self.battle_log.append(f"Не хватает маны! Нужно {стоимость_маны}")
            return False

        эффект = skill.get("эффект", "")
        значение = skill.get("значение", 0)

        # ===== ЗАЩИТА =====
        if эффект == "block_and_recover":
            if значение > 0:
                self.player["мана"] = min(
                    self.player.get("мана", 0) + значение,
                    self.player.get("макс_мана", 50)
                )
                self.battle_log.append(f"{skill['название']}: +{значение} маны!")
            else:
                self.battle_log.append(f"{skill['название']}!")
            self.blocking = True
            self.player["мана"] -= стоимость_маны
            self.battle_log.append("=" * 12)
            self.enemy_attack()
            return True

        # ===== ВАМПИРИЗМ =====
        elif эффект == "lifesteal":
            урон = self.calculate_damage(0.8)
            self.enemy_health -= урон

            if self.enemy_health <= 0:
                result = self.get_victory_result()
                self.battle_ended = True
                self.victory_result = result
                return result

            лечение = int(урон * 0.1)
            self.player["здоровье"] = min(self.player["здоровье"] + лечение, self.player["макс_здоровье"])
            self.battle_log.append(f"🧛 {skill['название']}: {урон} урона, +{лечение} HP!")
            self.player["мана"] -= стоимость_маны
            self.battle_log.append("=" * 12)
            self.enemy_attack()
            return True

        # ===== ОГЛУШЕНИЕ =====
        elif эффект == "stun_damage":
            урон = self.calculate_damage(1.0)
            self.enemy_health -= урон
            self.battle_log.append(f"{skill['название']}: {урон} урона!")

            if self.enemy_health <= 0:
                result = self.get_victory_result()
                self.battle_ended = True
                self.victory_result = result
                return result

            шанс_стана = значение
            if random.randint(1, 100) <= шанс_стана:
                self.enemy_stunned = True
                self.battle_log.append(f"{skill['название']} ОГЛУШИЛ врага!")

            self.player["мана"] -= стоимость_маны
            self.battle_log.append("=" * 12)
            self.enemy_attack()
            return True

        # ===== ОСЛАБЛЕНИЕ =====
        elif эффект == "enemy_damage_reduction":
            урон = self.calculate_damage(0.5)
            self.enemy_health -= урон
            self.battle_log.append(f"{skill['название']}: {урон} урона!")

            if self.enemy_health <= 0:
                result = self.get_victory_result()
                self.battle_ended = True
                self.victory_result = result
                return result

            self.enemy_weakened_duration = значение
            self.enemy_damage_multiplier = 0.85
            self.player["мана"] -= стоимость_маны
            self.battle_log.append("=" * 12)
            self.enemy_attack()
            return True

        # ===== КРОВОТЕЧЕНИЕ =====
        elif эффект == "bleed":
            урон = self.calculate_damage(0.7)
            self.enemy_health -= урон
            self.battle_log.append(f"{skill['название']}: {урон} урона!")

            if self.enemy_health <= 0:
                result = self.get_victory_result()
                self.battle_ended = True
                self.victory_result = result
                return result

            self.enemy_bleed_duration = значение
            self.enemy_bleed_damage = 5
            self.player["мана"] -= стоимость_маны
            self.battle_log.append("=" * 12)
            self.enemy_attack()
            return True

        # ===== ОБЫЧНАЯ АТАКА НАВЫКОМ =====
        else:
            множитель = skill.get("значение", 1.0)
            урон = self.calculate_damage(множитель)

            if "lethal_strike" in self.player.get("выученные_навыки", []):
                if self.enemy_health < self.enemy_data["здоровье"] * 0.3:
                    урон = int(урон * 2)
                    self.battle_log.append("СМЕРТЕЛЬНЫЙ УДАР! Урон удвоен!")

            шанс_крита = 5 + (self.player["ловкость"] // 2)
            is_crit = random.randint(1, 100) <= шанс_крита
            if is_crit:
                урон = int(урон * 1.5)
                self.battle_log.append(f"КРИТИЧЕСКИЙ {skill['название']}! {урон} урона!")
            else:
                self.battle_log.append(f"{skill['название']}: {урон} урона!")

            self.enemy_health -= урон

            if self.enemy_health <= 0:
                result = self.get_victory_result()
                self.battle_ended = True
                self.victory_result = result
                return result

            self.player["мана"] -= стоимость_маны

            if self.player.get("вампиризм", False):
                лечение = урон // 3
                if лечение > 0:
                    self.player["здоровье"] = min(self.player["здоровье"] + лечение, self.player["макс_здоровье"])
                    self.battle_log.append(f"Вампиризм: +{лечение} здоровья!")

            self.battle_log.append("=" * 12)
            self.enemy_attack()
            return True

    def battle_flee(self):
        """Побег из боя"""
        print("\n🏃 BATTLE_FLEE вызвана!")

        шанс = 30 + (self.player["ловкость"] // 2) + self.player["уровень"]
        шанс = min(90, шанс)
        print(f"   Шанс побега: {шанс}%")

        if random.randint(1, 100) <= шанс:
            self.battle_log.insert(0, "Ты успешно убежал!")
            время.пройти_время(5)
            self.blocking = False
            self.battle_ended = True
            return True
        else:
            self.battle_log.insert(0, "Не удалось убежать!")
            сила_врага = self.enemy_data["сила"]
            урон_врага = random.randint(5, сила_врага)

            шанс_уклонения = self.player["ловкость"] // 4
            if random.randint(1, 100) <= шанс_уклонения:
                self.battle_log.insert(0, "Но ты увернулся!")
                self.blocking = False
                return False

            self.player["здоровье"] -= урон_врага
            self.battle_log.insert(0, f"Враг нанёс {урон_врага} урона!")
            self.blocking = False
            return False

    def get_victory_result(self):
        """Возвращает результат победы (лут, опыт)"""
        print(f"\n🏆 ПОБЕДА! Получение результата...")

        self.enemy_health = 0

        # ===== ПРОВЕРЯЕМ, ЕСТЬ ЛИ ДАННЫЕ О ВРАГЕ =====
        if self.enemy_data is None:
            print("   ⚠️ enemy_data = None, используем запасные данные")
            return {
                "victory": True,
                "loot": ["хлеб"],
                "exp": 5,
                "rare_item": None
            }

        # ===== ОБНОВЛЯЕМ КВЕСТЫ (УБИЙСТВО) =====
        if self.game and hasattr(self.game, 'quest_system'):
            print(f"   📜 Обновляем квесты: убийство {self.current_enemy}")
            try:
                # ===== ОБЫЧНЫЕ КВЕСТЫ =====
                завершенные = self.game.quest_system.обновить_прогресс(
                    self.player,
                    "убить",
                    self.current_enemy
                )
                if завершенные:
                    print(f"   ✅ Завершены квесты: {завершенные}")
                    if hasattr(self.game, 'add_to_log'):
                        for квест_id in завершенные:
                            квест = self.game.quest_system.получить_квест(квест_id)
                            if квест:
                                self.game.add_to_log(f"Квест выполнен: {квест['название']}")

                # ===== ЕЖЕДНЕВНЫЕ КВЕСТЫ =====  # 👈 ДОБАВЬТЕ ЭТОТ БЛОК
                ежедневные = self.game.quest_system.обновить_ежедневный_прогресс(
                    self.player,
                    "убить",
                    self.current_enemy
                )
                if ежедневные:
                    print(f"   ✅ Ежедневные квесты выполнены: {ежедневные}")
                    if hasattr(self.game, 'add_to_log'):
                        for квест_id in ежедневные:
                            квест = None
                            for q in self.game.quest_system.ежедневные_квесты:
                                if q.get("id") == квест_id:
                                    квест = q
                                    break
                            if квест:
                                self.game.add_to_log(f"Ежедневный квест выполнен: {квест['название']}")

            except Exception as e:
                print(f"   ⚠️ Ошибка обновления квестов: {e}")

        game = getattr(self, "game", None)
        api = getattr(game, "api", None) if game is not None else None
        print(f"🔍 self.game.api: {api}")
        if api is not None:
            print(f"🔍 self.game.api.token: {getattr(api, 'token', None)}")
        else:
            print("⚠️ API недоступен (офлайн-режим)")
        # ===== ДОСТИЖЕНИЯ ЗА УБИЙСТВО ВРАГА =====
        if self.game and hasattr(self.game, 'api') and self.game.api:
            enemy_name = self.current_enemy
            achievement_data = self._get_achievement_for_enemy(enemy_name)
            if achievement_data:
                сохранено = self.game.api.save_achievement(
                    name=achievement_data["name"],
                    description=achievement_data["description"]
                )
                if hasattr(self.game, 'add_to_log'):
                    if сохранено:
                        self.game.add_to_log(f"🏆 Получено достижение: {achievement_data['name']}")
                    else:
                        self.game.add_to_log(f"ℹ️ Достижение «{achievement_data['name']}» уже было получено")

        # ===== ПОЛУЧАЕМ НАГРАДУ =====
        награда = self.enemy_data.get("награда", ("хлеб", 5))

        if isinstance(награда, (list, tuple)):
            первый_элемент = награда[0] if len(награда) > 0 else "хлеб"
            if isinstance(первый_элемент, list):
                loot_items = первый_элемент
            else:
                loot_items = [первый_элемент]
            опыт = награда[1] if len(награда) > 1 else 5
        else:
            loot_items = [награда]
            опыт = 5

        редкий_предмет = None

        особенности = self.enemy_data.get("особенности", {})
        шанс_редкого = особенности.get("шанс_редкого_дропа", 0)
        редкий_дроп = self.enemy_data.get("редкий_дроп", [])

        if редкий_дроп and random.randint(1, 100) <= шанс_редкого:
            редкий_предмет = random.choice(редкий_дроп)

        # Кровавое пиршество
        if "blood_feast" in self.player.get("выученные_навыки", []):
            лечение = int(self.player["макс_здоровье"] * 0.1)
            self.player["здоровье"] = min(self.player["здоровье"] + лечение, self.player["макс_здоровье"])

        self.blocking = False
        время.пройти_время(15)

        return {
            "victory": True,
            "loot": loot_items,
            "exp": опыт,
            "rare_item": редкий_предмет
        }
    def get_enemy_health_percent(self):
        """Возвращает процент здоровья врага"""
        if self.enemy_data and self.enemy_data["здоровье"] > 0:
            return self.enemy_health / self.enemy_data["здоровье"]
        return 0

    def is_battle_active(self):
        """Проверяет, активен ли бой"""
        return self.enemy_data is not None and self.enemy_health > 0

    def use_belt_potion(self, slot_index):
        """Использовать зелье с пояса по индексу слота (0-4)"""
        пояс = self.player.get("пояс", [])

        if slot_index >= len(пояс):
            return False, "Пустой слот"

        item = пояс[slot_index]
        if item is None:
            return False, "Пустой слот"

        from entities import items as предметы
        данные = предметы.предметы.get(item, {})

        if данные.get("тип") != "еда":
            return False, "Это не зелье!"

        # Проверяем здоровье
        if self.player["здоровье"] >= self.player["макс_здоровье"]:
            return False, "Здоровье уже полное!"

        # Лечение
        лечение = данные.get("здоровье", 5)
        лечение += self.player.get("кулинария", 0)

        self.player["здоровье"] = min(
            self.player["здоровье"] + лечение,
            self.player["макс_здоровье"]
        )

        # Удаляем зелье с пояса
        пояс[slot_index] = None
        self.player["пояс"] = пояс

        return True, f"Использовано {item}! +{лечение} здоровья!"

    def _get_achievement_for_enemy(self, enemy_name):
        """Возвращает достижение для врага, если оно есть"""
        achievements = {
            "таракан": {
                "name": "Король леса пал",
                "description": "Игрок победил лесного короля"
            },
            "лесная_ведьма": {
                "name": "Победитель ведьм",
                "description": "Игрок одолел лесную ведьму"
            },
            "повар_призрак": {
                "name": "Призрак побеждён",
                "description": "Игрок одолел призрака-повара"
            },
            "болотник": {
                "name": "Болотный страж",
                "description": "Игрок победил болотника"
            },
            "рыцарь_призрак": {
                "name": "Призрачный рыцарь",
                "description": "Игрок одолел рыцаря-призрака"
            },
            "древний_энт": {
                "name": "Древний страж",
                "description": "Игрок победил древнего энта"
            },
            "лесной_тролль": {
                "name": "Охотник на троллей",
                "description": "Игрок уничтожил лесного тролля"
            },
            "вурдалак": {
                "name": "Охотник на вампиров",
                "description": "Игрок победил вурдалака"
            },
            "лесная_ведьма": {
                "name": "Победитель ведьм",
                "description": "Игрок одолел лесную ведьму"
            },
            "ржавый_голем": {
                "name": "Разрушитель големов",
                "description": "Игрок уничтожил ржавого голема"
            },
            "королевский_страж": {
                "name": "Стражник королевства",
                "description": "Игрок победил королевского стража"
            },
        }
        return achievements.get(enemy_name, None)

def start_battle_gui(game, враг_имя):
    """Начинает бой с врагом"""
    pygame.event.clear()

    # ===== МУЗЫКА БОЯ =====
    game.music.переключить_плейлист("бой", game.игра_загружена)

    # ===== СБРОС ПАРАМЕТРОВ =====
    game.enemy_bleed_duration = 0
    game.enemy_bleed_damage = 0
    game.enemy_stunned = False
    game.enemy_weakened_duration = 0
    game.blocking = False
    game.enemy_damage_multiplier = 1.0
    game.battle.battle_ended = False
    game.battle.enemy_data = None
    # =============================

    game.enemy_sprite = load_enemy_sprite_by_name(game, враг_имя)

    # Если мы в данже — запоминаем это
    if hasattr(game, 'in_dungeon') and game.in_dungeon:
        game.exploration_in_battle = True
        print("⚔️ Бой в данже!")

    # Запускаем бой через BattleSystem
    battle_data = game.battle.start_battle(враг_имя)

    game.режим = "бой"
    game.current_enemy = battle_data["enemy_name"]
    game.enemy_data = battle_data["enemy_data"]
    game.enemy_health = battle_data["enemy_health"]
    game.battle_log = battle_data["battle_log"]

    # Запускаем анимацию
    start_battle_animation(game)
    pygame.time.wait(200)
    время.пройти_время(2)


def handle_battle_click(game, pos):
    """Обработка кликов в бою"""
    if game.battle.battle_ended:
        print("   ⚠️ Бой завершён, клики игнорируются")

        # ===== ПРОВЕРКА НА РЕЗУЛЬТАТ ПОБЕДЫ =====
        if hasattr(game.battle, 'victory_result') and game.battle.victory_result:
            print("   🔥 Обрабатываем результат победы из battle_ended")
            result = game.battle.victory_result
            if isinstance(result, dict) and result.get("victory"):
                game.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                battle_victory(game)
                game.battle.victory_result = None
                return
        return

    # ===== ПРОВЕРКА КЛИКОВ ПО ПОЯСУ =====
    if hasattr(game, 'belt_slots'):
        for slot_index, slot_rect in game.belt_slots:
            if slot_rect.collidepoint(pos):
                успех, сообщение = game.battle.use_belt_potion(slot_index)
                game.add_to_log(сообщение)

                if успех:
                    game.battle.enemy_attack()
                    game.enemy_health = game.battle.enemy_health
                    game.battle_log = game.battle.battle_log

                    if game.battle.battle_ended and game.battle.victory_result:
                        result = game.battle.victory_result
                        game.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                        battle_victory(game)
                        game.battle.victory_result = None
                return

    # ===== ОСТАЛЬНЫЕ КНОПКИ =====
    for action, rect in game.battle_buttons:
        if rect.collidepoint(pos):
            if action == "attack":
                print("⚔️ КЛИК ПО КНОПКЕ АТАКИ")
                result = game.battle.player_attack()

                game.enemy_health = game.battle.enemy_health
                game.battle_log = game.battle.battle_log
                print(f"   enemy_health после синхронизации: {game.enemy_health}")

                if isinstance(result, dict) and result.get("victory"):
                    print("   🏆 Враг убит!")
                    game.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                    battle_victory(game)
                return

            elif action == "flee":
                battle_flee(game)
                return

    # ===== АКТИВНЫЕ НАВЫКИ =====
    if hasattr(game, 'battle_skill_buttons'):
        for skill_id, rect in game.battle_skill_buttons:
            if rect.collidepoint(pos):
                result = game.battle.use_active_skill(skill_id, game.skills_data, game.add_to_log)

                game.enemy_health = game.battle.enemy_health
                game.battle_log = game.battle.battle_log
                game.blocking = game.battle.blocking

                if isinstance(result, dict) and result.get("victory"):
                    game.show_loot_panel(result["loot"], result["exp"], result["rare_item"])
                    battle_victory(game)
                return


def battle_flee(game):
    """Побег из боя"""
    успех = game.battle.battle_flee()
    if успех:
        game.режим = "игра"
    game.battle_log = game.battle.battle_log


def battle_victory(game):
    """Победа в бою — только переключаем режим (панель лута уже показана)"""
    print(f"\n🏆 BATTLE_VICTORY вызвана (GUI)!")

    game.music.остановить_музыку()

    if game.music.есть_музыка(game.текущая_локация):
        game.music.переключить_плейлист(game.текущая_локация, game.игра_загружена)
    else:
        game.music.остановить_музыку()

    # Если бой был в данже, удаляем врага
    if hasattr(game, 'exploration_in_battle') and game.exploration_in_battle:
        if hasattr(game, 'current_enemy'):
            from entities.enemies import ЛЕСНЫЕ_БОССЫ
            if game.current_enemy in ЛЕСНЫЕ_БОССЫ:
                for i, boss in enumerate(game.exploration_zone.bosses):
                    if boss.boss_name == game.current_enemy:
                        game.exploration_zone.bosses.pop(i)
                        game.add_to_log(f"Ты победил {game.current_enemy.replace('_', ' ')}!")
                        break
            else:
                for i, mob in enumerate(game.exploration_zone.mobs):
                    if mob.enemy_name == game.current_enemy and mob.is_alive:
                        game.exploration_zone.mobs.pop(i)
                        break

    game.battle_log = []

    # ===== ПЕРЕКЛЮЧАЕМ РЕЖИМ =====
    if hasattr(game, 'exploration_in_battle') and game.exploration_in_battle:
        game.режим = "эксплорейшн"
        game.exploration_in_battle = False
        print("🏰 Возвращаемся в данж")
    elif hasattr(game, 'in_dungeon') and game.in_dungeon:
        game.режим = "эксплорейшн"
        game.in_dungeon = False
        print("🏰 Возвращаемся в данж")
    elif hasattr(game, 'exploration_zone') and game.exploration_zone is not None:
        game.режим = "эксплорейшн"
        print("🏰 Возвращаемся в данж")
    else:
        game.режим = "игра"
        print("🎮 Возвращаемся в игру")

    game.blocking = False
    время.пройти_время(15)