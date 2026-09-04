import os
import json
import время
import pygame
import барьеры  # 👈 ДОБАВЛЯЕМ ИМПОРТ

# Папка для сохранений
SAVE_DIR = "saves"
MAX_SAVES = 5


def ensure_save_dir():
    """Создаёт папку для сохранений если её нет"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
        print(f"📁 Создана папка {SAVE_DIR}")


def get_save_info(slot):
    """Получает информацию о сохранении в слоте"""
    ensure_save_dir()
    save_file = f"{SAVE_DIR}/save_{slot}.json"

    if not os.path.exists(save_file):
        return None

    try:
        with open(save_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "slot": slot,
                "day": data.get("день", 1),
                "time": data.get("время_суток", "утро"),
                "location": data.get("локация", "Холл"),
                "level": data.get("уровень", 1),
                "class": data.get("класс", "Воин"),
                "timestamp": data.get("timestamp", 0)
            }
    except Exception as e:
        print(f"⚠️ Ошибка чтения слота {slot}: {e}")
        return None


def list_saves():
    """Возвращает список всех сохранений"""
    saves = []
    for slot in range(1, MAX_SAVES + 1):
        info = get_save_info(slot)
        if info:
            saves.append(info)
    return saves


def сохранить_игру(игрок, локация, chest_inventory, slot):
    """Сохраняет игру в указанный слот"""
    try:
        ensure_save_dir()

        # ===== СИНХРОНИЗАЦИЯ ВСЕХ ПОЛЕЙ =====
        обязательные_поля = {
            "пассивные_бонусы": {},
            "выученные_навыки": [],
            "очки_навыков": 0,
            "очки_умений": 0,
            "сила_бонус": 0,
            "здоровье_бонус": 0,
            "стойкость_бонус": 0,
            "защита_бонус": 0,
            "вампиризм": False,
            "амулет": None,
            "броня": None,
            "counter_chance": 0,
            "revive_hp": 0,
            "оружие": None,
            "инвентарь": [],
            "монета": 0,
        }

        for поле, значение_по_умолчанию in обязательные_поля.items():
            if поле not in игрок:
                игрок[поле] = значение_по_умолчанию
                print(f"🔧 Добавлено поле '{поле}' при сохранении")
        # =========================================

        данные = {
            "slot": slot,
            "игрок": игрок,
            "локация": локация,
            "chest_inventory": chest_inventory,
            "день": время.получить_день(),
            "время_суток": время.получить_время_суток(),
            "уровень": игрок.get("уровень", 1),
            "класс": игрок.get("класс", "Неизвестно"),
            "timestamp": pygame.time.get_ticks(),
            # ===== ДОБАВЛЯЕМ БАРЬЕРЫ В СЕЙВ =====
            "открытые_барьеры": list(барьеры.открытые_барьеры)
            # =====================================
        }

        save_path = f"{SAVE_DIR}/save_{slot}.json"
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(данные, f, ensure_ascii=False, indent=2)

        print(f"💾 Игра сохранена в слот {slot} -> {save_path}")
        print(f"   🔓 Барьеров сохранено: {len(барьеры.открытые_барьеры)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        import traceback
        traceback.print_exc()
        return False


def загрузить_игру(slot):
    """Загружает игру из указанного слота"""
    try:
        save_path = f"{SAVE_DIR}/save_{slot}.json"

        if not os.path.exists(save_path):
            print(f"❌ Файл {save_path} не найден!")
            return None, None, None

        with open(save_path, 'r', encoding='utf-8') as f:
            данные = json.load(f)

            игрок = данные.get("игрок", {})

            # ===== СИНХРОНИЗАЦИЯ ВСЕХ ПОЛЕЙ =====
            обязательные_поля = {
                "пассивные_бонусы": {},
                "выученные_навыки": [],
                "очки_навыков": 0,
                "очки_умений": 0,
                "сила_бонус": 0,
                "здоровье_бонус": 0,
                "стойкость_бонус": 0,
                "защита_бонус": 0,
                "вампиризм": False,
                "амулет": None,
                "броня": None,
                "counter_chance": 0,
                "revive_hp": 0,
                "оружие": None,
                "инвентарь": [],
                "монета": 0,
            }

            for поле, значение_по_умолчанию in обязательные_поля.items():
                if поле not in игрок:
                    игрок[поле] = значение_по_умолчанию
                    print(f"🔧 Добавлено поле '{поле}' при загрузке")
            # =========================================

            локация = данные.get("локация", "Холл")
            chest_inventory = данные.get("chest_inventory", [])

            # ===== ЗАГРУЖАЕМ БАРЬЕРЫ ИЗ СЕЙВА =====
            открытые_барьеры = данные.get("открытые_барьеры", [])
            барьеры.открытые_барьеры = set(открытые_барьеры)
            print(f"🔓 Загружено барьеров: {len(открытые_барьеры)}")
            if открытые_барьеры:
                print(f"   📋 Барьеры: {', '.join(открытые_барьеры)}")
            # =======================================

            print(f"✅ Загружена игра из слота {slot}")
            return игрок, локация, chest_inventory
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def есть_сохранение():
    """Проверяет наличие хотя бы одного сохранения"""
    return len(list_saves()) > 0