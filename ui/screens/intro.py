import pygame
from config import WIDTH, HEIGHT, BLACK, WHITE, GRAY, FPS

def show_intro(game):
    """Показывает вступительную заставку с историей"""

    # Затемняем экран
    game.screen.fill(BLACK)

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
                pygame.draw.rect(game.screen, BLACK, clear_rect)

                game.screen.blit(text_surface, text_rect)
                pygame.display.flip()

                # Задержка
                game.clock.tick(30)

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
                    game.clock.tick(60)
        else:
            # Пустая строка
            pass

    # Если пропустили анимацию - показываем весь текст сразу
    if skip_animation:
        # Полностью очищаем экран
        game.screen.fill(BLACK)

        # Рисуем все строки целиком
        for i, line in enumerate(intro_text):
            if line:
                text_surface = font_intro.render(line, True, WHITE)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset + i * line_height))
                game.screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Небольшая пауза, чтобы игрок увидел текст
        pause_until = pygame.time.get_ticks() + 500
        while pygame.time.get_ticks() < pause_until:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            game.clock.tick(60)

    # Ждём нажатия любой клавиши или клика
    waiting = True
    skip_text = game.font_small.render("Нажми любую клавишу или кликни, чтобы продолжить...", True, GRAY)
    skip_rect = skip_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
    game.screen.blit(skip_text, skip_rect)
    pygame.display.flip()

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                break
        game.clock.tick(FPS)

    return True