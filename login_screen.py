# login_screen.py
import pygame
import sys
from game_api import GameAPI

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (70, 130, 180)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

class LoginScreen:
    def __init__(self, width=400, height=300, api=None):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Вход в игру")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)

        # Используем переданный API или создаём новый
        self.api = api if api else GameAPI()  # ← ОСТАВЛЯЕМ ТОЛЬКО ЭТО

        # Поля ввода
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.message_color = WHITE

        # Кнопки
        self.login_button = pygame.Rect(100, 220, 80, 40)
        self.register_button = pygame.Rect(220, 220, 100, 40)

        self.token = None
        self.logged_in = False

    def draw_text(self, text, x, y, color=WHITE, font=None):
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_input(self, label, value, x, y, active):
        # Подпись
        self.draw_text(label, x, y - 30, WHITE, self.small_font)
        # Поле ввода
        rect = pygame.Rect(x, y, 280, 35)
        color = BLUE if active else GRAY
        pygame.draw.rect(self.screen, color, rect, 2)
        # Текст
        display_text = value if value else " "
        self.draw_text(display_text, x + 10, y + 5, WHITE)

    def draw_button(self, rect, text, color=BLUE):
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 2)
        self.draw_text(text, rect.x + 10, rect.y + 10, WHITE, self.small_font)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Клик по полям ввода
                if 70 <= event.pos[0] <= 350:
                    if 80 <= event.pos[1] <= 115:
                        self.active_field = "username"
                    elif 150 <= event.pos[1] <= 185:
                        self.active_field = "password"

                # Клик по кнопкам
                if self.login_button.collidepoint(event.pos):
                    self.try_login()
                if self.register_button.collidepoint(event.pos):
                    self.try_register()

            if event.type == pygame.KEYDOWN:
                if self.active_field == "username":
                    if event.key == pygame.K_RETURN:
                        self.active_field = "password"
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    else:
                        self.username += event.unicode
                elif self.active_field == "password":
                    if event.key == pygame.K_RETURN:
                        self.try_login()
                    elif event.key == pygame.K_BACKSPACE:
                        self.password = self.password[:-1]
                    else:
                        self.password += event.unicode

    def try_login(self):
        if not self.username or not self.password:
            self.message = "Заполните все поля"
            self.message_color = RED
            return

        if self.api.login(self.username, self.password):
            self.token = self.api.token
            self.logged_in = True
            self.message = "Вход выполнен! Запуск игры..."
            self.message_color = GREEN
            pygame.display.flip()
            pygame.time.wait(500)
        else:
            self.message = "Неверный логин или пароль"
            self.message_color = RED

    def try_register(self):
        if not self.username or not self.password:
            self.message = "Заполните все поля"
            self.message_color = RED
            return

        # Простой email для регистрации (можно заменить на реальный ввод)
        email = f"{self.username}@game.com"
        if self.api.register(self.username, email, self.password):
            self.message = "Аккаунт создан! Войдите."
            self.message_color = GREEN
            # Очищаем пароль после регистрации
            self.password = ""
        else:
            self.message = "Ошибка регистрации"
            self.message_color = RED

    def render(self):
        self.screen.fill(BLACK)

        # Заголовок
        self.draw_text("Вход в игру", 120, 15, WHITE)

        # Поля ввода
        self.draw_input("Логин:", self.username, 70, 80, self.active_field == "username")
        self.draw_input("Пароль:", "*" * len(self.password), 70, 150, self.active_field == "password")

        # Кнопки
        self.draw_button(self.login_button, "Войти")
        self.draw_button(self.register_button, "Регистрация")

        # Сообщение
        if self.message:
            self.draw_text(self.message, 70, 270, self.message_color, self.small_font)

        pygame.display.flip()

    def run(self):
        while not self.logged_in:
            self.handle_events()
            self.render()
            self.clock.tick(60)

        return self.token