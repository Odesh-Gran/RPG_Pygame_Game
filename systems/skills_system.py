from loaders.skill_loader import SkillLoader

def upgrade_skill(game, skill_key):
    """Прокачка профессионального навыка"""
    current_value = game.игрок.get(skill_key, 0)
    max_value = 10

    if current_value >= max_value:
        game.add_to_log("Навык достиг максимума!")
        return False

    if game.игрок.get("очки_умений", 0) <= 0:
        game.add_to_log("Нет очков умений!")
        return False

    game.игрок[skill_key] = current_value + 1
    game.игрок["очки_умений"] -= 1

    game.add_to_log(f"Навык {skill_key} повышен до {game.игрок[skill_key]}!")
    return True


def learn_skill(game, skill_id):
    """Изучение нового навыка"""
    print(f"\n📚 LEARN_SKILL вызвана! skill_id: {skill_id}")

    skill = SkillLoader.get_skill_by_id(game.skills_data, skill_id)
    if not skill:
        game.add_to_log(f"❌ Навык {skill_id} не найден!")
        return

    print(f"   Название: {skill.get('название')}")
    print(f"   Тип: {skill.get('тип')}")
    print(f"   Эффект: {skill.get('эффект')}")
    print(f"   Значение: {skill.get('значение')}")

    if skill_id in game.игрок.get("выученные_навыки", []):
        game.add_to_log(f"❌ Уже выучено!")
        return

    if game.игрок.get("очки_навыков", 0) <= 0:
        game.add_to_log(f"❌ Нет очков навыков!")
        return

    if "выученные_навыки" not in game.игрок:
        game.игрок["выученные_навыки"] = []

    game.игрок["выученные_навыки"].append(skill_id)
    game.игрок["очки_навыков"] -= 1
    game.add_to_log(f"✅ Выучен навык: {skill['название']}!")

    # ===== ПРИМЕНЯЕМ ЭФФЕКТ НАВЫКА (ЕСЛИ ПАССИВНЫЙ) =====
    if skill["тип"] == "пассивный":
        print(f"   → Применяем пассивный навык!")

        # ИСПОЛЬЗУЕМ СУЩЕСТВУЮЩУЮ ФУНКЦИЮ из player.py
        from entities.player import игрок as глобальный_игрок, добавить_пассивный_бонус

        # Синхронизация
        глобальный_игрок.update(game.игрок)

        # Применяем эффект
        эффект = skill.get('эффект', '')
        значение = skill.get('значение', 0)

        if эффект:
            добавить_пассивный_бонус(эффект, значение)
            print(f"   ✅ Применён бонус: {эффект} +{значение}")

            # Обновляем здоровье если нужно
            if эффект in ['здоровье', 'hp_bonus', 'стойкость', 'endurance_bonus']:
                game.inventory.update_max_health()
        else:
            print(f"   ⚠️ У навыка нет эффекта!")

        # Синхронизация обратно
        game.игрок.update(глобальный_игрок)

    else:
        print(f"   → Навык НЕ пассивный (тип: {skill['тип']})")