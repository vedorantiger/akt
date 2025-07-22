"""
Модуль для автоматичних розрахунків фізичних показників клієнта.
Всі обчислення виконуються в режимі реального часу.
"""

import math
from typing import Dict, Any, Optional


class FitnessCalculator:
    """Клас для автоматичних обчислень фітнес-показників"""
    
    @staticmethod
    def calculate_bmi(weight: Optional[float], height: Optional[float]) -> Optional[float]:
        """
        Розрахунок індексу маси тіла (BMI)
        BMI = вага(кг) / (зріст(м))²
        """
        if not weight or not height or weight <= 0 or height <= 0:
            return None
        
        height_m = height / 100  # Конвертуємо см в метри
        return round(weight / (height_m ** 2), 1)
    
    @staticmethod
    def get_bmi_category(bmi: Optional[float]) -> str:
        """Категорія BMI"""
        if not bmi:
            return "Не визначено"
        
        if bmi < 18.5:
            return "Недостатня вага"
        elif 18.5 <= bmi < 25:
            return "Нормальна вага"
        elif 25 <= bmi < 30:
            return "Надмірна вага"
        else:
            return "Ожиріння"
    
    @staticmethod
    def calculate_body_fat_percentage(
        weight: Optional[float], 
        height: Optional[float], 
        age: Optional[int], 
        gender: Optional[str]
    ) -> Optional[float]:
        """
        Розрахунок відсотка жиру в тілі за формулою Deurenberg
        """
        if not all([weight, height, age, gender]) or weight <= 0 or height <= 0 or age <= 0:
            return None
        
        bmi = FitnessCalculator.calculate_bmi(weight, height)
        if not bmi:
            return None
        
        # Формула Deurenberg
        if gender.lower() in ['чоловік', 'male', 'м']:
            body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
        else:  # жінка
            body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
        
        return max(0, round(body_fat, 1))
    
    @staticmethod
    def calculate_ideal_weight(height: Optional[float], gender: Optional[str]) -> Optional[float]:
        """
        Розрахунок ідеальної ваги за формулою Devine
        """
        if not height or not gender or height <= 0:
            return None
        
        height_inches = height / 2.54  # Конвертуємо см в дюйми
        
        if gender.lower() in ['чоловік', 'male', 'м']:
            # Чоловіки: 50 кг + 2.3 кг на кожен дюйм понад 5 футів
            ideal_weight = 50 + 2.3 * max(0, height_inches - 60)
        else:  # жінка
            # Жінки: 45.5 кг + 2.3 кг на кожен дюйм понад 5 футів
            ideal_weight = 45.5 + 2.3 * max(0, height_inches - 60)
        
        return round(ideal_weight, 1)
    
    @staticmethod
    def calculate_bmr(
        weight: Optional[float], 
        height: Optional[float], 
        age: Optional[int], 
        gender: Optional[str]
    ) -> Optional[float]:
        """
        Базальний метаболізм (BMR) за формулою Harris-Benedict
        """
        if not all([weight, height, age, gender]) or weight <= 0 or height <= 0 or age <= 0:
            return None
        
        if gender.lower() in ['чоловік', 'male', 'м']:
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:  # жінка
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return round(bmr, 0)
    
    @staticmethod
    def calculate_daily_calories(bmr: Optional[float], activity_level: str = "sedentary") -> Optional[float]:
        """
        Розрахунок денних калорій з урахуванням активності
        """
        if not bmr:
            return None
        
        activity_multipliers = {
            "sedentary": 1.2,       # Сидячий спосіб життя
            "lightly_active": 1.375, # Легка активність 1-3 дні/тиждень
            "moderately_active": 1.55, # Помірна активність 3-5 днів/тиждень
            "very_active": 1.725,   # Інтенсивна активність 6-7 днів/тиждень
            "extra_active": 1.9     # Дуже інтенсивна активність
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.2)
        return round(bmr * multiplier, 0)
    
    @staticmethod
    def calculate_water_intake(weight: Optional[float]) -> Optional[float]:
        """
        Розрахунок денної норми води (літри)
        Формула: 35 мл на кг ваги
        """
        if not weight or weight <= 0:
            return None
        
        water_ml = weight * 35
        return round(water_ml / 1000, 1)  # Конвертуємо в літри
    
    @staticmethod
    def calculate_muscle_mass(
        weight: Optional[float], 
        height: Optional[float], 
        age: Optional[int], 
        gender: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Розрахунок м'язової маси за формулою Janssen
        """
        if not all([weight, height, age, gender]) or weight <= 0 or height <= 0 or age <= 0:
            return None
        
        height_m = height / 100
        
        # Формула Janssen
        if gender.lower() in ['чоловік', 'male', 'м']:
            muscle_mass = (0.407 * weight) + (0.267 * height) - (0.049 * age) + 2.513
        else:  # жінка
            muscle_mass = (0.252 * weight) + (0.473 * height) - (0.048 * age) + 2.513
        
        muscle_mass = max(0, round(muscle_mass, 1))
        muscle_percentage = round((muscle_mass / weight) * 100, 1) if weight > 0 else 0
        
        # Категорії м'язової маси
        if gender.lower() in ['чоловік', 'male', 'м']:
            if muscle_percentage < 38:
                category = "Низький"
                color = "#EF4444"
            elif muscle_percentage < 44:
                category = "Нормальний" 
                color = "#10B981"
            else:
                category = "Високий"
                color = "#3B82F6"
        else:  # жінка
            if muscle_percentage < 31:
                category = "Низький"
                color = "#EF4444"
            elif muscle_percentage < 36:
                category = "Нормальний"
                color = "#10B981"
            else:
                category = "Високий"
                color = "#3B82F6"
        
        return {
            'mass_kg': muscle_mass,
            'percentage': muscle_percentage,
            'category': category,
            'color': color
        }
    
    @staticmethod
    def calculate_body_type(
        weight: Optional[float], 
        height: Optional[float], 
        age: Optional[int], 
        gender: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Визначення типу тілобудови (соматотип)
        """
        if not all([weight, height]) or weight <= 0 or height <= 0:
            return None
        
        bmi = FitnessCalculator.calculate_bmi(weight, height)
        if not bmi:
            return None
        
        body_fat = FitnessCalculator.calculate_body_fat_percentage(weight, height, age, gender)
        
        # Визначення соматотипу на основі ІМТ та жирового відсотка
        if bmi < 22 and (not body_fat or body_fat < 15):
            somatotype = "Ектоморф"
            description = "Тонке, худе тіло з вузькими кістками та низьким рівнем жиру. Метаболізм швидкий, важко набирати вагу, особливо м'язову масу."
            color = "#3B82F6"  # Блакитний
        elif 22 <= bmi <= 26 and (not body_fat or 15 <= body_fat <= 20):
            somatotype = "Мезоморф"
            description = "Атлетичне, мускулисте тіло з широкими плечима і вузькою талією. Метаболізм середній, легко нарощують м'язи, баланс між м'язовою масою і жиром."
            color = "#10B981"  # Зелений
        else:
            somatotype = "Ендоморф"
            description = "Широка кісткова структура, схильність до набору жиру. Метаболізм повільний, легко набирають вагу, мають труднощі з її втратою."
            color = "#EF4444"  # Червоний
        
        return {
            'type': somatotype,
            'description': description,
            'color': color
        }
    
    @staticmethod
    def calculate_heart_rate_status(hr_rest: Optional[int], age: Optional[int]) -> Optional[Dict[str, Any]]:
        """
        Оцінка статусу ЧСС у спокої
        """
        if not hr_rest or hr_rest <= 0:
            return None
        
        # Загальні норми ЧСС у спокої
        if hr_rest < 50:
            status = "❄️ Занадто низький"
            color = "#EF4444"
            description = "Може вимагати консультації лікаря"
        elif hr_rest < 60:
            status = "📉 Низький"
            color = "#F59E0B"
            description = "Часто у добре тренованих людей"
        elif hr_rest <= 80:
            status = "✅ Оптимальний"
            color = "#10B981"
            description = "Найкращі показники для здоров'я та фітнесу"
        elif hr_rest <= 90:
            status = "📈 Підвищений"
            color = "#F59E0B"
            description = "Може вказувати на низьку фізичну активність або стрес"
        else:
            status = "🔥 Високий"
            color = "#EF4444"
            description = "Ризик для здоров'я, може вимагати консультації лікаря"
        
        return {
            'status': status,
            'color': color,
            'description': description,
            'value': hr_rest
        }
    
    @staticmethod
    def calculate_heart_rate_zones(age: Optional[int]) -> Optional[Dict[str, Any]]:
        """
        Розрахунок пульсових зон тренувань
        """
        if not age or age <= 0:
            return None
        
        max_hr = 220 - age
        
        zones = {
            'max_hr': max_hr,
            'recovery': {
                'name': '😌 ВІДНОВЛЕННЯ',
                'percentage': '40-50%',
                'range': f"{int(max_hr * 0.4)} - {int(max_hr * 0.5)}",
                'color': '#10B981'
            },
            'fat_burn': {
                'name': '🔥 ЖИРОСПАЛЮВАННЯ',
                'percentage': '60-70%',
                'range': f"{int(max_hr * 0.6)} - {int(max_hr * 0.7)}",
                'color': '#F59E0B'
            },
            'aerobic': {
                'name': '🏃 АЕРОБНА',
                'percentage': '70-80%',
                'range': f"{int(max_hr * 0.7)} - {int(max_hr * 0.8)}",
                'color': '#3B82F6'
            },
            'anaerobic': {
                'name': '⚡ АНАЕРОБНА', 
                'percentage': '80-90%',
                'range': f"{int(max_hr * 0.8)} - {int(max_hr * 0.9)}",
                'color': '#8B5CF6'
            },
            'maximum': {
                'name': '🔥 МАКСИМАЛЬНА',
                'percentage': '90-100%',
                'range': f"{int(max_hr * 0.9)} - {max_hr}",
                'color': '#EF4444'
            }
        }
        
        return zones
    
    @staticmethod
    def calculate_daily_calories_detailed(
        bmr: Optional[float], 
        activity_level: str = "sedentary"
    ) -> Optional[Dict[str, Any]]:
        """
        Детальний розрахунок денних калорій з варіантами для різних цілей
        """
        if not bmr:
            return None
        
        activity_multipliers = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extra_active": 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.2)
        maintenance = round(bmr * multiplier, 0)
        
        # Для різних цілей
        weight_loss = round(maintenance * 0.8, 0)  # -20%
        weight_gain = round(maintenance * 1.2, 0)  # +20%
        
        return {
            'maintenance': int(maintenance),
            'weight_loss': int(weight_loss),
            'weight_gain': int(weight_gain),
            'activity_level': activity_level,
            'bmr': int(bmr)
        }
    
    @staticmethod
    def calculate_all_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Розрахунок всіх показників одночасно
        """
        weight = data.get('weight')
        height = data.get('height')
        age = data.get('age')
        gender = data.get('gender')
        activity_level = data.get('activity_level', 'sedentary')
        hr_rest = data.get('hr_rest')
        
        # Перетворюємо значення в правильні типи
        try:
            weight = float(weight) if weight else None
            height = float(height) if height else None
            age = int(age) if age else None
            hr_rest = int(hr_rest) if hr_rest else None
        except (ValueError, TypeError):
            weight = height = age = hr_rest = None
        
        # Основні розрахунки
        bmi = FitnessCalculator.calculate_bmi(weight, height)
        bmi_category = FitnessCalculator.get_bmi_category(bmi)
        body_fat = FitnessCalculator.calculate_body_fat_percentage(weight, height, age, gender)
        ideal_weight = FitnessCalculator.calculate_ideal_weight(height, gender)
        bmr = FitnessCalculator.calculate_bmr(weight, height, age, gender)
        daily_calories = FitnessCalculator.calculate_daily_calories(bmr, activity_level)
        daily_calories_detailed = FitnessCalculator.calculate_daily_calories_detailed(bmr, activity_level)
        water_intake = FitnessCalculator.calculate_water_intake(weight)
        
        # Додаткові розрахунки
        muscle_mass = FitnessCalculator.calculate_muscle_mass(weight, height, age, gender)
        body_type = FitnessCalculator.calculate_body_type(weight, height, age, gender)
        hr_status = FitnessCalculator.calculate_heart_rate_status(hr_rest, age)
        hr_zones = FitnessCalculator.calculate_heart_rate_zones(age)
        
        return {
            'bmi': bmi,
            'bmi_category': bmi_category,
            'body_fat_percentage': body_fat,
            'ideal_weight': ideal_weight,
            'bmr': bmr,
            'daily_calories': daily_calories,
            'daily_calories_detailed': daily_calories_detailed,
            'water_intake': water_intake,
            'muscle_mass': muscle_mass,
            'body_type': body_type,
            'hr_status': hr_status,
            'hr_zones': hr_zones
        }


# Функції для зворотної сумісності
def calculate_bmi(weight: Optional[float], height: Optional[float]) -> Optional[float]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_bmi(weight, height)


def get_bmi_category(bmi: Optional[float]) -> str:
    """Обгортка для статичного методу"""
    return FitnessCalculator.get_bmi_category(bmi)


def calculate_body_fat_percentage(
    weight: Optional[float], 
    height: Optional[float], 
    age: Optional[int], 
    gender: Optional[str]
) -> Optional[float]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_body_fat_percentage(weight, height, age, gender)


def calculate_ideal_weight(height: Optional[float], gender: Optional[str]) -> Optional[float]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_ideal_weight(height, gender)


def calculate_bmr(
    weight: Optional[float], 
    height: Optional[float], 
    age: Optional[int], 
    gender: Optional[str]
) -> Optional[float]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_bmr(weight, height, age, gender)


def calculate_daily_calories(bmr: Optional[float], activity_level: str = "sedentary") -> Optional[float]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_daily_calories(bmr, activity_level)


def calculate_water_intake(weight: Optional[float]) -> Optional[float]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_water_intake(weight)


def calculate_all_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Обгортка для статичного методу"""
    return FitnessCalculator.calculate_all_metrics(data)
