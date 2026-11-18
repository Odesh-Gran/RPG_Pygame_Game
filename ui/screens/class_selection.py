import pygame
from config import WIDTH, HEIGHT, BLACK, GOLD, WHITE, BLOOD_RED, DARK_BLUE

def show_class_selection(game):
    """Меню выбора класса с кликами мышью. Возвращает название класса или None."""
    from systems import classes as классы

    clock = pygame.time.Clock()
    классы_список = ["Воин", "Маг", "Вор"]

    # Сохраняем области клика для каждого класса
    class_rects = []

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверяем клик по карточкам классов
                for i, rect in enumerate(class_rects):
                    if rect.collidepoint(mouse_pos):
                        print(f"✅ Выбран класс: {классы_список[i]}")
                        return классы_список[i]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

        # ОТРИСОВКА
        game.screen.fill(BLACK)

        # Заголовок
        title = game.font_large.render("ВЫБЕРИ КЛАСС", True, GOLD)
        game.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Очищаем список областей клика
        class_rects = []

        # Рисуем карточки классов
        for i, название in enumerate(классы_список):
            x = 200 + i * 300
            y = 150
            width = 250
            height = 420

            # Создаём область для клика
            class_rect = pygame.Rect(x, y, width, height)
            class_rects.append(class_rect)

            # Проверяем наведение мыши
            if class_rect.collidepoint(mouse_pos):
                # Подсветка при наведении
                pygame.draw.rect(game.screen, GOLD, (x - 5, y - 5, width + 10, height + 10), 4)

            # Фон карточки
            color = классы.классы[название]["цвет"]
            pygame.draw.rect(game.screen, color, (x, y, width, height))
            pygame.draw.rect(game.screen, GOLD, (x, y, width, height), 2)

            # Название
            class_name = game.font_medium.render(название, True, GOLD)
            game.screen.blit(class_name, (x + width // 2 - class_name.get_width() // 2, y + 15))

            # Описание
            описание = классы.классы[название]["описание"]
            desc_text = game.font_small.render(описание, True, WHITE)
            game.screen.blit(desc_text, (x + width // 2 - desc_text.get_width() // 2, y + 55))

            # Разделитель
            pygame.draw.line(game.screen, GOLD, (x + 20, y + 85), (x + width - 20, y + 85), 1)

            # АТРИБУТЫ
            атрибуты = классы.классы[название]["начальные_атрибуты"]
            attr_y = y + 100
            for атр, знач in атрибуты.items():
                # Название атрибута
                атр_текст = game.font_tiny.render(атр.capitalize() + ":", True, WHITE)
                game.screen.blit(атр_текст, (x + 30, attr_y))

                # Значение
                знач_текст = game.font_tiny.render(f"+{знач}", True, WHITE)
                game.screen.blit(знач_текст, (x + 120, attr_y))

                attr_y += 20

            # Стартовое оружие
            оружие = классы.классы[название]["стартовое_оружие"]
            оружие_текст = game.font_tiny.render(f"{оружие}", True, BLOOD_RED)
            game.screen.blit(оружие_текст, (x + 30, attr_y + 5))

            # Стартовая броня
            броня = классы.классы[название]["стартовая_броня"]
            броня_текст = game.font_tiny.render(f"{броня}", True, DARK_BLUE)
            game.screen.blit(броня_текст, (x + 30, attr_y + 30))

        # Управление
        instr = game.font_small.render("Кликни по классу мышкой | ESC - назад", True, WHITE)
        game.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()
        clock.tick(30)