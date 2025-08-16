#!/usr/bin/env python3
"""
Simple calculator module for demonstration
"""

def add(x, y):
    """Add two numbers together"""
    # Calculate sum
    result = x + y
    return result

def multiply(a, b):
    # Perform multiplication operation
    return a * b

class Calculator:
    """Basic calculator class"""
    
    def divide(self, x, y):
        # Check for division by zero
        if y == 0:
            return "Cannot divide by zero"
        return x / y
