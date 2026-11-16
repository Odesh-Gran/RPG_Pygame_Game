import os
from pyvidplayer2 import Video


class VideoManager:
    def __init__(self):
        self.transition_video = None
        self.next_location = None
        self.video_transition_active = False

    def play_transition_video(self, game, video_path, target_location):
        """Запускает видео-переход. game передается для доступа к музыке, режиму и т.д."""
        try:
            print(f"🎬 play_transition_video: {video_path} -> {target_location}")
            game.music.остановить_музыку()

            print(f"🎬 Загрузка видео: {video_path}")
            self.transition_video = Video(video_path)
            self.transition_video.play()
            self.next_location = target_location
            self.video_transition_active = True
            game.режим = "видео_переход"
            print(f"▶️ Видео воспроизводится, переход к {target_location}")
            print(f"📍 РЕЖИМ УСТАНОВЛЕН: {game.режим}")
        except Exception as e:
            print(f"❌ Ошибка загрузки видео: {e}")
            game.текущая_локация = target_location
            game.show_description = True
            game.description_timer = 0
            game.режим = "игра"

            # Включаем музыку сразу при ошибке
            if game.текущая_локация != "меню" and game.music.есть_музыка(game.текущая_локация):
                game.music.переключить_плейлист(game.текущая_локация, game.игра_загружена)
            else:
                game.music.остановить_музыку()

    def update_transition_video(self, game):
        """Обновляет состояние видео-перехода. Вызывается из игрового цикла."""
        if game.режим != "видео_переход":
            return

        if self.transition_video is None:
            game.режим = "игра"
            return

        if not self.transition_video.active:
            print("🎬 ВИДЕО ЗАВЕРШЕНО! Обновляем квесты...")
            game.текущая_локация = self.next_location
            game.show_description = True
            game.description_timer = 0

            # Импортируем время здесь, чтобы не было циклических импортов
            from systems import time_system as время
            время.пройти_время(5)

            self.transition_video.close()
            self.transition_video = None
            self.video_transition_active = False
            game.режим = "игра"

            # Обновляем ежедневные квесты
            print(f"   📍 Текущая локация: {game.текущая_локация}")
            if hasattr(game, 'quest_system') and hasattr(game, 'игрок'):
                if "ежедневные_квесты" in game.игрок:
                    print(f"   🔄 ВЫЗЫВАЕМ обновить_ежедневный_прогресс(посетить, {game.текущая_локация})")
                    завершенные = game.quest_system.обновить_ежедневный_прогресс(
                        game.игрок,
                        "посетить",
                        game.текущая_локация
                    )
                    print(f"   📊 Результат: {завершенные}")
                    if завершенные:
                        for квест_id in завершенные:
                            for q in game.quest_system.ежедневные_квесты:
                                if q.get("id") == квест_id:
                                    game.add_to_log(f"📅 Ежедневный квест выполнен: {q['название']}")
                                    break
                else:
                    print("   ❌ Нет ежедневные_квесты в игроке!")
            else:
                print("   ❌ Нет quest_system или игрока!")

            # Включаем музыку
            if game.текущая_локация != "меню" and game.music.есть_музыка(game.текущая_локация):
                game.music.переключить_плейлист(game.текущая_локация, game.игра_загружена)
            else:
                game.music.остановить_музыку()

            print(f"🗺️ Видео-переход завершён: {game.текущая_локация}")
            return

        try:
            self.transition_video.draw(game.screen, (0, 0), force_draw=True)
        except Exception as e:
            print(f"⚠️ Ошибка отрисовки видео: {e}")