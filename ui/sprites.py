import pygame
from config import DARK_BLUE, DARK_RED, WHITE, BLACK, GOLD, BLOOD_RED


def load_player_sprite(game):
    try:
        game.player_sprite = pygame.image.load("assets/player/idle.png").convert_alpha()
        game.player_sprite = pygame.transform.scale(game.player_sprite, (game.player_size, game.player_size))
        print("✅ Спрайт персонажа загружен")
    except:
        print("❌ Не удалось загрузить спрайт, создаю заглушку")
        create_player_placeholder(game)


def create_player_placeholder(game):
    game.player_sprite = pygame.Surface((game.player_size, game.player_size), pygame.SRCALPHA)
    padding = game.player_size // 8
    body_size = game.player_size - padding * 2
    pygame.draw.rect(game.player_sprite, DARK_BLUE, (padding, padding, body_size, body_size))
    eye_size = game.player_size // 8
    eye_y = game.player_size // 3
    left_eye_x = game.player_size // 3
    right_eye_x = game.player_size * 2 // 3
    pygame.draw.circle(game.player_sprite, WHITE, (left_eye_x, eye_y), eye_size)
    pygame.draw.circle(game.player_sprite, WHITE, (right_eye_x, eye_y), eye_size)
    pygame.draw.circle(game.player_sprite, BLACK, (left_eye_x, eye_y), eye_size // 2)
    pygame.draw.circle(game.player_sprite, BLACK, (right_eye_x, eye_y), eye_size // 2)
    mouth_y = game.player_size * 2 // 3
    mouth_width = game.player_size // 2
    mouth_height = game.player_size // 4
    pygame.draw.arc(game.player_sprite, WHITE, (game.player_size // 4, mouth_y, mouth_width, mouth_height), 0, 3.14, game.player_size // 16)
    pygame.draw.rect(game.player_sprite, GOLD, (0, 0, game.player_size, game.player_size), 3)
    print(f"🎨 Создан спрайт-заглушка {game.player_size}x{game.player_size}")


def load_enemy_sprite_by_name(game, enemy_name):
    from entities import enemies as враги
    enemy_data = враги.враги.get(enemy_name)
    if not enemy_data:
        print(f"❌ Враг {enemy_name} не найден!")
        return create_enemy_placeholder(game)
    sprite_path = enemy_data.get("спрайт")
    if not sprite_path:
        print(f"⚠️ Для врага {enemy_name} не указан спрайт!")
        return create_enemy_placeholder(game)
    try:
        sprite = pygame.image.load(sprite_path).convert_alpha()
        sprite = pygame.transform.scale(sprite, (game.enemy_size, game.enemy_size))
        print(f"✅ Загружен спрайт для {enemy_name}")
        return sprite
    except Exception as e:
        print(f"❌ Ошибка загрузки спрайта {enemy_name}: {e}")
        return create_enemy_placeholder(game)


def create_enemy_placeholder(game):
    game.enemy_sprite = pygame.Surface((game.enemy_size, game.enemy_size), pygame.SRCALPHA)
    padding = game.enemy_size // 8
    body_size = game.enemy_size - padding * 2
    pygame.draw.rect(game.enemy_sprite, DARK_RED, (padding, padding, body_size, body_size))
    eye_size = game.enemy_size // 8
    eye_y = game.enemy_size // 3
    left_eye_x = game.enemy_size // 3
    right_eye_x = game.enemy_size * 2 // 3
    pygame.draw.circle(game.enemy_sprite, WHITE, (left_eye_x, eye_y), eye_size)
    pygame.draw.circle(game.enemy_sprite, WHITE, (right_eye_x, eye_y), eye_size)
    pygame.draw.circle(game.enemy_sprite, BLOOD_RED, (left_eye_x, eye_y), eye_size // 2)
    pygame.draw.circle(game.enemy_sprite, BLOOD_RED, (right_eye_x, eye_y), eye_size // 2)
    brow_y = eye_y - eye_size // 2
    pygame.draw.line(game.enemy_sprite, BLACK, (left_eye_x - eye_size, brow_y), (left_eye_x + eye_size, brow_y - eye_size // 2), 3)
    pygame.draw.line(game.enemy_sprite, BLACK, (right_eye_x + eye_size, brow_y), (right_eye_x - eye_size, brow_y - eye_size // 2), 3)
    mouth_y = game.enemy_size * 2 // 3
    mouth_width = game.enemy_size // 2
    mouth_height = game.enemy_size // 4
    pygame.draw.arc(game.enemy_sprite, BLOOD_RED, (game.enemy_size // 4, mouth_y, mouth_width, mouth_height), 3.14, 6.28, game.enemy_size // 16)
    pygame.draw.rect(game.enemy_sprite, BLOOD_RED, (0, 0, game.enemy_size, game.enemy_size), 3)
    print(f"🎨 Создан спрайт-заглушка врага {game.enemy_size}x{game.enemy_size}")