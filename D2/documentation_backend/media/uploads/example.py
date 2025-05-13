"""
Модуль для работы с математическими операциями.
Содержит функции для базовых вычислений.
"""

def add(a: float, b: float) -> float:
    """
    Складывает два числа.
    
    Аргументы:
        a: Первое число
        b: Второе число
    
    Возвращает:
        Сумму a и b
    """
    return a + b

def subtract(a: float, b: float) -> float:
    """Вычитает b из a"""
    return a - b

class Calculator:
    """
    Класс для сложных математических операций.
    
    Атрибуты:
        version: Версия калькулятора
    """
    
    version = "1.0"
    
    def multiply(self, a: float, b: float) -> float:
        """Умножает a на b"""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        Делит a на b
        
        Исключения:
            ValueError: Если b равно 0
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b