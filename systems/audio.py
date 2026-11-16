import pygame
import os
import random


class MusicManager:
    def __init__(self, музыка_локаций, громкость=0.3, включена=True):
        self.музыка_локаций = музыка_локаций
        self.громкость = громкость
        self.музыка_включена = включена

        self.текущая_музыка = None
        self.текущий_плейлист = []
        self.индекс_в_плейлисте = 0

    def загрузить_музыку(self, файл):
        """Загружает и воспроизводит музыку"""
        if not self.музыка_включена:
            return

        if not os.path.exists(файл):
            print(f"⚠️ Файл не найден: {файл}")
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(файл)
            pygame.mixer.music.set_volume(self.громкость)
            pygame.mixer.music.play(-1)
            self.текущая_музыка = файл
            print(f"🎵 Музыка: {файл.split('/')[-1]}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки музыки: {e}")

    def переключить_плейлист(self, локация, игра_загружена=False):
        """Переключает на новый плейлист локации"""
        # Флаг игра_загружена передается извне, чтобы не играть музыку меню в игре
        if локация == "меню" and игра_загружена:
            return

        if not self.есть_музыка(локация):
            return

        плейлист = self.музыка_локаций[локация]
        self.текущий_плейлист = плейлист.copy()
        random.shuffle(self.текущий_плейлист)
        self.индекс_в_плейлисте = 0
        self.играть_следующий_трек()

    def играть_следующий_трек(self):
        """Играет следующий трек из плейлиста"""
        if not self.текущий_плейлист:
            return

        while self.индекс_в_плейлисте < len(self.текущий_плейлист):
            файл = self.текущий_плейлист[self.индекс_в_плейлисте]
            if os.path.exists(файл):
                self.загрузить_музыку(файл)
                self.индекс_в_плейлисте += 1
                return
            else:
                print(f"⚠️ Пропускаем: {файл}")
                self.индекс_в_плейлисте += 1

        if self.индекс_в_плейлисте >= len(self.текущий_плейлист):
            random.shuffle(self.текущий_плейлист)
            self.индекс_в_плейлисте = 0
            self.играть_следующий_трек()

    def переключить_музыку(self):
        """Включает/выключает музыку"""
        self.музыка_включена = not self.музыка_включена
        if self.музыка_включена:
            pygame.mixer.music.unpause()
            print("🎵 Музыка включена")
        else:
            pygame.mixer.music.pause()
            print("🔇 Музыка выключена")

    def остановить_музыку(self):
        """Останавливает музыку"""
        try:
            pygame.mixer.music.stop()
            self.текущая_музыка = None
            print("🔇 Музыка остановлена")
        except Exception as e:
            print(f"⚠️ Ошибка остановки музыки: {e}")

    def есть_музыка(self, локация):
        """Проверяет, есть ли музыка для локации"""
        if локация not in self.музыка_локаций:
            return False

        плейлист = self.музыка_локаций[локация]
        if not плейлист:
            return False

        for файл in плейлист:
            if os.path.exists(файл):
                return True
        return False