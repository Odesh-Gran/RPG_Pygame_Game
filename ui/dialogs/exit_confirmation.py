import pygame
from config import WIDTH, HEIGHT, DARK_BLUE, GOLD, DARK_RED, BLACK, WHITE, FPS


def show_exit_confirmation(game):
    """Показывает диалог подтверждения выхода из игры. Возвращает True если игрок согласился."""

    # Затемнение фона
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    game.screen.blit(overlay, (0, 0))

    # Панель диалога
    panel_width = 400
    panel_height = 200
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2

    # Фон панели
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    # Текст
    question = game.font_medium.render("Выйти из игры?", True, GOLD)
    q_x = panel_x + panel_width // 2 - question.get_width() // 2
    game.screen.blit(question, (q_x, panel_y + 30))

    sub_text = game.font_small.render("Жду тебя снова", True, WHITE)
    sub_x = panel_x + panel_width // 2 - sub_text.get_width() // 2
    game.screen.blit(sub_text, (sub_x, panel_y + 70))

    # Кнопки
    yes_rect = pygame.Rect(panel_x + 50, panel_y + 120, 120, 40)
    no_rect = pygame.Rect(panel_x + panel_width - 170, panel_y + 120, 120, 40)

    mouse_pos = pygame.mouse.get_pos()

    # Кнопка ДА
    if yes_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, yes_rect)
        yes_text = game.font_medium.render("ДА", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, yes_rect)
        pygame.draw.rect(game.screen, GOLD, yes_rect, 2)
        yes_text = game.font_medium.render("ДА", True, WHITE)
    game.screen.blit(yes_text, (yes_rect.x + 45, yes_rect.y + 8))

    # Кнопка НЕТ
    if no_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, no_rect)
        no_text = game.font_medium.render("НЕТ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, no_rect)
        pygame.draw.rect(game.screen, GOLD, no_rect, 2)
        no_text = game.font_medium.render("НЕТ", True, WHITE)
    game.screen.blit(no_text, (no_rect.x + 40, no_rect.y + 8))

    pygame.display.flip()

    # Ожидание выбора
    while True:
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
        game.clock.tick(FPS)