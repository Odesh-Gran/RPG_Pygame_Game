# login_screen.py
import pygame
import sys
import os
import json
import base64
import webbrowser
from game_api import GameAPI

# Цвета
WHITE = (255, 255, 255)
BLACK = (20, 22, 30)
BG_DARK = (28, 32, 45)
BG_PANEL = (38, 43, 60)
FIELD_BG = (48, 54, 75)
FIELD_ACTIVE = (60, 68, 95)
ACCENT = (90, 150, 230)
ACCENT_HOVER = (110, 170, 250)
GREEN = (80, 200, 120)
RED = (230, 90, 90)
GRAY = (140, 145, 160)
DARK_GRAY = (100, 105, 120)
SHADOW = (10, 12, 18)
CLOSE_HOVER = (230, 90, 90)

REMEMBER_FILE = "remembered_account.json"
REGISTER_URL = "https://castle-survival.ru/"


class LoginScreen:
    def __init__(self, width=800, height=600, api=None):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Castle Survival — Вход")
        try:
            icon = pygame.image.load("assets/icon.png").convert_alpha()
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить иконку: {e}")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 20)

        self.api = api if api else GameAPI()

        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.message_color = WHITE

        self.remember = False
        self._load_remembered()

        # Панель по центру
        panel_w, panel_h = 520, 440
        self.panel_rect = pygame.Rect(
            (width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h
        )
        px, py = self.panel_rect.x, self.panel_rect.y

        self.username_rect = pygame.Rect(px + 70, py + 120, 380, 50)
        self.password_rect = pygame.Rect(px + 70, py + 210, 380, 50)
        self.checkbox_rect = pygame.Rect(px + 70, py + 285, 28, 28)
        self.login_button = pygame.Rect(px + 70, py + 335, 175, 55)
        self.register_button = pygame.Rect(px + 275, py + 335, 175, 55)

        # Кнопка закрытия (крестик) в правом верхнем углу панели
        self.close_button = pygame.Rect(
            self.panel_rect.right - 48, self.panel_rect.y + 12, 36, 36
        )

        self.token = None
        self.logged_in = False
        self.closed = False

        self.cursor_visible = True
        self.cursor_timer = 0

    # ---------------------- Сохранение аккаунта ----------------------
    def _load_remembered(self):
        if os.path.exists(REMEMBER_FILE):
            try:
                with open(REMEMBER_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.username = data.get("username", "")
                enc = data.get("password", "")
                if enc:
                    self.password = base64.b64decode(enc.encode()).decode()
                self.remember = True
            except Exception:
                pass

    def _save_remembered(self):
        try:
            enc = base64.b64encode(self.password.encode()).decode()
            with open(REMEMBER_FILE, "w", encoding="utf-8") as f:
                json.dump({"username": self.username, "password": enc}, f)
        except Exception:
            pass

    def _clear_remembered(self):
        try:
            if os.path.exists(REMEMBER_FILE):
                os.remove(REMEMBER_FILE)
        except Exception:
            pass

    # ---------------------- Отрисовка ----------------------
    def draw_text(self, text, x, y, color=WHITE, font=None, center=False):
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        if center:
            rect = surface.get_rect(center=(x, y))
            self.screen.blit(surface, rect)
        else:
            self.screen.blit(surface, (x, y))

    def draw_input(self, label, value, rect, active, placeholder=""):
        self.draw_text(label, rect.x, rect.y - 32, GRAY, self.small_font)
        bg_color = FIELD_ACTIVE if active else FIELD_BG
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=10)
        border_color = ACCENT if active else DARK_GRAY
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)

        display = value if value else placeholder
        text_color = WHITE if value else GRAY
        self.draw_text(display, rect.x + 15, rect.y + 13, text_color, self.font)

        if active and self.cursor_visible:
            cursor_x = rect.x + 15 + (self.small_font.size(display)[0] if value else 0) + 2
            pygame.draw.line(
                self.screen, WHITE,
                (cursor_x, rect.y + 12),
                (cursor_x, rect.y + rect.height - 12),
                2,
            )

    def draw_button(self, rect, text, hovered, color=ACCENT):
        c = ACCENT_HOVER if hovered else color
        shadow = rect.move(0, 3)
        pygame.draw.rect(self.screen, SHADOW, shadow, border_radius=10)
        pygame.draw.rect(self.screen, c, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 1, border_radius=10)
        self.draw_text(text, rect.centerx, rect.centery, WHITE, self.small_font, center=True)

    def draw_checkbox(self):
        pygame.draw.rect(self.screen, FIELD_BG, self.checkbox_rect, border_radius=6)
        pygame.draw.rect(
            self.screen, ACCENT if self.remember else DARK_GRAY,
            self.checkbox_rect, 2, border_radius=6,
        )
        if self.remember:
            cx, cy = self.checkbox_rect.center
            pts = [(cx - 8, cy), (cx - 2, cy + 7), (cx + 9, cy - 7)]
            pygame.draw.lines(self.screen, GREEN, False, pts, 3)
        self.draw_text(
            "Запомнить аккаунт",
            self.checkbox_rect.right + 12,
            self.checkbox_rect.y + 4,
            WHITE, self.small_font,
        )

    def draw_close_button(self, hovered):
        c = CLOSE_HOVER if hovered else FIELD_BG
        pygame.draw.rect(self.screen, c, self.close_button, border_radius=8)
        pygame.draw.rect(self.screen, DARK_GRAY, self.close_button, 1, border_radius=8)
        # Крестик
        x, y, s = self.close_button.x, self.close_button.y, self.close_button.width
        pad = 10
        pygame.draw.line(self.screen, WHITE,
                         (x + pad, y + pad), (x + s - pad, y + s - pad), 3)
        pygame.draw.line(self.screen, WHITE,
                         (x + s - pad, y + pad), (x + pad, y + s - pad), 3)

    def render(self):
        self.screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        shadow = self.panel_rect.move(0, 6)
        pygame.draw.rect(self.screen, SHADOW, shadow, border_radius=20)
        pygame.draw.rect(self.screen, BG_PANEL, self.panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, DARK_GRAY, self.panel_rect, 2, border_radius=20)

        self.draw_text(
            "Вход в игру",
            self.panel_rect.centerx,
            self.panel_rect.y + 45,
            WHITE, self.title_font, center=True,
        )

        self.draw_input(
            "Логин:", self.username, self.username_rect,
            self.active_field == "username", placeholder="Введите логин",
        )
        self.draw_input(
            "Пароль:", "*" * len(self.password), self.password_rect,
            self.active_field == "password", placeholder="Введите пароль",
        )

        self.draw_checkbox()

        self.draw_button(self.login_button, "Войти",
                         self.login_button.collidepoint(mouse_pos), ACCENT)
        self.draw_button(self.register_button, "Регистрация",
                         self.register_button.collidepoint(mouse_pos), (120, 100, 200))

        self.draw_close_button(self.close_button.collidepoint(mouse_pos))

        if self.message:
            self.draw_text(
                self.message,
                self.panel_rect.centerx,
                self.panel_rect.bottom - 30,
                self.message_color, self.small_font, center=True,
            )

        pygame.display.flip()

    # ---------------------- Закрытие ----------------------
    def close(self):
        self.closed = True
        self.logged_in = False

    # ---------------------- События ----------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.close()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.close_button.collidepoint(event.pos):
                    self.close()
                    return

                if self.username_rect.collidepoint(event.pos):
                    self.active_field = "username"
                elif self.password_rect.collidepoint(event.pos):
                    self.active_field = "password"
                elif self.checkbox_rect.collidepoint(event.pos):
                    self.remember = not self.remember
                    if not self.remember:
                        self._clear_remembered()

                if self.login_button.collidepoint(event.pos):
                    self.try_login()
                if self.register_button.collidepoint(event.pos):
                    self.try_register()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.active_field = (
                        "password" if self.active_field == "username" else "username"
                    )
                elif self.active_field == "username":
                    if event.key == pygame.K_RETURN:
                        self.active_field = "password"
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.unicode.isprintable():
                        self.username += event.unicode
                elif self.active_field == "password":
                    if event.key == pygame.K_RETURN:
                        self.try_login()
                    elif event.key == pygame.K_BACKSPACE:
                        self.password = self.password[:-1]
                    elif event.unicode.isprintable():
                        self.password += event.unicode

    # ---------------------- Логика ----------------------
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

            if self.remember:
                self._save_remembered()
            else:
                self._clear_remembered()

            self.render()
            pygame.time.wait(500)
        else:
            self.message = "Неверный логин или пароль"
            self.message_color = RED

    def try_register(self):
        # Регистрация — открываем сайт в браузере
        try:
            webbrowser.open(REGISTER_URL)
            self.message = "Открыт сайт регистрации"
            self.message_color = GREEN
        except Exception:
            self.message = f"Не удалось открыть {REGISTER_URL}"
            self.message_color = RED

    # ---------------------- Главный цикл ----------------------
    def run(self):
        while not self.logged_in and not self.closed:
            self.handle_events()
            self.cursor_timer += self.clock.tick(60)
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            if not self.closed:
                self.render()

        # Корректно завершаем pygame, если окно закрыто
        if self.closed:
            pygame.quit()
            return None

        return self.token


if __name__ == "__main__":
    screen = LoginScreen()
    token = screen.run()
    if token:
        print("Токен:", token)
    else:
        print("Вход отменён пользователем.")