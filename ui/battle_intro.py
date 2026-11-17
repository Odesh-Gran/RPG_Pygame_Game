import math
import random
import pygame
from config import WIDTH, HEIGHT


def start_battle_animation(game):
    game.battle_start_animation = True
    game.battle_start_timer = 45
    game.battle_start_alpha = 0
    game.battle_start_scale = 0.3
    print("🎬 Анимация начала боя запущена!")


def update_battle_animation(game):
    if not game.battle_start_animation:
        return
    game.battle_start_timer -= 1
    total_frames = 45
    progress = 1 - (game.battle_start_timer / total_frames)
    if progress < 0.4:
        phase = progress / 0.4
        game.battle_start_alpha = int(255 * phase)
        game.battle_start_scale = 0.3 + (0.7 * phase)
    elif progress < 0.7:
        game.battle_start_alpha = 255
        game.battle_start_scale = 1.0
    else:
        phase = (progress - 0.7) / 0.3
        game.battle_start_alpha = int(255 * (1 - phase))
        game.battle_start_scale = 1.0 - (0.2 * phase)
    if game.battle_start_timer <= 0:
        game.battle_start_animation = False
        print("✨ Анимация начала боя завершена!")


def draw_battle_start_animation(game):
    if not game.battle_start_animation:
        return
    animation_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    flash_radius = int(200 * game.battle_start_scale)
    flash_center = (WIDTH // 2, HEIGHT // 2)
    for i in range(4):
        radius = flash_radius - i * 25
        if radius > 0:
            alpha = min(200, game.battle_start_alpha // (i + 1))
            pygame.draw.circle(animation_surface, (255, 215, 0, alpha), flash_center, radius)
    if game.battle_start_timer > 25:
        font_size = int(72 * game.battle_start_scale)
        try:
            battle_font = pygame.font.Font(None, font_size)
        except:
            battle_font = game.font_large
        battle_text = battle_font.render("БОЙ!", True, (255, 215, 0))
        for offset in [(3, 3), (2, 2), (1, 1)]:
            shadow_text = battle_font.render("БОЙ!", True, (100, 50, 0))
            shadow_rect = shadow_text.get_rect(center=flash_center)
            shadow_rect.x += offset[0]
            shadow_rect.y += offset[1]
            shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
            shadow_surface.blit(shadow_text, (0, 0))
            shadow_surface.set_alpha(game.battle_start_alpha // 2)
            animation_surface.blit(shadow_surface, shadow_rect)
        text_rect = battle_text.get_rect(center=flash_center)
        text_surface = pygame.Surface(text_rect.size, pygame.SRCALPHA)
        text_surface.blit(battle_text, (0, 0))
        text_surface.set_alpha(game.battle_start_alpha)
        animation_surface.blit(text_surface, text_rect)
    if game.battle_start_timer > 15 and game.battle_start_alpha > 0:
        spark_count = int(30 * game.battle_start_scale)
        for _ in range(spark_count):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            spark_size = random.randint(2, 6)
            if game.battle_start_alpha > 50:
                spark_alpha = random.randint(50, game.battle_start_alpha)
            elif game.battle_start_alpha > 1:
                spark_alpha = random.randint(1, game.battle_start_alpha)
            else:
                spark_alpha = 1
            color_choice = random.choice([
                (255, 215, 0, spark_alpha),
                (255, 180, 0, spark_alpha),
                (255, 100, 0, spark_alpha),
            ])
            pygame.draw.circle(animation_surface, color_choice, (x, y), spark_size)
    if game.battle_start_timer > 20 and game.battle_start_alpha > 0:
        angle = pygame.time.get_ticks() * 0.005
        card_positions = [(80, 80), (WIDTH - 430, HEIGHT - 530)]
        for card in card_positions:
            cx, cy = card[0] + 175, card[1] + 225
            for i in range(12):
                rad = angle + (i * 3.14 / 6)
                x1 = cx + int(220 * math.cos(rad)) * game.battle_start_scale
                y1 = cy + int(220 * math.sin(rad)) * game.battle_start_scale
                x2 = cx + int(190 * math.cos(rad + 0.6)) * game.battle_start_scale
                y2 = cy + int(190 * math.sin(rad + 0.6)) * game.battle_start_scale
                alpha = min(200, int(game.battle_start_alpha / 1.5))
                line_width = max(1, int(3 * game.battle_start_scale))
                pygame.draw.line(animation_surface, (255, 215, 0, alpha), (x1, y1), (x2, y2), line_width)
    if game.battle_start_timer > 10 and game.battle_start_alpha > 50:
        particle_count = int(15 * game.battle_start_scale)
        for _ in range(particle_count):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 3)
            max_alpha = game.battle_start_alpha // 2
            if max_alpha > 30:
                alpha = random.randint(30, max_alpha)
            elif max_alpha > 1:
                alpha = random.randint(1, max_alpha)
            else:
                alpha = 1
            pygame.draw.circle(animation_surface, (255, 200, 100, alpha), (x, y), size)
    game.screen.blit(animation_surface, (0, 0))