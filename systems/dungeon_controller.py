# systems/dungeon_controller.py
"""
Управление данжами: Зачарованный лес и Древний склеп.
Выделено из gui_game.py при рефакторинге.
"""
import pygame

from config import HEIGHT, GOLD, DARK_RED, BLACK, WHITE
from systems import exploration
from systems import time_system as время
from entities import enemies as враги


# ===== КОНФИГУРАЦИЯ ДАНЖЕЙ =====
DUNGEONS = {
    "forest": {
        "title": "ЗАЧАРОВАННЫЙ ЛЕС",
        "icon": "🏰",
        "collision_map": "assets/dungeon/forest_collision.png",
        "visual_map": "assets/dungeon/forest_visual.png",
        "map_key": "forest",
    },
    "crypt": {
        "title": "ДРЕВНИЙ СКЛЕП",
        "icon": "💀",
        "collision_map": "assets/dungeon/crypt_collision.png",
        "visual_map": "assets/dungeon/crypt_visual.png",
        "map_key": "crypt",
    },
}


class DungeonController:
    """Управляет данжами: инициализация, игровой цикл, боссы."""

    def __init__(self, game):
        self.game = game

    # ========== ИНИЦИАЛИЗАЦИЯ ==========
    def init_forest(self):
        self._init_dungeon("forest")

    def init_crypt(self):
        self._init_dungeon("crypt")

    def _init_dungeon(self, dungeon_key):
        cfg = DUNGEONS[dungeon_key]
        game = self.game

        print("\n" + "=" * 50)
        print(f"{cfg['icon']} ИНИЦИАЛИЗАЦИЯ: {cfg['title']}")
        print("=" * 50)

        game.exploration_zone = exploration.ExplorationZone(
            2016, 3024,
            collision_map_path=cfg["collision_map"],
            visual_map_path=cfg["visual_map"],
        )
        game.exploration_zone.load_enemies_from_map(cfg["map_key"])

        game.exploration_in_battle = False
        game.in_dungeon = True

        print("\n" + "=" * 50)
        print(f"✅ ДАНЖ ИНИЦИАЛИЗИРОВАН: {cfg['title']}")
        print(f"   - Мобов: {len(game.exploration_zone.mobs)}")
        print(f"   - Боссов: {len(game.exploration_zone.bosses)}")
        print("=" * 50)

    # ========== ИГРОВОЙ ЦИКЛ ==========
    def handle(self):
        game = self.game
        if game.режим != "эксплорейшн":
            return

        if not hasattr(game, "exploration_zone"):
            print("❌ ОШИБКА: exploration_zone не создан!")
            game.режим = "игра"
            game.in_dungeon = False
            return

        keys = pygame.key.get_pressed()
        game.exploration_zone.update(keys)

        # Проверяем столкновения (только если не в бою)
        if not getattr(game, "exploration_in_battle", False):
            encounter = game.exploration_zone.check_encounters()
            if encounter:
                encounter_type, enemy_name, level = encounter
                print(f"⚔️ Столкновение с {enemy_name}!")

                if encounter_type == "boss" or enemy_name in враги.ЛЕСНЫЕ_БОССЫ:
                    self.start_boss_battle(enemy_name)
                else:
                    game.start_battle(enemy_name)

                game.режим = "бой"
                game.exploration_in_battle = True
                return

        # Отрисовка
        game.exploration_zone.draw(game.screen)
        game.draw_status()
        game.draw_actions()
        game.draw_log_panel()
        self.draw_ui()
        self._draw_exit_button()

    def draw_ui(self):
        game = self.game

        info_panel = pygame.Rect(10, 60, 250, 100)
        pygame.draw.rect(game.screen, (0, 0, 0, 180), info_panel)
        pygame.draw.rect(game.screen, GOLD, info_panel, 2)

        texts = [
            f"Позиция: ({int(game.exploration_zone.player_x)}, {int(game.exploration_zone.player_y)})",
            f"Мобы: {len([m for m in game.exploration_zone.mobs if m.is_alive])}",
            f"Босс: {'Жив' if not any(b.defeated for b in game.exploration_zone.bosses) else 'Побеждён'}",
        ]
        for i, text in enumerate(texts):
            game.screen.blit(game.font_small.render(text, True, (200, 200, 200)), (20, 70 + i * 25))

        controls = [
            "WASD/Стрелки - движение",
            "Выйти - кнопка в левом верхнем углу",
        ]
        for i, text in enumerate(controls):
            game.screen.blit(game.font_tiny.render(text, True, (150, 150, 150)), (20, HEIGHT - 40 + i * 15))

    def _draw_exit_button(self):
        game = self.game
        exit_button = pygame.Rect(10, 10, 100, 40)

        if exit_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(game.screen, GOLD, exit_button)
            exit_text = game.font_medium.render("ВЫЙТИ", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, exit_button)
            pygame.draw.rect(game.screen, GOLD, exit_button, 2)
            exit_text = game.font_medium.render("ВЫЙТИ", True, WHITE)

        game.screen.blit(exit_text, (exit_button.x + 15, exit_button.y + 8))
        game.exploration_exit_button = exit_button

    # ========== БОССЫ ==========
    def start_boss_battle(self, boss_name):
        game = self.game

        # Сброс боевых параметров
        game.battle.battle_ended = False
        game.battle.enemy_data = None
        game.enemy_bleed_duration = 0
        game.enemy_bleed_damage = 0
        game.enemy_stunned = False
        game.enemy_weakened_duration = 0
        game.blocking = False
        game.enemy_damage_multiplier = 1.0

        game.режим = "бой"
        game.current_enemy = boss_name
        game.enemy_data = враги.получить_босса(boss_name).copy()
        game.enemy_health = game.enemy_data["здоровье"]
        game.battle_log = [f"👑 ПЕРЕД ТОБОЙ {boss_name.replace('_', ' ').upper()}!"]
        game.is_boss_battle = True

        # Прокидываем данные в BattleSystem
        game.battle.current_enemy = boss_name
        game.battle.enemy_data = game.enemy_data
        game.battle.enemy_health = game.enemy_health
        game.battle.battle_log = game.battle_log

        game.start_battle_animation()
        время.пройти_время(2)