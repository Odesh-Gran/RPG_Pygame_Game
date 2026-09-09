# game_api.py
import requests
import json
import os

class GameAPI:
    def __init__(self, base_url="http://194.226.122.252:8000/api/v1"):
        self.base_url = base_url
        self.token = None
        self.token_file = "token.json"

    def set_token(self, token):
        self.token = token
        with open(self.token_file, "w") as f:
            json.dump({"token": token}, f)

    def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                data = json.load(f)
                self.token = data.get("token")
                return self.token
        return None

    def login(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.set_token(data["access_token"])
                return True
            else:
                print("❌ Ошибка входа:", response.json().get("detail", "Неизвестная ошибка"))
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Не удалось подключиться к серверу. Запущен ли бэкенд?")
            return False

    def register(self, username, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 201:
                print("✅ Аккаунт создан! Теперь войдите.")
                return True
            else:
                print("❌ Ошибка регистрации:", response.json().get("detail", "Неизвестная ошибка"))
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Не удалось подключиться к серверу.")
            return False

    def save_achievement(self, name, description=""):
        if not self.token:
            print("❌ Нет токена. Войдите в систему.")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/achievements",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"name": name, "description": description}
            )
            if response.status_code == 201:
                print(f"🏆 Достижение '{name}' сохранено!")
                return True
            else:
                print("❌ Ошибка сохранения:", response.json().get("detail", "Неизвестная ошибка"))
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Не удалось подключиться к серверу.")
            return False

    def get_achievements(self):
        if not self.token:
            print("❌ Нет токена. Войдите в систему.")
            return []

        try:
            response = requests.get(
                f"{self.base_url}/achievements",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print("❌ Ошибка получения достижений:", response.json().get("detail", "Неизвестная ошибка"))
                return []
        except requests.exceptions.ConnectionError:
            print("❌ Не удалось подключиться к серверу.")
            return []