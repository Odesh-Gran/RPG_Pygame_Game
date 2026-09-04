import json
import os


class SkillLoader:
    @staticmethod
    def load_skills(file_path="data/skills.json"):
        """Загружает навыки из JSON-файла"""
        # Получаем путь к файлу относительно расположения этого скрипта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, file_path)

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Загружено {len(data['ветки'])} веток навыков")
            return data
        except FileNotFoundError:
            print(f"❌ Файл {full_path} не найден!")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка в JSON: {e}")
            return None

    @staticmethod
    def get_skill_by_id(skills_data, skill_id):
        """Ищет навык по id во всех ветках"""
        if not skills_data:
            return None
        for branch_name, branch_data in skills_data["ветки"].items():
            for skill in branch_data["навыки"]:
                if skill["id"] == skill_id:
                    return skill
        return None

    @staticmethod
    def get_all_skills(skills_data):
        """Возвращает список всех навыков (плоский)"""
        if not skills_data:
            return []
        all_skills = []
        for branch_name, branch_data in skills_data["ветки"].items():
            for skill in branch_data["навыки"]:
                skill["ветка"] = branch_name  # добавляем информацию о ветке
                all_skills.append(skill)
        return all_skills