from systems import time_system as время

def rest_in_hub(game):
    текущий_день = время.получить_день()
    if hasattr(game, 'last_rest_day') and game.last_rest_day == текущий_день:
        game.add_to_log("Ты уже отдыхал сегодня! Отдохнуть можно только раз в день.")
        print("❌ Отдых недоступен - уже отдыхал сегодня")
        return

    game.игрок["здоровье"] = game.игрок["макс_здоровье"]
    game.inventory.update_max_health()
    if "мана" in game.игрок:
        game.игрок["мана"] = game.игрок["макс_мана"]

    game.last_rest_day = текущий_день
    время.пройти_время(300)
    game.add_to_log("Ты отдохнул в убежище и полностью восстановил силы!")
    print(f"🛌 Игрок отдохнул в убежище. День отдыха: {текущий_день}")