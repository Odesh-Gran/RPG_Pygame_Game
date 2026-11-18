import pygame
from config import WIDTH, HEIGHT, DARK_BLUE, GOLD, DARK_RED, BLACK, WHITE, FPS
from ui.save_menus import show_save_menu_for_exit


def show_exit_dialog(game):
    """Показывает диалог выхода с сохранением. Возвращает True/False."""

    # Затемнение фона
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    game.screen.blit(s, (0, 0))

    # Панель диалога
    panel_width = 320
    panel_height = 280
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2

    # Фон панели
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
    pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

    # Текст вопроса
    question = game.font_medium.render("СОХРАНИТЬ ИГРУ?", True, GOLD)
    q_x = panel_x + panel_width // 2 - question.get_width() // 2
    game.screen.blit(question, (q_x, panel_y + 30))

    # Разделитель
    pygame.draw.line(game.screen, GOLD,
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
        pygame.draw.rect(game.screen, GOLD, save_rect)
        save_text = game.font_medium.render("СОХРАНИТЬ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, save_rect)
        pygame.draw.rect(game.screen, GOLD, save_rect, 2)
        save_text = game.font_medium.render("СОХРАНИТЬ", True, WHITE)

    text_x = save_rect.x + save_rect.width // 2 - save_text.get_width() // 2
    text_y = save_rect.y + save_rect.height // 2 - save_text.get_height() // 2
    game.screen.blit(save_text, (text_x, text_y))

    # Кнопка "ВЫЙТИ"
    if exit_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, exit_rect)
        exit_text = game.font_medium.render("ВЫЙТИ", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, exit_rect)
        pygame.draw.rect(game.screen, GOLD, exit_rect, 2)
        exit_text = game.font_medium.render("ВЫЙТИ", True, WHITE)

    text_x = exit_rect.x + exit_rect.width // 2 - exit_text.get_width() // 2
    text_y = exit_rect.y + exit_rect.height // 2 - exit_text.get_height() // 2
    game.screen.blit(exit_text, (text_x, text_y))

    # Кнопка "ОТМЕНА"
    if cancel_rect.collidepoint(mouse_pos):
        pygame.draw.rect(game.screen, GOLD, cancel_rect)
        cancel_text = game.font_medium.render("ОТМЕНА", True, BLACK)
    else:
        pygame.draw.rect(game.screen, DARK_RED, cancel_rect)
        pygame.draw.rect(game.screen, GOLD, cancel_rect, 2)
        cancel_text = game.font_medium.render("ОТМЕНА", True, WHITE)

    text_x = cancel_rect.x + cancel_rect.width // 2 - cancel_text.get_width() // 2
    text_y = cancel_rect.y + cancel_rect.height // 2 - cancel_text.get_height() // 2
    game.screen.blit(cancel_text, (text_x, text_y))

    pygame.display.flip()

    # Ожидание выбора
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if save_rect.collidepoint(event.pos):
                        show_save_menu_for_exit(game)  # Вызов сохранения
                        return True
                    elif exit_rect.collidepoint(event.pos):
                        return True
                    elif cancel_rect.collidepoint(event.pos):
                        return False
            elif event.type == pygame.MOUSEMOTION:
                # Вместо рекурсивного вызова себя (что приводило к утечке памяти),
                # просто выходим из цикла событий, чтобы перерисовать диалог заново
                return show_exit_dialog(game)

        game.clock.tick(FPS)