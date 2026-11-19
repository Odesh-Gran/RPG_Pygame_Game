def show_loot_panel(game, items, exp, rare_item=None):
    """Показывает выезжающую панель с лутом"""
    game.loot_panel_active = True
    game.loot_items = items.copy()
    game.loot_exp = exp
    game.loot_rare_item = rare_item
    game.loot_animation_progress = 0
    print(f"📦 Панель лута открыта: {items}, опыт: {exp}")

def close_loot_panel(game):
    """Закрывает панель лута и добавляет предметы в инвентарь"""
    print(f"\n📦 close_loot_panel вызвана!")
    print(f"   loot_items: {game.loot_items}")
    print(f"   loot_exp: {game.loot_exp}")

    for item in game.loot_items:
        game.inventory.add_item(item)
        game.add_to_log(f"Получен: {item}")

    if game.loot_rare_item:
        game.inventory.add_item(game.loot_rare_item)
        game.add_to_log(f"РЕДКИЙ ДРОП: {game.loot_rare_item}!")

    from entities.player import игрок as глобальный_игрок, изменить_уровень

    глобальный_игрок.update(game.игрок)
    глобальный_игрок["опыт"] += game.loot_exp
    game.add_to_log(f"+{game.loot_exp} опыта")

    изменить_уровень()
    game.игрок.update(глобальный_игрок)

    game.loot_panel_active = False
    game.loot_items = []
    game.loot_exp = 0
    game.loot_rare_item = None
    game.loot_animation_progress = 0
    print(f"   Панель лута закрыта!")