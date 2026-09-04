"""
Модуль для коридорных данжей (подземелий)
С пошаговым движением как в Stoneshard
"""

import pygame
import random
import math

# Константы для исследования
EXPLORE_WIDTH = 2016    # Ширина карты в пикселях
EXPLORE_HEIGHT = 3024     # Высота карты в пикселях

# Цвета для данжа
COLOR_DUNGEON = (20, 20, 30)     # Тёмный фон подземелья
COLOR_WALL = (40, 40, 50)        # Стены
COLOR_FLOOR = (60, 60, 70)       # Пол
COLOR_PATH = (80, 70, 60)        # Коридор
COLOR_MOB = (150, 50, 50)        # Мобы (красные)
COLOR_MOB_BORDER = (200, 100, 100)  # Рамка моба
COLOR_BOSS = (200, 50, 50)       # Босс (ярко-красный)
COLOR_BOSS_BORDER = (255, 200, 50)  # Рамка босса (золотая)
COLOR_PLAYER = (50, 100, 200)    # Игрок (синий)
COLOR_OBSTACLE = (80, 60, 40)    # Препятствия


class Mob:
    """Класс для мобов на карте"""

    def __init__(self, x, y, enemy_name, level=1, collision_map=None):
        self.x = x
        self.y = y
        self.enemy_name = enemy_name
        self.level = level
        self.collision_map = collision_map
        self.size = 32
        self.tile_size = 48

        # Агро радиус (в клетках) - ДОБАВИТЬ!
        self.aggro_range = 8

        # Анимация
        self.animation_offset = 0
        self.animation_speed = 0.1
        self.animation_timer = random.uniform(0, 6.28)

        # Состояние
        self.is_alive = True

    def is_wall(self, x, y):
        """Проверяет, является ли точка стеной"""
        if not self.collision_map:
            return False
        if x < 0 or x >= self.collision_map.get_width():
            return True
        if y < 0 or y >= self.collision_map.get_height():
            return True
        try:
            color = self.collision_map.get_at((int(x), int(y)))
            return color[0] < 50 and color[1] < 50 and color[2] < 50
        except:
            return True

    def get_tile(self):
        """Возвращает позицию в клетках"""
        return (self.x // self.tile_size, self.y // self.tile_size)

    def move_to_tile(self, target_tile_x, target_tile_y):
        """Мгновенное перемещение на клетку"""
        new_pixel_x = target_tile_x * self.tile_size + self.tile_size // 2
        new_pixel_y = target_tile_y * self.tile_size + self.tile_size // 2
        if not self.is_wall(new_pixel_x, new_pixel_y):
            self.x = new_pixel_x
            self.y = new_pixel_y
            return True
        return False

    def update_animation(self):
        """Обновляет анимацию (Idle)"""
        self.animation_timer += self.animation_speed
        self.animation_offset = math.sin(self.animation_timer) * 3

    def get_rect(self):
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size, self.size
        )

    def check_collision(self, player_rect):
        return self.get_rect().colliderect(player_rect)

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.animation_offset

        if -self.size <= screen_x <= 1280 + self.size and -self.size <= screen_y <= 720 + self.size:
            pygame.draw.rect(screen, COLOR_MOB,
                             (screen_x - self.size // 2, screen_y - self.size // 2,
                              self.size, self.size))
            pygame.draw.rect(screen, COLOR_MOB_BORDER,
                             (screen_x - self.size // 2, screen_y - self.size // 2,
                              self.size, self.size), 2)

            eye_size = 6
            pygame.draw.circle(screen, (255, 255, 255),
                               (screen_x - 8, screen_y - 8), eye_size)
            pygame.draw.circle(screen, (255, 255, 255),
                               (screen_x + 8, screen_y - 8), eye_size)
            pygame.draw.circle(screen, (0, 0, 0),
                               (screen_x - 8, screen_y - 8), eye_size // 2)
            pygame.draw.circle(screen, (0, 0, 0),
                               (screen_x + 8, screen_y - 8), eye_size // 2)


class Boss:
    """Класс для босса на карте"""

    def __init__(self, x, y, boss_name, collision_map=None):
        self.x = x
        self.y = y
        self.boss_name = boss_name
        self.collision_map = collision_map
        self.size = 64
        self.tile_size = 48

        # Агро радиус для босса (в клетках) - ДОБАВИТЬ!
        self.aggro_range = 15

        self.animation_offset = 0
        self.animation_speed = 0.08
        self.animation_timer = random.uniform(0, 6.28)
        self.defeated = False

    def is_wall(self, x, y):
        if not self.collision_map:
            return False
        if x < 0 or x >= self.collision_map.get_width():
            return True
        if y < 0 or y >= self.collision_map.get_height():
            return True
        try:
            color = self.collision_map.get_at((int(x), int(y)))
            return color[0] < 50 and color[1] < 50 and color[2] < 50
        except:
            return True

    def get_tile(self):
        return (self.x // self.tile_size, self.y // self.tile_size)

    def move_to_tile(self, target_tile_x, target_tile_y):
        new_pixel_x = target_tile_x * self.tile_size + self.tile_size // 2
        new_pixel_y = target_tile_y * self.tile_size + self.tile_size // 2
        if not self.is_wall(new_pixel_x, new_pixel_y):
            self.x = new_pixel_x
            self.y = new_pixel_y
            return True
        return False

    def update_animation(self):
        self.animation_timer += self.animation_speed
        self.animation_offset = math.sin(self.animation_timer) * 3

    def get_rect(self):
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size, self.size
        )

    def check_collision(self, player_rect):
        return self.get_rect().colliderect(player_rect)

    def draw(self, screen, camera_x, camera_y):
        if self.defeated:
            return

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.animation_offset

        if -self.size <= screen_x <= 1280 + self.size and -self.size <= screen_y <= 720 + self.size:
            pygame.draw.rect(screen, COLOR_BOSS,
                             (screen_x - self.size // 2, screen_y - self.size // 2,
                              self.size, self.size))

            border_color = COLOR_BOSS_BORDER
            pygame.draw.rect(screen, border_color,
                             (screen_x - self.size // 2, screen_y - self.size // 2,
                              self.size, self.size), 3)

            crown_points = [
                (screen_x, screen_y - self.size // 2 - 10),
                (screen_x - 15, screen_y - self.size // 2),
                (screen_x + 15, screen_y - self.size // 2)
            ]
            pygame.draw.polygon(screen, (255, 200, 50), crown_points)

            eye_size = 10
            pygame.draw.circle(screen, (255, 255, 255),
                               (screen_x - 12, screen_y - 12), eye_size)
            pygame.draw.circle(screen, (255, 255, 255),
                               (screen_x + 12, screen_y - 12), eye_size)
            pygame.draw.circle(screen, (0, 0, 0),
                               (screen_x - 12, screen_y - 12), eye_size // 2)
            pygame.draw.circle(screen, (0, 0, 0),
                               (screen_x + 12, screen_y - 12), eye_size // 2)

            font = pygame.font.Font(None, 16)
            name_text = font.render(self.boss_name.replace('_', ' '), True, (255, 200, 50))
            name_x = screen_x - name_text.get_width() // 2
            name_y = screen_y - self.size // 2 - 25
            for ox, oy in [(name_x - 1, name_y), (name_x + 1, name_y),
                           (name_x, name_y - 1), (name_x, name_y + 1)]:
                screen.blit(name_text, (ox, oy))
            screen.blit(name_text, (name_x, name_y))


class ExplorationZone:
    """Класс для управления данжем с пошаговым движением"""

    def __init__(self, width, height, background_color=None, collision_map_path=None, visual_map_path=None):
        self.width = width
        self.height = height
        self.background_color = background_color or COLOR_DUNGEON

        # Параметры пошагового движения
        self.tile_size = 48  # Размер клетки в пикселях

        # Карты
        self.collision_map = None
        self.visual_map = None

        if collision_map_path:
            try:
                self.collision_map = pygame.image.load(collision_map_path).convert()
                self.width = self.collision_map.get_width()
                self.height = self.collision_map.get_height()
                print(f"✅ Загружена карта коллизий: {self.width}x{self.height}")
            except Exception as e:
                print(f"❌ Ошибка загрузки карты коллизий: {e}")

        if visual_map_path:
            try:
                self.visual_map = pygame.image.load(visual_map_path).convert()
                print(f"✅ Загружена визуальная карта: {self.visual_map.get_size()}")
            except Exception as e:
                print(f"⚠️ Визуальная карта не загружена: {e}")

        # Объекты на карте
        self.mobs = []
        self.bosses = []
        self.obstacles = []

        # Игрок
        if self.collision_map:
            self.player_x, self.player_y = self._find_start_position()
        else:
            self.player_x = width // 2
            self.player_y = height // 2

        # Выравниваем по сетке
        self._align_to_grid()

        self.player_size = 32

        # Анимация движения
        self.is_moving = False
        self.move_progress = 0
        self.move_speed = 0.15
        self.start_x = self.player_x
        self.start_y = self.player_y
        self.target_x = self.player_x
        self.target_y = self.player_y

        # Пошаговая система
        self.is_player_turn = True
        self.enemies_moved = False

        # Камера
        self.camera_x = 0
        self.camera_y = 0

        # Состояние
        self.in_battle = False

        # Анимация игрока
        self.player_animation_offset = 0
        self.player_animation_timer = 0

    def _align_to_grid(self):
        """Выравнивает позицию игрока по сетке"""
        old_x, old_y = self.player_x, self.player_y
        self.player_x = (self.player_x // self.tile_size) * self.tile_size + self.tile_size // 2
        self.player_y = (self.player_y // self.tile_size) * self.tile_size + self.tile_size // 2
        print(f"📐 Выравнивание позиции: ({old_x}, {old_y}) -> ({self.player_x}, {self.player_y})")

    def _find_start_position(self):
        """Находит стартовую позицию и выравнивает по центру клетки"""
        print("🔍 Поиск стартовой позиции...")

        # Сначала ищем зелёную точку (старт)
        for y in range(self.height):
            for x in range(self.width):
                try:
                    color = self.collision_map.get_at((x, y))
                    if color[1] > 200 and color[0] < 100 and color[2] < 100:
                        # ВЫРАВНИВАЕМ ПО ЦЕНТРУ КЛЕТКИ
                        tile_x = x // self.tile_size
                        tile_y = y // self.tile_size
                        center_x = tile_x * self.tile_size + self.tile_size // 2
                        center_y = tile_y * self.tile_size + self.tile_size // 2
                        print(f"   ✅ Стартовая позиция: ({center_x}, {center_y})")
                        return center_x, center_y
                except:
                    continue

    def is_wall(self, x, y):
        if not self.collision_map:
            return False
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        try:
            color = self.collision_map.get_at((int(x), int(y)))
            return color[0] < 50 and color[1] < 50 and color[2] < 50
        except:
            return True

    def get_player_tile(self):
        """Возвращает текущую клетку игрока"""
        return (self.player_x // self.tile_size, self.player_y // self.tile_size)

    def try_move_to_tile(self, target_tile_x, target_tile_y):
        """Попытка переместиться на указанную клетку"""
        if self.is_moving or not self.is_player_turn:
            return False

        if target_tile_x < 0 or target_tile_x >= self.width // self.tile_size:
            return False
        if target_tile_y < 0 or target_tile_y >= self.height // self.tile_size:
            return False

        target_pixel_x = target_tile_x * self.tile_size + self.tile_size // 2
        target_pixel_y = target_tile_y * self.tile_size + self.tile_size // 2

        if self.is_wall(target_pixel_x, target_pixel_y):
            return False

        self.start_x = self.player_x
        self.start_y = self.player_y
        self.target_x = target_pixel_x
        self.target_y = target_pixel_y
        self.is_moving = True
        self.move_progress = 0
        return True

    def update_movement(self):
        """Обновляет анимацию движения"""
        if not self.is_moving:
            return

        self.move_progress += self.move_speed
        if self.move_progress >= 1:
            self.player_x = self.target_x
            self.player_y = self.target_y
            self.is_moving = False
            self.move_progress = 0
            self.is_player_turn = False
            self.enemies_moved = False
        else:
            t = self.move_progress
            t = 1 - (1 - t) ** 2  # Плавное замедление
            self.player_x = self.start_x + (self.target_x - self.start_x) * t
            self.player_y = self.start_y + (self.target_y - self.start_y) * t

    def move_enemy_towards_player(self, enemy):
        """Двигает врага к игроку (на одну клетку) с учётом агро радиуса"""

        # Получаем агро радиус (по умолчанию 8 клеток)
        aggro_range = getattr(enemy, 'aggro_range', 8)

        enemy_tile = enemy.get_tile()
        player_tile = self.get_player_tile()

        # Проверяем дистанцию
        dx_cells = abs(enemy_tile[0] - player_tile[0])
        dy_cells = abs(enemy_tile[1] - player_tile[1])

        if dx_cells > aggro_range or dy_cells > aggro_range:
            return False  # Вне радиуса агро

        if isinstance(enemy, Boss) and enemy.defeated:
            return False

        dx = 0
        dy = 0

        # Простая логика: сначала по горизонтали, потом по вертикали
        if abs(enemy_tile[0] - player_tile[0]) > abs(enemy_tile[1] - player_tile[1]):
            dx = 1 if player_tile[0] > enemy_tile[0] else -1 if player_tile[0] < enemy_tile[0] else 0
        else:
            dy = 1 if player_tile[1] > enemy_tile[1] else -1 if player_tile[1] < enemy_tile[1] else 0

        if dx != 0 or dy != 0:
            new_tile_x = enemy_tile[0] + dx
            new_tile_y = enemy_tile[1] + dy

            # Проверяем стену
            test_pixel_x = new_tile_x * self.tile_size + self.tile_size // 2
            test_pixel_y = new_tile_y * self.tile_size + self.tile_size // 2
            if self.is_wall(test_pixel_x, test_pixel_y):
                return False

            # Проверяем, не занята ли клетка другим врагом
            for other in self.mobs:
                if other != enemy and other.is_alive:
                    if other.get_tile() == (new_tile_x, new_tile_y):
                        return False
            for other in self.bosses:
                if other != enemy and not other.defeated:
                    if other.get_tile() == (new_tile_x, new_tile_y):
                        return False

            enemy.move_to_tile(new_tile_x, new_tile_y)
            return True
        return False

    def update_enemies_turn(self):
        """Обновляет ход врагов - ДВИГАЮТСЯ ВСЕ, КТО В РАДИУСЕ АГРО"""
        if self.is_player_turn or self.is_moving:
            return

        if self.enemies_moved:
            self.is_player_turn = True
            self.enemies_moved = False
            return

        # Собираем всех врагов, которые в радиусе агро
        enemies_to_move = []

        # Проверяем боссов
        for boss in self.bosses:
            if not boss.defeated:
                boss_tile = boss.get_tile()
                player_tile = self.get_player_tile()
                dx_cells = abs(boss_tile[0] - player_tile[0])
                dy_cells = abs(boss_tile[1] - player_tile[1])
                aggro_range = getattr(boss, 'aggro_range', 15)

                if dx_cells <= aggro_range and dy_cells <= aggro_range:
                    enemies_to_move.append(boss)

        # Проверяем мобов
        for mob in self.mobs:
            if mob.is_alive:
                mob_tile = mob.get_tile()
                player_tile = self.get_player_tile()
                dx_cells = abs(mob_tile[0] - player_tile[0])
                dy_cells = abs(mob_tile[1] - player_tile[1])
                aggro_range = getattr(mob, 'aggro_range', 8)

                if dx_cells <= aggro_range and dy_cells <= aggro_range:
                    enemies_to_move.append(mob)

        # Двигаем ВСЕХ врагов в радиусе агро
        any_moved = False
        for enemy in enemies_to_move:
            if self.move_enemy_towards_player(enemy):
                any_moved = True

        # Ход закончен
        self.enemies_moved = True

    def update_animations(self):
        """Обновляет анимации всех объектов"""
        # Анимация игрока (Idle)
        self.player_animation_timer += 0.1
        self.player_animation_offset = math.sin(self.player_animation_timer) * 2

        # Анимация мобов
        for mob in self.mobs:
            if mob.is_alive:
                mob.update_animation()
        for boss in self.bosses:
            boss.update_animation()

    def update(self, keys):
        """Обновление состояния с пошаговым движением"""
        if self.in_battle:
            return

        # Обновляем анимации
        self.update_animations()

        # Обновляем движение
        self.update_movement()

        # Обрабатываем ход игрока
        if not self.is_moving and self.is_player_turn:
            move_x, move_y = 0, 0

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move_y = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x = 1

            if move_x != 0 or move_y != 0:
                player_tile = self.get_player_tile()
                new_tile_x = player_tile[0] + move_x
                new_tile_y = player_tile[1] + move_y
                self.try_move_to_tile(new_tile_x, new_tile_y)

        # Обновляем ход врагов
        if not self.is_moving and not self.is_player_turn:
            self.update_enemies_turn()

        # Обновление камеры
        self.camera_x = self.player_x - 640
        self.camera_y = self.player_y - 360
        self.camera_x = max(0, min(self.width - 1280, self.camera_x))
        self.camera_y = max(0, min(self.height - 720, self.camera_y))

    def check_encounters(self):
        """Проверка столкновений с мобами и боссами"""
        player_rect = pygame.Rect(
            self.player_x - self.player_size // 2,
            self.player_y - self.player_size // 2,
            self.player_size, self.player_size
        )

        for mob in self.mobs:
            if mob.is_alive and mob.check_collision(player_rect):
                return ("mob", mob.enemy_name, mob.level)

        for boss in self.bosses:
            if not boss.defeated and boss.check_collision(player_rect):
                return ("boss", boss.boss_name, 1)

        return None

    def add_mob(self, mob):
        self.mobs.append(mob)

    def add_boss(self, boss):
        self.bosses.append(boss)

    def add_obstacle(self, x, y, width, height):
        self.obstacles.append(pygame.Rect(x, y, width, height))

    def draw(self, screen):
        """Отрисовка данжа"""
        if self.visual_map:
            screen.blit(self.visual_map, (0, 0),
                       area=(self.camera_x, self.camera_y, 1280, 720))
        else:
            screen.fill(self.background_color)
            if self.collision_map:
                for y in range(0, self.height, 20):
                    for x in range(0, self.width, 20):
                        if self.is_wall(x, y):
                            screen_x = x - self.camera_x
                            screen_y = y - self.camera_y
                            if 0 <= screen_x <= 1280 and 0 <= screen_y <= 720:
                                pygame.draw.rect(screen, COLOR_WALL,
                                               (screen_x, screen_y, 20, 20))

        for obstacle in self.obstacles:
            screen_rect = pygame.Rect(
                obstacle.x - self.camera_x,
                obstacle.y - self.camera_y,
                obstacle.width, obstacle.height
            )
            if screen_rect.right > 0 and screen_rect.left < 1280 and \
               screen_rect.bottom > 0 and screen_rect.top < 720:
                pygame.draw.rect(screen, COLOR_OBSTACLE, screen_rect)
                pygame.draw.rect(screen, (100, 80, 60), screen_rect, 2)

        for mob in self.mobs:
            if mob.is_alive:
                mob.draw(screen, self.camera_x, self.camera_y)

        for boss in self.bosses:
            boss.draw(screen, self.camera_x, self.camera_y)

        # Рисуем игрока со смещением
        player_screen_x = self.player_x - self.camera_x
        player_screen_y = self.player_y - self.camera_y

        offset_x = 10  # смещение вправо
        offset_y = 0

        # Тело
        pygame.draw.rect(screen, COLOR_PLAYER,
                         (player_screen_x - self.player_size // 2 + offset_x,
                          player_screen_y - self.player_size // 2 + offset_y,
                          self.player_size, self.player_size))

        # Рамка
        pygame.draw.rect(screen, (100, 150, 255),
                         (player_screen_x - self.player_size // 2 + offset_x,
                          player_screen_y - self.player_size // 2 + offset_y,
                          self.player_size, self.player_size), 2)

        # Глаза
        eye_size = 6
        pygame.draw.circle(screen, (255, 255, 255),
                           (player_screen_x - 8 + offset_x, player_screen_y - 8 + offset_y), eye_size)
        pygame.draw.circle(screen, (255, 255, 255),
                           (player_screen_x + 8 + offset_x, player_screen_y - 8 + offset_y), eye_size)
        pygame.draw.circle(screen, (0, 0, 0),
                           (player_screen_x - 8 + offset_x, player_screen_y - 8 + offset_y), eye_size // 2)
        pygame.draw.circle(screen, (0, 0, 0),
                           (player_screen_x + 8 + offset_x, player_screen_y - 8 + offset_y), eye_size // 2)

        self._draw_minimap(screen)

    def _draw_minimap(self, screen):
        """Рисует мини-карту"""
        minimap_size = 180
        minimap_x = 1280 - minimap_size - 10
        minimap_y = 10

        minimap_bg = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        minimap_bg.fill((0, 0, 0, 180))
        screen.blit(minimap_bg, (minimap_x, minimap_y))
        pygame.draw.rect(screen, (200, 200, 200),
                         (minimap_x, minimap_y, minimap_size, minimap_size), 2)

        scale_x = minimap_size / self.width
        scale_y = minimap_size / self.height

        if self.collision_map:
            for y in range(0, self.height, 50):
                for x in range(0, self.width, 50):
                    if self.is_wall(x, y):
                        mini_x = minimap_x + x * scale_x
                        mini_y = minimap_y + y * scale_y
                        pygame.draw.rect(screen, (40, 40, 50),
                                       (mini_x, mini_y, 3, 3))

        for obstacle in self.obstacles:
            mini_x = minimap_x + obstacle.centerx * scale_x
            mini_y = minimap_y + obstacle.centery * scale_y
            pygame.draw.rect(screen, (80, 60, 40),
                             (mini_x - 2, mini_y - 2, 4, 4))

        for mob in self.mobs:
            if mob.is_alive:
                mini_x = minimap_x + mob.x * scale_x
                mini_y = minimap_y + mob.y * scale_y
                pygame.draw.circle(screen, (200, 50, 50),
                                   (int(mini_x), int(mini_y)), 3)

        for boss in self.bosses:
            if not boss.defeated:
                mini_x = minimap_x + boss.x * scale_x
                mini_y = minimap_y + boss.y * scale_y
                pygame.draw.circle(screen, (255, 100, 100),
                                   (int(mini_x), int(mini_y)), 5)
                pygame.draw.circle(screen, (255, 200, 50),
                                   (int(mini_x), int(mini_y)), 5, 2)

        mini_x = minimap_x + self.player_x * scale_x
        mini_y = minimap_y + self.player_y * scale_y
        pygame.draw.circle(screen, (100, 150, 255),
                           (int(mini_x), int(mini_y)), 4)
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(mini_x), int(mini_y)), 4, 1)

        pygame.draw.polygon(screen, (255, 255, 255),
                           [(int(mini_x), int(mini_y) - 6),
                            (int(mini_x) - 2, int(mini_y) - 2),
                            (int(mini_x) + 2, int(mini_y) - 2)])

    def load_enemies_from_map(self, dungeon_type="forest"):
        """
        Загружает врагов из карты коллизий по цветам
        """
        if not self.collision_map:
            print("❌ Нет карты коллизий для загрузки врагов")
            return

        print(f"\n👾 ЗАГРУЗКА ВРАГОВ ДЛЯ {dungeon_type.upper()}")

        # Выбираем набор врагов в зависимости от типа данжа
        if dungeon_type == "crypt":
            color_enemies = {
                (255, 255, 0): {
                    "enemies": ["скелет", "скелет", "скелет"],
                    "level_range": (1, 2),
                    "type": "normal"
                },
                (255, 165, 0): {
                    "enemies": ["призрак", "призрак", "скелет"],
                    "level_range": (3, 4),
                    "type": "medium"
                },
                (255, 0, 0): {
                    "enemies": ["рыцарь_призрак", "рыцарь_призрак"],
                    "level_range": (5, 6),
                    "type": "elite"
                },
                (128, 0, 128): {
                    "enemies": ["королевский_страж"],
                    "level_range": (7, 7),
                    "type": "boss"
                },
            }
        elif dungeon_type == "library":
            color_enemies = {
                (255, 255, 0): {
                    "enemies": ["летучая_мышь", "летучая_мышь"],
                    "level_range": (1, 2),
                    "type": "normal"
                },
                (255, 165, 0): {
                    "enemies": ["призрак", "призрак"],
                    "level_range": (3, 4),
                    "type": "medium"
                },
                (255, 0, 0): {
                    "enemies": ["рыцарь_призрак"],
                    "level_range": (5, 6),
                    "type": "elite"
                },
                (128, 0, 128): {
                    "enemies": ["лесной_король"],
                    "level_range": (7, 7),
                    "type": "boss"
                },
            }
        else:  # forest (по умолчанию)
            color_enemies = {
                (255, 255, 0): {
                    "enemies": ["лесной_гоблин", "лесной_гоблин", "лесной_волк", "лесная_фея"],
                    "level_range": (1, 2),
                    "type": "normal"
                },
                (255, 165, 0): {
                    "enemies": ["лесной_волк", "лесной_волк", "древний_энт", "лесной_тролль"],
                    "level_range": (3, 4),
                    "type": "medium"
                },
                (255, 0, 0): {
                    "enemies": ["древний_энт", "лесной_тролль", "лесной_тролль"],
                    "level_range": (5, 6),
                    "type": "elite"
                },
                (128, 0, 128): {
                    "enemies": ["лесной_король"],
                    "level_range": (7, 7),
                    "type": "boss"
                },
            }

        # ===== СКАНИРУЕМ КАРТУ =====
        enemy_count = 0
        boss_count = 0
        processed_positions = set()

        step = 5  # Шаг 5 пикселей
        for y in range(0, self.height, step):
            for x in range(0, self.width, step):
                try:
                    color = self.collision_map.get_at((x, y))
                    r, g, b = color[0], color[1], color[2]

                    if (r < 30 and g < 30 and b < 30):
                        continue
                    if (r > 220 and g > 220 and b > 220):
                        continue

                    for target_color, data in color_enemies.items():
                        if (abs(r - target_color[0]) < 60 and
                                abs(g - target_color[1]) < 60 and
                                abs(b - target_color[2]) < 60):

                            cell_x = (x // self.tile_size) * self.tile_size + self.tile_size // 2
                            cell_y = (y // self.tile_size) * self.tile_size + self.tile_size // 2
                            pos_key = (cell_x // self.tile_size, cell_y // self.tile_size)

                            if pos_key in processed_positions:
                                break
                            processed_positions.add(pos_key)

                            print(f"   🎨 Найден {data['type']} RGB({r},{g},{b}) на ({x}, {y})")

                            if data["type"] == "boss":
                                boss = Boss(cell_x, cell_y, data["enemies"][0], self.collision_map)
                                self.add_boss(boss)
                                boss_count += 1
                                print(f"   👑 БОСС создан на ({cell_x}, {cell_y})")
                            else:
                                import random
                                enemy_name = random.choice(data["enemies"])
                                level = random.randint(data["level_range"][0], data["level_range"][1])
                                mob = Mob(cell_x, cell_y, enemy_name, level, self.collision_map)
                                self.add_mob(mob)
                                enemy_count += 1
                                print(f"   👾 {enemy_name} (ур.{level}) создан на ({cell_x}, {cell_y})")
                            break
                except:
                    continue

        print(f"\n✅ ЗАГРУЗКА ЗАВЕРШЕНА!")
        print(f"   - Мобов: {enemy_count}")
        print(f"   - Боссов: {boss_count}")