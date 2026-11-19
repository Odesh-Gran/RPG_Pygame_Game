from systems import randomizer as рандомайзер
from systems import time_system as время
from entities import locations as локации
from systems.battle_system import start_battle_gui

def выполнить_обыск(game):
    print("🔍 ВЫПОЛНЯЕМ ОБЫСК")
    локация_данные = локации.локации[game.текущая_локация]
    событие = рандомайзер.выбрать_событие(локация_данные)

    if событие == "враг" and локация_данные.get("возможные_враги", []):
        враг = рандомайзер.выбрать_врага(локация_данные["возможные_враги"])
        game.add_to_log(f"Нападает: {враг.replace('_', ' ')}!")
        start_battle_gui(game, враг)

    elif событие == "предмет" and локация_данные.get("возможные_предметы", {}):
        предмет = рандомайзер.выбрать_предмет(локация_данные["возможные_предметы"])
        if предмет:
            game.inventory.add_item(предмет)
            game.add_to_log(f"Ты нашёл: {предмет}!")

            if hasattr(game, 'quest_system') and hasattr(game, 'игрок'):
                if "ежедневные_квесты" in game.игрок:
                    from entities import items as предметы
                    данные = предметы.предметы.get(предмет, {})
                    тип_предмета = данные.get("тип", "")

                    if тип_предмета == "ресурс":
                        завершенные = game.quest_system.обновить_ежедневный_прогресс(
                            game.игрок, "найти", предмет
                        )
                        if завершенные:
                            for квест_id in завершенные:
                                for q in game.quest_system.ежедневные_квесты:
                                    if q.get("id") == квест_id:
                                        game.add_to_log(f"📅 Ежедневный квест выполнен: {q['название']}")
                                        break
    else:
        game.add_to_log("Здесь ничего нет...")

    время.пройти_время(10)