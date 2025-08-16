#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая программа калькулятора для тестирования перевода кода
Этот модуль предоставляет базовые математические операции
"""

import math

class Calculator:
    """Базовый класс калькулятора с общими операциями"""
    
    def __init__(self):
        # Инициализируем калькулятор с настройками по умолчанию
        self.history = []
        self.last_result = 0
        print("Калькулятор успешно инициализирован")
    
    def add(self, a, b):
        """Сложить два числа и вернуть результат"""
        # Выполняем операцию сложения
        result = a + b
        self.history.append(f"Сложение: {a} + {b} = {result}")
        print("Сложение выполнено")  # Логируем операцию
        return result
    
    def multiply(self, x, y):
        """Умножить два числа друг на друга"""
        # Вычисляем произведение
        product = x * y
        self.history.append(f"Умножение: {x} * {y} = {product}")
        return product
    
    def get_square_root(self, number):
        """Вычислить квадратный корень числа"""
        if number < 0:
            error_message = "Невозможно вычислить квадратный корень отрицательного числа"
            print(error_message)
            return None
        
        # Используем библиотеку math для точного вычисления
        result = math.sqrt(number)
        success_message = "Вычисление квадратного корня успешно завершено"
        print(success_message)
        return result
    
    def show_history(self):
        """Показать историю вычислений"""
        if not self.history:
            print("Вычисления еще не выполнялись")
            return
        
        # Выводим все предыдущие вычисления
        print("История вычислений:")
        for i, operation in enumerate(self.history, 1):
            print(f"{i}. {operation}")

def main():
    """Главная функция для демонстрации использования калькулятора"""
    # Создаем экземпляр калькулятора
    calc = Calculator()
    
    # Выполняем тестовые вычисления
    result1 = calc.add(10, 5)
    print(f"Первый результат: {result1}")
    
    result2 = calc.multiply(4, 7)
    print(f"Второй результат: {result2}")
    
    # Тестируем функцию квадратного корня
    sqrt_result = calc.get_square_root(16)
    if sqrt_result:
        print(f"Результат квадратного корня: {sqrt_result}")
    
    # Показываем историю вычислений
    calc.show_history()
    
    completion_message = "Выполнение программы успешно завершено"
    print(completion_message)

if __name__ == "__main__":
    # Точка входа в программу
    print("Запускаем программу калькулятора...")
    main()
    print("Спасибо за использование калькулятора!")
