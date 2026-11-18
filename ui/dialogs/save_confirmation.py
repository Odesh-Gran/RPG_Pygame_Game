import pygame
from config import WIDTH, HEIGHT, DARK_BLUE, GOLD, DARK_RED, BLACK, WHITE, FPS
import sys


def show_save_confirmation(game, slot):
    """Показывает подтверждение сохранения. Возвращает True если сохранено, иначе False."""

    from loaders import save_manager as сохранение  # Импорт внутри функции, чтобы избежать циклических зависимостей

    while True:
        # Затемнение фона
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        game.screen.blit(s, (0, 0))

        # Панель подтверждения
        panel_width = 400
        panel_height = 200
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2

        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(game.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(game.screen, GOLD, panel_rect, 3)

        # Текст
        title = game.font_medium.render("ПОДТВЕРЖДЕНИЕ", True, GOLD)
        title_x = panel_x + panel_width // 2 - title.get_width() // 2
        game.screen.blit(title, (title_x, panel_y + 20))

        question = game.font_small.render(f"Сохранить игру в слот {slot}?", True, WHITE)
        question_x = panel_x + panel_width // 2 - question.get_width() // 2
        game.screen.blit(question, (question_x, panel_y + 70))

        # Кнопки
        yes_rect = pygame.Rect(panel_x + 70, panel_y + 120, 100, 40)
        no_rect = pygame.Rect(panel_x + panel_width - 170, panel_y + 120, 100, 40)

        mouse_pos = pygame.mouse.get_pos()

        # Кнопка ДА
        if yes_rect.collidepoint(mouse_pos):
            pygame.draw.rect(game.screen, GOLD, yes_rect)
            yes_text = game.font_medium.render("ДА", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, yes_rect)
            pygame.draw.rect(game.screen, GOLD, yes_rect, 2)
            yes_text = game.font_medium.render("ДА", True, WHITE)

        text_x = yes_rect.x + yes_rect.width // 2 - yes_text.get_width() // 2
        text_y = yes_rect.y + yes_rect.height // 2 - yes_text.get_height() // 2
        game.screen.blit(yes_text, (text_x, text_y))

        # Кнопка НЕТ
        if no_rect.collidepoint(mouse_pos):
            pygame.draw.rect(game.screen, GOLD, no_rect)
            no_text = game.font_medium.render("НЕТ", True, BLACK)
        else:
            pygame.draw.rect(game.screen, DARK_RED, no_rect)
            pygame.draw.rect(game.screen, GOLD, no_rect, 2)
            no_text = game.font_medium.render("НЕТ", True, WHITE)

        text_x = no_rect.x + no_rect.width // 2 - no_text.get_width() // 2
        text_y = no_rect.y + no_rect.height // 2 - no_text.get_height() // 2
        game.screen.blit(no_text, (text_x, text_y))

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
                        сохранение.сохранить_игру(game.игрок, game.текущая_локация, game.chest_inventory, slot)
                        game.add_to_log(f"Игра сохранена в слот {slot}!")
                        return True
                    elif no_rect.collidepoint(event.pos):
                        return False

        game.clock.tick(FPS)